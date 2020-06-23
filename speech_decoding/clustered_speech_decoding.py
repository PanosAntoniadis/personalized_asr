import os
import sys
import pickle
import shutil
import argparse
import subprocess

if __name__ == '__main__':
    # Create an argument parser
    parser = argparse.ArgumentParser(description='''
        Tool that converts a set of sound files to text using the language model of their cluster. The clusters have been
            computed based on the asr output using the general language model.
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
        '--hmm', help="Path to the acoustic model to be used", required=True)
    required.add_argument(
        '--labels', help="Pickle file that holds the cluster of each file", required=True)
    required.add_argument(
        '--n_clusters', help="Number of clusters", required=True, type=int)
    required.add_argument(
        '--output', help="Folder to save all created files", required=True)
    required.add_argument(
        '--clusters', help="Path of the clusters that have been created", required=True)
    required.add_argument(
        '--merged_name', help="Name of the merged model to be used", required=True)
    optional.add_argument(
        '--mllr_path', help="Path to the mllr matrix", required=True)

    args = parser.parse_args()
    wav = args.wav
    ids = args.ids
    dic = args.dic
    hmm = args.hmm
    labels_path = args.labels
    n_clusters = args.n_clusters
    output_dir = args.output
    clusters = args.clusters
    merged_name = args.merged_name
    mllr_path = args.mllr_path
    merged_name = args.merged_name

    if not wav.endswith('/'):
        wav = wav + '/'
    if not hmm.endswith('/'):
        hmm = hmm + '/'
    if not output_dir.endswith('/'):
        output = output + '/'
    if not clusters.endswith('/'):
        clusters = clusters + '/'

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Unpickle labels of the test emails.
    with open(labels_path, 'rb') as f:
        labels = pickle.load(f)

    # Create outputs directories
    for i in range(n_clusters):
        if not os.path.exists(os.path.join(output_dir, 'cluster_' + str(i))):
            os.makedirs(os.path.join(output_dir, 'cluster_' + str(i)))

    for i in range(n_clusters):
        cluster_path = os.path.join(output_dir, 'cluster_' + str(i))
        if not os.path.exists(os.path.join(cluster_path, 'wav')):
            os.makedirs(os.path.join(cluster_path, 'wav'))

    # Copy wav files in their cluster
    for message in labels:
        shutil.copy2(os.path.join(wav, message + '.wav'),
                     os.path.join(output_dir + '/cluster_' + str(labels[message]), 'wav'))

    # Copy ids in the their cluster
    for i in range(n_clusters):
        cluster_path = os.path.join(output_dir, 'cluster_' + str(i))
        with open(os.path.join(cluster_path, 'fileids'), 'w') as w:
            for message in labels:
                if labels[message] == i:
                    w.write(message)
                    w.write('\n')

    output_hyp = open(os.path.join(output_dir, 'mllr.hyp'), 'w')

    # Decode each cluster separately
    for i in range(n_clusters):
        wav_path = output_dir + '/cluster_' + str(i) + '/wav'
        id_path = output_dir + '/cluster_' + str(i) + '/fileids'
        lm_path = clusters + '/cluster_' + str(i) + '/' + merged_name
        hyp_mllr_path = output_dir + '/cluster_' + str(i) + '/mllr.hyp'
        command = 'pocketsphinx_batch  -adcin yes  -cepdir ' + wav_path + ' -cepext .wav  -ctl ' + id_path + ' -lm ' + lm_path + \
            ' -dict ' + dic + ' -hmm ' + hmm + \
            ' -mllr ' + mllr_path + ' -hyp ' + hyp_mllr_path
        print(command)
        if subprocess.call([command], shell=True):
            sys.exit('Error in cluster ' + str(i))

        with open(hyp_mllr_path, 'r') as f:
            output_hyp.write(f.read())

    output_hyp.close()
