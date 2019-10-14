# -*- coding: utf-8 -*-
"""
Created on 2019.9.19
Description:tkinter界面切换
Version:

@author: ShenGJ
"""
import ctypes
import inspect
import multiprocessing
import random
import string
import threading
import time
import tkinter
from tkinter import *
import tkinter.messagebox
import tkinter as tk
from multiprocessing.context import Process
from tkinter.filedialog import askdirectory
from tkinter.ttk import Treeview

import pyperclip

from TaobaoSimple.tmall.spiders.TransactionMain import TransactionMain
from TaobaoSimple.tmall.spiders.Utils.ListQueue import ListQueue
from TaobaoSimple.tmall.spiders.Utils.MyThread import MyThread
from TaobaoSimple.tmall.spiders.Utils.switch import switch

downloadqueue = multiprocessing.Queue()

threadingqueue = ListQueue()

class basedesk():
	def __init__(self, master):
		self.root = master
		self.root.config()
		self.root.title('TBProjectStart')
		self.root.geometry('1200x600+100+100')
		self.root.resizable(False,False)
		self.transaction = TransactionMain()
		
		# CheckDownload(self.root)
		initface(self.root,self.transaction,[[],[]])


class initface():
	def __init__(self, master,transaction, args):
		self.transaction = transaction
		self.master = master
		self.isOkToNextUI = True    #判断是否可以进入URL分析程序
		self.isOkToSelectSurface = True #判断是否可以进入选择界面
		self.classify_result = None #用于储存元组数据
		self.frame2 = Frame(self.master, height=200)
		# self.frame2.pack()
		self.frame2.grid(row=0, column=0)
		selectbtn = Button(self.frame2, text="选择数据", command=self.selectDatasSurface)
		label = Label(self.frame2, text="URL:  ")
		self.name = StringVar()
		self.entryName = Entry(self.frame2, textvariable=self.name, width=80)
		
		label2 = Label(self.frame2, text="标签:  ")
		self.lable2 = StringVar()
		self.entryName2 = Entry(self.frame2, textvariable=self.lable2, width=30)
		
		btGetName = Button(self.frame2, text="添加URL", command=self.processAddURL)
		startDlButton = Button(self.frame2, text="开始下载", command=self.processDownload)
		selectbtn.grid(row=1,column = 0)
		label.grid(row=1, column=1)
		self.entryName.grid(row=1, column=2)
		label2.grid(row=1, column=3)
		self.entryName2.grid(row=1, column=4)
		btGetName.grid(row=1, column=5)
		startDlButton.grid(row=1, column=6)
		self.tree_date = Treeview(self.master, columns=['URL','LABLE2'], show='headings', height=30)
		# self.tree_date.pack()
		self.tree_date.grid(row=2)
		# 设置列宽度
		self.tree_date.column('URL', width=758, anchor='center')
		self.tree_date.column('LABLE2', width=442, anchor='center')
		# 添加列名
		self.tree_date.heading('URL', text='URL')
		self.tree_date.heading('LABLE2', text='标签')
		# 绑定事件
		self.tree_date.bind('<Double-3>', self.deleteItem)
		# 当从数据分析页面返回时调用
		if self.transaction.urllists != []:
			for index in range(len(args[0])):
				self.tree_date.insert('', 1, values=(args[0][index], args[1][index]))
			
			# for key,value in self.receptdata[0].items():
			# 	self.tree_date.insert('', 1, values=(key,value['lable_']))
			# for key,value in self.receptdata[1].items():
			# 	self.tree_date.insert('', 1, values=(key, value['lable_']))
			
			# for item in self.transaction.urllists:
			# 	self.tree_date.insert('', 1, values=item)
	
	def selectDatasSurface(self):
		# print('点击了选择按钮')
		
		# 获取合适的URL
		if self.isOkToSelectSurface:
			self.isOkToSelectSurface = False
			t_classify = threading.Thread(target=self.loadAllDatas)
			t_classify.start()
		else:
			tkinter.messagebox.showinfo('TBProject Info', '请等待数据库数据提取完毕！')
	
	def loadAllDatas(self):
		# t_judge = MyThread(func=self.transaction.loadAllDatasFromDetials, args=("loadAllDatasFromDetials",))
		# t_judge.start()
		# t_judge.join()
		# # threadingqueue.put(1)
		# result_datas = t_judge.get_result()
		try:
			result_datas = self.transaction.loadAllDatasFromDetials()
		except:
			self.isOkToSelectSurface = True
			tkinter.messagebox.showerror('TBProject Error', 'initface ---> loadAllDatas: 数据库链接出现错误，请重试！')
			return
		self.frame2.destroy()
		self.tree_date.destroy()
		SelectionSurface(self.master, self.transaction, result_datas)
	
	
	def deleteItem(self, event):  # 右键双击删除
		for item in self.tree_date.selection():
			self.tree_date.delete(item)
			# item_text = self.tree_date.item(item, "values")
			# print(item_text[0])  # 输出所选行的第一列的值
	
	def processAddURL(self):
		url_ = self.name.get().strip()
		if url_==None or url_.strip()=="":
			self.entryName.delete(0, END)
			self.entryName2.delete(0, END)
			return
		if url_[0:4] != 'http':
			self.entryName.delete(0, END)
			self.entryName2.delete(0, END)
			tkinter.messagebox.showinfo('TBProject Info', "非正确网址格式: \r\n" + url_)
			return
		if ('tmall' not in url_) and ('taobao' not in url_):
			self.entryName.delete(0, END)
			self.entryName2.delete(0, END)
			tkinter.messagebox.showinfo('TBProject Info', "此URL不属于目标网站: \r\n" + url_)
			return
		lable_ = self.lable2.get()
		if lable_==None or lable_.strip()=="":
			lable_ = "-Default Lable-"
		self.tree_date.insert('', 1, values=(url_,lable_))
		self.entryName.delete(0,END)
		self.entryName2.delete(0, END)
		
	
	def processDownload(self):
		if len(self.tree_date.get_children())==0:
			return None
		# 获取合适的URL
		if self.isOkToNextUI:
			self.isOkToNextUI = False
			kids = self.tree_date.get_children()
			urllists = []
			lablelist = []
			for item in kids:
				# 对输入的值进行去重
				url_ = self.tree_date.item(item, "values")[0]
				lable_ = self.tree_date.item(item, "values")[1]
				if url_ not in urllists:
					urllists.append(url_)
					lablelist.append(lable_)
			# 如果可用网址为0，则清空treeview
			if len(urllists)==0:
				self.entryName.delete(0, END)
				for item in kids:
					self.tree_date.delete(item)
				return
			self.transaction.urllists = urllists
			t_classify = threading.Thread(target=self.classifyURL, args=(urllists,lablelist))
			t_classify.start()
		else:
			tkinter.messagebox.showinfo('TBProject Info', '请等待URL分析完毕')
		
		
		
	
	def classifyURL(self, urllists, lablelist):
		try:
			self.classify_result = self.transaction.classifyURLNewOrOld(urllists, lablelist)
		except:
			self.isOkToNextUI = True
			tkinter.messagebox.showerror('TBProject Error', 'initface ---> classifyURL: 数据库链接出现错误，请重试！')
			return
		
		self.judgeNextUI(urllists, lablelist)
	
	
	def judgeNextUI(self, oriurl, orilable):
		if len(self.classify_result[0]) != 0:
			newurllists = list(self.classify_result[0].keys())
		else:
			newurllists = []
		oldurllists = self.classify_result[1]
		if len(oldurllists) == 0: #说明没有旧数据
			# p = Process(target=self.transaction.downloadDatas, args=(downloadqueue, oriurl, orilable, newurllists))
			# p.start()
			p = threading.Thread(target=self.transaction.downloadDatas, args=(downloadqueue, oriurl, orilable, newurllists))
			p.start()
			self.workSurfaceUI([oriurl, orilable])
		else:   #说明存在一些URL在数据库中有存
			# 将两个列表都传给下一个界面，在下一个界面将数据分类展示
			self.checkDownloadUI(self.classify_result, oriurl, orilable)

	def workSurfaceUI(self, args):
		self.frame2.destroy()
		self.tree_date.destroy()
		WorkSurface(self.master, self.transaction, self.classify_result, args)
	
	def checkDownloadUI(self, args, oriurl, orilable):
		self.frame2.destroy()
		self.tree_date.destroy()
		CheckDownload(self.master, self.transaction, args, [oriurl, orilable])


class SelectionSurface():
	def __init__(self, master, transaction, result_data):
		self.transaction = transaction
		self.master = master
		self.result_data = result_data
		self.selecturl = []
		self.selectlable = []
		self.selecttime = []
		self.frame2 = Frame(self.master, width=10, height=2)
		# self.frame2.pack()
		self.frame2.grid(row=0, column=0)
		label = Label(self.frame2, text="数据库中已经存在的数据", width=30, height=3)
		label.grid(row=1, column=1)
		self.tree_date = Treeview(self.master, columns=['URL', 'Lable', 'Time'], show='headings', height=23)
		# self.tree_date.pack()
		self.tree_date.grid(row=2,column=0)
		# 设置列宽度
		self.tree_date.column('URL', width=450, anchor='center')
		self.tree_date.column('Lable', width=500, anchor='center')
		self.tree_date.column('Time', width=250, anchor='center')
		# 添加列名
		self.tree_date.heading('URL', text='URL')
		self.tree_date.heading('Lable', text='标签')
		self.tree_date.heading('Time', text='上次下载时间')
		
		# 绑定事件
		# 绑定左键单击 选中
		self.tree_date.bind('<Double-Button-1>', self.selectone)
		# 绑定右键单击 取消选中
		self.tree_date.bind('<Double-3>', self.refuseone)
		# 绑定键盘 Enter事件，展示URL
		self.tree_date.bind('<Return>', self.infoURL)
		self.frame3 = Frame(self.master)
		btn_yes = tk.Button(self.frame3, text='使用已经挑选的数据', command=self.useSelectedData)
		# btn_no = tk.Button(self.frame3, text='使用数据库数据', command=self.usingOldData)
		self.frame3.grid(row=3)
		# btn_no.grid(row=3, column=1)
		btn_yes.grid(row=3, column=2)
	
		self.vsb = tk.ttk.Scrollbar(self.master, orient="vertical", command=self.tree_date.yview)
		# vsb.place(x=30 + 1100, y=95, height=300 + 20)
		self.tree_date.configure(yscrollcommand=self.vsb.set)
		# vsb.grid(row=2, columns = 1,sticky=NS)
		self.vsb.place(x=1182, y=60, height=480 + 20)
		# vsb.place(x=50 + 200, y=95, height=200 + 20)
		
		# 将存在于数据库中的URL数据展示出来
		# for key, value in self.tuple_result[1].items():
		# 	self.tree_date.insert('', 1, values=(key, self.orilable[self.oriurl.index(key)], value['creattime_']))
		for item in self.result_data:
			self.tree_date.insert('', 1, values=(item[0], item[1], item[2]), tags=self.getrandomtgs())
	
	
	def deleteItem(self, event):  # 右键双击删除
		for item in self.tree_date.selection():
			self.tree_date.delete(item)
			
	def selectone(self, event):
		for item in self.tree_date.selection():
			# self.tree_date.columnconfigure (0,weight=1,background='yellow', foreground="red")
			# self.tree_date.configure ( background = 'yellow',foreground="red")
			# tages = self.tree_date.item(item, "values")[0]
			tages = self.tree_date.item(item, "tags")[0]
			url_ = self.tree_date.item(item, "values")[0].strip()
			lable_ = self.tree_date.item(item, "values")[1]
			time_ = self.tree_date.item(item, "values")[2]
			if url_ not in self.selecturl:
				self.selecturl.append(url_)
				self.selectlable.append(lable_)
				self.selecttime.append(time_)
			self.tree_date.tag_configure (tages, background = 'yellow',foreground="red")
			
	def refuseone(self, event):
		for item in self.tree_date.selection():
			tages = self.tree_date.item(item, "tags")[0]
			try:
				self.selecturl.remove(self.tree_date.item(item, "values")[0].strip())
				self.selectlable.remove(self.tree_date.item(item, "values")[1])
				self.selecttime.remove(self.tree_date.item(item, "values")[2])
			except:
				pass
			self.tree_date.tag_configure(tages, background='white', foreground="black")
	
	def infoURL(self, event):
		for item in self.tree_date.selection():
			url_ = self.tree_date.item(item, "values")[0].strip()
			lable_ = self.tree_date.item(item, "values")[1]
			pyperclip.copy(url_)
			tkinter.messagebox.showinfo('TBProject Info', '选中的url为：\r\n%s'%url_+"\r\n选中的标签为：\r\n%s"%lable_)
			
	def getrandomtgs(self):
		return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(6))
	
	
	
	
	def useSelectedData(self):
		self.frame2.destroy()
		self.frame3.destroy()
		self.tree_date.destroy()
		self.vsb.destroy()
		self.transaction.urllists = 1
		initface(self.master, self.transaction, [self.selecturl,self.selectlable, self.selecttime])


class handleDatasSurface():
	def __init__(self, master, transaction, tuple_result, args):
		self.transaction = transaction
		self.master = master
		self.args = args
		self.tuple_result = tuple_result
		self.deleteurls = []
		self.frame2 = Frame(self.master, width=10, height=2)
		# self.frame2.pack()
		self.frame2.grid(row=0, column=0)
		label = Label(self.frame2, text="本次运行时候使用的数据", width=30, height=3)
		label.grid(row=1, column=1)
		self.tree_date = Treeview(self.master, columns=['URL', 'Lable', 'Time'], show='headings', height=23)
		# self.tree_date.pack()
		self.tree_date.grid(row=2, column=0)
		# 设置列宽度
		self.tree_date.column('URL', width=450, anchor='center')
		self.tree_date.column('Lable', width=500, anchor='center')
		self.tree_date.column('Time', width=250, anchor='center')
		# 添加列名
		self.tree_date.heading('URL', text='URL')
		self.tree_date.heading('Lable', text='标签')
		self.tree_date.heading('Time', text='上次下载时间')
		
		# 绑定事件
		# 绑定左键单击 选中
		self.tree_date.bind('<Double-Button-1>', self.selectone)
		# 绑定右键单击 取消选中
		self.tree_date.bind('<Double-3>', self.refuseone)
		# 绑定键盘 Enter事件，展示URL
		self.tree_date.bind('<Return>', self.infoURL)
		self.frame3 = Frame(self.master)
		btn_yes = tk.Button(self.frame3, text='删除已经选择的数据', command=self.useSelectedData)
		# btn_no = tk.Button(self.frame3, text='使用数据库数据', command=self.usingOldData)
		self.frame3.grid(row=3)
		# btn_no.grid(row=3, column=1)
		btn_yes.grid(row=3, column=2)
		
		self.vsb = tk.ttk.Scrollbar(self.master, orient="vertical", command=self.tree_date.yview)
		# vsb.place(x=30 + 1100, y=95, height=300 + 20)
		self.tree_date.configure(yscrollcommand=self.vsb.set)
		# vsb.grid(row=2, columns = 1,sticky=NS)
		self.vsb.place(x=1182, y=60, height=480 + 20)
		# vsb.place(x=50 + 200, y=95, height=200 + 20)
		
		# 将存在于数据库中的URL数据展示出来
		# for key, value in self.tuple_result[1].items():
		# 	self.tree_date.insert('', 1, values=(key, self.orilable[self.oriurl.index(key)], value['creattime_']))
		tuple_ = self.tuple_result[0].copy()
		tuple_.update(self.tuple_result[1])
		for key,value in tuple_.items():
			self.tree_date.insert('', 1, values=(key, value['lable_'], value['creattime_']), tags=self.getrandomtgs())
				
		
		
	
	def deleteItem(self, event):  # 右键双击删除
		for item in self.tree_date.selection():
			self.tree_date.delete(item)
	
	def selectone(self, event):
		for item in self.tree_date.selection():
			# self.tree_date.columnconfigure (0,weight=1,background='yellow', foreground="red")
			# self.tree_date.configure ( background = 'yellow',foreground="red")
			# tages = self.tree_date.item(item, "values")[0]
			tages = self.tree_date.item(item, "tags")[0]
			url_ = self.tree_date.item(item, "values")[0].strip()
			if url_ not in self.deleteurls:
				self.deleteurls.append(url_)
			self.tree_date.tag_configure(tages, background='yellow', foreground="red")
	
	def refuseone(self, event):
		for item in self.tree_date.selection():
			tages = self.tree_date.item(item, "tags")[0]
			try:
				self.deleteurls.remove(self.tree_date.item(item, "values")[0].strip())
			except:
				pass
			self.tree_date.tag_configure(tages, background='white', foreground="black")
	
	def infoURL(self, event):
		for item in self.tree_date.selection():
			url_ = self.tree_date.item(item, "values")[0].strip()
			lable_ = self.tree_date.item(item, "values")[1]
			pyperclip.copy(url_)
			tkinter.messagebox.showinfo('TBProject Info', '选中的url为：\r\n%s' % url_ + "\r\n选中的标签为：\r\n%s" % lable_)
	
	def getrandomtgs(self):
		return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(6))
	
	def useSelectedData(self):
		try:
			if len(self.deleteurls) != 0:
				t_classify = threading.Thread(target=self.transaction.deleteOldDatas, args=(self.deleteurls,))
				t_classify.start()
		except:
			tkinter.messagebox.showerror('TBProject Error', 'tryAnalysize: 数据库链接出现错误，请重试！')
			return
		tuple_ = self.tuple_result[0].copy()
		tuple_.update(self.tuple_result[1])
		for item in self.deleteurls:
			tuple_[item]['creattime_'] = "- Deleted -"
		self.frame2.destroy()
		self.frame3.destroy()
		self.tree_date.destroy()
		self.vsb.destroy()
		# self.transaction.urllists = 1
		WorkSurface(self.master, self.transaction, self.tuple_result, self.args, ishandle = True)
	
	


isOkToAnalysize = False

class WorkSurface():
	def __init__(self,master, transaction, tuple_result, args, ishandle = False):
		global isOkToAnalysize
		isOkToAnalysize = False
		self.analysequeue = multiprocessing.Queue()
		self.transaction = transaction
		self.tuple_result = tuple_result
		self.args = args
		self.needids = []
		self.analyselist = []
		self.ishandle = ishandle    # 判断是否是从handle界面转过来的
		self.master = master
		self.isOKToNextAnalysize = True #判断正在执行的数据分析程序是否执行完毕
		# self.isOkToAnalysize = False    #判断是否可以进行数据分析
		'''窗体控件'''
		# 标题显示
		self.lab = tk.Label(self.master, text='请选择本次分析项目：')
		self.lab.grid(row=0, columnspan=3, sticky=tk.W)
		
		# 多选框
		self.frm = tk.Frame(self.master)
		self.frm.grid(row=1)
		self.var_ck1 = IntVar()
		ck1 = tk.Checkbutton(self.frm, padx = 10, text='口感关键词分析', onvalue=1,offvalue=0,variable = self.var_ck1 ,command=lambda :self.collectNeeds(needid='kougan',var_ck = 'var_ck1'))
		self.var_ck2 = IntVar()
		ck2 = tk.Checkbutton(self.frm, text='形态关键词分析', onvalue=1,offvalue=0, variable = self.var_ck2 , command=lambda :self.collectNeeds(needid='xingtai',var_ck = 'var_ck2'))
		self.var_ck3 = IntVar()
		ck3 = tk.Checkbutton(self.frm, text='服务关键词分析', onvalue=1,offvalue=0, variable = self.var_ck3 , command=lambda :self.collectNeeds(needid='fuwu',var_ck = 'var_ck3'))
		self.var_ck4 = IntVar()
		ck4 = tk.Checkbutton(self.frm, text='使用习惯关键词分析', onvalue=1,offvalue=0, variable = self.var_ck4 , command=lambda :self.collectNeeds(needid='shiyongxiguan',var_ck = 'var_ck4'))
		self.var_ck5 = IntVar()
		ck5 = tk.Checkbutton(self.frm, text='效果关键词分析', onvalue=1,offvalue=0, variable = self.var_ck5 , command=lambda :self.collectNeeds(needid='xiaoguo',var_ck = 'var_ck5'))
		self.var_ck6 = IntVar()
		ck6 = tk.Checkbutton(self.frm, text='决策传播关键词分析', onvalue=1,offvalue=0, variable = self.var_ck6 , command=lambda :self.collectNeeds(needid='juece_chuanbo',var_ck = 'var_ck6'))
		self.var_ck7 = IntVar()
		ck7 = tk.Checkbutton(self.frm, text='原料关键词分析', onvalue=1,offvalue=0, variable = self.var_ck7 , command=lambda :self.collectNeeds(needid='yuanliao',var_ck = 'var_ck7'))
		self.var_ck8 = IntVar()
		ck8 = tk.Checkbutton(self.frm, text='包装关键词分析', onvalue=1, offvalue=0, variable=self.var_ck8, command=lambda: self.collectNeeds(needid='baozhuang', var_ck='var_ck8'))
		self.var_ck9 = IntVar()
		ck9 = tk.Checkbutton(self.frm, text='重复购买关键词分析', onvalue=1, offvalue=0, variable=self.var_ck9, command=lambda: self.collectNeeds(needid='chongfugoumai', var_ck='var_ck9'))
		self.var_ck10 = IntVar()
		ck10 = tk.Checkbutton(self.frm, text='价格关键词分析', onvalue=1, offvalue=0, variable=self.var_ck10, command=lambda: self.collectNeeds(needid='jiage', var_ck='var_ck10'))
		self.var_ck11 = IntVar()
		ck11 = tk.Checkbutton(self.frm, text='口味关键词分析', onvalue=1, offvalue=0, variable=self.var_ck11, command=lambda: self.collectNeeds(needid='kouwei', var_ck='var_ck11'))

		ck1.grid(row=0, column=0)
		ck2.grid(row=0, column=1)
		ck3.grid(row=0, column=2)
		ck4.grid(row=0, column=3)
		ck5.grid(row=1)
		ck6.grid(row=1, column=1)
		ck7.grid(row=1, column=2)
		ck8.grid(row=1, column=3)
		ck9.grid(row=2)
		ck10.grid(row=2, column=1)
		ck11.grid(row=2, column=2)
		
		self.path = StringVar()
		Label(self.frm, text="结果储存路径:").grid(row=4, column=0)
		self.path.set(r'C:\Users\Administrator\Desktop')
		self.setsavepath = Entry(self.frm, textvariable=self.path, width=80)
		self.setsavepath.grid(row=4, column=1)
		Button(self.frm, text="路径选择", command=self.selectPath).grid(row=4, column=2)
		
		btn_modify = tk.Button(self.frm, text='返回修改URL', command=self.rtnModify)
		btn_analysize = tk.Button(self.frm, text='进行数据分析', command=self.tryAnalysize)
		btn_handle = tk.Button(self.frm, text='删除数据', command=self.datahandle)
		btn_modify.grid(row=5)
		btn_analysize.grid(row=5, column=1)
		btn_handle.grid(row=5, column=2)
		
		#启动探索线程，探索数据下载是否完全
		self.downloadIsOKThread = threading.Thread(target=self.remindok)
		self.downloadIsOKThread.setDaemon(True)
		self.downloadIsOKThread.start()
		#启动探索线程，探索数据分析是否完毕
		self.analysizeIsOKThread = threading.Thread(target=self.analyseIsOk)
		self.analysizeIsOKThread.setDaemon(True)
		self.analysizeIsOKThread.start()
	
	
	def selectPath(self):
		path_ = askdirectory()
		self.path.set(path_)
	
	def collectNeeds(self,needid,var_ck):
		for case in switch(var_ck):
			if case('var_ck1'):
				if self.var_ck1.get() == 1:
					self.needids.append(needid)
				else:
					self.needids.remove(needid)
				break
			if case('var_ck2'):
				if self.var_ck2.get() == 1:
					self.needids.append(needid)
				else:
					self.needids.remove(needid)
				break
			if case('var_ck3'):
				if self.var_ck3.get() == 1:
					self.needids.append(needid)
				else:
					self.needids.remove(needid)
				break
			if case('var_ck4'):
				if self.var_ck4.get() == 1:
					self.needids.append(needid)
				else:
					self.needids.remove(needid)
				break
			if case('var_ck5'):
				if self.var_ck5.get() == 1:
					self.needids.append(needid)
				else:
					self.needids.remove(needid)
				break
			if case('var_ck6'):
				if self.var_ck6.get() == 1:
					self.needids.append(needid)
				else:
					self.needids.remove(needid)
				break
			if case('var_ck7'):
				if self.var_ck7.get() == 1:
					self.needids.append(needid)
				else:
					self.needids.remove(needid)
				break
			if case('var_ck8'):
				if self.var_ck8.get() == 1:
					self.needids.append(needid)
				else:
					self.needids.remove(needid)
				break
			if case('var_ck9'):
				if self.var_ck9.get() == 1:
					self.needids.append(needid)
				else:
					self.needids.remove(needid)
				break
			if case('var_ck10'):
				if self.var_ck10.get() == 1:
					self.needids.append(needid)
				else:
					self.needids.remove(needid)
				break
			if case('var_ck11'):
				if self.var_ck11.get() == 1:
					self.needids.append(needid)
				else:
					self.needids.remove(needid)
				break
			if case():  # default, could also just omit condition or 'if True'
				tkinter.messagebox.showerror('TBProject Error', 'WorkSurface ---> collectNeeds: 出现错误')
	
	
	def datahandle(self):
		global isOkToAnalysize
		if self.ishandle:
			self.stop_thread(self.analysizeIsOKThread)
			# self.stop_thread(self.downloadIsOKThread)
			# downloadqueue.put("fill_queue.get()_leave")
			# downloadqueue.put("fill_queue.get()_leave")
			# downloadqueue.put("fill_queue.get()_leave")
			self.lab.destroy()
			self.frm.destroy()
			handleDatasSurface(self.master, self.transaction, self.tuple_result, self.args)
		else:
			if isOkToAnalysize:
				if self.isOKToNextAnalysize:
					self.stop_thread(self.analysizeIsOKThread)
					# self.stop_thread(self.downloadIsOKThread)
					# downloadqueue.put("fill_queue.get()_leave")
					# downloadqueue.put("fill_queue.get()_leave")
					# downloadqueue.put("fill_queue.get()_leave")
					self.lab.destroy()
					self.frm.destroy()
					handleDatasSurface(self.master, self.transaction, self.tuple_result, self.args)
				else:
					tkinter.messagebox.showwarning('TBProject Warning', '请等待本次数据分析程序执行完毕')
			else:
				tkinter.messagebox.showwarning('TBProject Warning', '请等待数据下载完毕')
		
	
	def tryAnalysize(self):
		global isOkToAnalysize
		# print("tryAnalysize 一开始isOkToAnalysize的值： ")
		# print(isOkToAnalysize)
		# print(type(isOkToAnalysize))
		
		if self.ishandle:
			tkinter.messagebox.showinfo('TBProject Info', '由于您刚才点击了"删除数据"按钮，为保证数据分析有效性，请点击"返回修改URL"按钮')
		else:
			if isOkToAnalysize:    #   判断数据下载完毕没有
				# print("点击数据分析按钮时候 self.isOKToNextAnalysize:    %s"% str(self.isOKToNextAnalysize))
				if self.isOKToNextAnalysize:
					self.isOKToNextAnalysize = False  # 当进入数据分析执行程序之后就不让程序再次进入，等待第一次数据分析执行完毕
					needids = list(set(self.needids))
					if len(needids)==0:
						tkinter.messagebox.showinfo('TBProject Info', '请选择需要分析的项目')
						self.isOKToNextAnalysize = True
						return
					try:
						self.analysize(needids)
					except:
						tkinter.messagebox.showerror('TBProject Error', 'tryAnalysize: 数据库链接出现错误，请重试！')
				else:
					tkinter.messagebox.showinfo('TBProject Info', '请等待本次数据分析程序执行完毕')
			else:
				tkinter.messagebox.showinfo('TBProject Info', '请等待数据下载完毕后再进入数据分析功能')
		
	
	def analysize(self, category):
		savepath = self.setsavepath.get()
		savepath = savepath.rstrip("\\").rstrip("/").rstrip("\\")
		p = threading.Thread(target=self.transaction.analysizeDatas,  args=(self.analysequeue, self.transaction.urllists, category, 0.02, 0.01, savepath))
		p.start()
		
	def remindok(self):
		global isOkToAnalysize
		while True:
			# print("进来了remindok方法，此时 isOkToAnalysize 为：  ")
			# print(isOkToAnalysize)
			queueget = downloadqueue.get()
			# print("downloadqueue获取的值为：  %s"%queueget)
			if queueget=='downloadDatas_method_is_over' or queueget=='no_download_urls':
				isOkToAnalysize = True  #疑问：为什么不把isOkToAnalysize设置为全局变量时候，这里写self.isOkToAnalysize=True不能够改变对象的isOkToAnalysize值（猜想是变量的作用域问题）
				tkinter.messagebox.showinfo('TBProject Info', '目标数据准备完毕，可开始执行数据分析！')
				break
			
				
		#
		# while True:
		# 	if downloadqueue.empty():
		
		
		
	
	def analyseIsOk(self):
		while True:
			rtn = self.analysequeue.get()
			# print("self.analysequeue.get() 的类型是: ")
			# print(type(rtn))
			if isinstance(rtn,str):
				tkinter.messagebox.showwarning('TBProject Warning', 'WorkSurface ---> analysize: \r\n代码为[ %s ]的分析项目因为数据量不够未能成功出结果'%rtn)
			elif rtn == 1:
				self.isOKToNextAnalysize = True
				tkinter.messagebox.showinfo('TBProject Info', '本次数据分析完毕，结果已经保存在指定路径！')
			else:
				self.isOKToNextAnalysize = True
				tkinter.messagebox.showwarning('TBProject Warning', 'WorkSurface ---> analysize:  数据库未取到数据  \r\n可能是由于输入的网址评论数据量为0，请清查')
				

	def rtnModify(self):
		global isOkToAnalysize
		if self.ishandle:
			self.stop_thread(self.analysizeIsOKThread)
			# self.stop_thread(self.downloadIsOKThread)
			# downloadqueue.put("fill_queue.get()_leave")
			# downloadqueue.put("fill_queue.get()_leave")
			# downloadqueue.put("fill_queue.get()_leave")
			self.lab.destroy()
			self.frm.destroy()
			initface(self.master, self.transaction, self.args)
		else:
			if isOkToAnalysize:
				if self.isOKToNextAnalysize:
					self.stop_thread(self.analysizeIsOKThread)
					# self.stop_thread(self.downloadIsOKThread)
					# downloadqueue.put("fill_queue.get()_leave")
					# downloadqueue.put("fill_queue.get()_leave")
					# downloadqueue.put("fill_queue.get()_leave")
					self.lab.destroy()
					self.frm.destroy()
					initface(self.master, self.transaction, self.args)
				else:
					tkinter.messagebox.showwarning('TBProject Warning', '请等待本次数据分析程序执行完毕')
			else:
				tkinter.messagebox.showwarning('TBProject Warning', '请等待数据下载完毕后再返回修改')
		
	
	
	
	def stop_thread(self, thread):
		# print("thread.ident: ")
		# print(thread.ident)
		self._async_raise(thread.ident, SystemExit)
	
	def _async_raise(self, tid, exctype):
		"""raises the exception, performs cleanup if needed"""
		tid = ctypes.c_long(tid)
		if not inspect.isclass(exctype):
			exctype = type(exctype)
		res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
		if res == 0:
			raise ValueError("invalid thread id")
		elif res != 1:
			# """if it returns a number greater than one, you're in trouble,
			# and you should call it again with exc=NULL to revert the effect"""
			ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
			raise SystemError("PyThreadState_SetAsyncExc failed")
	
	



class CheckDownload():
	"""
	检测需要下载的URL是否存在于数据库，展示面板
	"""
	def __init__(self, master, transaction, tuple_result, ori_args ):
		self.master = master
		self.tuple_result = tuple_result    #已经分好类的URL元组
		self.oriurl = ori_args[0]
		self.orilable = ori_args[1]
		self.transaction = transaction
		self.frame2 = Frame(self.master,width=10, height=2)
		# self.frame2.pack()
		self.frame2.grid(row=0, column=0)
		label = Label(self.frame2, text="数据库中已经存在的数据",width = 30,height = 3)
		label.grid(row=1, column=1)
		self.tree_date = Treeview(self.master, columns=['URL', 'Lable', 'Time'], show='headings', height=23)
		# self.tree_date.pack()
		self.tree_date.grid(row=2)
		# 设置列宽度
		self.tree_date.column('URL', width=600, anchor='center')
		self.tree_date.column('Lable', width=350, anchor='center')
		self.tree_date.column('Time', width=250, anchor='center')
		# 添加列名
		self.tree_date.heading('URL', text='URL')
		self.tree_date.heading('Lable', text='标签')
		self.tree_date.heading('Time', text='上次下载时间')
		
		# 绑定事件
		self.tree_date.bind('<Double-3>', self.deleteItem)
		self.frame3 = Frame(self.master)
		btn_yes = tk.Button(self.frame3, text='所列URL重新下载', command=self.downloadNewData)
		btn_no = tk.Button(self.frame3, text='使用数据库数据', command=self.usingOldData)
		self.frame3.grid(row=3)
		btn_no.grid(row=3, column=1)
		btn_yes.grid(row=3, column=2)
		
		# 将存在于数据库中的URL数据展示出来
		for key, value in self.tuple_result[1].items():
			self.tree_date.insert('', 1, values=(key, self.orilable[self.oriurl.index(key)], value['creattime_']))
		
	
	def deleteItem(self, event):  # 右键双击删除
		for item in self.tree_date.selection():
			self.tree_date.delete(item)
	
	
	def downloadNewData(self):
		kids = self.tree_date.get_children()
		urllists = []
		lablelist = []
		for item in kids:
			# 对输入的值进行去重
			url_ = self.tree_date.item(item, "values")[0]
			lable_ = self.tree_date.item(item, "values")[1]
			if url_ not in urllists:
				urllists.append(url_)
				lablelist.append(lable_)
		url_download = urllists + list(self.tuple_result[0].keys())
		#   此时urllists意味着需要新下载的数据，数据库中的旧数据需要即刻清除
		# p = Process(target=self.transaction.downloadDatas, args=(downloadqueue, self.oriurl, self.orilable, url_download, urllists))
		# p.start()
		p = threading.Thread(target=self.transaction.downloadDatas, args=(downloadqueue, self.oriurl, self.orilable, url_download, urllists))
		p.start()
		self.workSurfaceUI([self.oriurl, self.orilable])
	
	def usingOldData(self):
		kids = self.tree_date.get_children()
		urllists = []
		for item in kids:
			# 对输入的值进行去重
			url_ = self.tree_date.item(item, "values")[0]
			if url_ not in urllists:
				urllists.append(url_)
		# print("self.transaction.urllists:")
		# print(self.transaction.urllists)
		# print("urllists:")
		# print(urllists)
		download_urls = list(set(self.transaction.urllists) - set(urllists))
		delete_urls = list(set(self.tuple_result[1].keys()) - set(urllists))
		# print("本次数据URL: ")
		# print(download_urls)
		# print(delete_urls)
		if len(download_urls) != 0:
			# p = Process(target=self.transaction.downloadDatas, args=(downloadqueue, self.oriurl, self.orilable, download_urls, delete_urls))
			# p.start()
			p = threading.Thread(target=self.transaction.downloadDatas, args=(downloadqueue, self.oriurl, self.orilable, download_urls, delete_urls))
			p.start()
		else:
			# print("usingOldData方法中 len(download_urls)!=0 所以执行 downloadqueue.put(1)")
			downloadqueue.put("no_download_urls")
		self.workSurfaceUI([self.oriurl, self.orilable])
		
	def workSurfaceUI(self, args):
		self.frame2.destroy()
		self.frame3.destroy()
		self.tree_date.destroy()
		WorkSurface(self.master, self.transaction, self.tuple_result, args)



# if __name__ == '__main__':
# 	root = tk.Tk()
# 	basedesk(root)
# 	root.mainloop()
