import sys
import os
import argparse
import subprocess
import shutil
import logging

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))


if __name__ == '__main__':
    # Create an argument parser
    parser = argparse.ArgumentParser(description='''
        Tool for adapting an acoustic model based on given transcription
    ''')

    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')

    required.add_argument(
        '--wav', help="Directory that contains the sound files", required=True)
    required.add_argument(
        '--ids', help="The ids of the sound files", required=True)
    required.add_argument(
        '--general_hmm', help="Folder that contains the general acoustic model", required=True)
    required.add_argument(
        '--dic', help="The dictionary to be used", required=True)
    required.add_argument(
        '--transcriptions', help="Transcriptions of the sound files", required=True)
    required.add_argument(
        '--output', help="Output directory", required=True)
    required.add_argument(
        '--sphinxtrain', help="Sphinxtrain installation folder", required=True)

    args = parser.parse_args()
    wav = args.wav
    ids = args.ids
    general_hmm = args.general_hmm
    dic = args.dic
    transcriptions = args.transcriptions
    output_dir = args.output
    sphinxtrain = args.sphinxtrain

    if not wav.endswith('/'):
        wav = wav + '/'
    if not general_hmm.endswith('/'):
        hmm = hmm + '/'
    if not output_dir.endswith('/'):
        output_dir = output_dir + '/'
    if not sphinxtrain.endswith('/'):
        sphinxtrain = sphinxtrain + '/'

    logging.info('Generate acoustic model features from recordings')
    feat_params = os.path.join(general_hmm, 'feat.params')
    mfc_path = os.path.join(output_dir, 'mfc')
    generate_command = ['sphinx_fe -argfile', feat_params, '-samprate 16000 -c',
                        ids, '-di', wav, '-do', mfc_path, '-ei wav -eo mfc -mswav yes']
    if subprocess.call(" ".join(generate_command), shell=True):
        sys.exit('Error in subprocess')

    logging.info('Collect statistics from the adaptation data')
    # Copy bw, map_adapt and mk_s2sendump scripts.
    shutil.copy2(sphinxtrain + 'bw', output_dir)
    shutil.copy2(sphinxtrain + 'map_adapt', output_dir)
    shutil.copy2(sphinxtrain + 'mk_s2sendump', output_dir)

    mdef_path = os.path.join(general_hmm, 'mdef.txt')
    counts_path = os.path.join(output_dir, 'counts')
    os.makedirs(counts_path)
    feature_path = os.path.join(general_hmm, 'feature_transform')
    bw_command = ['./' + output_dir + 'bw -hmmdir', general_hmm, '-cepdir', mfc_path, '-moddeffn', mdef_path, '-ts2cbfn .cont. -feat 1s_c_d_dd -cmn batch -agc none -dictfn',
                  dic, '-ctlfn', ids, '-lsnfn', transcriptions, '-accumdir', counts_path, '-lda', feature_path, '-varnorm no -cmninit 40,3,-1']

    if subprocess.call(" ".join(bw_command), shell=True):
        sys.exit('Error in subprocess')

    shutil.copy2(sphinxtrain + 'mllr_solve', output_dir)
    means_path = os.path.join(general_hmm, 'means')
    variance_path = os.path.join(general_hmm, 'variances')
    mllr_path = os.path.join(output_dir, 'mllr_matrix')
    mllr_command = ['./' + output_dir + 'mllr_solve -meanfn', means_path,
                    '-varfn', variance_path, '-outmllrfn',  mllr_path, '-accumdir', counts_path]

    logging.info('Generate mllr transformation')
    if subprocess.call(" ".join(mllr_command), shell=True):
        sys.exit('Error in subprocess')
