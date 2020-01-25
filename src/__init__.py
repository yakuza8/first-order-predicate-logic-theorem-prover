from typing import List
from src.entity.predicate import Predicate


class ProblemState(object):
    """
    Problem state composed from first order predicates to be proved

    Method to prove the given problem is Resolution Refutation Technique
    by searching knowledge base with breadth first strategy where the statement
    is composed of two main variables

    * Knowledge base: Group of predicates which creates knowledge space in the problem
    * Negated version of clauses to be proved: Group of clauses which are negated beforehand
    so that we can refute the target clauses via trying to reach contradiction in knowledge
    space
    """
    def __init__(self, knowledge_base: List[List[Predicate]], negated_theorem_clauses: List[List[Predicate]]):
        # Combine all the clauses into a single clause list
        from src.entity.clause import Clause
        self.clauses = [Clause(clause) for clause in knowledge_base]
        self.clauses.extend([Clause(clause) for clause in negated_theorem_clauses])
