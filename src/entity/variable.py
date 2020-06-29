import unittest
from typing import Optional, List

from .first_order_predicate_logic_entity import FirstOrderPredicateLogicEntity


class Variable(FirstOrderPredicateLogicEntity):
    """
    Variables are atomic values whose names start with a lower case letter.
    """

    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.name

    def __eq__(self, other):
        """
        Check other instance to be Variable as well and their names are equal
        """
        if not isinstance(other, Variable):
            return False
        return self.get_name() == other.get_name()

    def __contains__(self, item):
        return self == item

    def get_name(self) -> str:
        return self.name

    def has_child(self) -> bool:
        return False

    def get_child(self) -> Optional[List[FirstOrderPredicateLogicEntity]]:
        return None

    def find_variable_and_apply_substitution(self, substitute: 'FirstOrderPredicateLogicEntity',
                                             variable: 'FirstOrderPredicateLogicEntity'):
        """
        Variables cannot be iterated and their children cannot substituted so do nothing
        """
        pass

    def is_less_specific(self, other: 'FirstOrderPredicateLogicEntity') -> bool:
        """
        In any case, Variable entities are the least specific entity in the domain
        """
        return True

    @staticmethod
    def build(value: str) -> Optional[FirstOrderPredicateLogicEntity]:
        """
        Variable builder where unnecessary whitespaces are removed and first letter of entity is checked to be lowercase
        """
        value = value.strip()
        if value.isalnum() and value[0].islower():
            return Variable(value)
        return None


class VariableUnitTest(unittest.TestCase):

    def test_basic_properties(self):
        variable_str = 'abc1'
        variable = Variable.build(variable_str)

        self.assertEqual(variable_str, variable.get_name())
        self.assertEqual(variable_str, repr(variable))
        self.assertFalse(variable.has_child())
        self.assertIsNone(variable.get_child())

    def test_equality(self):
        variable1 = Variable.build('abc')
        variable2 = Variable.build('abc')
        variable3 = Variable.build('abc2')

        self.assertEqual(variable1, variable2)
        self.assertNotEqual(variable1, variable3)

    def test_in_operator(self):
        variable1 = Variable.build('abc')
        variable2 = Variable.build('abc')
        variable3 = Variable.build('abc2')

        self.assertTrue(variable1 in variable2)
        self.assertFalse(variable1 in variable3)

    def test_build_is_lower(self):
        variable1 = 'abc1'
        self.assertTrue(Variable.build(variable1))

        variable2 = 'Abc1'
        self.assertFalse(Variable.build(variable2))

        variable3 = 'ABC1'
        self.assertFalse(Variable.build(variable3))

        variable4 = 'aBC1'
        self.assertTrue(Variable.build(variable4))

        variable4 = '1BC1'
        self.assertFalse(Variable.build(variable4))

    def test_build_is_alnum(self):
        variable1 = 'abc '
        self.assertTrue(Variable.build(variable1))

        variable2 = ' abc'
        self.assertTrue(Variable.build(variable2))

        variable3 = 'a BC'
        self.assertFalse(Variable.build(variable3))

        variable4 = 'a,BC'
        self.assertFalse(Variable.build(variable4))

        variable5 = 'a1b2c'
        self.assertTrue(Variable.build(variable5))

    def test_build_zero_length(self):
        variable1 = 'abc'
        self.assertTrue(Variable.build(variable1))

        variable2 = ''
        self.assertFalse(Variable.build(variable2))
