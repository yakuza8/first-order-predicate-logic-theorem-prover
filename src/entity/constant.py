import unittest
from typing import Optional, List

from src.entity.first_order_predicate_logic_entity import FirstOrderPredicateLogicEntity


class Constant(FirstOrderPredicateLogicEntity):
    """
    Constants are also atomic values whose names start with an upper case letter.
    """
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if not isinstance(other, Constant):
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
        pass

    @staticmethod
    def build(value: str) -> Optional[FirstOrderPredicateLogicEntity]:
        try:
            value = value.strip()
            if value.isalnum() and value[0].isupper():
                return Constant(value)
            return None
        except IndexError:
            return None


class ConstantUnitTest(unittest.TestCase):

    def test_basic_properties(self):
        constant_str = 'Abc1'
        constant = Constant.build(constant_str)

        self.assertEqual(constant_str, constant.get_name())
        self.assertFalse(constant.has_child())
        self.assertIsNone(constant.get_child())

    def test_equality(self):
        constant1 = Constant.build('Abc')
        constant2 = Constant.build('Abc')
        constant3 = Constant.build('Abc2')

        self.assertEqual(constant1, constant2)
        self.assertNotEqual(constant1, constant3)

    def test_in_operator(self):
        constant1 = Constant.build('Abc')
        constant2 = Constant.build('Abc')
        constant3 = Constant.build('Abc2')

        self.assertTrue(constant1 in constant2)
        self.assertFalse(constant1 in constant3)

    def test_build_is_lower(self):
        constant1 = 'abc1'
        self.assertFalse(Constant.build(constant1))

        constant2 = 'Abc1'
        self.assertTrue(Constant.build(constant2))

        constant3 = 'ABC1'
        self.assertTrue(Constant.build(constant3))

        constant4 = 'aBC1'
        self.assertFalse(Constant.build(constant4))

        constant4 = '1BC1'
        self.assertFalse(Constant.build(constant4))

    def test_build_is_alnum(self):
        constant1 = 'Abc '
        self.assertTrue(Constant.build(constant1))

        constant2 = ' Abc'
        self.assertTrue(Constant.build(constant2))

        constant3 = 'A BC'
        self.assertFalse(Constant.build(constant3))

        constant4 = 'A,BC'
        self.assertFalse(Constant.build(constant4))

        constant5 = 'A1b2c'
        self.assertTrue(Constant.build(constant5))

    def test_build_zero_length(self):
        constant1 = 'Abc'
        self.assertTrue(Constant.build(constant1))

        constant2 = ''
        self.assertFalse(Constant.build(constant2))


if __name__ == '__main__':
    unittest.main()
