#!bash
#
# Set up a python env for a RAG 'application' that will answer questions
# using the content of a PDF file. Based on (copied from) Class 2 in the
# Coursera series on Agentic AI (Build RAG Applications: Get Started).
#
# Use this with the RAG_PDF.py code. That needs python 3.11.
# jhrg 7/30/26

# Install python 3.11
brew install python@3.11

# Get virtualenv
pip3 install virtualenv

# Make a virtual env that uses/contains python 3.11
virtualenv -p python3.11 myenv

source myenv/bin/activate # activate myenv

# installing necessary packages in myenv
python3.11 -m pip install \
gradio==4.44.0 \
jinja2==3.1.2 \
fastapi==0.110.0 \
starlette==0.36.3 \
huggingface_hub==0.23.5 \
ibm-watsonx-ai==1.1.2 \
langchain==0.2.11 \
langchain-community==0.2.10 \
langchain-ibm==0.1.11 \
chromadb==0.4.24 \
pypdf==4.3.1 \
pydantic==2.9.1
