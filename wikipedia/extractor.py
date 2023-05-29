import re
import opencc
import json
import argparse



def title_attr():
    index = open("zhwiki-latest-abstract-zh-cn1.xml", "r", encoding='utf-8')
    kg = {}
    try:
        while True:
            text = index.readline()
            if text[:7] == "<title>":
                kg[text[17:-9]]={}
                title = text
                text = index.readline()
                while True:
                    if text[:7] == "<title>":
                        break
                    if text[:8] == "<sublink":
                        tmp = re.search("</anchor>", text)
                        if not tmp == None:
                            loc = tmp.span()
                            kg[title[17:-9]][text[32:loc[0]]] = []
                    text = index.readline()
    except EOFError:
        index.close()
    return kg

def get_kg(input_file):
    kg = {}
    num = 0
    simple_chinese = opencc.OpenCC('t2s.json')
    with open(input_file, "r", encoding="utf-8") as index:
        text = index.readline()
        while True:
            text = simple_chinese.convert(index.readline())
            num += 1
            if num % 1000 == 0:
                print("第"+str(num)+"个词："+text)
            # print(text)
            kg[text] = {}
            attr = "简介"
            kg[text][attr] = []
            title = text
            index.readline()
            while True:
                text = simple_chinese.convert(index.readline())
                if text == "</doc>\n":
                    break
                if len(text) > 1:
                    if text[-2] == '.':
                        attr = text[:-2]+'\n'
                        kg[title][attr] = []
                    else:
                        kg[title][attr].append(text)
            text = index.readline()
            if not text[:4] == "<doc":
                break
    print("完成了"+str(num)+"个词的抽取")
    '''
    for i, k in kg.items():
        print('i')
        print(i)
        for j, l in k.items():
            print('j')
            print(j)
            for p in l:
                print('p')
                print(p)
    '''
    '''
    attrs = []
    for i, k in kg.items():
        for j in k.keys():
            if j not in attrs:
                attrs.append(j)
    print(str(len(attrs))+"种关系")
    '''
    return kg

def get_relation(input_file):
    with open(input_file, 'r', encoding='utf-8') as input:
        data = json.load(input)
        attr = []
        num = 0
        for i in data.values():
            num += 1
            if num % 1000 == 0:
                print("第"+str(num)+"个词")
            for k in i.keys():
                if k not in attr:
                    print(k)
                    attr.append(k)
    return attr

def main():
    '''
    for i in range(1,11):
        parser = argparse.ArgumentParser()
        parser.add_argument('--input_file', type=str, default="./wikipedia/wiki_"+str(i)+str(i))
        parser.add_argument('--output_file', type=str, default="./data/data"+str(i)+".json")
        parser.add_argument('--output_dir', type=str, default='./data/relation'+str(i)+'.txt')
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_file', type=str, default="./wikipedia/wiki_11")
    parser.add_argument('--output_file', type=str, default="./data/data.json")
    parser.add_argument('--output_dir', type=str, default='./data/relation.txt')
    args = parser.parse_args()

#    with open("data_no_attrs.json", 'w', encoding='utf-8') as output:
#        json.dump(title_attr(), output, ensure_ascii=False)

#    with open(args.output_file, 'w', encoding='utf-8') as output:
#        json.dump(get_kg(args.input_file), output, ensure_ascii=False)

    relations = get_relation(args.output_file)
    with open(args.output_dir, 'w', encoding='utf-8') as output:
        for i in relations:
            output.write(i)


if __name__ == '__main__':
    main()