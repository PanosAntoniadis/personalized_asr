import os
import pickle
import logging
import argparse
import numpy as np

from helper import get_messages_from_transcription

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))


if __name__ == '__main__':
    # Create an argument parser
    parser = argparse.ArgumentParser(description='''
        Tool for classify new messages in clusters computed with lda
    ''')

    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')

    required.add_argument(
        '--input', help="Input transriptions (one per line)", required=True)

    required.add_argument(
        '--ids', help="File that contains the ids of the transcriptions", required=True)

    optional.add_argument(
        '--lda_path', help="The path of the lda model", required=True)
    optional.add_argument(
        '--vect_path', help="The path of the vectorizer model", required=True)
    optional.add_argument(
        '--has_id', help="If set, each email contains his id in the end (Sphinx format)", action='store_true')
    optional.add_argument(
        '--save', help="If set, save labels in pickle format", action='store_true')
    optional.add_argument(
        '--output', help="If set, name of the pickle output", required=True)
    

    args = parser.parse_args()
    input_dir = args.input
    ids_path = args.ids

    lda_path = args.lda_path
    vect_path = args.vect_path
    has_id = args.has_id
    save = args.save
    output_dir = args.output

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
    with open(vect_path, 'rb') as f:
        vectorizer = pickle.load(f)
    
    count_data = vectorizer.transform(messages)

    with open(lda_path, 'rb') as f:
        lda = pickle.load(f)
    
    X = lda.transform(count_data)
    
    logging.info(
        'Compute the cluster of each message based on the given metric...')
    # Compute closest cluster of each messages based on given metric.
    labels = {}
    for i, prob in enumerate(X):
        labels[ids[i]] = np.argmax(prob)
    
    # Save labels in pickle format
    if save:
        with open(output_dir, 'wb') as f:
            pickle.dump(labels, f)
