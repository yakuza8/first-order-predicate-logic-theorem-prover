import argparse
import logging
from collections import deque
from typing import Set

from entity.clause import Clause
from src import ProblemState
from src.input_parser import InputParser

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)-8s : %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


class AutonomousTheoremProver(object):

    def __init__(self, _problem_state: ProblemState):
        self.problem_state = _problem_state
        self.clauses = set(self.problem_state.clauses)

        # Remove tautologies
        self.clauses = set(clause for clause in self.clauses if not clause.has_tautology())
        # Remove subsumptions
        self.clauses = self.remove_subsumptions(self.clauses)
        self.last_generated_resolvent = self.clauses

    def prove(self):
        """
        Autonomous Theorem Prover
        =========================
        Pseudo code for procedure of resolution is explained

        Symbols:
            1) KB: Knowledge base
            2) :math:`{\\alpha}`: Predicates to be proved

        Aim: Prove KB -> :math:`{\\alpha}`

        Code:

        * CLAUSES <- CONVERT_TO_CNF( KB + :math:`{\\alpha}` )
        * while EMPTY_RESOLVENT not in CLAUSES do
            * select two distinct clauses {c_i} and {c_j} in CLAUSES
            * compute a resolvent {r_ij} of {c_i} and {c_j}
            * CLAUSES <- CLAUSES + {r_ij}
        * end while
        * return satisfaction
        """
        # Result of founding empty clause or not which represents contradiction in knowledge base
        result = False
        # Dictionary to keep track of which clauses resulted into key clause
        resolvent_dictionary = {}
        level = 1

        while len(self.last_generated_resolvent) != 0:
            new_resolvent_set = set(
                self.generate_next_level_resolvent(self.clauses, self.last_generated_resolvent, resolvent_dictionary,
                                                   level))

            if any(resolvent for resolvent in new_resolvent_set if resolvent.get_clause_length() == 0):
                # Collect all the clauses, we found the result
                result = True
                self.clauses = self.clauses.union(new_resolvent_set)
                self.clauses = self.clauses.union(self.last_generated_resolvent)
                break

            # Check any new clause is generated or not, if so we do not need to iterate over and over again
            if len(self.clauses.intersection(new_resolvent_set)) == len(new_resolvent_set):
                # Collect all the clauses
                self.clauses = self.clauses.union(new_resolvent_set)
                self.clauses = self.clauses.union(self.last_generated_resolvent)
                break

            self.clauses = self.clauses.union(self.last_generated_resolvent)
            self.last_generated_resolvent = new_resolvent_set

            # Increment level of BFS
            level += 1

        self.show_results(result, resolvent_dictionary, level + 1)

    @staticmethod
    def generate_next_level_resolvent(known_clauses: Set[Clause], new_clauses: Set[Clause], clause_dictionary: dict,
                                      level: int) -> Set[Clause]:
        """
        Generate new set of resolvent with known clauses and last level of resolvent
        :param known_clauses: Known resolvent set up to now
        :param new_clauses: New clauses from the last level of breath first search
        :param clause_dictionary: Dictionary storage to keep track of resolvent pairs
        :param level: Generated clauses' level information in breadth first search
        :return: Newly generated resolvent sey
        """
        from itertools import product

        new_resolvent_set = set()
        for clause1, clause2 in product(known_clauses, new_clauses):
            resolvent, substitutions = clause1.resolve_with(clause2)
            if resolvent is not None:
                new_resolvent_set.add(resolvent)

                # Will be used while showing results
                if resolvent not in clause_dictionary:
                    clause_dictionary[str(resolvent)] = (str(clause1), str(clause2), substitutions, level)
        return new_resolvent_set

    @staticmethod
    def remove_subsumptions(clauses: Set[Clause]) -> Set[Clause]:
        """
        Removal of subsumptions by checking each pair of clauses
        :param clauses: Clauses to check whether subsumption exists or not
        :return: Set of clauses where subsumptions are removed
        """
        from itertools import combinations

        remove_set = set()
        for clause1, clause2 in combinations(clauses, 2):
            # For each combination, check whether subsumption holds or not
            if clause1.does_subsume(clause2):
                remove_set.add(clause2)
            elif clause2.does_subsume(clause1):
                remove_set.add(clause1)
            else:
                # Do nothing
                pass
        # At the end, remove subsumed clauses from original list
        return set(clause for clause in clauses if clause not in remove_set)

    def show_results(self, result: bool, clause_dictionary: dict, max_level: int):
        """
        Functionality to show result where if we reach aim then show resolvent set of the EMPTY_CLAUSE, otherwise show
        all the generated resolvent set
        :param result: Boolean flag whether we reach EMPTY_CLAUSE or not
        :param clause_dictionary: Generated clause dictionary
        :param max_level: Maximum reached level in BFS
        :return: None
        """
        # Initial knowledge base
        logging.info('Initial knowledge base clauses are:')
        for index, clause in enumerate(self.problem_state.clauses):
            logging.info('Clause {0} \t| {1}'.format(index, clause))

        # Level-wise generation of clauses
        for level in range(1, max_level):
            logging.debug('Level {0} generated clauses:'.format(level))
            for resolvent, (
                    first_resolver, second_resolver, substitution, resolution_level) in clause_dictionary.items():
                if resolution_level == level:
                    logging.debug('{0} | {1} -> {2}'.format(first_resolver, second_resolver, resolvent))

        # If EMPTY_CLAUSE is reached, show path to resolution
        if result:
            logging.info('Knowledge base contradicts, so inverse of the negated target clause is provable.')
            generation_stack = []
            process_queue = deque(['[]'])
            while process_queue:
                for clause_index in range(len(process_queue)):
                    clause = process_queue.popleft()
                    if clause in clause_dictionary:
                        first_resolver, second_resolver, substitution, _ = clause_dictionary[clause]
                        generation_stack.append((first_resolver, second_resolver, clause, substitution))
                        process_queue.append(first_resolver)
                        process_queue.append(second_resolver)

            logging.info('Prove by refutation resolution order will be shown.')
            while generation_stack:
                first_resolver, second_resolver, resolvent, substitution = generation_stack.pop()
                logging.info('{0} | {1} -> {2} with substitution {3}'.format(first_resolver, second_resolver, resolvent,
                                                                             substitution))
        else:
            logging.warning(
                'Knowledge base does not have contradiction resulting into the fact that we cannot prove the negated target clause.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', help='File name to parse and create problem base',
                        type=argparse.FileType('r'), required=True)
    args = parser.parse_args()

    # Get filename
    _file = args.file

    # Parse problem state
    problem_state = InputParser.parse(_file)
    # Prove the theorem
    AutonomousTheoremProver(problem_state).prove()
