import unittest

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
    def validate(value: str) -> bool:
        try:
            value = value.strip()
            return value.isalnum() and value[0].isupper()
        except IndexError:
            return False


class ConstantUnitTest(unittest.TestCase):

    def test_validate_is_lower(self):
        constant1 = 'abc1'
        self.assertFalse(Constant.validate(constant1))

        constant2 = 'Abc1'
        self.assertTrue(Constant.validate(constant2))

        constant3 = 'ABC1'
        self.assertTrue(Constant.validate(constant3))

        constant4 = 'aBC1'
        self.assertFalse(Constant.validate(constant4))

        constant4 = '1BC1'
        self.assertFalse(Constant.validate(constant4))

    def test_validate_is_alnum(self):
        constant1 = 'Abc '
        self.assertTrue(Constant.validate(constant1))

        constant2 = ' Abc'
        self.assertTrue(Constant.validate(constant2))

        constant3 = 'A BC'
        self.assertFalse(Constant.validate(constant3))

        constant4 = 'A,BC'
        self.assertFalse(Constant.validate(constant4))

        constant5 = 'A1b2c'
        self.assertTrue(Constant.validate(constant5))

    def test_validate_zero_length(self):
        constant1 = 'Abc'
        self.assertTrue(Constant.validate(constant1))

        constant2 = ''
        self.assertFalse(Constant.validate(constant2))

if __name__ == '__main__':
    unittest.main()
