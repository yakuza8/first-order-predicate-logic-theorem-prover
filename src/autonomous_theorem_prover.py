import argparse

from src.input_parser import InputParser

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', help='File name to parse and create problem base',
                        type=argparse.FileType('r'), required=True)
    args = parser.parse_args()

    # Get filename
    _file = args.file

    # Parse problem state
    problem_state = InputParser.parse(_file)
    print()
