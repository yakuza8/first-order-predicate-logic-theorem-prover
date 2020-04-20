# First Order Predicate Logic Theorem Prover

## Description
The main aim of this project is to implement autonomous theorem prover for **First Order Predicate Logic** where
proof method is **Proof by Refutation** with **Breadth First Search** strategy.

For first order predicate logic entities, _Variable_, _Constant_, _Function_ and _Predicate_ are used where
there are several semantics and rules on each entity. The mentioned semantics and rules are listed below:

### Domain Information: 
Entity Name | Definition | Rules
------------|------------|------
Variable    | The most generic entity (also atomic) which can substitute any other entity | Name of variable should start with lower case 
Constant    | The most specific atomic entity which represents phenomenon in the world | Name of constant should start with upper case 
Function    | Transformation entities in the world which map several entities to other entities, they can take other functions, variables and constants as its children | Name of function should start with lower case and predicates cannot be child of any function 
Predicate   | Entities which represent facts in the knowledge base, they can be negated for carrying the opposite meaning of itself, and they can take other functions, variables and constants as its children | Name of predicate should start with lower case, negation symbol is '~' symbol and predicates cannot take other predicates as their children

### Most General Unifier - Meaning Formation:
Meaning fusion is achieved via _Most General Unifier_ method since resolution of predicates will need some base of
meaning where resolver predicates can form common meaning and generate new resolvent from the commonly used terms.

Unification may be done in the following entities:
* Variable - variable: Can be unified in any order
* Variable - constant: Can be unified by writing constant into where variable exists
* Variable - function: Can be unified by writing function into where variable exists
* Constant - variable: Can be unified by writing constant into where variable exists
* Constant - constant: Can be unified if both constants are the same by EMPTY_SUBSTITUTION
* Constant - function: Cannot be unified
* Function - variable: Can be unified by writing function into where variable exists
* Function - constant: Cannot be unified
* Function - function: Can be unified if both functions have the same naming and their children can also be unified

#### Example:
Expression `p(f(h(w)), y, g(k(f(h(w))), x))` and `p(u, k(f(h(w))), g(z, h(w)))` can be unified with the following
substitutions `[f(h(w)) / u, k(f(h(w))) / y, k(f(h(w))) / z, h(w) / x]` where right values will be replaced with
left values so that both expression will become the same fact.

### Theorem Prover
Pseudo code for theorem prover is as the following, where my implementation waits for already CNF converted
clauses in knowledge base and negated state of the target clauses. It will use proof by refutation method and
this is why it expects negated versions of the target clauses. Here, the aim is to reach contradiction in knowledge
base so that known clauses and negated version of target clauses create contradiction in the world, and that means
inverse of target clauses should hold. 

```
Symbols:
    1) KB: Knowledge base
    2) :math:`{\\alpha}`: Predicates to be proved

Aim: Prove KB -> :math:`{\\alpha}`

CLAUSES <- CONVERT_TO_CNF( KB + :math:`{\\alpha}` )
while EMPTY_RESOLVENT not in CLAUSES do
    select two distinct clauses {c_i} and {c_j} in CLAUSES
    compute a resolvent {r_ij} of {c_i} and {c_j}
    CLAUSES <- CLAUSES + {r_ij}
end while
return satisfaction
```

Breadth first strategy is used while generating new level clauses until **EMPTY_CLAUSE** is reached or there is
no new clause to add among already known clauses. Here, **EMPTY_CLAUSE** means we achieved to resolve two opposite
clause and get contradiction. Let's have a look at simple example for resolution.

Additionally, removing of tautologies and subsumption eliminations are applied for each layer of the search.

```
# Here, predicates q(z) and ~q(y) can be unified and resolved. The remaining predicates from both clauses
# They will be merged into single clause and previously unification substitution will be applied into combined clause
Clause [~p(z,f(B)), q(z)] and clause [~q(y), r(y)] resolved into clause [~p(y,f(B)), r(y)] with substitution [y / z]
```

#### Input - Output
In this section sample inputs and corresponding outputs will be listed. But, before getting deep into examples,
I want to mention about input format. Knowledge base and negated theorem predicates should be contained in the input
which should have its format as **JSON**. You need to pay attention to key names since parser expects them as 
"knowledge_base" and "negated_theorem_predicates". Both of these are lists and each item in these list represents
a single clause which may have one or more predicates in it. Negated theorem predicates should be the negated version
of clauses that you want to prove.

**Important Note:** Your clauses will be interpreted in CNF (Conjunctive normal form) i.e. `q(z),~p(z,f(B))` will be
interpreted as `q(z) v ~p(z,f(B))` where symbol **v** means **OR** operator in first order logic.

```json
{
    "knowledge_base": [
        "p(A,f(t))",
        "q(z),~p(z,f(B))",
        "~q(y),r(y)"
    ],
    "negated_theorem_predicates": [
        "~r(A)"
    ]
}
```

##### Examples 1
Input:
```json
{
    "knowledge_base": [
        "~p(x),q(x)",
        "p(y),r(y)",
        "~q(z),s(z)",
        "~r(t),s(t)"
    ],
    "negated_theorem_predicates": [
        "~s(A)"
    ]
}
```

Output:
```
Initial knowledge base clauses are:
Clause 0 	| [~p(x), q(x)]
Clause 1 	| [p(y), r(y)]
Clause 2 	| [~q(z), s(z)]
Clause 3 	| [~r(t), s(t)]
Clause 4 	| [~s(A)]
Knowledge base contradicts, so inverse of the negated target clause is provable.
Prove by refutation resolution order will be shown.
[p(y), r(y)] | [~r(t), s(t)] -> [p(t), s(t)] with substitution [t / y]
[~s(A)] | [p(t), s(t)] -> [p(A)] with substitution [A / t]
[~p(x), q(x)] | [p(A)] -> [q(A)] with substitution [A / x]
[~q(z), s(z)] | [~s(A)] -> [~q(A)] with substitution [A / z]
[~q(A)] | [q(A)] -> [] with substitution []
```

##### Examples 1
Input:
```json
{
    "knowledge_base": [
        "p(A,f(t))",
        "q(z),~p(z,f(B))",
        "r(y),~q(y)"
    ],
    "negated_theorem_predicates": [
        "~r(A)"
    ]
}
```

Output:
```
Initial knowledge base clauses are:
Clause 0 	| [p(A,f(t))]
Clause 1 	| [~p(z,f(B)), q(z)]
Clause 2 	| [~q(y), r(y)]
Clause 3 	| [~r(A)]
Knowledge base contradicts, so inverse of the negated target clause is provable.
Prove by refutation resolution order will be shown.
[~q(y), r(y)] | [~r(A)] -> [~q(A)] with substitution [A / y]
[~p(z,f(B)), q(z)] | [~q(A)] -> [~p(A,f(B))] with substitution [A / z]
[p(A,f(t))] | [~p(A,f(B))] -> [] with substitution [B / t]
```

## Running
Example running command is provided below. Script expects file path for the input with _-f_ flag.
```shell
$ autonomous_theorem_prover.py -f ../sample_inputs/input3.inp
``` 

## Notes
The project is written with **Python3.6** and no external library is used.

## References
* Russell, Stuart J. (Stuart Jonathan). (2010). Artificial intelligence : a modern approach. Upper Saddle River, N.J. :Prentice Hall, 285-365 
* http://intrologic.stanford.edu/sections/section_12_09.html
* http://www.mathcs.duq.edu/simon/Fall04/notes-7-4/node6.html
