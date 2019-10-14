# from twisted.enterprise import adbapi
# from twisted.internet import reactor
#
#
#
# dbpool = adbapi.ConnectionPool(
#                     "pymysql",
#                     db='taobao',
#                     port=3306,
#                     user='root',
#                     passwd='root',
#                     host='localhost',
#                     cp_reconnect=True
#                 )
#
# # equivalent of cursor.execute(statement), return cursor.fetchall():
# # def getAge(user):
# #     print("user input is :  "+user)
# #     return dbpool.cursor.execute("insert into urldetials3(hashurl,detial,creattime) values (123, 213, 321)")
#
#
# def _getAge(txn, user,qwe):
#     print(qwe)
#     # this will run in a thread, we can use blocking calls
#     txn.execute("SELECT * FROM urldetials3 WHERE hashurl='5126e12f2f87d821b982eb78348a3ac23393118b'")
#     # ... other cursor commands called on txn ...
#     # txn.execute("SELECT age FROM users WHERE name = ?", user)
#     # result = txn.fetchall()
#     # if result:
#     #     return result[0][0]
#     # else:
#     #     return None
#     result = txn.fetchall()
#     print(result)
#     return result
#
#
#
# def getAge(user):
#     return dbpool.runInteraction(_getAge, user,"qwe")
#
# def printResult(l):
#     print(l)
#     if l:
#         print(l[0][0], "years old")
#         reactor.callLater(1, finish)
#     else:
#         print(l)
#         print("No such user")
#         reactor.callLater(1, finish)
#
# def finish():
#     dbpool.close()
#     reactor.stop()
#
# getAge("joe").addCallback(printResult)
#
# reactor.run()
# print("结束")