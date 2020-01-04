import unittest
from typing import Optional

from src.entity.first_order_predicate_logic_entity import FirstOrderPredicateLogicEntity


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

    @staticmethod
    def build(value: str) -> Optional[FirstOrderPredicateLogicEntity]:
        try:
            value = value.strip()
            if value.isalnum() and value[0].islower():
                return Variable(value)
            return None
        except IndexError:
            return None


class VariableUnitTest(unittest.TestCase):

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


if __name__ == '__main__':
    unittest.main()
