import os
import sys
import logging
import argparse
import subprocess

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))

if __name__ == '__main__':
    # Create an argument parser
    parser = argparse.ArgumentParser(description='''
        Tool that takes two ASR outputs and computes the top-2 accuracy
    ''')

    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional argument')

    required.add_argument(
        '--hyp1', help="The 1st hypothesis file", required=True)
    required.add_argument(
        '--hyp2', help="The 2nd hypothesis file", required=True)
    required.add_argument(
        '--transcription', help="The file that contains the transcriptions", required=True)
    required.add_argument(
        '--output', help="Final output file", required=True)

    args = parser.parse_args()
    hyp1 = args.hyp1
    hyp2 = args.hyp2
    transcription = args.transcription
    output = args.output

    logging.info('Computing accuracy for each hypothesis file...')

    command = ['word_align.pl', transcription, hyp1, '>', 'hyp1.out']
    if subprocess.call(" ".join(command), shell=True):
        sys.exit('Error in subprocess')

    command = ['word_align.pl', transcription, hyp2, '>', 'hyp2.out']
    if subprocess.call(" ".join(command), shell=True):
        sys.exit('Error in subprocess')

    logging.info('Computing top-2 accuracy...')

    cnt1 = 0
    cnt2 = 0
    with open(output, 'w') as out, open('hyp1.out', 'r') as f1, open('hyp2.out', 'r') as f2:
        lines1 = f1.readlines()
        lines2 = f2.readlines()
        for i in range(0, len(lines1), 4):
            if lines1[i].startswith('TOTAL Words:'):
                break
            acc1 = float(lines1[i+2].strip('\n').split(' ')[-1][:-1])
            acc2 = float(lines2[i+2].strip('\n').split(' ')[-1][:-1])

            if acc1 >= acc2:
                cnt1 += 1
                out.write(lines1[i+1].strip('\n'))
            else:
                cnt2 += 1
                out.write(lines2[i+1].strip('\n'))
            out.write('\n')

    print("Sentences from 1: {}".format(cnt1))
    print("Sentences from 2: {}".format(cnt2))
