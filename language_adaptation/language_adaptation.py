import os
import sys
import logging
import argparse
import subprocess

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))

if __name__ == '__main__':
    # Create an argument parser
    parser = argparse.ArgumentParser(description='''
        Tool for adapting a language model using on a set of messages
    ''')

    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional argument')

    required.add_argument(
        '--general_lm', help="Path to the general language model", required=True)
    required.add_argument(
        '--input_data', help="Path to the folder that contains the input messages", required=True)
    required.add_argument(
        '--output', help="Output directory to save the adapted language models", required=True)

    args = parser.parse_args()
    general_lm = args.general_lm
    input_data = args.input_data
    output_dir = args.output

    if not os.path.exists(general_lm):
        sys.exit('General language model does not exist')
    if not os.path.exists(input_data):
        sys.exit('Path to input data does not exist')

    logging.info('Creating corpus of input data...')

    with open(os.path.join(output_dir, 'corpus'), 'w') as w:
        for message in sorted(os.listdir(input_data)):
            with open(os.path.join(input_data, message), 'r') as f:
                for line in f:
                    w.write(line)

    logging.info('Generating adapted language model using n-grams...')

    command = ['ngram-count -kndiscount -wbdiscount1 -wbdiscount2 -wbdiscount3 -interpolate',
               '-text', os.path.join(output_dir, 'corpus'), '-lm', os.path.join(output_dir, 'adapted.lm')]
    if subprocess.call(" ".join(command), shell=True):
        sys.exit('Error in subprocess')

    logging.info(
        'Generating merged adapted language model using interpolation...')

    command = ['ngram -lm', general_lm, '-mix-lm', os.path.join(
        output_dir, 'adapted.lm'), '-lambda 0.5 -write-lm', os.path.join(output_dir, 'merged_adapted.lm')]
    if subprocess.call(" ".join(command), shell=True):
        sys.exit('Error in subprocess')
