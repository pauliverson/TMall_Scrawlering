# 用twisted库将数据进行异步插入到数据库
import threading
import time
from multiprocessing.context import Process

import pymysql
import pymysql.cursors

from twisted.enterprise import adbapi
from twisted.internet import reactor, defer

from TaobaoSimple.tmall import settings


class TwistedAdbapiSQLHelper(object):
	def __init__(self, dbpool):
		self.dbpool = dbpool
	
	@classmethod
	def from_settings(cls):
		# 需要在setting中设置数据库配置参数
		dbparms = dict(
			host=settings.MYSQL_HOST,
			db=settings.MYSQL_DBNAME,
			user=settings.MYSQL_USER,
			passwd=settings.MYSQL_PASSWORD,
			charset=settings.MYSQL_ENCODING,
			cursorclass=pymysql.cursors.DictCursor,
			use_unicode=True,
		)
		# 连接ConnectionPool（使用MySQLdb连接，或者pymysql）
		dbpool = adbapi.ConnectionPool("pymysql", **dbparms)  # **让参数变成可变化参数
		return cls(dbpool)  # 返回实例化对象
	
	def process_item(self, item, spider):
		# 使用twisted将MySQL插入变成异步执行
		query = self.dbpool.runInteraction(self.do_insert, item)
		# 添加异常处理
		query.addCallback(self.handle_error)
	
	def handle_error(self, failure):
		# 处理异步插入时的异常
		print(failure)
	
	def do_insert(self, cursor, item):
		# 执行具体的插入
		insert_sql = """
                    insert into jobbole_artitle(name, base_url, date, comment)
                    VALUES (%s, %s, %s, %s)
                """
		cursor.execute(insert_sql, (item['name'], item['base_url'], item['date'], item['coment'],))

	def do_select(self, tablename, is_and=True , cond_dict=[], order='', fields='*'):
		defer = self.dbpool.runInteraction(self.selectDataByPool, tablename, is_and=is_and , cond_dict=cond_dict, order=order, fields=fields)
		defer.addErrback(self.handle_error, "TwistedAdbapiSQLHelper：----->  self.dbpool.runInteraction.do_select出错了！")
		return defer
	
	def do_delete(self, tablename, cond_dict):
		defer = self.dbpool.runInteraction(self.deleteDataByPool, tablename=tablename, cond_dict=cond_dict)
		defer.addErrback(self.handle_error, "TwistedAdbapiSQLHelper：----->  self.dbpool.runInteraction.do_delete出错了！")
		return defer
	
	def selectDataByPool(self, cursor,  tablename, is_and = True,cond_dict=[], order='', fields='*'):
		"""查询数据
			# 				args：
			# 					tablename  ：表名字
			#                   is_and      :是否为and的关系
			# 					cond_dict  ：查询条件
			# 					order      ：排序条件
			#
			# 				example：
			# 					print mydb.select(table)
			# 					print mydb.select(table, fields=["name"])
			# 					print mydb.select(table, fields=["name", "age"])
			# 					print mydb.select(table, fields=["age", "name"])
			# 					print mydb.select(table, cond_dict=['url1','url2','url3'], fields=["name"])
			# 			"""
		consql = ' '
		#print(cond_dict)
		if is_and:  #是否为“且”的关系
			if cond_dict != []:
				for item_ in cond_dict:
					consql = consql + "hashurl" + '=' + "'" + item_ + "' and "
				consql = consql[:-5]
			else:
				consql = consql + '1=1'
		else:
			if cond_dict != []:
				for item_ in cond_dict:
					consql = consql + "hashurl" + '=' + "'" + item_ + "' or "
				consql = consql[:-4]
			else:
				consql = consql + '1=1'
			
		if fields == "*":
			sql = 'select * from %s where ' % tablename
		else:
			if isinstance(fields, list):
				fields = ",".join(fields)
				sql = 'select %s from %s where ' % (fields, tablename)
			else:
				print("fields input error, please input list fields.")
		sql = sql + consql + order
		print("本次执行查询的sql为： "+sql)
		cursor.execute(sql)
		result = cursor.fetchall()
		return result
	
	
	def deleteDataByPool(self, cursor, tablename, cond_dict):
		"""删除数据
			args：
				tablename  ：表名字
				cond_dict  ：删除条件字典

			example：
				params = {"name" : "caixinglong", "age" : "38"}
				mydb.delete(table, params)
		"""
		consql = ' '
		if cond_dict != '':
			for k, v in cond_dict.items():
				if isinstance(v, str):
					v = "\'" + v + "\'"
				consql = consql + tablename + "." + k + '=' + v + ' and '
		consql = consql + ' 1=1 '
		sql = "DELETE FROM %s where%s" % (tablename, consql)
		print("本次执行删除的命令为： "+sql)
		cursor.execute(sql)
		

def printResult(data,qwe):
	print(qwe)
	print(data)

def printResult1(data):
	print(data)
	reactor.callLater(3, stophelper)

def stophelper():
	# sqlhelper.dbpool.close()
	reactor.stop()

def starthelper():

	t1 = threading.Thread(target=reactor.run(installSignalHandlers = 0))
	t1.start()
	print("reactor.run()启动完毕")
	

# 所有deferred完成之后，触发回调提醒我们
def all_jobs_done(result):
    print(str(result))
    # ll = []
    # for i in result:
	#     print(type(i))
	#     ll.append(i)
    print('all jobs are done!')
    time.sleep(3)
    reactor.stop()
    # reactor.callLater(3, reactor.stop())




# if __name__=="__main__":
# 	sqlhelper = TwistedAdbapiSQLHelper.from_settings()
# 	# urls = ['b9c58ec3c6bb3187dacbc20f561a3036e9eec74b']
# 	urls = ['5126e12f2f87d821b982eb78348a3ac23393118bq', '91c19ac868f8368860fe2aa8129e2b986622d988',
# 	        '0cb328c7611f42471766bedc12ebf59f8856ed30', '5126e12f2f87d821b982eb78348a3ac23393118b',
# 	        '91c19ac868f8368860fe2aa8129e2b986622d988',
# 	        '0cb328c7611f42471766bedc12ebf59f8856ed30', 'b9c58ec3c6bb3187dacbc20f561a3036e9eec74b',
# 	        '89a94366284682bad0a04cf856533999ee0a2f3c',
# 	        '5126e12f2f87d821b982eb78348a3ac23393118b', '91c19ac868f8368860fe2aa8129e2b986622d988',
# 	        '0cb328c7611f42471766bedc12ebf59f8856ed30',
# 	        '5126e12f2f87d821b982eb78348a3ac23393118b', '91c19ac868f8368860fe2aa8129e2b986622d988',
# 	        '0cb328c7611f42471766bedc12ebf59f8856ed30',
# 	        '5126e12f2f87d821b982eb78348a3ac23393118b', '91c19ac868f8368860fe2aa8129e2b986622d988',
# 	        '0cb328c7611f42471766bedc12ebf59f8856ed30',
# 	        '5126e12f2f87d821b982eb78348a3ac23393118b', '91c19ac868f8368860fe2aa8129e2b986622d988',
# 	        '0cb328c7611f42471766bedc12ebf59f8856ed30',
# 	        '5126e12f2f87d821b982eb78348a3ac23393118b', '91c19ac868f8368860fe2aa8129e2b986622d988',
# 	        '0cb328c7611f42471766bedc12ebf59f8856ed30',
# 	        ]
# 	index = 0
# 	job_list = []
# 	for item_ in urls:
# 		# sqlhelper.do_select('urldetials3',is_and=True,cond_dict = [item_])
# 		job = sqlhelper.do_select('urldetials3', is_and=True, cond_dict=[item_]).addCallback(printResult, ("qwe",))
# 		print("result is :")
# 		print(job)
# 		index += 1
# 		print("第 %s 次运行完毕" % (index + 1))
# 		job_list.append(job)
# 	deferred_list = defer.DeferredList(job_list)
# 	# for item in deferred_list:
# 	# 	print(type(item))
# 	deferred_list.addCallback(all_jobs_done)
# 	# threading.Thread(target=lambda :threading.Thread(target=reactor.run(installSignalHandlers = 0)).start()).start()
# 	# threading.Thread(target=starthelper).start()
# 	reactor.run()
# 	# for item in deferred_list:
# 	# 	print(type(item))
# 	# print(deferred_list)
# 	# time.sleep(3)
# 	# deferred.addBoth(lambda _: reactor.stop())
# 	# reactor.stop()
# 	time.sleep(2)
# 	print("reactor.run()执行完毕主线程")
#
# 	# p = Process(target=)






























