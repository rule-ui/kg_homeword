# Knowledge Graph
    本项目主要包含四个部分，对应于作业的四条要求
    1_clawer    :   网页爬虫, 构建三元组, 抽取实体和关系
    2_buildKG   :   构建图数据库
    3_transE    :   transE算法的实现
    4_chatbot   :   基于图数据库的问答机器人

## 运行方式
    data文件夹中所有文件都是由程序生成的，原始文件只有4个.py文件和一个空的data文件夹。

### 开始准备

#### 安装neo4j
#### 将文件2_buildKG.py中第9行和文件4_chatbot.py中第9行的信息改为自己的neo4j的信息
#### 配置python环境
```cmd
pip install -r requirements.txt
```


### 正式运行
    依次运行1_clawer.py, 2_buildKG.py, 3_transE.py, 4_chatbot.py