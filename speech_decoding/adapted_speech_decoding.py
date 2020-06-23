import os
import sys
import argparse
import subprocess

if __name__ == '__main__':
    # Create an argument parser
    parser = argparse.ArgumentParser(description='''
        Tool that converts a set of sound files to text using either
        the general or the adapted language and acoustic models
    ''')

    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional argument')

    required.add_argument(
        '--wav', help="Folder that contains the sound files", required=True)
    required.add_argument(
        '--ids', help="Folder that contains the ids file", required=True)
    required.add_argument(
        '--dic', help="Path to the dictionary to be used", required=True)
    required.add_argument(
        '--hmm', help="Path to the general acoustic model", required=True)
    required.add_argument(
        '--hyp', help="Path to save the hypothesis output file", required=True)
    required.add_argument(
        '--lm', help="Path to the language model to be used", required=True)
    optional.add_argument(
        '--mllr_path', help="Path to the mllr matrix if adapted acoustic model is used", required=True)

    args = parser.parse_args()
    wav = args.wav
    ids = args.ids
    dic = args.dic
    hmm = args.hmm
    hyp = args.hyp
    lm = args.lm
    mllr_path = args.mllr_path

    if not wav.endswith('/'):
        wav = wav + '/'
    if not hmm.endswith('/'):
        hmm = hmm + '/'

    if mllr_path == None:
        command = ['pocketsphinx_batch', '-adcin yes', '-cepdir',  wav, '-cepext .wav',
                   '-ctl', ids, '-lm', lm, '-dict', dic, '-hmm',  hmm, '-hyp', hyp]
    else:
        command = ['pocketsphinx_batch', '-adcin yes', '-cepdir',  wav, '-cepext .wav',
                   '-ctl', ids, '-lm', lm, '-dict', dic, '-hmm',  hmm, '-mllr', mllr_path, '-hyp', hyp]
    if subprocess.call(" ".join(command), shell=True):
        sys.exit('Error in subprocess')
