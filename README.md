# TextMining

Here lies code used to extract entity from raw text. 

See TokenPipeline for our two-stage token level entity recognition work.

See DataPreprocessing for the wtsv documents and codes used to transform them in form that can be understood by BERT-NER (.conll). Codes used to process jsons and generate conll files for unannotated articles are also available here.

See DataPostprocessing for codes regarding aligning output of two-stage model in article-level, after which we can get articles with their corresponding concepts and evaluate performance of the whole model. Query_generator is a file used to retrieve top-k articles using NBC, which can automatize the retrieval of articles used in human judgement.

See TextClassification for a very simple example showing the performance of sentence-level classification.


