# A mechanism for personalized Automatic Speech Recognition for less frequently spoken languages: the Greek case


## Abstract
> Automatic Speech Recognition (ASR) has become increasingly popular given that it signif-
icantly simplifies human-computer interaction, providing a more intuitive way of communica-
tion. Building an accurate, general-purpose ASR system is a challenging task that requires a
lot of data and computing power. Especially for languages not widely spoken, such as Greek,
the lack of adequately large speech datasets leads to the development of ASR systems that
are adapted to a restricted text corpus and for specific activities. When used in specific do-
mains, these systems can be both accurate and fast, without the need for large datasets and
extended training. An interesting domain of application of such narrow-scope ASR systems
is the development of personalized speech to text systems that can be used for dictation. In
this work we propose three personalisation-via-adaptation modules, that can be integrated into
any ASR/dictation system and increase its accuracy. The adaptation can be achieved both on
the language model (based on the previous input of the user) as well as on the acoustic model
(by using a set of user’s narrations). To provide more precise recommendations, clustering
algorithms are applied and topic-specific language models are created. Also, heterogeneous
adaptation methods are combined to provide recommendations to the user. Evaluation per-
formed on a self-created database containing 746 corpora included in messaging applications
and mails from the same user, demonstrates that the proposed approach can achieve better
results than the existing Greek models.

## Installation

Install necessary requirements using pip:

```
$ pip install -r requirements.txt
```


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


- Final data format of a dataset (or of a single fold):

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

<p align="center">
  <img src="/language_adaptation/language_adaptation.png">
</p>

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

<p align="center">
  <img src="/acoustic_adaptation/acoustic_adaptation.png">
</p>

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

<p align="center">
  <img src="/clustered_adaptation/clustered_language_adaptation.png">
</p>

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

##### Without clustering

Specify the language and acoustic model you want to use (adapted or general) and run the following:

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



##### With clustering

<p align="center">
  <img src="/speech_decoding/decoding_clustering.png">
</p>

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

- In order to evaluate the model, `word_align.pl` script of sphinxtrain is used. It aligns the output with the reference file and computes the total accuracy.

```
$ word_align.pl --help
Usage:
     calculate_wer [options] reference_file hypothesis_file

Options:
    --help, -?
            Print a brief help message and exit.

    --verbose, -v
            Print out messages tracing the alignment algorithm.
```


- Compute top-2 accuracy using outputs from two adaptation models

```
$ python evaluation/compute_top2.py --help
usage: compute_top2.py [-h] --hyp1 HYP1 --hyp2 HYP2 --transcription
                       TRANSCRIPTION --output OUTPUT

Tool that takes two ASR outputs and computes the top-2 accuracy

optional arguments:
  -h, --help            show this help message and exit

required arguments:
  --hyp1 HYP1           The 1st hypothesis file
  --hyp2 HYP2           The 2nd hypothesis file
  --transcription TRANSCRIPTION
                        The file that contains the transcriptions
  --output OUTPUT       Final output file
```

- Compute top-3 accuracy using outputs from three adaptation models

```
$ python evaluation/compute_top3.py --help
usage: compute_top3.py [-h] --hyp1 HYP1 --hyp2 HYP2 --hyp3 HYP3
                       --transcription TRANSCRIPTION --output OUTPUT

Tool that takes three ASR outputs and computes the top-3 accuracy

optional arguments:
  -h, --help            show this help message and exit

required arguments:
  --hyp1 HYP1           The 1st hypothesis file
  --hyp2 HYP2           The 2nd hypothesis file
  --hyp3 HYP3           The 3rd hypothesis file
  --transcription TRANSCRIPTION
                        The file that contains the transcriptions
  --output OUTPUT       Final output file
```

## Technologies Used

- spaCy
- sklearn
- numpy

## Results

- Recognition accuracy comparison on proposed adaptation methods

| Acoustic Model  |         Language Model      | Accuracy | 
| :-------------: | :-------------------------: | :------: |
|    Baseline     |           Baseline          |  64.24%  |
|    Baseline     |           Adapted           |  67.21%  |
|    Adapted      |           Baseline          |  67.56%  |
|    Adapted      |           Adapted           |  70.59%  |
|    Adapted      | Clustered adapted (k-means) |  69.3%   |
|    Adapted      |   Clustered adapted (lda)   |  69.19%  |

- Recognition accuracy comparison using more suggestions

|                 Method                        | Accuracy | 
| :-------------------------------------------: | :------: |
|                 Baseline                      |  64.24%  |
|              Top-1 best method                |  70.59%  |
|      Top-2 combining general and k-means      |  72.57%  |
|      Top-2 combining general and lda          |  72.48%  |
|    Top-3 combining general, k-means and lda   |  73.54%   |


## Citing




