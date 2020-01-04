import unittest
from typing import List

from src.entity import BLOCK_OPEN_SYMBOL, ENTITY_SEPARATE_SYMBOL, BLOCK_CLOSE_SYMBOL
from src.entity.first_order_predicate_logic_entity import FirstOrderPredicateLogicEntity


class Function(FirstOrderPredicateLogicEntity):
    """
    Functions are the entities which are pretty similar to predicates, but they cannot be negated
    and take other functions as its children. Their names should start with lower case letter.
    """

    def __init__(self, name: str, children: List[FirstOrderPredicateLogicEntity]):
        self.name = name
        self.children = children

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.name + BLOCK_OPEN_SYMBOL \
               + ENTITY_SEPARATE_SYMBOL.join(repr(child) for child in self.children) + BLOCK_CLOSE_SYMBOL

    @staticmethod
    def validate(value: str) -> bool:
        import src.entity.constant as c
        import src.entity.variable as v
        try:
            # Remove whitespaces beginning and end of the string
            value = value.strip()
            # Find blocks
            first_open_block_index = value.index(BLOCK_OPEN_SYMBOL)
            last_close_block_index = value.rindex(BLOCK_CLOSE_SYMBOL)
            function_name = value[:first_open_block_index].strip()
            # It should be alphanumeric and must be start with lower case
            if function_name.isalnum() and function_name[0].islower():
                children = value[first_open_block_index + 1: last_close_block_index].split(ENTITY_SEPARATE_SYMBOL)
                # Inside of a function there must be these entities only
                return all(Function.validate(child) or v.Variable.validate(child) or c.Constant.validate(child)
                           for child in children)
            else:
                return False
        except (ValueError, IndexError):
            return False


class FunctionUnitTest(unittest.TestCase):

    def test_validate_open_block_symbol(self):
        function = 'fx,y)))'
        self.assertFalse(Function.validate(function))

    def test_validate_close_block_symbol(self):
        function = 'f(((x,y'
        self.assertFalse(Function.validate(function))

    def test_validate_zero_length_function_name(self):
        function = '(a,b,c,f(a))'
        self.assertFalse(Function.validate(function))

    def test_validate_invalid_function_name(self):
        function1 = 'A(a,b,c,f(a))'
        self.assertFalse(Function.validate(function1))

        function2 = 'f A (a,b,c,f(a))'
        self.assertFalse(Function.validate(function2))

    def test_validate_valid_function(self):
        function = 'f(a,b,c,g(a))'
        self.assertTrue(Function.validate(function))

    def test_validate_valid_function_with_spaces(self):
        function = '  f( a , b , c ,   g (  a  )    )         '
        self.assertTrue(Function.validate(function))

    def test_validate_invalid_children(self):
        function1 = '  f( a , b , c A ,   g (  a  )    )         '
        self.assertFalse(Function.validate(function1))

        function2 = '  f( a , b, , cA ,   g (  a  )    )         '
        self.assertFalse(Function.validate(function2))

        function3 = '  f( a , b, , cA ,   g ( ( a  )    )         '
        self.assertFalse(Function.validate(function3))


if __name__ == '__main__':
    unittest.main()
