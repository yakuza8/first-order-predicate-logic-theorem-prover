# First Order Predicate Logic Theorem Prover

## Description
The main aim of this project is to implement autonomous theorem prover for **First Order Predicate Logic** where
proof method is **Proof by Refutation** with **Breadth First Search** strategy.

For first order predicate logic entities, _Variable_, _Constant_, _Function_ and _Predicate_ are used where
there are several semantics and rules on each entity. The mentioned semantics and rules are listed below:

### Rule set: 
Entity Name | Definition | Rules
------------|------------|------
Variable    | The most generic entity (also atomic) which can substitute any other entity | Name of variable should start with lower case 
Constant    | The most specific atomic entity which represents phenomenon in the world | Name of constant should start with upper case 
Function    | Transformation entities in the world which maps several entities to other entities, they can take other functions, variables and constants as its children | Name of function should start with lower case and predicates cannot be child of any function 
Predicate   | Entities which represent facts in the knowledge base, they can be negated for carrying the opposite meaning of itself, and they can take other functions, variables and constants as its children | Name of predicate should start with lower case, negation symbol is '~' symbol and predicates cannot take other predicates as their children

