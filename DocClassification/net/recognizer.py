import torch
import torch.nn as nn
import torch.nn.functional as F
import json
import re
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import WordPunctTokenizer

import nltk
nltk.download('wordnet')

import nltk
nltk.download('stopwords')

class CNN(nn.Module):
    def __init__(self, batch_size, output_size, in_channels, out_channels, kernel_heights, stride, padding, keep_probab, vocab_size, embedding_length):
        super(CNN, self).__init__()

        self.batch_size = batch_size
        self.output_size = output_size
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.kernel_heights = kernel_heights
        self.stride = stride
        self.padding = padding
        self.vocab_size = vocab_size
        self.embedding_length = embedding_length

        self.word_embeddings = nn.Embedding(vocab_size, embedding_length)
        self.conv1 = nn.Conv2d(in_channels, out_channels, (kernel_heights[0], embedding_length), stride, padding)
        self.conv2 = nn.Conv2d(in_channels, out_channels, (kernel_heights[1], embedding_length), stride, padding)
        self.conv3 = nn.Conv2d(in_channels, out_channels, (kernel_heights[2], embedding_length), stride, padding)
        self.dropout = nn.Dropout(keep_probab)
        self.label = nn.Linear(len(kernel_heights)*out_channels, output_size)
        self.sigmoid = nn.Sigmoid() 
        
    def conv_block(self, input, conv_layer):
        conv_out = conv_layer(input)# conv_out.size() = (batch_size, out_channels, dim, 1)
        activation = F.relu(conv_out.squeeze(3))# activation.size() = (batch_size, out_channels, dim1)
        max_out = F.max_pool1d(activation, activation.size()[2]).squeeze(2)# maxpool_out.size() = (batch_size, out_channels)

        return max_out

    def forward(self, input_sentences, batch_size=None):

        input = self.word_embeddings(input_sentences)
#         print(input.size())
        # input.size() = (batch_size, num_seq, embedding_length)
        input = input.unsqueeze(1)
        # input.size() = (batch_size, 1, num_seq, embedding_length)
        max_out1 = self.conv_block(input, self.conv1)
        max_out2 = self.conv_block(input, self.conv2)
        max_out3 = self.conv_block(input, self.conv3)

        all_out = torch.cat((max_out1, max_out2, max_out3), 1)
        # all_out.size() = (batch_size, num_kernels*out_channels)
        fc_in = self.dropout(all_out)
        # fc_in.size()) = (batch_size, num_kernels*out_channels)
        logits = self.label(fc_in)
        logits = self.sigmoid(logits)
        return logits
      
def normalize(text):
    # print(text)
    ret = [i for i in re.split('\W', text.lower()) if i.isalpha()]
    ret = ' '.join(ret)
    return ret

def tokenize(text):
    tokenizer = WordPunctTokenizer()
    return tokenizer.tokenize(text)

def lemmatize(tokens):
    lemmatizer = WordNetLemmatizer()
    return [lemmatizer.lemmatize(token) for token in tokens]

def remove_stop_word(tokens):
    stopWords = set(stopwords.words('english'))
    return [i for i in tokens if i not in stopWords]

def label_encoding(text, vocab):
    code = []
    for t in text:
        if t in vocab:
            code.append(vocab[t])
    return code

def preprocess(text, vocab):
    ret = normalize(text)
    ret = tokenize(ret)
    ret = lemmatize(ret)
    ret = remove_stop_word(ret)
    return label_encoding(ret, vocab)



with open('./names.json', 'r') as fp:
    name_map = json.load(fp)  

with open('./vocab.json', 'r') as fp:
    vocab = json.load(fp)  

inv_name_map = {name_map[key]:key for key in name_map}

cnn = CNN(batch_size=16, 
    output_size = len(name_map),
    in_channels = 1, 
    out_channels = 128,
    kernel_heights = [1,3,5],
    stride = 1,
    padding = 0,
    keep_probab = 0.5,
    vocab_size = len(vocab)+1,
    embedding_length = 300).cuda()

cnn.load_state_dict(torch.load('./model.pth', map_location='cpu'))
cnn.eval()
print('DONE')