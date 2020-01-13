import unittest
from typing import List, Optional

from src.entity import BLOCK_OPEN_SYMBOL, ENTITY_SEPARATE_SYMBOL, BLOCK_CLOSE_SYMBOL, NEGATION_SYMBOL, children_entity_parser
from src.entity.first_order_predicate_logic_entity import FirstOrderPredicateLogicEntity


class Predicate(FirstOrderPredicateLogicEntity):
    """
    Predicates are the top level entities and they can take any other entity except for predicate.
    One or more than one entity can be child of predicates. Also, they can be negated with '~'.
    Their names should start with lower case letter.
    """

    def __init__(self, name: str, children: List[FirstOrderPredicateLogicEntity], is_negated: bool = False):
        self.name = name
        self.children = children
        self.is_negated = is_negated

    def __repr__(self):
        return str(self)

    def __str__(self):
        return ('' if not self.is_negated else NEGATION_SYMBOL) + self.name + \
               BLOCK_OPEN_SYMBOL + ENTITY_SEPARATE_SYMBOL.join(repr(child) for child in self.children) + BLOCK_CLOSE_SYMBOL

    def get_name(self) -> str:
        return self.name

    def has_child(self) -> bool:
        return True

    def get_child(self) -> Optional[List[FirstOrderPredicateLogicEntity]]:
        return self.children

    @staticmethod
    def build(value: str) -> Optional[FirstOrderPredicateLogicEntity]:
        import src.entity.constant as c
        import src.entity.function as f
        import src.entity.variable as v
        
        try:
            # Remove whitespaces beginning and end of the string 
            value = value.strip()
            # Find blocks
            first_open_block_index = value.index(BLOCK_OPEN_SYMBOL)
            last_close_block_index = value.rindex(BLOCK_CLOSE_SYMBOL)
            # Check negation
            predicate_name_with_negation = value[:first_open_block_index].strip()
            is_negated = predicate_name_with_negation[0] == NEGATION_SYMBOL
            predicate_name = predicate_name_with_negation[1:] if is_negated else predicate_name_with_negation
            predicate_name = predicate_name.strip()
            # It should be alphanumeric and must be start with lower case
            if predicate_name.isalnum() and predicate_name[0].islower():
                children = children_entity_parser(value[first_open_block_index + 1: last_close_block_index])
                if children is None:
                    return None
                # Inside of a predicate there must be these entities only
                built_children = [f.Function.build(child) or v.Variable.build(child) or c.Constant.build(child) for child in children]
                if all(built_children):
                    return Predicate(predicate_name, built_children, is_negated)
            return None
        except (ValueError, IndexError):
            return None


class PredicateUnitTest(unittest.TestCase):

    def test_basic_properties(self):
        predicate_str = '~p(a,b,c,g(a))'
        predicate = Predicate.build(predicate_str)

        self.assertEqual('p', predicate.get_name())
        self.assertTrue(predicate.has_child())
        self.assertIsNotNone(predicate.get_child())
        self.assertEqual(4, len(predicate.get_child()))

    def test_build_open_block_symbol(self):
        predicate = 'px,y)))'
        self.assertFalse(Predicate.build(predicate))

    def test_build_close_block_symbol(self):
        predicate = 'p(((x,y'
        self.assertFalse(Predicate.build(predicate))

    def test_build_zero_length_predicate_name(self):
        predicate = '(a,b,c,f(a))'
        self.assertFalse(Predicate.build(predicate))

    def test_build_invalid_predicate_name(self):
        predicate1 = 'A(a,b,c,f(a))'
        self.assertFalse(Predicate.build(predicate1))

        predicate2 = 'p A (a,b,c,f(a))'
        self.assertFalse(Predicate.build(predicate2))

    def test_build_valid_predicate(self):
        predicate1 = 'p(a,b,c,g(a))'
        output1 = Predicate.build(predicate1)
        self.assertTrue(output1)
        self.assertFalse(output1.is_negated)
        self.assertEqual(4, len(output1.children))

        predicate2 = '~p(a,b,c,g(a))'
        output2 = Predicate.build(predicate2)
        self.assertTrue(output2)
        self.assertTrue(output2.is_negated)
        self.assertEqual(4, len(output2.children))

    def test_build_valid_predicate_with_spaces(self):
        predicate1 = ' ~  p (  a , b , c ,   g (  a,  b,  c  )    )         '
        output1 = Predicate.build(predicate1)
        self.assertTrue(output1)
        self.assertTrue(output1.is_negated)
        self.assertEqual(4, len(output1.children))

        predicate2 = ' ~  p (  a , f ( y, h, z) , c ,   g (  a  )    )         '
        output2 = Predicate.build(predicate2)
        self.assertTrue(output2)
        self.assertTrue(output2.is_negated)
        self.assertEqual(4, len(output2.children))

        predicate3 = ' ~  p (  a , b , c ,   g (  a  )    )         '
        output3 = Predicate.build(predicate3)
        self.assertTrue(output3)
        self.assertTrue(output3.is_negated)
        self.assertEqual(4, len(output3.children))

    def test_build_invalid_children(self):
        predicate1 = '  p ( a , b , c A ,   g (  a  )    )         '
        self.assertFalse(Predicate.build(predicate1))

        predicate2 = '  p ( a , b, , cA ,   g (  a  )    )         '
        self.assertFalse(Predicate.build(predicate2))

        predicate3 = '  p ( a , b, , cA ,   g (  a  )    )         '
        self.assertFalse(Predicate.build(predicate3))


if __name__ == '__main__':
    unittest.main()