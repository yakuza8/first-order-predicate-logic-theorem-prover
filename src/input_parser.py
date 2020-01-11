from typing import TextIO

from src.entity import children_entity_parser


class InputParser(object):
    KNOWLEDGE_BASE_LABEL = 'knowledge_base'
    NEGATED_THEOREM_PREDICATES_LABEL = 'negated_theorem_predicates'

    @staticmethod
    def parse(file: TextIO):
        from src import Predicate
        from src import ProblemState

        # Read file and get predicates
        problem_input = eval(file.read())
        knowledge_base = problem_input[InputParser.KNOWLEDGE_BASE_LABEL]
        negated_theorem_predicates = problem_input[InputParser.NEGATED_THEOREM_PREDICATES_LABEL]

        knowledge_base = [
            [Predicate.build(predicate) for predicate in children_entity_parser(knowledge_base_predicate)]
            for knowledge_base_predicate in knowledge_base
        ]

        negated_theorem_predicates = [
            [Predicate.build(predicate) for predicate in children_entity_parser(negated_theorem_predicate)]
            for negated_theorem_predicate in negated_theorem_predicates
        ]

        if knowledge_base is None or negated_theorem_predicates is None:
            raise ValueError("Please check the given input again and fix the format issue!")

        return ProblemState(knowledge_base, negated_theorem_predicates)
