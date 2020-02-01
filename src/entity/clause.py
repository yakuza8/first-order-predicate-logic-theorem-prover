import itertools
import unittest
from enum import Enum
from typing import List, Optional

from src import Predicate
from src.entity import children_entity_parser
from src.most_general_unifier import MostGeneralUnifier


class Subsumption(Enum):
    LEFT_CLAUSE_SUBSUMES = 1
    RIGHT_CLAUSE_SUBSUMES = 2
    NO_SUBSUMPTION = 3


class Clause(object):
    def __init__(self, predicates: List[Optional[Predicate]]):
        self.predicates = predicates
        self.predicates = sorted(self.predicates, key=lambda predicate: (predicate.get_name(), predicate.is_negated))

    def get_clause_length(self):
        return len(self.predicates)

    def has_tautology(self) -> bool:
        """
        Tautology checking procedure in the list of predicates
        :return: Boolean flag representing whether the list has tautology or not. In case of having tautology True will
        be returned, otherwise False.
        """
        # Group each predicate by their name
        for key, group in itertools.groupby(self.predicates, lambda predicate: predicate.get_name()):
            # Separate them by their negation and test all the unification results of permutations of paired predicates
            non_negated, negated = Clause._predicate_separator_by_sign(group)
            for non_negated_predicate in non_negated:
                for negated_predicate in negated:
                    unification, _ = MostGeneralUnifier.unify(non_negated_predicate.get_child(),
                                                              negated_predicate.get_child())
                    if unification:
                        return True
        # If not achieved any tautology, it means we have no tautology
        return False

    def does_subsume(self, other: 'Clause') -> bool:
        """
        Subsumption controlling function where the function tries to find
        whether the other clause is more specific than the current clause
        :param other: Other clause to check subsumption
        :return: Boolean flag representing that the current clause subsumes the other clause
        """
        # If no meet naming and negation match as a subset then immediately return False since subsumption cannot occur
        fast_check_result = Clause._fast_check_by_negation_and_name(self, other)
        if fast_check_result:
            # Group by both name and negation
            first_group = {key: list(group) for key, group in
                           itertools.groupby(self.predicates, lambda p: (p.get_name(), p.is_negated))}
            second_group = {key: list(group) for key, group in
                            itertools.groupby(other.predicates, lambda p: (p.get_name(), p.is_negated))}
            # Then take common keys of each dict so that we can check if there exists any substitution which unifies them
            common_keys = first_group.keys() & second_group.keys()
            # And filter common predicates
            filtered_first_group = [first_group[key] for key in common_keys]
            filtered_second_group = [second_group[key] for key in common_keys]
            # Then take multiplication of them
            for multiplication in itertools.product(itertools.product(*filtered_first_group),
                                                    itertools.product(*filtered_second_group)):
                # Each of the predicates must be the same or be less specific than the other's predicates
                result = all(child == other_child or child.is_less_specific(other_child)
                             for child, other_child in zip(multiplication[0], multiplication[1]))
                if result:
                    return True
            # If none of them holds the condition, then return False
            return False
        else:
            # If fast check fails
            return False

    @staticmethod
    def _predicate_separator_by_sign(predicates):
        non_negated, negated = [], []
        for predicate in predicates:
            (non_negated, negated)[predicate.is_negated].append(predicate)
        return non_negated, negated

    @staticmethod
    def _fast_check_by_negation_and_name(clause1: 'Clause', clause2: 'Clause') -> bool:
        clause1 = set(map(lambda predicate: (predicate.is_negated, predicate.get_name()), clause1.predicates))
        clause2 = set(map(lambda predicate: (predicate.is_negated, predicate.get_name()), clause2.predicates))
        return clause1.issubset(clause2)


class ClauseUnitTest(unittest.TestCase):

    @staticmethod
    def _predicate_parser(predicates):
        return [Predicate.build(predicate) for predicate in children_entity_parser(predicates)]

    def test_get_predicate_length(self):
        clause = Clause([])
        self.assertEqual(0, clause.get_clause_length())

        clause = Clause(ClauseUnitTest._predicate_parser('p(y)'))
        self.assertEqual(1, clause.get_clause_length())

        clause = Clause(ClauseUnitTest._predicate_parser('p(y),q(y, A),r(A)'))
        self.assertEqual(3, clause.get_clause_length())

    def test_has_tautology_empty_list(self):
        clause = Clause([])
        self.assertFalse(clause.has_tautology())

    def test_has_tautology_singleton_list(self):
        clause = Clause(ClauseUnitTest._predicate_parser('p(y)'))
        self.assertFalse(clause.has_tautology())

    def test_has_tautology_with_different_predicates(self):
        clause = Clause(ClauseUnitTest._predicate_parser('p(y),q(y, A),r(A)'))
        self.assertFalse(clause.has_tautology())

    def test_has_tautology_variables(self):
        clause = Clause(ClauseUnitTest._predicate_parser('p(y),q(y, A),r(A),~p(y)'))
        self.assertTrue(clause.has_tautology())

    def test_has_tautology_variable_constant(self):
        clause = Clause(ClauseUnitTest._predicate_parser('p(y),q(y, A),r(A),~p(H)'))
        self.assertTrue(clause.has_tautology())

    def test_has_tautology_variable_function(self):
        clause = Clause(ClauseUnitTest._predicate_parser('p(y),q(y, A),r(A),~p(c(a, T))'))
        self.assertTrue(clause.has_tautology())

    def test_has_tautology_constant(self):
        clause = Clause(ClauseUnitTest._predicate_parser('p(H),q(y, A),r(A),~p(H)'))
        self.assertTrue(clause.has_tautology())

        clause = Clause(ClauseUnitTest._predicate_parser('p(J),q(y, A),r(A),~p(H)'))
        self.assertFalse(clause.has_tautology())

    def test_has_tautology_function(self):
        clause = Clause(ClauseUnitTest._predicate_parser('p(x, r(ABC, k)),q(y, A),r(A),~p(x, r(GTX, k))'))
        self.assertFalse(clause.has_tautology())

        clause = Clause(ClauseUnitTest._predicate_parser('p(x, r(ABC, k)),q(y, A),r(A),~p(x, r(b, k))'))
        self.assertTrue(clause.has_tautology())

        clause = Clause(ClauseUnitTest._predicate_parser('p(x, r(ABC, k)),q(y, A),r(A),~p(u, r(b, k))'))
        self.assertTrue(clause.has_tautology())

    def test_fast_check_valid(self):
        clause1 = Clause(ClauseUnitTest._predicate_parser('p(y)'))
        clause2 = Clause(ClauseUnitTest._predicate_parser('q(z),p(v)'))
        self.assertTrue(Clause._fast_check_by_negation_and_name(clause1, clause2))

        clause1 = Clause(ClauseUnitTest._predicate_parser('p(y)'))
        clause2 = Clause(ClauseUnitTest._predicate_parser('q(z),~p(v)'))
        self.assertFalse(Clause._fast_check_by_negation_and_name(clause1, clause2))

        clause1 = Clause(ClauseUnitTest._predicate_parser('p(y)'))
        clause2 = Clause(ClauseUnitTest._predicate_parser('q(z),p(k(l, ABC))'))
        self.assertTrue(Clause._fast_check_by_negation_and_name(clause1, clause2))

        clause1 = Clause(ClauseUnitTest._predicate_parser('p(y)'))
        clause2 = Clause(ClauseUnitTest._predicate_parser('q(z),~p(k(l, ABC))'))
        self.assertFalse(Clause._fast_check_by_negation_and_name(clause1, clause2))

        clause1 = Clause(ClauseUnitTest._predicate_parser('p(y)'))
        clause2 = Clause(ClauseUnitTest._predicate_parser('q(z),p(ABC, ACB, BAC, BCA, CAB, CBA)'))
        self.assertTrue(Clause._fast_check_by_negation_and_name(clause1, clause2))

        clause1 = Clause(ClauseUnitTest._predicate_parser('p(y)'))
        clause2 = Clause(ClauseUnitTest._predicate_parser('q(z),~p(ABC, ACB, BAC, BCA, CAB, CBA)'))
        self.assertFalse(Clause._fast_check_by_negation_and_name(clause1, clause2))

        clause1 = Clause(ClauseUnitTest._predicate_parser('p(y)'))
        clause2 = Clause(ClauseUnitTest._predicate_parser('q(z),p(ABC, ACB, BAC, BCA, CAB, CBA)'))
        self.assertTrue(Clause._fast_check_by_negation_and_name(clause1, clause2))

        clause1 = Clause(ClauseUnitTest._predicate_parser('p(y),~q(x)'))
        clause2 = Clause(ClauseUnitTest._predicate_parser('q(z),p(ABC, ACB, BAC, BCA, CAB, CBA)'))
        self.assertFalse(Clause._fast_check_by_negation_and_name(clause1, clause2))

        clause1 = Clause(ClauseUnitTest._predicate_parser('p(y),q(x)'))
        clause2 = Clause(ClauseUnitTest._predicate_parser('q(z),p(ABC, ACB, BAC, BCA, CAB, CBA)'))
        self.assertTrue(Clause._fast_check_by_negation_and_name(clause1, clause2))

        clause1 = Clause(ClauseUnitTest._predicate_parser('p(y),q(x),z(m)'))
        clause2 = Clause(ClauseUnitTest._predicate_parser('q(z),p(ABC, ACB, BAC, BCA, CAB, CBA)'))
        self.assertFalse(Clause._fast_check_by_negation_and_name(clause1, clause2))

        clause1 = Clause(ClauseUnitTest._predicate_parser('p(y),p(x),p(o)'))
        clause2 = Clause(ClauseUnitTest._predicate_parser('q(z),p(ABC, ACB, BAC, BCA, CAB, CBA)'))
        self.assertTrue(Clause._fast_check_by_negation_and_name(clause1, clause2))

    def test_subsumption_with_fast_check_holds(self):
        clause1 = Clause(ClauseUnitTest._predicate_parser('~p(y)'))
        clause2 = Clause(ClauseUnitTest._predicate_parser('q(z),p(v)'))
        self.assertFalse(clause1.does_subsume(clause2))

        clause1 = Clause(ClauseUnitTest._predicate_parser('~p(y),p(u)'))
        clause2 = Clause(ClauseUnitTest._predicate_parser('q(z),p(v)'))
        self.assertFalse(clause1.does_subsume(clause2))

        clause1 = Clause(ClauseUnitTest._predicate_parser('~p(y),~p(u)'))
        clause2 = Clause(ClauseUnitTest._predicate_parser('p(z),p(v)'))
        self.assertFalse(clause1.does_subsume(clause2))

    def test_subsumption_with_fast_check_does_not_hold(self):
        clause1 = Clause(ClauseUnitTest._predicate_parser('p(x)'))
        clause2 = Clause(ClauseUnitTest._predicate_parser('p(A)'))
        self.assertTrue(clause1.does_subsume(clause2))

        clause1 = Clause(ClauseUnitTest._predicate_parser('p(A),q(z)'))
        clause2 = Clause(ClauseUnitTest._predicate_parser('p(B),z(f),q(H),p(A)'))
        self.assertTrue(clause1.does_subsume(clause2))
