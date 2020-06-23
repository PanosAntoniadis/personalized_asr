import os
import pickle
import logging
import argparse

from helper import get_messages_from_transcription, get_spacy, closest_cluster

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))

if __name__ == '__main__':
    # Create an argument parser
    parser = argparse.ArgumentParser(description='''
        Tool for classify new messages in clusters computed with k-means 
    ''')

    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')

    required.add_argument(
        '--input', help="Input transriptions to be classified (one per line)", required=True)
    required.add_argument(
        '--centers', help="Pickle file that contains the centers of the clusters", required=True)
    required.add_argument(
        '--ids', help="File that contains the ids of the transcriptions", required=True)
    optional.add_argument(
        '--has_id', help="If set, each message contains his id in the end (Sphinx format)", action='store_true')
    optional.add_argument(
        '--save', help="If set, save labels in pickle format", action='store_true')
    optional.add_argument(
        '--output', help="If set, name of the pickle output", default='labels.pickle')

    args = parser.parse_args()
    input_dir = args.input
    centers_path = args.centers
    ids_path = args.ids

    has_id = args.has_id
    save = args.save
    output_dir = args.output

    logging.info('Reading the centers of the computed clusters...')
    # Read centers
    with open(centers_path, 'rb') as f:
        centers = pickle.load(f)

    logging.info('Reading input messages...')
    # Read ids
    ids = []
    with open(ids_path, 'r') as r:
        for line in r:
            ids.append(line.strip('\n'))

    # Get messages to classify
    messages = get_messages_from_transcription(input_dir, has_id)
    logging.info('Represent them as vectors...')
    # Represent them as vectors
    vectors = get_spacy(messages)

    logging.info(
        'Compute the cluster of each message based on the given metric...')
    # Compute closest cluster of each email based on given metric.
    labels = {}
    for i, vec in enumerate(vectors):
        cluster, distance = closest_cluster(centers, vec)
        labels[ids[i]] = cluster

    # Save labels in pickle format
    if save:
        with open(output_dir, 'wb') as f:
            pickle.dump(labels, f)
