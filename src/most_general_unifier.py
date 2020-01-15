import unittest
from typing import Union, List, Tuple, Optional

from src.entity.first_order_predicate_logic_entity import FirstOrderPredicateLogicEntity
from src.entity.constant import Constant
from src.entity.function import Function
from src.entity.variable import Variable


class Substitution(object):
    """
    Substitution definition to be used in most general unifier procedure
    where each substitution is composed of
    * Substitute: Expression which will be replaced instead of right hand side of substitution
    * Variable: Expression to be replaced with substitute

    Sample substitution examples:
    1) {A / x}
    2) {x / y}
    3) {f(x) / w}
    """

    def __init__(self, substitute: FirstOrderPredicateLogicEntity, variable: Variable):
        self.substitute = substitute
        self.variable = variable

    def __repr__(self):
        return str(self)

    def __str__(self):
        return repr(self.substitute) + " / " + repr(self.variable)

    def __eq__(self, other):
        if not isinstance(other, Substitution):
            return False
        return self.substitute == other.substitute and self.variable == other.variable

    def apply_substitution(self, applied_substitution: 'Substitution'):
        # If the current substitute can be replaced then immediately replace it
        if self.substitute == applied_substitution.variable:
            self.substitute = applied_substitution.substitute
        else:
            # Otherwise, try to replace its children
            self.substitute.find_variable_and_apply_substitution(applied_substitution.substitute,
                                                                 applied_substitution.variable)


class MostGeneralUnifier(object):

    @staticmethod
    def unify(expression1: Union[FirstOrderPredicateLogicEntity, List[FirstOrderPredicateLogicEntity]],
              expression2: Union[FirstOrderPredicateLogicEntity, List[FirstOrderPredicateLogicEntity]]) -> \
            Tuple[bool, Optional[List[Substitution]]]:
        """
        Unification Procedure
        =====================
        The following procedure is applied while unification:

        1) First check whether both expressions are atomic element or not. If so, then redirect them into unification of
         atomic elements
        2) If both of them are composite entities, then
            * Check whether they meet length property. If they cannot, then return FAIL
            * Else apply the following operations
                * Fetch first elements of each composite
                * Unify them and get result. If result says that they cannot be unifiable, then return FAIL
                * If they can be, then apply substitution to rest of composites and check whether rest can be unifiable
                * In case of non-unifiable entities, then FAIL, otherwise compose this substitution with the previous
                substitution and return the composite substitution

        :param expression1: The first expression as a first order predicate logic entity
        :param expression2: The second expression as a first order predicate logic entity
        :return: Composition result of expression in case of SUCCESS otherwise None in case of FAILURE
        """
        type_expression1 = type(expression1)
        type_expression2 = type(expression2)

        # If both of them are atomic entities
        if type_expression1 != List or type_expression2 != List:
            return MostGeneralUnifier._unify_atomic_entity(expression1, expression2)
        elif type_expression1 == List or type_expression2 == List:
            # They have to be of the same length
            if len(expression1) != len(expression2):
                return False, None

            first_element_of_expression1 = expression1[0]
            rest_of_children_of_expression1 = expression1[1:]
            first_element_of_expression2 = expression2[0]
            rest_of_children_of_expression2 = expression2[1:]

            # Get substitution result of the first elements
            result, substitutions = MostGeneralUnifier \
                ._unify_atomic_entity(first_element_of_expression1, first_element_of_expression2)

            # If it is unsuccessful, then propagate this information
            if not result:
                return False, None

            # Apply retrieved substitution to the rest of entities
            substitution_applied_rest_of_expression1 = MostGeneralUnifier.apply_substitution(
                rest_of_children_of_expression1, substitutions)
            substitution_applied_rest_of_expression2 = MostGeneralUnifier.apply_substitution(
                rest_of_children_of_expression2, substitutions)

            result, unification_of_rest = MostGeneralUnifier \
                .unify(substitution_applied_rest_of_expression1, substitution_applied_rest_of_expression2)

            if not result:
                return False, None
            else:
                # Compose both obtained unification substitutions to each other and then return as a result
                return True, MostGeneralUnifier.apply_composition_to_substitution(substitutions, unification_of_rest)
        else:
            # They cannot be unifiable
            return False, None

    @staticmethod
    def _unify_atomic_entity(expression1: FirstOrderPredicateLogicEntity,
                             expression2: FirstOrderPredicateLogicEntity) -> Tuple[bool, Optional[List[Substitution]]]:
        """
        Unification of single entity type of First Order Predicate Logic
        Unification may be done in the following entities:

        * Variable - variable: Can be unified in any order
        * Variable - constant: Can be unified by writing constant into where variable exists
        * Variable - function: Can be unified by writing function into where variable exists
        * Constant - variable: Can be unified by writing constant into where variable exists
        * Constant - constant: Can be unified if both constants are the same by EMPTY_SUBSTITUTION
        * Constant - function: Cannot be unified
        * Function - variable: Can be unified by writing function into where variable exists
        * Function - constant: Cannot be unified
        * Function - function: Can be unified if both functions have the same naming and their children can also be unified
        """
        type_expression1 = type(expression1)
        type_expression2 = type(expression2)
        if type_expression1 == Variable or type_expression2 == Variable:
            if expression1 == expression2:
                # If they are the same, then return EMPTY_SUBSTITUTION
                return True, []
            if type_expression1 == Variable:
                if expression1 in expression2:
                    return False, None
                return True, [Substitution(expression2, expression1)]
            else:
                if expression2 in expression1:
                    return False, None
                return True, [Substitution(expression1, expression2)]
        elif type_expression1 != type_expression2:
            # If none of them variable and their types are not the same, then fail unification
            return False, None
        else:
            if type_expression1 == Constant:
                # In case of constants, just check their names
                return expression1.get_name() == expression2.get_name(), None
            elif type_expression1 == Function:
                if expression1.get_name() == expression2.get_name():
                    # If function names, are the same, then return unification result of their children
                    return MostGeneralUnifier.unify(expression1.get_child(), expression2.get_child())
                else:
                    # If functions do not have the same name, then fail unification
                    return False, None
            else:
                raise ValueError('Unknown type for unification.')

    @staticmethod
    def apply_substitution(elements: List[FirstOrderPredicateLogicEntity], substitution: List[Substitution]) -> \
            List[FirstOrderPredicateLogicEntity]:
        pass

    @staticmethod
    def apply_composition_to_substitution(first_substitutions: List[Substitution],
                                          second_substitutions: List[Substitution]):
        """
        Composition of Substitutions
        ============================
        The composition procedure of list of substitutions to each other where
        all the substitutions in the second list is composed into the entities
        in the first list at the beginning. Then, unit substitutions are eliminated
        to get final substitution list.

        Reference: http://www.csd.uwo.ca/~moreno/cs2209_moreno/read/read6-unification.pdf (Pages: 12-13)
        """
        # First apply composition to first substitutions with second substitutions
        for substitution_to_be_compose in first_substitutions:
            for substitution_to_be_applied in second_substitutions:
                substitution_to_be_compose.apply_substitution(substitution_to_be_applied)

        # Then do not add the same variable more than once
        first_substitutions_variables = list(map(lambda s: s.variable, first_substitutions))
        for substitution in second_substitutions:
            if substitution.variable not in first_substitutions_variables:
                first_substitutions.append(substitution)
        # And remove unnecessary substitutions which variables substitutes itself
        first_substitutions = list(filter(lambda s: s.substitute != s.variable, first_substitutions))
        return first_substitutions


class MGUUnitTest(unittest.TestCase):

    def test_composition_of_substitution_1(self):
        empty_substitution = []
        first_substitution = [
            Substitution(Function.build('f(y)'), Variable.build('x')),
            Substitution(Variable.build('z'), Variable.build('y'))
        ]

        self.assertEqual(first_substitution, MostGeneralUnifier.apply_composition_to_substitution(empty_substitution, first_substitution))
        self.assertEqual(first_substitution, MostGeneralUnifier.apply_composition_to_substitution(first_substitution, empty_substitution))

    def test_composition_of_substitution_2(self):
        first_substitution = [
            Substitution(Function.build('f(y)'), Variable.build('x')),
            Substitution(Variable.build('z'), Variable.build('y'))
        ]

        second_substitution = [
            Substitution(Variable.build('a'), Variable.build('x')),
            Substitution(Variable.build('b'), Variable.build('y')),
            Substitution(Variable.build('y'), Variable.build('z'))
        ]

        expected = [
            Substitution(Function.build('f(b)'), Variable.build('x')),
            Substitution(Variable.build('y'), Variable.build('z'))
        ]

        output = MostGeneralUnifier.apply_composition_to_substitution(first_substitution, second_substitution)
        self.assertEqual(expected, output)

    def test_composition_of_substitution_3(self):
        first_substitution = [
            Substitution(Function.build('g(x, y)'), Variable.build('z'))
        ]

        second_substitution = [
            Substitution(Constant.build('A'), Variable.build('x')),
            Substitution(Constant.build('B'), Variable.build('y')),
            Substitution(Variable.build('w'), Variable.build('c')),
            Substitution(Constant.build('D'), Variable.build('z'))
        ]

        expected = [
            Substitution(Function.build('g(A, B)'), Variable.build('z')),
            Substitution(Constant.build('A'), Variable.build('x')),
            Substitution(Constant.build('B'), Variable.build('y')),
            Substitution(Variable.build('w'), Variable.build('c'))
        ]

        output = MostGeneralUnifier.apply_composition_to_substitution(first_substitution, second_substitution)
        self.assertEqual(expected, output)

    def test_composition_of_substitution_4(self):
        first_substitution = [
            Substitution(Function.build('f(x)'), Variable.build('u'))
        ]

        second_substitution = [
            Substitution(Function.build('k(f(x))'), Variable.build('y'))
        ]

        third_substitution = [
            Substitution(Function.build('k(f(x))'), Variable.build('z'))
        ]

        fourth_substitution = [
            Substitution(Function.build('h(w)'), Variable.build('x'))
        ]

        expected = [
            Substitution(Function.build('f(h(w))'), Variable.build('u')),
            Substitution(Function.build('k(f(h(w)))'), Variable.build('y')),
            Substitution(Function.build('k(f(h(w)))'), Variable.build('z')),
            Substitution(Function.build('h(w)'), Variable.build('x'))
        ]

        output = []
        output = MostGeneralUnifier.apply_composition_to_substitution(output, first_substitution)
        output = MostGeneralUnifier.apply_composition_to_substitution(output, second_substitution)
        output = MostGeneralUnifier.apply_composition_to_substitution(output, third_substitution)
        output = MostGeneralUnifier.apply_composition_to_substitution(output, fourth_substitution)
        self.assertEqual(expected, output)
