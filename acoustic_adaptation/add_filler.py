import os
import sys
import argparse

if __name__ == '__main__':
    # Create an argument parser
    parser = argparse.ArgumentParser(description='''
        Tool for adding the filler symbol (<s> and </s>) in a transcription.
    ''')

    required = parser.add_argument_group('required arguments')

    required.add_argument(
        '--input', help="Input transcription file", required=True)
    required.add_argument(
        '--output', help="Output transcription file that contains the fillers", required=True)

    args = parser.parse_args()

    input_tr = args.input
    output_tr = args.output

    if not os.path.isfile(input):
        sys.exit("Wrong arguments")

    with open(output_tr, 'w') as w, open(input_tr, 'r') as r:
        for line in r:
            words = line.split(' ')
            # Last word is the file id according to Sphinx format.
            w.write(
                '<s> ' + ' '.join(words[:len(words) - 1]) + ' </s> ' + words[-1])
