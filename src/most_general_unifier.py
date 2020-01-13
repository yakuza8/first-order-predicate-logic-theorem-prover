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


class MostGeneralUnifier(object):

    @staticmethod
    def unify(expression1: Union[FirstOrderPredicateLogicEntity, List[FirstOrderPredicateLogicEntity]],
              expression2: Union[FirstOrderPredicateLogicEntity, List[FirstOrderPredicateLogicEntity]]) -> \
            Tuple[bool, Optional[Substitution]]:
        """
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
            result, substitution = MostGeneralUnifier._unify_atomic_entity(first_element_of_expression1, first_element_of_expression2)

            # If it is unsuccessful, then propagate this information
            if not result:
                return False, None

            # Apply retrieved substitution to the rest of entities
            substitution_applied_rest_of_expression1 = MostGeneralUnifier.apply_substitution(
                rest_of_children_of_expression1, substitution)
            substitution_applied_rest_of_expression2 = MostGeneralUnifier.apply_substitution(
                rest_of_children_of_expression2, substitution)

            result, unification_of_rest = MostGeneralUnifier.unify(substitution_applied_rest_of_expression1, substitution_applied_rest_of_expression2)

            if not result:
                return False, None
            else:
                # Compose both obtained unification substitutions to each other and then return as a result
                return True, MostGeneralUnifier.apply_composition_to_substitution(substitution, unification_of_rest)
        else:
            # They cannot be unifiable
            return False, None

    @staticmethod
    def _unify_atomic_entity(expression1: FirstOrderPredicateLogicEntity,
                             expression2: FirstOrderPredicateLogicEntity) -> Tuple[bool, Optional[Substitution]]:
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
                return True, None
            if type_expression1 == Variable:
                if expression1 in expression2:
                    return False, None
                return True, Substitution(expression2, expression1)
            else:
                if expression2 in expression1:
                    return False, None
                return True, Substitution(expression1, expression2)
        elif type_expression1 != type_expression2:
            # If none of them variable and their types are not the same, then fail unification
            return False, None
        else:
            if type_expression1 == Constant:
                # In case of constants, just check their names
                return type_expression1.get_name() == type_expression2.get_name(), None
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
    def apply_substitution(elements: List[FirstOrderPredicateLogicEntity], substitution: Substitution) -> \
            List[FirstOrderPredicateLogicEntity]:
        pass

    @staticmethod
    def apply_composition_to_substitution():
        pass
