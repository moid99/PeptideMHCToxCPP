# -*- coding: utf-8 -*-
"""EmbeddingGenerator.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1R_Fmr9FDlj551wBMhzjVWGdn9K40OBd8
"""

import torch
import argparse
from transformers import BertModel, BertTokenizer
import re
import requests
import os
import numpy as np
import pandas as pd
import sklearn
from tqdm import tqdm
import seaborn as sns
from pylab import rcParams
import matplotlib.pyplot as plt
from matplotlib import rc
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.utils import shuffle
import csv
from torch import nn, optim

import torch.nn.functional as F
parser = argparse.ArgumentParser()
parser = argparse.ArgumentParser()
parser.add_argument("--list", nargs="+")
value = parser.parse_args()
listpep = value.list
final1=list()
for peptide in listpep:
  separated = " ".join(peptide)
  final1.append(separated)
print(final1)

modelUrl = 'https://www.dropbox.com/s/luv2r115bumo90z/pytorch_model.bin?dl=1'
configUrl = 'https://www.dropbox.com/s/33en5mbl4wf27om/bert_config.json?dl=1'
vocabUrl = 'https://www.dropbox.com/s/tffddoqfubkfcsw/vocab.txt?dl=1'

downloadFolderPath = 'models/ProtBert-BFD/'

modelFolderPath = downloadFolderPath

modelFilePath = os.path.join(modelFolderPath, 'pytorch_model.bin')

configFilePath = os.path.join(modelFolderPath, 'config.json')

vocabFilePath = os.path.join(modelFolderPath, 'vocab.txt')

if not os.path.exists(modelFolderPath):
    os.makedirs(modelFolderPath)

def download_file(url, filename):
  response = requests.get(url, stream=True)
  with tqdm.wrapattr(open(filename, "wb"), "write", miniters=1,
                    total=int(response.headers.get('content-length', 0)),
                    desc=filename) as fout:
      for chunk in response.iter_content(chunk_size=4096):
          fout.write(chunk)

if not os.path.exists(modelFilePath):
    download_file(modelUrl, modelFilePath)

if not os.path.exists(configFilePath):
    download_file(configUrl, configFilePath)

if not os.path.exists(vocabFilePath):
    download_file(vocabUrl, vocabFilePath)

tokenizer = BertTokenizer(vocabFilePath, do_lower_case=False )

model = BertModel.from_pretrained(modelFolderPath)

device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

model = model.to(device)
model = model.eval()

sequences_Example = final1

sequences_Example = [re.sub(r"[UZOB]", "X", sequence) for sequence in sequences_Example]

ids = tokenizer.batch_encode_plus(sequences_Example, add_special_tokens=True, padding=True)

input_ids = torch.tensor(ids['input_ids']).to(device)
attention_mask = torch.tensor(ids['attention_mask']).to(device)

with torch.no_grad():
    embedding = model(input_ids=input_ids,attention_mask=attention_mask)[0]

embedding = embedding.cpu().numpy()

features = [] 
for seq_num in range(len(embedding)):
    seq_len = (attention_mask[seq_num] == 1).sum()
    seq_emd = embedding[seq_num][1:seq_len-1]
    features.append(seq_emd)


import statistics
final_features = list()
for peptide in features:
  length = len(peptide)
  peptide_features = list()
  for j in range(1024):
    feature_vector = list()
    for i in range(length):
      feature_vector.append(peptide[i][j])
    peptide_features.append(statistics.mean(feature_vector))
  final_features.append(peptide_features)

print(len(final_features))
print(len(final_features[0]))
print(final_features)

with open("peptide_features.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(final_features)