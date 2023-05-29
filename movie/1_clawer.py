# -*-coding = utf-8-*-

# 模块引入
from bs4 import BeautifulSoup
import urllib.request,urllib.error
import re
import time
import csv
import jieba
import pandas as pd

# 全局变量
titleList = []
rateLst = []
numLst = []
infoLst = []
directorLst = []
actorLst = []
timeLst = []
countryLst = []
typeLst = []

# jieba中文分词
def jiebaCut(text):
    '''
    :param text:待分词的字符串 
    :return: 分词后的字符结果
    '''
    textCut = ' '.join(jieba.cut(text)).split(' ')
    ## 此处字符串处理必须保证'中国大陆'在原有列表中的位置(使用insert函数，而不是append函数)
    if '中国大陆' in text:
        index = textCut.index('中国')
        textCut.remove('中国')
        textCut.remove('大陆')
        textCut.insert(index,'中国大陆')
    return textCut[0]

# 处理演员信息，获得主演中的第一个，否则赋值'演职人员不详'
def ActorDealing(ActorInfo):
    '''
    :param ActorInfo:待处理的演职人员信息 
    :return: 演职人员名称或'演职人员不详'
    '''
    if '主演:' in ActorInfo:
        ActorInfo = ActorInfo.strip('主演:')
        if ActorInfo == "":
            ActorInfo = '演职人员不详'
        else:
            ActorInfo = ActorInfo.split('/')[0] # 获得演职员表中的第一个
    if ActorInfo == '主' or ActorInfo == '主演':
        ActorInfo = '演职人员不详'
    return ActorInfo


# 正则表达式匹配
findTitle = re.compile(r'<span class="title">(.*?)</span>') # 获取标题title
'''
1. 注意从网页源码复制，而不是手敲 2. 内容匹配时注意忽略其中的换行符 
'''
findContent = re.compile(r'<p class="">(.*?)</p>',re.S) # 获取电影主要内容
findRate = re.compile(r'<span class="rating_num" property="v:average">(.*?)</span>') # 获取评分
findNum = re.compile(r'<span>(.*?)</span>') # 获取评价人数
findInfo = re.compile(r'<span class="inq">(.*?)</span>') # 获取电影简介


# 请求获取网页信息
def askURL(url):
    '''模拟浏览器进行网页请求，返回网页信息
    :param url:待爬取的网页链接 
    :return: 获取到html网页信息
    '''
    head = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36 Edg/99.0.1150.39'
    }
    request = urllib.request.Request(url,headers = head)
    html = ''
    try:
        responseInfo = urllib.request.urlopen(request)
        html = responseInfo.read().decode('utf-8')
    except urllib.error.URLError as e: # 异常处理机制
        if hasattr(e,'code'):
            print(e.reason)
        if hasattr(e,'reason'):
            print(e.reason)

    return html

# 解析网页获得目标信息
def getData(html):
    '''网页内容解析，获取目标字段
    :param html: 获取到的html网页对象
    :return: None
    '''

    soup = BeautifulSoup(html,'lxml') # 网页解析

    ObjectPart = soup.find_all('ol',class_ = "grid_view")[0]
    for item in ObjectPart.find_all('li'):
        flag = 0

        item = str(item)

        movieDict = {}

        # title匹配，仅提取中文名称
        title = re.findall(findTitle,item)[0]
        titleList.append(title)

        # 电影内容内容匹配
        content = re.findall(findContent,item)[0]
        # 电影内容解析
        contentLst = content.split('\n')
        Time_Country_type = contentLst[2].replace(' ','').strip('/') # 去除所有的空格借助于replace(' ','')函数
        # 导演信息
        director = contentLst[1].replace(' ','').split('\xa0\xa0\xa0')[0].strip('导演:').split('/')[0]
        directorLst.append(director)

        # 演员信息(解决演员信息获取不到的问题)
        if len(contentLst[1].replace(' ','').split('\xa0\xa0\xa0')) == 1:
            actor = '演职人员不详'
        else:
            actor = contentLst[1].replace(' ','').split('\xa0\xa0\xa0')[1].strip('...<br/>') # 多人之间以'/'区分
        actor = ActorDealing(actor)
        actorLst.append(actor)

        # 上映时间信息
        time = Time_Country_type.split('/')[0].strip('\xa0')
        ## 添加数据筛选代码:后续报错->[py2neo]TypeError: Neo4j does not support JSON parameters of type int64尚未解决
        # if '(中国大陆)' in time:
        #     time = time.strip('(中国大陆)')
        timeLst.append(str(time))

        # 国家信息获取
        # country = Time_Country_type.split('/')[1].strip('\xa0')
        country = Time_Country_type.split('/')[1].replace('\xa0','')
        countryCut = jiebaCut(country)
        countryLst.append(countryCut)

        # 类型信息获取
        type = contentLst[2].strip('/').split('/')[-1].strip('\xa0').split(' ')[0] # 多类型之间以' '区分
        typeLst.append(type)

        # 电影评分内容匹配
        rate = re.findall(findRate,item)[0]
        rateLst.append(str(rate))
        # 电影评价人数匹配
        num = re.findall(findNum,item)[0].strip('评价')
        numLst.append(num)
        # 电影简介获取
        info = re.findall(findInfo,item)
        # 解决信息可能获取不到
        if len(info) != 0:
            info = info[0]
        else:
            info = '电影详细信息不详'
        infoLst.append(info)

def ClawerCode(fileName):
    '''网络爬虫主体程序：获取电影各部分信息,写入csv文件
    :return: None
    '''
    # 比较网页url区别，多界面爬取
    for i in range(10):
        LoopUrl = 'https://movie.douban.com/top250?start=' + str(i*25) + '&filter=' # 网页切换
        time.sleep(2) # 爬虫速率控制(自己添加，不知道有没有用)
        html = askURL(LoopUrl)
        getData(html)
        print(i)
        pass

    with open(fileName,'w',encoding = 'utf-8') as f:
        # 构建列表头
        f.write('title,rate,num,info,director,actor,time,country,type')
        f.write('\n')
        for i in range(len(titleList)):
            f.write(titleList[i] + ',' + rateLst[i] + ',' + numLst[i] + ',' + infoLst[i] + ',' + directorLst[i] + ',' + actorLst[i] + ',' + timeLst[i] + ',' + countryLst[i] + ',' + typeLst[i])
            f.write('\n')
            pass
        f.close()

def defDict(fileName_1, fileName_2):
    ## jiaba分词添加自定义词典，以保证电影名称分词正确
    ## 自定义词典构建时，分别写入 名词 词频 词性(词性，可以省略，但建议自定义写出，方便后续使用)
    # 读取原数据库
    storage_df = pd.read_csv(fileName_1, encoding = 'utf-8')
    movieNameLst = [name for name in storage_df['title']]

    # 构建自定义词典
    with open(fileName_2, 'w', encoding = 'utf-8') as f:
        for name in movieNameLst:
            f.write(name + ' 100 lqy')
            f.write('\n')
            pass
        f.close()

    pass

# make triplets for transE

# create a file that contains the triplets
def create_triplets_file(file_path, triplet_file_path):
    # read movies.csv into a pandas DataFrame
    df = pd.read_csv(file_path)
     
    # extract the columns that contain the entities and relations
    entity_cols = ['title','rate','num','info','director','actor','time','country','type']
    relation_cols = ['title_by','gradeed_by','watched_by','main_info','directed_by','starring','released_in','made_in','of_type']
    
    # create a list of triplets
    triplets = []
    for i, row in df.iterrows():
        for j, entity_col in enumerate(entity_cols):
            head_entity = row['title']
            relation = relation_cols[j]
            tail_entity = row[entity_col]
            triplets.append((head_entity, relation, tail_entity))
    

    # write the triplets to a file
    with open(triplet_file_path, 'w', encoding='utf-8') as f:
        for triplet in triplets:
            f.write(f"{triplet[0]}\t{triplet[1]}\t{triplet[2]}\n")
    
    print(f"Triplets written to {triplet_file_path}")

# create files that contain the entity2id and relation2id mappings
def create_entity2id_relation2id_files(train_file_path, entity2id_file_path, relation2id_file_path):
    # read the train file into a list of lines
    with open(train_file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # extract the unique entities and relations from the train file
    entities = set()
    relations = set()
    for line in lines:
        parts = line.strip().split('\t')
        entities.add(parts[0])
        entities.add(parts[2])
        relations.add(parts[1])
    
    # assign a unique ID to each entity and relation
    entity2id = {}
    relation2id = {}
    for i, entity in enumerate(entities):
        entity2id[entity] = i
    for i, relation in enumerate(relations):
        relation2id[relation] = i
    
    # write the entity2id mapping to a file
    with open(entity2id_file_path, 'w', encoding='utf-8') as f:
        for entity, entity_id in entity2id.items():
            f.write(f"{entity}\t{entity_id}\n")
    
    print(f"Entity2id mapping written to {entity2id_file_path}")
    
    # write the relation2id mapping to a file
    with open(relation2id_file_path, 'w', encoding='utf-8') as f:
        for relation, relation_id in relation2id.items():
            f.write(f"{relation}\t{relation_id}\n")
    
    print(f"Relation2id mapping written to {relation2id_file_path}")


if __name__ == '__main__':
    file_path = './data/movies.csv'
    dict_file_path = './data/defDict.txt'
    triplet_file_path = './data/triplet.txt'
    entity2id_file_path = './data/entity2id.txt'
    relation2id_file_path = './data/relation2id.txt'

    # 爬虫主体程序
    ClawerCode(file_path)

    # 构建自定义词典
    defDict(file_path, dict_file_path)

    # 构建三元组
    create_triplets_file(file_path, triplet_file_path)

    # 构建实体和关系映射
    create_entity2id_relation2id_files(triplet_file_path, entity2id_file_path, relation2id_file_path)
