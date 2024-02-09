import argparse
import traceback

from exception import InputError
from grammar import Grammar
from earley import Earley


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-i",
        "--input",
        nargs='?',
        help="Specify the input file.",
        type=str,
        required=True,
        dest="input"
    )

    parser.add_argument(
        "-o",
        "--output",
        nargs='?',
        help="Specify the output file.",
        type=str,
        required=True,
        dest="output"
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    content = open(args.input, 'r').read().strip()
    try:
        # grammar and parser initialization
        grammar, content = Grammar.read(content)
        parser = Earley.fit(grammar)
        # answering requests
        content = content.split('\n')
        if len(content) == 0:
            raise InputError("There are no number_of_requests!")
        if not content[0].isnumeric() or not 0 <= int(content[0]) == len(content) - 1:
            raise InputError(f"Incorrect number of requests: '{content[0]}'!")
        number_of_requests = int(content[0])
        answers = []
        for i in range(number_of_requests):
            word = content[i + 1]
            if not grammar.check_word(word):
                raise InputError(f"Incorrent word: '{word}'!")
            answers.append("Yes" if parser.predict(word) else "No")
    except InputError:
        answers = ["InputError"]
    except Exception:
        answers = [traceback.format_exc()]
    # saving answers
    with open(args.output, 'w') as output:
        output.write('\n'.join(answers))