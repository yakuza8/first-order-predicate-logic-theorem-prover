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

NEGATION_SYMBOL = '~'
BLOCK_OPEN_SYMBOL = '('
ENTITY_SEPARATE_SYMBOL = ','
BLOCK_CLOSE_SYMBOL = ')'
PREDICATE_SPECIFIC_SYMBOLS = [NEGATION_SYMBOL]
FUNCTION_AND_PREDICATE_SPECIFIC_SYMBOLS = [BLOCK_OPEN_SYMBOL, ENTITY_SEPARATE_SYMBOL, BLOCK_CLOSE_SYMBOL]
