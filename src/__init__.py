import unittest
from typing import List

from .entity import children_entity_parser
from .entity.predicate import Predicate


class ProblemState(object):
    """
    Problem state composed from first order predicates to be proved

    Method to prove the given problem is Resolution Refutation Technique
    by searching knowledge base with breadth first strategy where the statement
    is composed of two main variables

    * Knowledge base: Group of predicates which creates knowledge space in the problem
    * Negated version of clauses to be proved: Group of clauses which are negated beforehand
    so that we can refute the target clauses via trying to reach contradiction in knowledge
    space
    """

    def __init__(self, knowledge_base: List[List[Predicate]],
                 negated_theorem_clauses: List[List[Predicate]]):
        # Combine all the clauses into a single clause list
        from src.entity.clause import Clause
        self.clauses = [Clause(clause) for clause in knowledge_base]
        self.clauses.extend([Clause(clause) for clause in negated_theorem_clauses])


class ProblemStateUnitTest(unittest.TestCase):

    @staticmethod
    def _predicate_parser(predicates):
        return [Predicate.build(predicate) for predicate in children_entity_parser(predicates)]

    def test_constructor(self):
        knowledge_base = [ProblemStateUnitTest._predicate_parser('p(y),q(P, A),r(x)'),
                          ProblemStateUnitTest._predicate_parser('p(y),r(A)')]

        negated_theorem_clauses = [ProblemStateUnitTest._predicate_parser('p(y),l(y, A),k(A)'),
                                   ProblemStateUnitTest._predicate_parser('m(y),q(y, A),r(A)'),
                                   ProblemStateUnitTest._predicate_parser('l(y)')]

        problem_state = ProblemState(knowledge_base=knowledge_base,
                                     negated_theorem_clauses=negated_theorem_clauses)

        self.assertEqual(5, len(problem_state.clauses))
