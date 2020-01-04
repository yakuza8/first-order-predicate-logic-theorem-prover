import unittest
from typing import Optional

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
