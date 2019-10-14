import functools
import hashlib
import threading
import time

import numpy
import os
from multiprocessing import Process
import multiprocessing

import jieba
import jieba.analyse
import pandas as pd
from scrapy import cmdline
from twisted.internet import reactor, defer
from pyecharts import options as opts
from pyecharts.globals import SymbolType
from pyecharts.charts import Pie, Bar, Map, WordCloud

from TaobaoSimple.tmall.spiders.Utils.SQLUtils import MysqldbHelper
from ..items import TmallItem
import orangecontrib.associate.fpgrowth as oaf  # 进行关联规则分析的包
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


class TransactionMain:
	def __init__(self):
		self.urllists = []
		self.items = TmallItem()
	
	def handleDatas(self,  oriurl, orilable, urllists, delete_urllists):
		"""
		当点击下载时候，获取所添加的URL，启动爬虫开始下载
		:return:
		"""
		self.urllists = urllists
		if delete_urllists != []:
			# p_delete = Process(target=self.deleteOldDatas,args=(delete_urllists,))
			# p_delete.start()
			# p_delete.join()
			# p_delete = threading.Thread(target=self.deleteOldDatas, args=(delete_urllists,))
			# p_delete.start()
			# p_delete.join()
			self.deleteOldDatas(delete_urllists)
		
		aim_lables = []
		for item in urllists:
			aim_lables.append(orilable[oriurl.index(item)])
		
		# 这里执行插入语句，将新的url+lable数据插入到details数据表
		threading.Thread(target=self.insertUrlLableIntoSQL, args=(urllists, aim_lables)).start()
		
		urllists = ','.join(urllists)
		# cmdline.execute(["scrapy", "crawl", "tmallMain","-a","url_lists="+urllists])
		process = CrawlerProcess(get_project_settings())
		# 'credit'替换成你自己的爬虫名
		process.crawl('tmallMain', url_lists=urllists)
		process.start()  # the script will block here until the crawling is finished
		process.join()
	

	def downloadDatas(self, dataqueue, oriurl, orilable, download_urllists, delete_urllists=[]):
		p = Process(target=self.handleDatas, args=( oriurl, orilable, download_urllists, delete_urllists))
		p.start()
		p.join()
		# self.handleDatas(oriurl, orilable, download_urllists, delete_urllists)
		print("数据下载完毕，执行 dataqueue.put(1) 语句")
		dataqueue.put("downloadDatas_method_is_over")
	
	def all_job_rtn(self,result):
		reactor.stop()
	
	def collectDataFromDeffered(self, result, url_item, queue):
		print({url_item: result})
		queue.put({url_item: result})
	
	# def checkAboutDatas(self, abouturl_list, queue):
	# 	twistadapihelper = TwistedAdbapiSQLHelper.from_settings()
	# 	job_list = []
	# 	for item_ in abouturl_list:
	# 		job1 =twistadapihelper.do_select('urldetials3', True, [self.url_encrypt(item_)]).addCallback(self.collectDataFromDeffered, item_,queue,)
	# 		job_list.append(job1)
	# 	deferred_list = defer.DeferredList(job_list)
	# 	deferred_list.addCallback(self.all_job_rtn)
	# 	reactor.run()
		
	def checkAboutDatas(self, abouturl_list):
		sqlhelper = MysqldbHelper()
		aim_dicts = {}
		for item_ in abouturl_list:
			resu_ = sqlhelper.select_byHashUrl('urldetials3', [self.url_encrypt(item_)])
			print("resu_: ")
			print(resu_)
			aim_dicts[item_] = resu_
		return aim_dicts
	
	
	
		
	def classifyURLNewOrOld(self, url_list, lablelist):
		newurllists = {}
		oldurllist = {}
		# global processqueue
		# p_put = Process(target=self.checkAboutDatas, args=(url_list, processqueue))
		# p_put.start()
		# p_put.join()
		aim_dicts = self.checkAboutDatas(url_list)
		del_urllist = []
		for key_,value_ in aim_dicts.items():
			datas = value_
			url_ = key_
			if len(datas) == 0:
				creattime = time.strftime('%Y.%m.%d %H:%M:%S ', time.localtime(time.time()))
				newurllists[url_] = {'lable_': str(lablelist[url_list.index(url_)]), 'creattime_': str(creattime)}
			elif len(datas) == 1:
				oldurllist[url_] = {'lable_': str(datas[0]['lable']), 'creattime_': str(datas[0]['creattime'])}
			else:
				# p_delete = Process(target=self.deleteOldDatas, args=([url_],))
				# # self.deleteOldDatas(delete_urllists)
				# p_delete.start()
				# p_delete.join()
				del_urllist.append(url_)
				newurllists[url_] = {'lable_': str(lablelist[url_list.index(url_)])}
		if len(del_urllist) != 0:
			self.deleteOldDatas(del_urllist)
		return newurllists, oldurllist
	
	# def deleteOldDatas(self,oldurl_list):
	# 	twistadapihelper = TwistedAdbapiSQLHelper.from_settings()
	# 	job_list = []
	# 	for item_ in oldurl_list:
	# 		job1 = twistadapihelper.do_delete('urldetials3', {'hashurl': self.url_encrypt(item_)})
	# 		job2 = twistadapihelper.do_delete('taobaocomment3', {'hashurl': self.url_encrypt(item_)})
	# 		job_list.append(job1)
	# 		job_list.append(job2)
	# 	# time.sleep(10)
	# 	deferred_list = defer.DeferredList(job_list)
	# 	deferred_list.addCallback(self.all_jobs_done)
	# 	reactor.run()
	
	# 所有deferred完成之后，触发回调提醒我们
	# def all_jobs_done(self,result):
	# 	reactor.stop()
		
	def deleteOldDatas(self, oldurl_list):
		mysqlhelper = MysqldbHelper()
		urls_ = [self.url_encrypt(item) for item in oldurl_list]
		print(urls_)
		mysqlhelper.deleteManyByUrls('urldetials3', urls_)
		mysqlhelper.deleteManyByUrls('taobaocomment3', urls_)
	
	
	
	def analysizeDatas(self, analyselist, urllists, category, supportRate=0.02, confidenceRate=0.5, savepath=r'C:\Users\Administrator\Desktop'):
		# 首先是得到分词前的数据集
		if not os.path.exists(savepath):
			os.makedirs(savepath)
		pd_oragin = self.getStandardDataFromSQL(urllists)
		if pd_oragin is None:
			analyselist.put(0)     #   analysequeue.put(0) 返回值为0时候说明为渠道数据，数据库数据不存在
			return None
		# 根据评论信息做出词云图
		self.doWordCloud(pd_oragin, savepath)
		# 对所选择的分析功能进行分析
		for item in category:
			try:
				self.doAnalysize(pd_oragin, item, supportRate, confidenceRate, savepath)
			except:
				analyselist.put(item)
				continue
		analyselist.put(1)
		print("**********************数据分析完毕！********************")
		
	def getStandardDataFromSQL(self, urllists):
		sqlhepler = MysqldbHelper()
		hashurls = list(map(self.url_encrypt, urllists))
		datas = sqlhepler.select_byHashUrl(tablename='taobaocomment3', cond_dict=hashurls, fields=['rateContent', 'appendComment'])
		if len(datas) == 0:
			return None
		pd_data1 = pd.DataFrame(datas)
		ratecontent_str = pd_data1['rateContent'].str
		is_emptycoment = ratecontent_str.contains("评价方未及时做出评价,系统默认好评!") | ratecontent_str.contains("此用户没有填写评论!") | (
					ratecontent_str.strip() == "")
		pd_data1.loc[is_emptycoment, 'rateContent'] = pd_data1.loc[is_emptycoment, 'appendComment']
		pd_data2 = pd_data1.loc[pd_data1['rateContent'].str.strip() != ""][['rateContent']]
		return pd_data2
	
	def insertUrlLableIntoSQL(self, urllists, lablelist):
		sqlhepler = MysqldbHelper()
		aim_list = []
		hashurls = list(map(self.url_encrypt, urllists))
		# print("urllists列表为: ")
		# print(urllists)
		# print("hashurls列表为: ")
		# print(hashurls)
		creattime = time.strftime('%Y.%m.%d %H:%M:%S ', time.localtime(time.time()))
		for index in range(len(urllists)):
			aim_list.append([hashurls[index], urllists[index], lablelist[index], creattime])
		sqlhepler.insertMany('urldetials3',['hashurl','detial','lable','creattime'], aim_list)


	def doAnalysize(self, pd_data, category, supportRate=0.02, confidenceRate=0.5, savepath=r'C:\Users\Administrator\Desktop'):
		# 初始化词库路径
		savepath = savepath+"\\"+category
		if not os.path.exists(savepath):
			os.makedirs(savepath)
		initpath = "tmall\\spiders\\DataAnalysize\\jiebaInit\\"+category+".txt"
		jieba.load_userdict(initpath)
		pd_data['ratecontent_list'] = pd_data.apply(lambda r: list(jieba.cut(r['rateContent'])), axis=1)
		
		aim_list = []
		with open(initpath, 'r', encoding="utf-8") as f:
			for line in f.readlines():
				aim_list.append(line.strip('\n'))
		pd_data['aim_list'] = pd_data.apply(lambda r: list(set(r['ratecontent_list']).intersection(set(aim_list))), axis=1)
		simple_aimdata = []
		pd_data.apply(lambda r: simple_aimdata.append(r['aim_list']) if not r['aim_list'] == [] else 1, axis=1)
		wordcloudlist = []
		for item in simple_aimdata:
			for i in item:
				wordcloudlist.append(i)
		# 生成每种分析的词云图
		self.everyWordCloud(wordcloudlist, savepath)
		
		
		#经过上面两行操作，得到目标列表： simple_aimdata
		strSet = set(functools.reduce(lambda a, b: a + b, simple_aimdata))
		strEncode = dict(zip(strSet, range(len(strSet))))  # 编码字典，即:{'甜腻': 6,'鱼腥味': 53,etc...}
		strDecode = dict(zip(strEncode.values(), strEncode.keys()))  # 解码字典，即:{6:'甜腻',53:'鱼腥味',etc...}
		listToAnalysis_int = [list(map(lambda item: strEncode[item], row)) for row in simple_aimdata]
		# 开始进行关联分析
		itemsets = dict(oaf.frequent_itemsets(listToAnalysis_int, supportRate))
		# print("itemsets : ")
		# print(itemsets)
		rules = oaf.association_rules(itemsets, confidenceRate)
		rules = list(rules)
		regularNum = len(rules)
		printRules = self.dealRules(rules, strDecode)   # 该变量可以打印查看生成的规则
		# print(printRules)
		result = list(oaf.rules_stats(rules, itemsets, len(listToAnalysis_int)))  # 下面这个函数改变了rules，把rules用完了！
		# print(result)
		printResult = self.dealResult(result, strDecode)  # 该变量可以打印查看结果
		# print(printResult)
		
		#################################################下面将结果保存成excel格式的文件
		# save rules to excel
		dfToSave = self.ResultDFToSave(result, strDecode)
		saveRegularName = savepath+"\\"+str(supportRate) + '支持度_' + str(confidenceRate) + '置信度_产生了' + str(regularNum) + '条规则' + '.xlsx'
		dfToSave.to_excel(saveRegularName)
		# save itemsets to excel
		self.saveItemSets(itemsets, strDecode, savepath)
		
		#######################################################下面是根据不同置信度和关联度得到关联规则数目
		listTable = []
		supportRate = 0.01
		confidenceRate = 0.1
		for i in range(9):
			support = supportRate * (i + 1)
			listS = []
			for j in range(9):
				confidence = confidenceRate * (j + 1)
				itemsets = dict(oaf.frequent_itemsets(listToAnalysis_int, support))
				rules = list(oaf.association_rules(itemsets, confidence))
				listS.append(len(rules))
			listTable.append(listS)
		dfList = pd.DataFrame(listTable, index=[supportRate * (i + 1) for i in range(9)], columns=[confidenceRate * (i + 1) for i in range(9)])
		dfList.to_excel(savepath+"\\"+'regularNum.xlsx')
	
	def dealRules(self, rules, strDecode):
		returnRules = []
		for i in rules:
			temStr = ''
			for j in i[0]:  # 处理第一个frozenset
				temStr = temStr + strDecode[j] + ' & '
			temStr = temStr[:-1]
			temStr = temStr + ' ==> '
			for j in i[1]:
				temStr = temStr + strDecode[j] + ' & '
			temStr = temStr[:-1]
			temStr = temStr + ';' + '\t' + str(i[2]) + ';' + '\t' + str(i[3])
			returnRules.append(temStr)
		return returnRules
	
	def saveItemSets(self, data, strDecode, savepath):
		returnItemSets = []
		for key_,value_ in data.items():
			name_ = []
			for item in key_:
				name_.append(strDecode[item])
			names = " + ".join(name_)
			returnItemSets.append([names, value_])
		aim_datas = pd.DataFrame(returnItemSets, columns=('同时出现的关键字', '项集出现数目'))
		aim_datas.to_excel(savepath + "\\" + 'KeyWord.xlsx')
		
		
	
	
	def dealResult(self, rules, strDecode):
		returnRules = []
		for i in rules:
			temStr = ''
			for j in i[0]:  # 处理第一个frozenset
				temStr = temStr + strDecode[j] + ' & '
			temStr = temStr[:-1]
			temStr = temStr + ' ==> '
			for j in i[1]:
				temStr = temStr + strDecode[j] + ' & '
			temStr = temStr[:-1]
			temStr = temStr + ';' + '\t' + str(i[2]) + ';' + '\t' + str(i[3]) + ';' + '\t' + str(
				i[4]) + ';' + '\t' + str(
				i[5]) + ';' + '\t' + str(i[6]) + ';' + '\t' + str(i[7])
			returnRules.append(temStr)
		return returnRules
	
	def ResultDFToSave(self, rules, strDecode):  # 根据Qrange3关联分析生成的规则得到并返回对于的DataFrame数据结构的函数
		returnRules = []
		for i in rules:
			temList = []
			temStr = ''
			for j in i[0]:  # 处理第一个frozenset
				temStr = temStr + strDecode[j] + '&'
			temStr = temStr[:-1]
			temStr = temStr + ' ==> '
			for j in i[1]:
				temStr = temStr + strDecode[j] + '&'
			temStr = temStr[:-1]
			temList.append(temStr)
			temList.append(i[2])
			temList.append(i[3])
			temList.append(i[4])
			temList.append(i[5])
			temList.append(i[6])
			temList.append(i[7])
			returnRules.append(temList)
		return pd.DataFrame(returnRules, columns=('规则', '项集出现数目', '置信度', '覆盖度', '力度', '提升度', '利用度'))
	
	def doWordCloud(self, pd_data, savepath):
		# 数据清洗，去掉无效词
		STOP_WORDS_FILE_PATH = "tmall\\spiders\\DataAnalysize\\stop_words.txt"
		jieba.analyse.set_stop_words(STOP_WORDS_FILE_PATH)
		# 1、词数统计
		keywords_count_list = jieba.analyse.textrank(' '.join(pd_data.rateContent), topK=50, withWeight=True)
		# 生成词云
		word_cloud = (
			WordCloud()
				.add("", keywords_count_list, word_size_range=[20, 100], shape=SymbolType.DIAMOND)
				.set_global_opts(title_opts=opts.TitleOpts(title="词云图(Top50)"))
		)
		word_cloud.render(savepath+'/word-cloud.html')
	
	def everyWordCloud(self, segment, savepath):
		words_df = pd.DataFrame({'segment':segment})
		# 1、词数统计
		words_stat = words_df.groupby(by=['segment'])['segment'].agg({"计数":numpy.size})
		words_stat = words_stat.reset_index().sort_values(by=["计数"],ascending=False)
		with open(savepath+"/词频统计.txt",'w+',encoding='utf-8') as fw:
			fw.write(str(words_stat.head(1000).values))
		headitems = words_stat.head(20).values
		word_cloud = (
			WordCloud()
				.add("", headitems, word_size_range=[20, 100], shape=SymbolType.DIAMOND)
				.set_global_opts(title_opts=opts.TitleOpts(title="词云图(Top50)"))
		)
		word_cloud.render(savepath+'/word-cloud.html')


	def url_encrypt(self, url):
		"""
	    使用sha1加密算法，返回str加密后的字符串
	    """
		sha = hashlib.sha1(url.encode('utf-8'))
		encrypts = sha.hexdigest()
		return encrypts
	
	def loadAllDatasFromDetials(self):
		# try:
		sqlhepler = MysqldbHelper()
		rtn = sqlhepler.selectAllDatasFromDetials('urldetials3')
		# except:
		# 	# 获取数据出现错误
		# 	rtn = []
		aim_datas = []
		for item in rtn:
			tem_ = []
			tem_.append(item['detial'])
			tem_.append(item['lable'])
			tem_.append(item['creattime'])
			aim_datas.append(tem_)
			
		return aim_datas
































