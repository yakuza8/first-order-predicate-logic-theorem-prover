import unittest
from typing import List, Optional

from src.entity import BLOCK_OPEN_SYMBOL, ENTITY_SEPARATE_SYMBOL, BLOCK_CLOSE_SYMBOL, children_entity_parser
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

    def __eq__(self, other):
        if not isinstance(other, Function):
            return False
        return self.get_name() == other.get_name() and len(self.get_child()) == len(other.get_child()) \
            and all([child_tuple[0] == child_tuple[1] for child_tuple in zip(self.get_child(), other.get_child())])

    def __contains__(self, item):
        return self == item or any([item in child for child in self.children])

    def get_name(self) -> str:
        return self.name

    def has_child(self) -> bool:
        return True

    def get_child(self) -> Optional[List[FirstOrderPredicateLogicEntity]]:
        return self.children

    def find_variable_and_apply_substitution(self, substitute: 'FirstOrderPredicateLogicEntity',
                                             variable: 'FirstOrderPredicateLogicEntity'):
        for index, value in enumerate(self.children):
            if value == variable:
                self.children[index] = substitute
            elif value.has_child:
                value.find_variable_and_apply_substitution(substitute, variable)

    def is_less_specific(self, other: 'FirstOrderPredicateLogicEntity') -> bool:
        if isinstance(other, Function) and self.name == other.name:
            return all(child1 == child2 or child1.is_less_specific(child2)for child1, child2 in zip(self.children, other.children))
        return False

    @staticmethod
    def build(value: str) -> Optional[FirstOrderPredicateLogicEntity]:
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
                children = children_entity_parser(value[first_open_block_index + 1: last_close_block_index])
                if children is None:
                    return None
                # Inside of a function there must be these entities only
                built_children = [Function.build(child) or v.Variable.build(child) or c.Constant.build(child) for child
                                  in children]
                if all(built_children):
                    return Function(function_name, built_children)
            return None
        except (ValueError, IndexError):
            return None


class FunctionUnitTest(unittest.TestCase):

    def test_basic_properties(self):
        function_str = 'f(a,b,c,g(a))'
        function = Function.build(function_str)

        self.assertEqual('f', function.get_name())
        self.assertTrue(function.has_child())
        self.assertIsNotNone(function.get_child())
        self.assertEqual(4, len(function.get_child()))

    def test_equality(self):
        function1 = Function.build('f(a,b,c,g(a))')
        function2 = Function.build('f(a,b,c,g(a))')
        function3 = Function.build('f(a,b,c,g(b))')

        self.assertEqual(function1, function2)
        self.assertNotEqual(function1, function3)

    def test_in_operator(self):
        import src.entity.constant as c
        import src.entity.variable as v

        function1 = Function.build('f(a,B,c,g(a))')
        function2 = Function.build('f(a,B,c,g(a))')
        function3 = Function.build('f(a,B,c,g(x))')

        constant1 = c.Constant.build('B')
        variable1 = v.Variable.build('b')
        constant2 = c.Constant.build('A')
        variable2 = v.Variable.build('a')
        function4 = Function.build('g(a)')
        function5 = Function.build('g(y)')

        self.assertTrue(function2 in function1)
        self.assertFalse(function3 in function1)
        self.assertTrue(constant1 in function1)
        self.assertFalse(variable1 in function1)
        self.assertFalse(constant2 in function1)
        self.assertTrue(variable2 in function1)
        self.assertTrue(function4 in function1)
        self.assertFalse(function5 in function1)

    def test_build_open_block_symbol(self):
        function = 'fx,y)))'
        self.assertFalse(Function.build(function))

    def test_build_close_block_symbol(self):
        function = 'f(((x,y'
        self.assertFalse(Function.build(function))

    def test_build_zero_length_function_name(self):
        function = '(a,b,c,f(a))'
        self.assertFalse(Function.build(function))

    def test_build_invalid_function_name(self):
        function1 = 'A(a,b,c,f(a))'
        self.assertFalse(Function.build(function1))

        function2 = 'f A (a,b,c,f(a))'
        self.assertFalse(Function.build(function2))

    def test_build_valid_function(self):
        function1 = 'f(a,b,c,g(a))'
        output1 = Function.build(function1)
        self.assertTrue(output1)
        self.assertEqual(4, len(output1.children))

        function2 = 'f(a,b,c,g(a, b, c))'
        output2 = Function.build(function2)
        self.assertTrue(output2)
        self.assertEqual(4, len(output2.children))

        function3 = 'f(a,h(h(h(h(a, h(a, b))))),c,g(a))'
        output3 = Function.build(function3)
        self.assertTrue(output3)
        self.assertEqual(4, len(output3.children))

    def test_build_valid_function_with_spaces(self):
        function = '  f( a , b , c ,   g (  a  )    )         '
        output = Function.build(function)
        self.assertTrue(output)
        self.assertEqual(4, len(output.children))

    def test_build_invalid_children(self):
        function1 = '  f( a , b , c A ,   g (  a  )    )         '
        self.assertFalse(Function.build(function1))

        function2 = '  f( a , b, , cA ,   g (  a  )    )         '
        self.assertFalse(Function.build(function2))

        function3 = '  f( a , b, , cA ,   g ( ( a  )    )         '
        self.assertFalse(Function.build(function3))

    def test_is_less_specific(self):
        function1 = Function.build('f(a)')
        function2 = Function.build('f(A)')
        self.assertTrue(function1.is_less_specific(function2))

        function1 = Function.build('f(A)')
        function2 = Function.build('f(A)')
        self.assertTrue(function1.is_less_specific(function2))

        function1 = Function.build('f(B)')
        function2 = Function.build('f(A)')
        self.assertFalse(function1.is_less_specific(function2))

        function1 = Function.build('f(a, B)')
        function2 = Function.build('f(A, x)')
        self.assertFalse(function1.is_less_specific(function2))

        function1 = Function.build('f(a, b)')
        function2 = Function.build('f(A, x)')
        self.assertTrue(function1.is_less_specific(function2))

        function1 = Function.build('f(a, g(z))')
        function2 = Function.build('f(A, g(m))')
        self.assertTrue(function1.is_less_specific(function2))

        function1 = Function.build('f(a, g(H))')
        function2 = Function.build('f(A, g(m))')
        self.assertFalse(function1.is_less_specific(function2))

        function1 = Function.build('f(a, g(z))')
        function2 = Function.build('f(A, p(m))')
        self.assertFalse(function1.is_less_specific(function2))

        function1 = Function.build('f(a, H)')
        function2 = Function.build('f(A, g(m))')
        self.assertFalse(function1.is_less_specific(function2))

        function1 = Function.build('f(a, b)')
        function2 = Function.build('f(A, g(m))')
        self.assertTrue(function1.is_less_specific(function2))

        function1 = Function.build('f(A, b)')
        function2 = Function.build('f(A, g(m))')
        self.assertTrue(function1.is_less_specific(function2))

        function1 = Function.build('f(A, b)')
        function2 = Function.build('f(A, g(m))')
        self.assertTrue(function1.is_less_specific(function2))
