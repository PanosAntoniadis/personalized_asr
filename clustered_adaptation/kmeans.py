import os
import pickle
import logging
import argparse

from helper import get_sentences, get_messages, get_spacy, run_kmeans, save_clusters, cluster2text

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='''
        Tool for clustering messages using the k-means algorithm.
    ''')

    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')

    required.add_argument(
        '--input', help="Input directory that contains the input messages", required=True)
    required.add_argument(
        '--output', help="Ouput directory to save the computed clusters", required=True)

    optional.add_argument(
        '--n_clusters', help="Number of clusters to be used", type=int, required=True)
    optional.add_argument(
        '--sentence',
        help="If set, clustering is done in sentence-level and not in message-level",
        action='store_true')

    args = parser.parse_args()
    input_dir = args.input
    output_dir = args.output
    n_clusters = args.n_clusters
    sentence = args.sentence

    if not input_dir.endswith('/'):
        input_dir = input_dir + '/'
    if not output_dir.endswith('/'):
        output_dir = output_dir + '/'

    if sentence:
        logging.info('Reading sentences of messages...')
        # Get sentences of messages
        messages = get_sentences(input_dir)
    else:
        logging.info('Reading messages...')
        # Get the whole messages
        messages = get_messages(input_dir)

    logging.info('Get spacy vector representation...')
    # Get vector representation of messages.
    X = get_spacy(messages)

    logging.info('Run k-means with {} number of clusters...'.format(n_clusters))
    # Run k-means with given number of clusters.
    labels, centers = run_kmeans(X, n_clusters)

    # Save clusters in given folders.
    save_clusters(messages, labels, output_dir)

    # Save in each cluster a file that contains all the messages of it.
    # It will be used in the language model.
    cluster2text(output_dir, n_clusters)

    # Save centers in a pickle, in order to classify
    # other messages.
    with open(os.path.join(output_dir, 'centers.pickle'), 'wb') as f:
        pickle.dump(centers, f)
