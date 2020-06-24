# adaptation_asr




## Installation





## Usage


### Step 1: Data preparation

- First, download our slack dataset from [add link]. In case you want to adapt to your own messages make sure they are in the following format (Sphinx format):
  - `\data` directory that contains the messages as *name_id*. The messages should contain only alphabetical Greek words.
  - `\wav` directory that contains the corresponding recordings as *name_id.wav*. The recorded files should be in 16kHz sampling rate and single channel.

- Create the IDs file.

```
$ python data_utils/create_ids.py --help
usage: create_ids.py [-h] --name NAME --total TOTAL --output OUTPUT

Tool for creating IDs file of a speech dataset in Sphinx format.

optional arguments:
  -h, --help       show this help message and exit

required arguments:
  --name NAME      Basename of the sound files
  --total TOTAL    Total number of files
  --output OUTPUT  Output directory

```

- Split data in folds, in case you want k-fold cross validation.

```
$ python data_utils/create_folds.py --help
usage: create_folds.py [-h] --wav WAV --ids IDS --data DATA --name NAME
                       --total TOTAL --output OUTPUT [--folds FOLDS]

Tool that splits a speech dataset (Sphinx format) for k-fold cross validation.

optional arguments:
  -h, --help       show this help message and exit

required arguments:
  --wav WAV        Folder that contains the recordings
  --ids IDS        File that contains the ids of the files
  --data DATA      Folder that contains the messages
  --name NAME      Name of the dataset. Files in data and wav folder should be
                   name_{id} and name_{id}.wav respectively
  --total TOTAL    Total number of samples
  --output OUTPUT  Output directory

optional arguments:
  --folds FOLDS    Number of folds (k)
```

- Create the transcription file in each fold.

```
$ python data_utils/create_transcription.py --help
usage: create_transcription.py [-h] --input INPUT --name NAME --output OUTPUT

Tool for creating the transcription file of a speech dataset in Sphinx format.

optional arguments:
  -h, --help       show this help message and exit

required arguments:
  --input INPUT    Folder that contains the messages
  --name NAME      Basename of the sound files
  --output OUTPUT  Output directory
```


- Final data format of a dataset (or of a signle fold):

```
slack_dataset
├── train
│   ├── data
|   │   ├── data_000
|   |   ├── data_001
|   │   └── data_
|   ├── fileids
|   ├── transcriptions
│   └── wav
|       ├── data_000.wav
|       ├── data_001.wav
|       └── ...
└── test
    ├── data
    │   ├── data_002
    |   ├── data_003
    │   └── ...
    ├── fileids
    ├── transcriptions
    └── wav
        ├── data_002.wav
        ├── data_003.wav
        └── ...

```

### Step 2: Language model adaptation

The general language model can be found [here](https://sourceforge.net/projects/cmusphinx/files/Acoustic%20and%20Language%20Models/Greek/). To adapt your messages to the general language model (first module in paper) run:

```
$ python language_adaptation/language_adaptation.py --help
usage: language_adaptation.py [-h] --general_lm GENERAL_LM --input_data
                              INPUT_DATA --output OUTPUT

Tool for adapting a language model using on a set of messages

optional arguments:
  -h, --help            show this help message and exit

required arguments:
  --general_lm GENERAL_LM
                        Path to the general language model
  --input_data INPUT_DATA
                        Path to the folder that contains the input messages
  --output OUTPUT       Output directory to save the adapted language models
```



### Step 3: Acoustic model adaptation

The general acoustic model and the dictionary can be found [here](https://sourceforge.net/projects/cmusphinx/files/Acoustic%20and%20Language%20Models/Greek/). To adapt your recordings to the general acoustic model (second module in paper) run:

```
$ python acoustic_adaptation/acoustic_adaptation.py --help
usage: acoustic_adaptation.py [-h] --wav WAV --ids IDS --general_hmm
                              GENERAL_HMM --dic DIC --transcriptions
                              TRANSCRIPTIONS --output OUTPUT --sphinxtrain
                              SPHINXTRAIN

Tool for adapting an acoustic model based on given transcription

optional arguments:
  -h, --help            show this help message and exit

required arguments:
  --wav WAV             Directory that contains the sound files
  --ids IDS             The ids of the sound files
  --general_hmm GENERAL_HMM
                        Folder that contains the general acoustic model
  --dic DIC             The dictionary to be used
  --transcriptions TRANSCRIPTIONS
                        Transcriptions of the sound files
  --output OUTPUT       Output directory
  --sphinxtrain SPHINXTRAIN
                        Sphinxtrain installation folder

 ```

### Step 4: Clustered language model adaptation

In order to create the clustered language models (third module in paper), first apply the clustering algorithm in the training data and then generate the domain-specific language model.

- Run the k-means algorithm:

```
$ python clustered_adaptation/kmeans.py --help
usage: kmeans.py [-h] --input INPUT --output OUTPUT --n_clusters N_CLUSTERS
                 [--sentence]

Tool for clustering messages using the k-means allgorithm.

optional arguments:
  -h, --help            show this help message and exit

required arguments:
  --input INPUT         Input directory that contains the input messages
  --output OUTPUT       Ouput directory to save the computed clusters

optional arguments:
  --n_clusters N_CLUSTERS
                        Number of clusters to be used
  --sentence            If set, clustering is done in sentence-level and not
                        in message-level
```

- Run the lda-based algorithm: 

```
$ python clustered_adaptation/lda.py --help
usage: lda.py [-h] --input INPUT --output OUTPUT --n_clusters N_CLUSTERS
              [--sentence] [--alpha ALPHA] [--eta ETA] [--bigram]
              [--max_df MAX_DF] [--min_df MIN_DF]

Tool for clustering messages using the lda allgorithm.

optional arguments:
  -h, --help            show this help message and exit

required arguments:
  --input INPUT         Input directory that contains the input messages
  --output OUTPUT       Ouput directory to save the computed clusters

optional arguments:
  --n_clusters N_CLUSTERS
                        Number of clusters to be used
  --sentence            If set, clustering is done in sentence-level and not
                        in message-level
  --alpha ALPHA         Prior of document topic distribution
  --eta ETA             Prior of topic word distribution
  --bigram              Use bigrams along with unigrams in the vectorizer
  --max_df MAX_DF       Max_df parameter of the vectorizer
  --min_df MIN_DF       Min_df parameter of the vectorizer
```

- Generate domain-specific language models:
```
$ python clustered_adaptation/create_cluster_lm.py --help
usage: create_cluster_lm.py [-h] --input INPUT --general_lm GENERAL_LM
                            --model_name MODEL_NAME --lambda_par LAMBDA_PAR

Tool for creating the language models after clustering

optional arguments:
  -h, --help            show this help message and exit

required arguments:
  --input INPUT         Folder that contains the clusters
  --general_lm GENERAL_LM
                        General language model
  --model_name MODEL_NAME
                        Name of language models
  --lambda_par LAMBDA_PAR
                        Lambda parameter in interpolation

```

### Step 5: Speech decoding

#### Without clustering

Specify the language and acoustic model you want to use (adapted of general) and run the following:

```
$ python speech_decoding/speech_decoding.py --help
usage: speech_decoding.py [-h] --wav WAV --ids IDS --dic DIC --hmm HMM --hyp
                          HYP --lm LM [--mllr_path MLLR_PATH]

Tool that converts a set of sound files to text using either the general or
the adapted language and acoustic models

optional arguments:
  -h, --help            show this help message and exit

required arguments:
  --wav WAV             Folder that contains the sound files
  --ids IDS             Folder that contains the ids file
  --dic DIC             Path to the dictionary to be used
  --hmm HMM             Path to the general acoustic model
  --hyp HYP             Path to save the hypothesis output file
  --lm LM               Path to the language model to be used

optional argument:
  --mllr_path MLLR_PATH
                        Path to the mllr matrix if adapted acoustic model is
                        used
```



#### With clustering

Here, the 3-stage decoding module is implemented as stated in the paper.

- Classify in clusters computed with k-means
```
$ python speech_decoding/classify_kmeans.py --help
usage: classify_kmeans.py [-h] --input INPUT --centers CENTERS --ids IDS
                          [--has_id] [--save] [--output OUTPUT]

Tool for classify new messages in clusters computed with k-means

optional arguments:
  -h, --help         show this help message and exit

required arguments:
  --input INPUT      Input transriptions to be classified (one per line)
  --centers CENTERS  Pickle file that contains the centers of the clusters
  --ids IDS          File that contains the ids of the transcriptions

optional arguments:
  --has_id           If set, each message contains his id in the end (Sphinx
                     format)
  --save             If set, save labels in pickle format
  --output OUTPUT    If set, name of the pickle output

```

- Classify in clusters computed with lda


```
$ python speech_decoding/classify_lda.py --help
usage: classify_lda.py [-h] --input INPUT --ids IDS --lda_path LDA_PATH
                       --vect_path VECT_PATH [--has_id] [--save] --output
                       OUTPUT

Tool for classify new messages in clusters computed with lda

optional arguments:
  -h, --help            show this help message and exit

required arguments:
  --input INPUT         Input transriptions (one per line)
  --ids IDS             File that contains the ids of the transcriptions

optional arguments:
  --lda_path LDA_PATH   The path of the lda model
  --vect_path VECT_PATH
                        The path of the vectorizer model
  --has_id              If set, each email contains his id in the end (Sphinx
                        format)
  --save                If set, save labels in pickle format
  --output OUTPUT       If set, name of the pickle output


```
- Speech to text using clustered language models

```
$ python speech_decoding/clustered_speech_decoding.py --help
usage: clustered_speech_decoding.py [-h] --wav WAV --ids IDS --dic DIC --hmm
                                    HMM --labels LABELS --n_clusters
                                    N_CLUSTERS --output OUTPUT --clusters
                                    CLUSTERS --merged_name MERGED_NAME
                                    --mllr_path MLLR_PATH

Tool that converts a set of sound files to text using the language model of
their cluster. The clusters have been computed based on the asr output using
the general language model.

optional arguments:
  -h, --help            show this help message and exit

required arguments:
  --wav WAV             Folder that contains the sound files
  --ids IDS             Folder that contains the ids file
  --dic DIC             Path to the dictionary to be used
  --hmm HMM             Path to the acoustic model to be used
  --labels LABELS       Pickle file that holds the cluster of each file
  --n_clusters N_CLUSTERS
                        Number of clusters
  --output OUTPUT       Folder to save all created files
  --clusters CLUSTERS   Path of the clusters that have been created
  --merged_name MERGED_NAME
                        Name of the merged model to be used

optional argument:
  --mllr_path MLLR_PATH
                        Path to the mllr matrix
```

### Step 6: Evaluation







