# api_key_detector
Neural Network Based, Automatic API Key Detector

A Multilayer-Perceptron-based system, able to identify API Key strings with an accuracy of over 99%.

For technical details, [see my thesis and, in particular, **Chapter 3** of the work.](https://drive.google.com/open?id=0B59pyODQqCxiUVkzb3diU0JNVzA)

## Requirements

- Python 3.5+
- Modules in requirements.txt (use pip3 to install)
```
pip install -r requirements.txt
```

## Library Usage

```python
>>> from api_key_detector import detector
>>> test = ["justsomething", "reallynothingimportant", "AizaSyDtEV5rwG_F1jvyj6WVlOOzD2vZa8DEpLE","eqwioqweioqiwoe"]
>>> detector.detect_api_keys(test)
[False, False, True, False]
>>> detector.filter_api_keys(test)
['AizaSyDtEV5rwG_F1jvyj6WVlOOzD2vZa8DEpLE']
```

## Commandline Usage

A commandline interface can be used to test the library functionalities

```bash
usage: api_key_detector [-h] [--debug] [--test] [--entropy] [--sequentiality]
                   [--gibberish] [--charset-length] [--words-percentage]
                   [--string STRING | -a | -e | -s | -g]
                   [--generate-training-set] [--plot-training-set]
                   [--api-key-files API_KEY_FILES [API_KEY_FILES ...]]
                   [--generic-text-files GENERIC_TEXT_FILES [GENERIC_TEXT_FILES ...]]
                   [--output-file DUMP_FILE] [--filter-apikeys]
                   [--detect-apikeys]

A python program that detects API Keys

optional arguments:
  -h, --help            show this help message and exit
  --debug               Print debug information
  --test                Test mode; calculates all features for strings in
                        stdin
  --entropy             Calculates the charset-normalized Shannon Entropy for
                        strings in stdin
  --sequentiality       Calculates the Sequentiality Index for strings in
                        stdin
  --gibberish           Calculates the Gibberish Index for strings in stdin
  --charset-length      Calculates the Induced Charset Length for strings in
                        stdin
  --words-percentage    Calculates the percentage of dictionary words for each
                        string in stdin
  --string STRING       Calculate all features for a single string, to be used
                        in conjunction with --test.
  -a                    Sort in alphabetical order, ascending
  -e                    Sort by entropy, ascending
  -s                    Sort by sequentiality, ascending
  -g                    Sort by gibberish index, ascending

  --generate-training-set
                        Generate training set for string classifier. Needs
                        --api-key-files, --generic-text-files and --output-
                        file to be specified
  --plot-training-set   Generate a 3d scatterplot for the training set. Needs
                        --api-key-files, --generic-text-files and --output-
                        file to be specified
  --api-key-files API_KEY_FILES [API_KEY_FILES ...]
                        List of files containing valid api-key examples, one
                        for each line
  --generic-text-files GENERIC_TEXT_FILES [GENERIC_TEXT_FILES ...]
                        List of files containing generic text examples that
                        DOESN'T contain any Api Key
  --output-file DUMP_FILE
                        Where to output the training set file

  --filter-apikeys      Filter potential apikeys from strings in stdin.
  --detect-apikeys      Detect potential apikeys from strings in stdin.
```

## Config File Explained
### config.json
**dump** => Where to save the trained Neural Network. Delete it to retrain the algorithm

**min_key_length** => The minimum length of an API Key

**blacklists** => Txt files containing strings (one for each line) that should never be considered as API Keys

**wordlists** => Txt files containing real words (one for each line), used to detect words inside strings

**word_content_threshold** => If a potential API Key string is made of a fraction of word_content_threshold real words, the API Key is discarded

**api_learnsets** => Txt files containing API Keys (one for each line), used to train the Neural Network

**text_learnsets** => Txt files containing generic strings (no API Keys, one for each line), used to train the Neural Network

**good_test** => Same as api_learnsets, but used to test the Neural Network

**bad_test** => Same as text_learnsets, but used to test the Neural Network

**re_train** => If true, than the Neural Network gets re-trained during initialization

**logging** => Used to config logging capabilities, see [here](https://docs.python.org/3/howto/logging.html)

### gibberish_detector/config.json
**dump** => Where to save the trained algorithm. Delete it to retrain the algorithm

**learnsets** => Txt files containing language-specific tex (e.g. books), used to calculate the transition probability from each letter to another

**good_test** => Txt files containing syntactically correct sentences, used to test the algorithm

**bad_test** => Txt files containing gibberish, used to test the algorithm