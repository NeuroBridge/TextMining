#!/usr/bin/env bash

  python BERT_NER.py\
    --task_name="NER"  \
    --do_lower_case=False \
    --crf=True \
    --do_train=True   \
    --do_eval=False   \
    --do_predict=True \
    --data_dir=data   \
    --vocab_file=cased_L-12_H-768_A-12/vocab.txt  \
    --bert_config_file=cased_L-12_H-768_A-12/bert_config.json \
    --init_checkpoint=cased_L-12_H-768_A-12/bert_model.ckpt   \
    --max_seq_length=512   \
    --train_batch_size=8   \
    --learning_rate=2e-5   \
    --num_train_epochs=4.0   \
    --output_dir=./output/result_dir \
    --data_train="train.txt"  \
    --data_dev="dev.txt"  \
    --data_test="test.txt"  


perl conlleval.pl -d '\t' < ./output/result_dir/label_test.txt
  python3 Entity_linking.py 
