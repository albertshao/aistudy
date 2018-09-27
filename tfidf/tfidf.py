# -*- coding: utf-8  -*-
"""
介绍博客地址：https://blog.csdn.net/sxb0841901116/article/details/82839602
"""
import jieba
import math
import operator
import re
import requests
from collections import Counter


class TFIDFAnalyzer(object):
    def __init__(self):
        self.total_chinese_doc = 60000000000  # 假设所有的中文文档有60亿

    def cut_context(self, context):
        """
        调用结巴分词进行切分
        :return:seg_list 包含分析的迭代器
        """
        seg_list = jieba.cut(context, cut_all=False)
        return seg_list

    def get_tf(self, context):
        """
        计算每个词的词频term frequency 计算公式tf=count of word / total number of context
        :param context: 文本内容
        :return: 根据词频从高到底排列的OrderedDict字典， key为word, value为tf值
        """
        word_tf_dict = {}
        # step 1: 针对语句进行分析， 此处利用结巴进行分析
        seg_list = self.cut_context(context)

        # step 2: 统计每隔分词的次数, 计算tf
        for word, count in Counter(seg_list).iteritems():
            word_tf_dict[word] = operator.div(float(count), len(context))

        return word_tf_dict

    def get_idf(self, context):
        """
        计算输入文本中每隔分词的逆文档频率 idf, 在此处假设中文总文档为D=65亿
        各个分词出现文档为
        :param context: 输入分文
        :return:
        """
        word_idf_dict = {}
        seg_list = self.cut_context(context)
        for seg in seg_list:
            seg_doc_count = self.get_doc_count(seg)
            idf = math.log(operator.div(self.total_chinese_doc, operator.add(seg_doc_count, 1)), 10)
            print seg, seg_doc_count, idf
            word_idf_dict[seg] = idf

        return word_idf_dict

    def get_df_idf_values(self, word_idf_dict, word_tf_dict):
        """
        计算df_idf的值
        :param word_idf_dict: 逆文档频率数据
        :param word_tf_dict: 词频数据
        :return: df_idf的数据
        """
        df_idf_value_dict = {}
        for word in word_idf_dict:
            df_idf_value_dict[word] = operator.mul(word_idf_dict.get(word), word_tf_dict.get(word))

        return df_idf_value_dict

    def get_doc_count(self, word):
        """
        通过百度上进行搜索，获取每个分词出现在的中文文档的个数
        :param word:
        :return:
        """
        doc_count = 0
        try:
            url = r'http://www.baidu.com/s?wd=' + word
            res = requests.get(url)
            word_count_list = re.findall(ur'百度为您找到相关结果约(.*)个', res.text)
            if word_count_list:
                doc_count = re.sub(r'\D', '', word_count_list[0]).strip()
        except:
            doc_count = 0

        return int(doc_count)


if __name__ == '__main__':
    similar_calculator = TFIDFAnalyzer()
    context = u'查看一下亚马逊服务器硬盘'
    word_idf_dict = similar_calculator.get_idf(context)
    word_tf_dict = similar_calculator.get_tf(context)
    idf_values = similar_calculator.get_df_idf_values(word_idf_dict, word_tf_dict)
    idf_values = sorted(idf_values.iteritems(), key=lambda x: x[1], reverse=True)
    for key, value in idf_values:
        print key, round(value, 2)
