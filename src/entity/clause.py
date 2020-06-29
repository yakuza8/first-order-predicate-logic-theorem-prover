import itertools
import unittest

from typing import List, Optional, Union, Tuple

from . import children_entity_parser
from .predicate import Predicate
from ..most_general_unifier import MostGeneralUnifier


class Clause(object):
    """
    Class for keeping predicates together and some several multi-predicate supported functionality
    """

    def __init__(self, predicates: List[Optional[Predicate]]):
        self.predicates = predicates
        self.predicates = sorted(self.predicates, key=lambda predicate: (predicate.get_name(), predicate.is_negated))

    def __repr__(self):
        return str(self)

    def __str__(self):
        return str(self.predicates)

    def __eq__(self, other):
        if not isinstance(other, Clause):
            return False
        return str(self.predicates) == str(other)

    def __hash__(self):
        return hash(str(self.predicates))

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
            non_negated_predicates, negated_predicates = Clause._predicate_separator_by_sign(group)
            for non_negated_predicate in non_negated_predicates:
                for negated_predicate in negated_predicates:
                    unification, _ = MostGeneralUnifier.unify(non_negated_predicate.get_child(),
                                                              negated_predicate.get_child())
                    # If any of them can be unified, it means we got tautology
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
            # Take common keys of each dict so that we can check if there exists any substitution which unifies them
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

    def resolve_with(self, other: 'Clause') -> Tuple[Union['Clause', None], Union['Clause', None]]:
        """
        Function to resolve two clauses
        :param other: Other clause
        :return: Resolvent clause in case of resolution otherwise None
        """
        for predicate1, predicate2 in itertools.product(self.predicates, other.predicates):
            # Try to unify them if they represent the same predicate but they have different negation states
            if predicate1.get_name() == predicate2.get_name() and predicate1.is_negated != predicate2.is_negated:
                result, substitutions = MostGeneralUnifier.unify(predicate1.get_child(), predicate2.get_child())
                # Compose new predicate with combined predicates of both clauses except for resolvent predicates
                new_clause_children = [Predicate.build(str(predicate)) for predicate in self.predicates]
                new_clause_children.extend([Predicate.build(str(predicate)) for predicate in other.predicates])
                new_clause_children.remove(predicate1)
                new_clause_children.remove(predicate2)
                # Return composed clause
                return Clause(MostGeneralUnifier.apply_substitution(new_clause_children, substitutions)), substitutions
        # If none of them can be resolved, return none
        return None, None

    @staticmethod
    def _predicate_separator_by_sign(predicates):
        """
        Grouping functionality of predicates
        """
        non_negated, negated = [], []
        for predicate in predicates:
            (non_negated, negated)[predicate.is_negated].append(predicate)
        return non_negated, negated

    @staticmethod
    def _fast_check_by_negation_and_name(clause1: 'Clause', clause2: 'Clause') -> bool:
        """
        Fast subsumption check procedure which try to check there is any different predicate exists in other clause
        so that the first clause cannot subsume
        :param clause1: Clause to check subsume onto other clause
        :param clause2: Clause which assumed to be subsumed by the first clause
        :return: Boolean flag representing all predicates in the first clause are subset of that for second clause
        """
        clause1 = set(map(lambda predicate: (predicate.is_negated, predicate.get_name()), clause1.predicates))
        clause2 = set(map(lambda predicate: (predicate.is_negated, predicate.get_name()), clause2.predicates))
        return clause1.issubset(clause2)


class ClauseUnitTest(unittest.TestCase):

    @staticmethod
    def _predicate_parser(predicates):
        return [Predicate.build(predicate) for predicate in children_entity_parser(predicates)]

    def test_basic_properties(self):
        predicate_string = 'p(y), q(y,A), r(A)'
        predicates = ClauseUnitTest._predicate_parser(predicate_string)
        predicates2 = ClauseUnitTest._predicate_parser(predicate_string + ', p(x)')

        clause = Clause(predicates)
        clause2 = Clause(predicates)
        clause3 = Clause(predicates2)

        expected_string = '[' + ', '.join(str(p) for p in predicates) + ']'

        self.assertEqual(expected_string, str(clause))
        self.assertEqual(expected_string, repr(clause))

        self.assertEqual(hash(clause), hash(clause2))
        self.assertNotEqual(hash(clause), hash(clause3))

        self.assertEqual(clause, clause2)
        self.assertNotEqual(clause, clause3)
        self.assertNotEqual(clause, 8)

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
        # Should pass fast check since we have Predicate p
        clause1 = Clause(ClauseUnitTest._predicate_parser('p(y)'))
        clause2 = Clause(ClauseUnitTest._predicate_parser('q(z),p(v)'))
        self.assertTrue(Clause._fast_check_by_negation_and_name(clause1, clause2))

        # Should not pass since we have negated Predicate p
        clause1 = Clause(ClauseUnitTest._predicate_parser('p(y)'))
        clause2 = Clause(ClauseUnitTest._predicate_parser('q(z),~p(v)'))
        self.assertFalse(Clause._fast_check_by_negation_and_name(clause1, clause2))

        # Should pass fast check since we have Predicate p and more general than second clause
        clause1 = Clause(ClauseUnitTest._predicate_parser('p(y)'))
        clause2 = Clause(ClauseUnitTest._predicate_parser('q(z),p(k(l, ABC))'))
        self.assertTrue(Clause._fast_check_by_negation_and_name(clause1, clause2))

        # Should not pass since we have negated Predicate p
        clause1 = Clause(ClauseUnitTest._predicate_parser('p(y)'))
        clause2 = Clause(ClauseUnitTest._predicate_parser('q(z),~p(k(l, ABC))'))
        self.assertFalse(Clause._fast_check_by_negation_and_name(clause1, clause2))

        # Should pass fast check since we have Predicate p and more general than second clause
        clause1 = Clause(ClauseUnitTest._predicate_parser('p(y)'))
        clause2 = Clause(ClauseUnitTest._predicate_parser('q(z),p(ABC, ACB, BAC, BCA, CAB, CBA)'))
        self.assertTrue(Clause._fast_check_by_negation_and_name(clause1, clause2))

        # Should not pass since we have negated Predicate p
        clause1 = Clause(ClauseUnitTest._predicate_parser('p(y)'))
        clause2 = Clause(ClauseUnitTest._predicate_parser('q(z),~p(ABC, ACB, BAC, BCA, CAB, CBA)'))
        self.assertFalse(Clause._fast_check_by_negation_and_name(clause1, clause2))

        # Should not pass since we have negated Predicate q
        clause1 = Clause(ClauseUnitTest._predicate_parser('p(y),~q(x)'))
        clause2 = Clause(ClauseUnitTest._predicate_parser('q(z),p(ABC, ACB, BAC, BCA, CAB, CBA)'))
        self.assertFalse(Clause._fast_check_by_negation_and_name(clause1, clause2))

        # Should pass since we have negated Predicate p and q
        clause1 = Clause(ClauseUnitTest._predicate_parser('p(y),q(x)'))
        clause2 = Clause(ClauseUnitTest._predicate_parser('q(z),p(ABC, ACB, BAC, BCA, CAB, CBA)'))
        self.assertTrue(Clause._fast_check_by_negation_and_name(clause1, clause2))

        # Should not pass since we have additional Predicate z
        clause1 = Clause(ClauseUnitTest._predicate_parser('p(y),q(x),z(m)'))
        clause2 = Clause(ClauseUnitTest._predicate_parser('q(z),p(ABC, ACB, BAC, BCA, CAB, CBA)'))
        self.assertFalse(Clause._fast_check_by_negation_and_name(clause1, clause2))

        # Should pass we have subset of other clause
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
        # Should subsume { A / x }
        clause1 = Clause(ClauseUnitTest._predicate_parser('p(x)'))
        clause2 = Clause(ClauseUnitTest._predicate_parser('p(A)'))
        self.assertTrue(clause1.does_subsume(clause2))

        # Should subsume { H / z }
        clause1 = Clause(ClauseUnitTest._predicate_parser('p(A),q(z)'))
        clause2 = Clause(ClauseUnitTest._predicate_parser('p(B),z(f),q(H),p(A)'))
        self.assertTrue(clause1.does_subsume(clause2))

        # Should not subsume { B / A } is not applicable both are constants
        clause1 = Clause(ClauseUnitTest._predicate_parser('p(A),q(z)'))
        clause2 = Clause(ClauseUnitTest._predicate_parser('p(B),z(f),q(H)'))
        self.assertFalse(clause1.does_subsume(clause2))

        # Should subsume { A / x } also we have extra predicate
        clause1 = Clause(ClauseUnitTest._predicate_parser('p(x)'))
        clause2 = Clause(ClauseUnitTest._predicate_parser('p(A),q(y)'))
        self.assertTrue(clause1.does_subsume(clause2))

        # Should not subsume { y / B } is not applicable constant is more specific than variable
        clause1 = Clause(ClauseUnitTest._predicate_parser('p(B)'))
        clause2 = Clause(ClauseUnitTest._predicate_parser('p(x),q(y)'))
        self.assertFalse(clause1.does_subsume(clause2))

        # Should not subsume { B / A } is not applicable both are constants
        clause1 = Clause(ClauseUnitTest._predicate_parser('p(B)'))
        clause2 = Clause(ClauseUnitTest._predicate_parser('p(A),q(y)'))
        self.assertFalse(clause1.does_subsume(clause2))

        clause1 = Clause(ClauseUnitTest._predicate_parser('p(x),q(x)'))
        clause2 = Clause(ClauseUnitTest._predicate_parser('p(y),q(y),r(y,B)'))
        self.assertTrue(clause1.does_subsume(clause2))

        # Should not subsume { y / A } is not applicable constant is more specific than variable
        clause1 = Clause(ClauseUnitTest._predicate_parser('p(x),q(A)'))
        clause2 = Clause(ClauseUnitTest._predicate_parser('p(y),q(y),r(y,B)'))
        self.assertFalse(clause1.does_subsume(clause2))

    def test_resolve_with_with_match(self):
        clause1 = Clause(ClauseUnitTest._predicate_parser('~q(y), r(y)'))
        clause2 = Clause(ClauseUnitTest._predicate_parser('~r(A)'))

        resolvent, substitution = clause1.resolve_with(clause2)

        self.assertIsNotNone(resolvent)
        self.assertIsNotNone(substitution)

        expected_resolvent = Clause(ClauseUnitTest._predicate_parser('~q(y)'))
        expected_substitution_list = '[A / y]'

        self.assertEqual(expected_resolvent, resolvent)
        self.assertEqual(expected_substitution_list, str(substitution))

    def test_resolve_with_with_no_match(self):
        clause1 = Clause(ClauseUnitTest._predicate_parser('~q(y), r(y)'))
        clause2 = Clause(ClauseUnitTest._predicate_parser('p(A,f(t))'))

        resolvent, substitution = clause1.resolve_with(clause2)

        self.assertIsNone(resolvent)
        self.assertIsNone(substitution)
