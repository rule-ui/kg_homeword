import json
from collections import OrderedDict
from gensim.models import KeyedVectors
from annoy import AnnoyIndex
import os
import argparse
import copy

def get_title(input_file, input_dir):
    with open(input_file, 'r', encoding='utf-8') as input:
        data = json.load(input)
        with open(os.path.join(input_dir, 'title.txt'), 'w', encoding='utf-8') as output:
            for title in data.keys():
                output.write(title[:-1]+' 100 qhy \n')


def get_words(word, num):
    with open('tc_word_index.json', 'r') as input:
        word_index = json.load(input)
    tc_index = AnnoyIndex(200)
    tc_index.load('tc_index_build10.index')
    reverse_word_index = dict([(value, key) for (key, value) in word_index.items()])
    words = []
    for item in tc_index.get_nns_by_item(word_index[word], num):
        words.append(reverse_word_index[item])
    return words


def merge_data(dir):
    kg = {}
    for i in range(1, 11):
        with open(os.path.join(dir, 'data'+str(i)+'.json'), 'r', encoding='utf-8') as input:
            data = json.load(input)
            for title, attrs in data.items():
                if kg.get(title, 'not find title') == 'not find title':
                    kg[title] = {}
                for attr, content in attrs.items():
                    attr_tmp = attr
                    if attr == '简介':
                        attr_tmp = '简介\n'
                    if kg[title].get(attr_tmp, 'not find attr') == 'not find attr':
                        kg[title][attr_tmp] = copy.deepcopy(content)
                    else:
                        kg[title][attr_tmp] = kg[title][attr_tmp] + copy.deepcopy(content)
    return kg


def get_embedding(model_path, output_dir):
    tc_wv_model = KeyedVectors.load_word2vec_format(model_path, binary=False)
    word_index = OrderedDict()
    for counter, key in enumerate(tc_wv_model.key_to_index.keys()):
        word_index[key] = counter
    with open(os.path.join(output_dir, 'tc_word_index.json'), 'w') as fp:
        json.dump(word_index, fp)
    tc_index = AnnoyIndex(200)
    i = 0
    for key in tc_wv_model.key_to_index.keys():
        v = tc_wv_model[key]
        tc_index.add_item(i, v)
        i += 1
    tc_index.build(10)
    tc_index.save(os.path.join(output_dir, 'tc_index_build10.index'))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_file', type=str, default="./data/data.json")
    parser.add_argument('--output_file', type=str, default="./data/data.json")
    parser.add_argument('--input_dir', type=str, default='./data')
    parser.add_argument('--embedding_model_path', type=str, default='./embedding_model/tencent-ailab-embedding-zh-d200-v0.2.0-s.txt')
    args = parser.parse_args()
    
    with open(args.output_file, 'w', encoding='utf-8') as output:
        json.dump(merge_data(args.input_dir), output, ensure_ascii=False)

    get_title(args.input_file, args.input_dir)

    get_embedding(args.embedding_model_path, args.input_dir)
    
if __name__ == '__main__':
    main()