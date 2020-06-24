import os
import shutil
import argparse
from sklearn.model_selection import KFold

if __name__ == '__main__':
    # Create an argument parser
    parser = argparse.ArgumentParser(description='''
        Tool that splits a speech dataset (Sphinx format) for k-fold cross validation.
    ''')

    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')

    required.add_argument(
        '--wav', help="Folder that contains the recordings", required=True)
    required.add_argument(
        '--ids', help="File that contains the ids of the files", required=True)
    required.add_argument(
        '--data', help="Folder that contains the messages", required=True)
    required.add_argument(
        '--name', help="Name of the dataset. Files in data and wav folder should be name_{id} and name_{id}.wav respectively", required=True)
    required.add_argument(
        '--total', help="Total number of samples", required=True, type=int)
    required.add_argument(
        '--output', help="Output directory", required=True)

    optional.add_argument(
        '--folds', help="Number of folds (k)", type=int, default=5)

    args = parser.parse_args()
    wav = args.wav
    ids = args.ids
    data = args.data
    name = args.name
    total = args.total
    output = args.output
    folds = args.folds

    # Define a K-Folds cross-validator
    kf = KFold(n_splits=folds, shuffle=True)
    total_indices = [i for i in range(total)]

    i = 0

    for train, test in kf.split(total_indices):
        fold_dir = os.path.join(output, 'fold_' + str(i))

        # If train or test directory do not exist, create them.
        if not os.path.exists(os.path.join(fold_dir, 'train')):
            os.makedirs(os.path.join(fold_dir, 'train'))
        if not os.path.exists(os.path.join(fold_dir, 'test')):
            os.makedirs(os.path.join(fold_dir, 'test'))

        # Split wav files
        if not os.path.exists(os.path.join(fold_dir, 'train/wav')):
            os.makedirs(os.path.join(fold_dir, 'train/wav'))
        if not os.path.exists(os.path.join(fold_dir, 'test/wav')):
            os.makedirs(os.path.join(fold_dir, 'test/wav'))
        wav_path = os.path.join(wav, name) + '_'
        for id in range(total):
            id_zeroed = str(id).rjust(len(str(total)), '0')
            if id in train:
                shutil.copy2(wav_path + str(id_zeroed) + '.wav',
                             os.path.join(fold_dir, 'train/wav'))
            if id in test:
                shutil.copy2(wav_path + str(id_zeroed) + '.wav',
                             os.path.join(fold_dir, 'test/wav'))

        # Split data files
        if not os.path.exists(os.path.join(fold_dir, 'train/data')):
            os.makedirs(os.path.join(fold_dir, 'train/data'))
        if not os.path.exists(os.path.join(fold_dir, 'test/data')):
            os.makedirs(os.path.join(fold_dir, 'test/data'))
        data_path = os.path.join(data, name) + '_'
        for id in range(total):
            id_zeroed = str(id).rjust(len(str(total)), '0')
            if id in train:
                shutil.copy2(data_path + str(id_zeroed),
                             os.path.join(fold_dir, 'train/data'))
            if id in test:
                shutil.copy2(data_path + str(id_zeroed),
                             os.path.join(fold_dir, 'test/data'))

        # Split id file
        with open(ids, 'r') as r, open(os.path.join(fold_dir, 'train/fileids'), 'w') as w1, open(os.path.join(fold_dir, 'test/fileids'), 'w') as w2:
            for idx, line in enumerate(r):
                if idx in train:
                    w1.write(line)
                if idx in test:
                    w2.write(line)

        i += 1
