import os
import pickle
import logging
import argparse
import numpy as np

from stop_words import STOP_WORDS
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation as LDA

from helper import get_sentences, get_messages, cluster2text, save_clusters

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='''
        Tool for clustering messages using the lda allgorithm.
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
    optional.add_argument(
        '--alpha', help="Prior of document topic distribution", type=float)
    optional.add_argument(
        '--eta', help="Prior of topic word distribution ", type=float)
    optional.add_argument(
        '--bigram', help="Use bigrams along with unigrams in the vectorizer", action='store_true')
    optional.add_argument(
        '--max_df', help="Max_df parameter of the vectorizer", type=float, default=0.5)
    optional.add_argument(
        '--min_df', help="Min_df parameter of the vectorizer", type=int, default=2)

    args = parser.parse_args()
    input_dir = args.input
    output_dir = args.output
    n_topics = args.n_topics
    sentence = args.sentence
    alpha = args.alpha
    eta = args.eta
    bigram = args.bigram
    max_df = args.max_df
    min_df = args.min_df

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

    logging.info(
        'Run lda with {} number of topics...'.format(n_topics))

    # Initialise the count vectorizer
    if bigram:
        count_vectorizer = CountVectorizer(
            analyzer='word', stop_words=STOP_WORDS, ngram_range=(1, 2), max_df=max_df, min_df=min_df)
    else:
        count_vectorizer = CountVectorizer(
            analyzer='word', stop_words=STOP_WORDS, max_df=max_df, min_df=min_df)

    # Fit and transform the processed titles
    count_data = count_vectorizer.fit_transform(messages)

    if alpha and eta:
        lda = LDA(n_components=n_topics, n_jobs=-1,
                  doc_topic_prior=alpha, topic_word_prior=eta)
    else:
        lda = LDA(n_components=n_topics, n_jobs=-1)
    X = lda.fit_transform(count_data)

    # A sentence is included in the topic that represents the most.
    labels = np.argmax(X, axis=1)

    # Save clusters in given folders.
    save_clusters(messages, labels, output_dir)

    with open(os.path.join(output_dir, 'lda.model'), 'wb') as f:
        pickle.dump(lda, f)
    with open(os.path.join(output_dir, 'vect.model'), 'wb') as f:
        pickle.dump(count_vectorizer, f)

    # Save in each cluster a file that contains all the emails of it.
    # It will be used in the language model.
    cluster2text(output_dir, n_topics)
