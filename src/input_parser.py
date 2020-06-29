import unittest
from typing import TextIO

from .entity import children_entity_parser


class InputParser(object):
    KNOWLEDGE_BASE_LABEL = 'knowledge_base'
    NEGATED_THEOREM_PREDICATES_LABEL = 'negated_theorem_predicates'

    @staticmethod
    def parse(file: TextIO):
        from src import Predicate
        from src import ProblemState

        # Read file and get predicates
        problem_input = eval(file.read())

        try:
            knowledge_base = problem_input[InputParser.KNOWLEDGE_BASE_LABEL]
            negated_theorem_predicates = problem_input[InputParser.NEGATED_THEOREM_PREDICATES_LABEL]
        except KeyError as e:
            raise ValueError("Please check the given input again and fix the format issue!") from e

        knowledge_base = [[Predicate.build(predicate) for predicate in
                           children_entity_parser(knowledge_base_predicate)] for
                          knowledge_base_predicate in knowledge_base]

        negated_theorem_predicates = [[Predicate.build(predicate) for predicate in
                                       children_entity_parser(negated_theorem_predicate)] for
                                      negated_theorem_predicate in negated_theorem_predicates]

        if any(None in p for p in knowledge_base) or any(
                None in p for p in negated_theorem_predicates):
            raise ValueError("Please check the given input again and fix the format issue!")

        return ProblemState(knowledge_base, negated_theorem_predicates)


class InputParserUnitTest(unittest.TestCase):

    def test_input_parser(self):
        from io import StringIO
        file = StringIO(str({
            "knowledge_base": ["~p(x),q(x)", "p(y),r(y)", "~q(z),s(z)", "~r(t),s(t)"],
            "negated_theorem_predicates": ["~s(A)"]
        }))
        problem_state = InputParser.parse(file)
        self.assertEqual(5, len(problem_state.clauses))

    def test_input_parser_with_invalid_input_1(self):
        from io import StringIO
        file = StringIO(str({
            "negated_theorem_predicates": ["~s(A)"]
        }))

        with self.assertRaises(ValueError):
            _ = InputParser.parse(file)

    def test_input_parser_with_invalid_input_2(self):
        from io import StringIO
        file = StringIO(str({
            "knowledge_base": ["~p(x),q(x)", "p(y),r(y)", "~q(z),s(z)", "~r(t),s(t)"],
            "negated_theorem_predicates": ["p A (a,b,c,f(a))"]
        }))

        with self.assertRaises(ValueError):
            _ = InputParser.parse(file)
