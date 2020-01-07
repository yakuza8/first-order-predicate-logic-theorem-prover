"""
Entities of First Order Predicate Logic will be defined under this package

In the domain, there can be four types of entity:
* Predicate :   Predicates are the top level entities and they can take any other entity except for predicate.
                One or more than one entity can be child of predicates. Also, they can be negated with '~'.
                Their names should start with lower case letter.
* Variable  :   Variables are atomic values whose names start with a lower case letter.
* Function  :   Functions are the entities which are pretty similar to predicates, but they cannot be negated
                and take other functions as its children. Their names should start with lower case letter.
* Constant  :   Constants are also atomic values whose names start with an upper case letter.
"""
import unittest

NEGATION_SYMBOL = '~'
BLOCK_OPEN_SYMBOL = '('
ENTITY_SEPARATE_SYMBOL = ','
BLOCK_CLOSE_SYMBOL = ')'
IGNORE_EMPTY_CHARACTER = ' '
PREDICATE_SPECIFIC_SYMBOLS = [NEGATION_SYMBOL]
FUNCTION_AND_PREDICATE_SPECIFIC_SYMBOLS = [BLOCK_OPEN_SYMBOL, ENTITY_SEPARATE_SYMBOL, BLOCK_CLOSE_SYMBOL]


def children_entity_parser(children: str):
    """
    The procedure of separating of children entities properly from the given parameter
    The main aim is not verification/correctness of children entities, but separating them and verifying whether
    the parameter is separable or not
    :param children: Children entities as string
    :return: Parsed children entities as a list of strings
    """
    # Symbol stack which will be used verification of closing symbol matchings
    symbol_stack = []
    # Verified children list
    parsed_children = []

    # Initialization of local variables
    start_index_of_current_child, index = 0, 0

    # Iterate over each character in the given parameter
    for index, char in enumerate(children):
        if char == ENTITY_SEPARATE_SYMBOL and len(symbol_stack) == 0:
            # If it is separation symbol and symbol stack is empty meaning that no problem exists for the current child
            # Append the current child into parsed children container and update indexes
            parsed_children.append(children[start_index_of_current_child: index])
            start_index_of_current_child = index + 1
        elif char == BLOCK_OPEN_SYMBOL:
            # If it is opening block symbol, then push it to the symbol stack so that we can verify closing symbols
            symbol_stack.append(char)
        elif char == BLOCK_CLOSE_SYMBOL:
            # Otherwise, check symbol stack if there is non matching symbols. If so return nothing else remove symbol
            if len(symbol_stack) == 0:
                return None
            else:
                symbol_stack.pop(0)

    if len(symbol_stack) != 0:
        return None

    # In case of empty parameter
    parsed_children.append(children[start_index_of_current_child: index + 1])
    return parsed_children


class CommonEntityUnitTest(unittest.TestCase):

    def test_valid_children_parsing(self):
        children1 = '  a , f ( y, h, z) , c ,   g (  a  )    '
        output1 = children_entity_parser(children1)
        self.assertEqual(4, len(output1))

        children2 = '  f ( g(p,r, s), h, z) , c ,  g (  a,q,z  )    '
        output2 = children_entity_parser(children2)
        self.assertEqual(3, len(output2))

        children3 = '  h(h(h(x))) '
        output3 = children_entity_parser(children3)
        self.assertEqual(1, len(output3))

        children4 = 'h ( h ( h ( x,  y, z , h( y ) ) ) ) '
        output4 = children_entity_parser(children4)
        self.assertEqual(1, len(output4))

        children5 = ' '
        output5 = children_entity_parser(children5)
        self.assertEqual(1, len(output5))

        children6 = ' a '
        output6 = children_entity_parser(children6)
        self.assertEqual(1, len(output6))

        children7 = ''
        output7 = children_entity_parser(children7)
        self.assertEqual(1, len(output7))

    def test_invalid_children_parsing(self):
        children1 = '  a , f ( y, h, z) ) , c ,   g (  a  )    '
        output1 = children_entity_parser(children1)
        self.assertIsNone(output1)

        children2 = '  f ( g(p,r, s), h, z) , c) ,  g (  a,q,z  )    '
        output2 = children_entity_parser(children2)
        self.assertIsNone(output2)

        children3 = '  h(h(h(x, ())) '
        output3 = children_entity_parser(children3)
        self.assertIsNone(output3)

        children4 = 'h ( h ( h ( x, ( y, z , h( y ) ) ) ) '
        output4 = children_entity_parser(children4)
        self.assertIsNone(output4)


if __name__ == '__main__':
    unittest.main()
