import os
import re
import sys
from multiprocessing import cpu_count
import spacy

from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity


def get_sentences(input_dir):
    '''Get all the sentences of the messages from a specific directory and return them as a list.

        Args:
            input_dir: Directory that contains the messages in text files.
        Returns:
            messages: A list that contains the sentences of the messages in string format.

        '''
    if not os.path.exists(input_dir):
        sys.exit('Message folder does not exist')

    messages = []
    for message in os.listdir(input_dir):
        with open(os.path.join(input_dir, message), 'r') as f:
            # Each line represents a sentence.
            for line in f:
                messages.append(line.strip('\n'))
    return messages


def get_messages(input_dir):
    '''Get messsages from a specific directory and return them as a list.

        Args:
            input_dir: Directory that contains the messages in text files.
        Returns:
            messages: A list that contains the messages in string format.

        '''
    if not os.path.exists(input_dir):
        sys.exit('Message folder does not exist')

    messages = []
    for message in os.listdir(input_dir):
        with open(os.path.join(input_dir, message), 'r') as f:
            messages.append(f.read())
    return messages


def get_spacy(messages):
    '''Represent messages as vectors using the spacy Greek model.

        Args:
            messages: A list that contains the messages in string format.
        Returns:
            X: A list that contains the vectors of the messages.

        '''
    nlp = spacy.load('el_core_news_md')
    X = []
    for message in messages:
        doc = nlp(message)
        X.append(doc.vector)
    return X


def run_kmeans(X, n_clusters):
    '''Run k-means algorithm for given number of clusters.

        Args:
            X: A list that contains the vectors.
            n_clusters: number of clusters
        Returns:
            labels: Label of each vector.

        '''
    # Run k-means usign n_clusters
    kmeans = KMeans(n_clusters=n_clusters, n_jobs=cpu_count(),
                    n_init=10 * cpu_count())
    labels = kmeans.fit_predict(X)
    return labels, kmeans.cluster_centers_


def save_clusters(messages, labels, out):
    '''Saves data according to the computed clusters.

        Args:
            messages: A list that contains the messages in string format.
            labels: A list that contains the label of each message.
            out: Output directory

        '''
    # If output directory does not exist, create it.
    if not os.path.exists(out):
        os.makedirs(out)

    total_str = str(len(messages) - 1)
    for i, message in enumerate(messages):
        # Add leading zeros in order to have all names in the right order.
        i_zeroed = str(i).rjust(len(total_str), '0')
        path = os.path.join(out, 'cluster_' +
                            str(labels[i]) + '/data/data_' + i_zeroed)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            f.write(message)


def cluster2text(out, n_clusters):
    '''Save in each cluster a file that contains all the messages of it.

        Args:
            out: Directoty that contains the clusters
            n_clusters: Number of clusters

        '''
    for i in range(n_clusters):
        cluster_path = os.path.join(out, 'cluster_' + str(i))
        message_path = os.path.join(out, 'cluster_' + str(i) + '/data')
        with open(os.path.join(cluster_path, 'corpus'), 'w') as w:
            for message in os.listdir(message_path):
                with open(os.path.join(message_path, message), 'r') as r:
                    w.write(r.read())
                    w.write('\n')


def get_messages_from_transcription(file, has_id):
    '''Read messages from a transcription file (one per line).

        Args:
            file: Path to the transription file.
            has_id: If true, the file contains the id of the message at the end of each line (Sphinx format).
        Returns:
            messages: A list the contains the emails.
        '''
    messages = []
    with open(file, 'r') as f:
        for message in f:
            if has_id:
                # Remove id from each email.
                messages.append(
                    re.sub(r'\([^)]*\)$', '', message).strip('\n').strip(' '))
            else:
                message.append(message.strip('\n').strip(' '))
    return messages


def closest_cluster(centers, point):
    '''Find the cluster that a point belongs.

        Args:
            centers: The coordinates of the centers of the clusters
            point: The coordinates of the point (vector representation of a text)
        Returns:
            cluster: Closest cluster to the point.
        '''
    cluster_id = 0
    distance = cosine_similarity([centers[0]], [point])[0][0]
    for i in range(1, len(centers)):
        cur_distance = cosine_similarity(
            [centers[i]], [point])[0][0]
        if cur_distance > distance:
            distance = cur_distance
            cluster_id = i
    return cluster_id, distance
