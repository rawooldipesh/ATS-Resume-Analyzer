#!/bin/bash

# Install dependencies
pip install -r requirements.txt

# Download NLTK data to custom path inside the project
python -m nltk.downloader -d ./nltk_data punkt stopwords wordnet
