import argparse

from src import ProblemState
from src.input_parser import InputParser


class AutonomousTheoremProver(object):

    def __init__(self, _problem_state: ProblemState):
        self.problem_state = _problem_state

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
        pass


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
