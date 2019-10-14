from queue import Queue

class ListQueue(Queue):

	def _init(self, maxsize):
		self.maxsize = maxsize
		self.queue = [] # 将数据存储方式改为list

	def _put(self, item):
		self.queue.append(item)

	def _get(self):
		return self.queue.pop()