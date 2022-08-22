# Please see https://github.com/kyzhouhzau/BERT-NER for more detail of the BERT-NER model.

This model should be used in Tensorflow 1.x and Python 3.x environment.


### Usage:
```
bash run_ner.sh
```

### Download BERT Base Cased:

```
wget https://storage.googleapis.com/bert_models/2018_10_18/cased_L-12_H-768_A-12.zip
unzip cased_L-12_H-768_A-12.zip
```

### Binary Classification

Currently we use Bert-Base along with CRF layer. Result of the binary classification will be available in ./output/result_dir/label_test.txt after running the script.



### Entity linker:

Trigrams Jaccard similarity is utilized by default. Results of entity linking can be found in 2stage_res.txt


### Data Format:

Every line of these two files contains three items: [word, true_label, predicted_label].

