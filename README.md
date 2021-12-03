# TextMining

Here lies code used to extract entity from raw text. 

See TokenPipeline for our two-stage token level entity recognition work. Preprocessed data and results are available in this folder. 

## Other code that will appear here later:

Basic data preprocessing: Codes transforming the original wtsv files to Conll form will be available here, as well as code used to split train/test data and generate sentence-level annotated files.

Sentence-level binary classification: A single file utilizing FastText to determine whether a sentence contains any type of entity or not.

Data preparation for usage of Solr search engine: some scripts used to generate json files containing information readable and necessary for Solr to index.
