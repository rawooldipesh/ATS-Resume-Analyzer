#!/bin/bash

# Upgrade pip and install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Download required NLTK data to local directory
python -m nltk.downloader -d ./nltk_data punkt stopwords wordnet
