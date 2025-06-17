#!/bin/bash

# Install dependencies
pip install -r requirements.txt

# Force download all required NLTK tokenizers to a known directory
python -m nltk.downloader -d ./nltk_data punkt punkt_tab stopwords wordnet
