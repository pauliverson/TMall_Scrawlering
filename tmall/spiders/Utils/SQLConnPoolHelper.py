# -*- coding: UTF-8 -*-
"""
Created on 2016年5月7日

@author: baocheng
1、执行带参数的ＳＱＬ时，请先用sql语句指定需要输入的条件列表，然后再用tuple/list进行条件批配
２、在格式ＳＱＬ中不需要使用引号指定数据类型，系统会根据输入参数自动识别
３、在输入的值中不需要使用转意函数，系统会自动处理
"""

import MySQLdb
from MySQLdb.cursors import DictCursor
from DBUtils.PooledDB import PooledDB

from TaobaoSimple.tmall import settings

"""
Config是一些数据库的配置文件
"""

class SQLConnPoolHelper(object):
    """
    MYSQL数据库对象，负责产生数据库连接 , 此类中的连接采用连接池实现获取连接对象：conn = Mysql.getConn()
            释放连接对象;conn.close()或del conn
    """
    #连接池对象
    __pool = None
    def __init__(self):
        #数据库构造函数，从连接池中取出连接，并生成操作游标
        self._conn = SQLConnPoolHelper.__getConn()
        self._cursor = self._conn.cursor()

    @staticmethod
    def __getConn():
        """
        @summary: 静态方法，从连接池中取出连接
        @return MySQLdb.connection
        """
        if SQLConnPoolHelper.__pool is None:
            __pool = PooledDB(creator=MySQLdb, mincached=1 , maxcached=20 ,
                              host=settings.MYSQL_HOST , port=settings.MYSQL_PORT , user=settings.MYSQL_USER , passwd=settings.MYSQL_PASSWORD ,
                              db=settings.MYSQL_DBNAME,use_unicode=False,charset=settings.MYSQL_ENCODING,cursorclass=DictCursor)
        return __pool.connection()

    def getAll(self,sql,param=None):
        """
        @summary: 执行查询，并取出所有结果集
        @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list(字典对象)/boolean 查询到的结果集
        """
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql,param)
        if count>0:
            result = self._cursor.fetchall()
        else:
            result = False
        return result

    def getOne(self,sql,param=None):
        """
        @summary: 执行查询，并取出第一条
        @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list/boolean 查询到的结果集
        """
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql,param)
        if count>0:
            result = self._cursor.fetchone()
        else:
            result = False
        return result

    def getMany(self,sql,num,param=None):
        """
        @summary: 执行查询，并取出num条结果
        @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param num:取得的结果条数
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list/boolean 查询到的结果集
        """
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql,param)
        if count>0:
            result = self._cursor.fetchmany(num)
        else:
            result = False
        return result

    def insertOne(self,sql,value):
        """
        @summary: 向数据表插入一条记录
        @param sql:要插入的ＳＱＬ格式
        @param value:要插入的记录数据tuple/list
        @return: insertId 受影响的行数
        """
        self._cursor.execute(sql,value)
        return self.__getInsertId()

    def insertMany(self,sql,values):
        """
        @summary: 向数据表插入多条记录
        @param sql:要插入的ＳＱＬ格式
        @param values:要插入的记录数据tuple(tuple)/list[list]
        @return: count 受影响的行数
        """
        count = self._cursor.executemany(sql,values)
        return count

    def __getInsertId(self):
        """
        获取当前连接最后一次插入操作生成的id,如果没有则为０
        """
        self._cursor.execute("SELECT @@IDENTITY AS id")
        result = self._cursor.fetchall()
        return result[0]['id']

    def __query(self,sql,param=None):
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql,param)
        return count

    def update(self,sql,param=None):
        """
        @summary: 更新数据表记录
        @param sql: ＳＱＬ格式及条件，使用(%s,%s)
        @param param: 要更新的  值 tuple/list
        @return: count 受影响的行数
        """
        return self.__query(sql,param)

    def delete(self,sql,param=None):
        """
        @summary: 删除数据表记录
        @param sql: ＳＱＬ格式及条件，使用(%s,%s)
        @param param: 要删除的条件 值 tuple/list
        @return: count 受影响的行数
        """
        return self.__query(sql,param)

    def begin_commit(self):
        """
        @summary: 开启事务
        """
        self._conn.autocommit(0)

    def end_commit(self,option='commit'):
        """
        @summary: 结束事务
        """
        if option=='commit':
            self._conn.commit()
        else:
            self._conn.rollback()
    
    def setautocommit(self):
        """
        @summary: 关闭事务，进行主动提交
        """
        self._conn.autocommit(1)

    def dispose(self,isEnd=1):
        """
        @summary: 释放连接池资源
        """
        if isEnd==1:
            self.end_commit('commit')
        else:
            self.end_commit('rollback');
        self._cursor.close()
        self._conn.close()

    
    def selectDataByPool(self,tablename, is_and=True, cond_dict=[], order='', fields='*'):
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
        print(cond_dict)
        if is_and:  # 是否为“且”的关系
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
        return self.getAll(sql)

    def deleteDataByPool(self, tablename, cond_dict):
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
        return self.delete(sql)

    def insertDataByPool(self, tablename, params):
        """插入数据
        args：
            tablename  ：表名字
            key        ：属性键
            value      ：属性值
        """
        key = []
        value = []
        for tmpkey, tmpvalue in params.items():
            key.append(tmpkey)
            if isinstance(tmpvalue, str):
                value.append("\'" + tmpvalue + "\'")
            else:
                value.append(tmpvalue)
        attrs_sql = '(' + ','.join(key) + ')'
        value_ = ['%s' for i in range(len(value))]
        values_sql = ' values(' + ','.join(value_) + ')'
        sql = 'insert into %s' % tablename
        sql = sql + attrs_sql + values_sql
        print('_insert:' + sql)
        return self.insertMany(sql,value)
        
        
        
        
# if __name__=="__main__":
#     helper = SQLConnPoolHelper()
#     result = helper.selectDataByPool("urldetials3")
#     if result:
#         print(result)
#
#
        
        
        
        
        
        
        