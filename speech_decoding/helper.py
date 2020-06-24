import os
import re
import sys
from multiprocessing import cpu_count
import spacy

from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity


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
