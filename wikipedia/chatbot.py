# -*-coding = utf-8-*-

import jieba.posseg as pseg
import jieba
from fuzzywuzzy import fuzz
import json
from collections import OrderedDict
from gensim.models import KeyedVectors
from annoy import AnnoyIndex
import os
import argparse
import copy


def load_embedding(model_path):
    with open(os.path.join(model_path, 'tc_word_index.json'), 'r') as input:
        word_index = json.load(input)
    
    reverse_word_index = dict([(value, key) for (key, value) in word_index.items()])

    tc_index = AnnoyIndex(200)
    tc_index.build(10)
    tc_index.load(os.path.join(model_path, 'tc_index_build10.index'))    

    return reverse_word_index, tc_index, word_index


def get_embedding(text, num, model):
    res = []

    if model[2].get(text, 'not find title') == 'not find title':   
        return res
    
    for item in model[1].get_nns_by_item(model[2][text], num):
        res.append(model[0][item])

    return res


def best_match(text, titles, num, model):
    titleDegree = {}
    for title in titles:
        titleDegree[title] = fuzz.partial_ratio(text, title)
    title_sort = sorted(titleDegree.items(), key=lambda x: x[1], reverse=True)
    ratio = -1.0
    title = ''
    Degree = {}
    for i in range(min(len(title_sort), num)):
        ratio_tmp = 0.0
        ner_title = get_embedding(title_sort[i][0], 3, model)
        if len(ner_title) == 0:
            words = pseg.cut(title_sort[i][0])
            for word in words:
                ner_title = copy.deepcopy(get_embedding(word.word, 3, model)) + ner_title
        for title_tmp in ner_title:
            ratio_tmp += fuzz.partial_ratio(text, title_tmp)
        ratio_tmp += fuzz.partial_ratio(text, title_sort[i][0])
        ratio_tmp = ratio_tmp / (len(ner_title) + 1)
        Degree[title_sort[i][0]] = ratio_tmp
    Degree_sort = sorted(Degree.items(), key=lambda x: x[1], reverse=True)
    return Degree_sort


def AssignIntension(text, titles, kg, model):
    if len(titles) == 0:
        return '', ''
    title_degree = best_match(text, titles, 3, model)
    title = ''
    
    for i in title_degree:
        for _, value in kg[i[0]].items():
            if len(value) > 0:
                title = i[0]
                break
        if not title == '':
            break
        
    if title == '':
        return '',''
    
    attr = ''
    list_tmp = copy.deepcopy(list(kg[title].keys()))
    while True:
        attr_degree = best_match(text, list_tmp, 4, model)
        for i in attr_degree:
            if len(kg[title][i[0]]) > 0:
                attr = i[0]
                break
            else:
                list_tmp.remove(i[0])
        if not attr == '':
            break
    return attr, title


def get_title(text, kg, model):
    title = []
    words =pseg.cut(text)
    for word in words:
        if word.flag == 'qhy':
            title.append(word.word+'\n')
    if len(title) == 0:
        print('ner_title')
        for word in words:
            ner_words = get_embedding(word.word, 10, model)
            for ner_title in ner_words:
                print(ner_title)
                if kg.get(ner_title+'\n', 'not find title') == 'not find title':
                    continue
                title.append(ner_title)
    
    return title


def get_answer(attr, title, kg):
    answer = ''
    if title == '' or attr == '' or kg[title][attr] == []:
        answer = '知识库未找到数据'
        return answer

    for cont in kg[title][attr]:
        answer = answer + cont
    return answer


def chat_main(question, kg, model):

    title = get_title(question, kg, model)
    print(title)
    '''
    for i, k in kg[title[0]].items():
        print(i,':',k)
    '''
    attr, title = AssignIntension(question, title, kg, model)
    print(title)
    print(attr)

    answer = get_answer(attr, title, kg)

    return answer


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--input_file', type=str, default="./data/data.json")
    parser.add_argument('--input_dir', type=str, default='./data')
    parser.add_argument('--embedding_model_path', type=str, default='./data')
    args = parser.parse_args()

    '''
    reverse_word_index, tc_index, word_index = load_embedding(args.embedding_model_path)
    for i in get_embedding('南京市长江大桥', 10, reverse_word_index, tc_index, word_index):
        print(i)
    '''

    with open(args.input_file, 'r', encoding='utf-8') as Input:
        
        data = json.load(Input)
        jieba.load_userdict(os.path.join(args.input_dir, 'title.txt'))
        model = load_embedding(args.embedding_model_path)

        while True:

            question = input("问题：")
            answer = chat_main(question, data, model)
            print('ChatBot:', answer)
