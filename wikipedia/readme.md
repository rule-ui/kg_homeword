# Knowledge Graph
    首先下载wikipedia官网上对应的page-article文件。
    然后在wikiExtractor文件夹下进行文件的解析、抽取。
    接着利用extractor.py和preprocess.py对数据进行处理，并存储为json格式。
    最后利用chatbot.py进行推理问答。

```
如果只想要试试效果，可以直接使用处理好的json文件。直接运行chatbot.py进行推理。
```

# 准备

安装jave SE。

下载腾讯的中文词向量模型[原始模型](https://pan.baidu.com/s/1ftR2iroMSBz0YVL88Nwu8A?pwd=KG44)[处理后的模型](https://pan.baidu.com/s/1pEjQBeBO0nQxC99Dxrv-Xg?pwd=KG44)。如果想直接运行chatbot.py，可以仅下载处理好的模型。

下载opencc等python包需要的文件。

# 补充

如果想要完全复现团队在这个模块的操作，[可以参见github](https://github.com/rule-ui/kg_homeword)，后续团队会封装出完善的shell文件。
