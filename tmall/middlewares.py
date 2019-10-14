# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import random
import logging
import re
import scrapy.downloadermiddlewares.redirect
from scrapy import signals
from scrapy.downloadermiddlewares.retry import RetryMiddleware, logger
from scrapy.http import HtmlResponse
from twisted.internet import defer
from twisted.internet.error import TimeoutError, DNSLookupError, \
        ConnectionRefusedError, ConnectionDone, ConnectError, \
        ConnectionLost, TCPTimedOutError
from twisted.web.client import ResponseFailed

from scrapy.exceptions import NotConfigured
from scrapy.utils.response import response_status_message
from scrapy.core.downloader.handlers.http11 import TunnelError
from scrapy.utils.python import global_object_name


class TmallSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class TmallDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

class UserAgentIpDownloaderMiddleware(object):
	
	USER_AGENTS = [
	"Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
	"Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
	"Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
	"Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
	"Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
	"Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
	"Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
	"Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5"
	]
	IPLISTS = ["60.13.42.71:9999",
	"180.104.62.166:9000",
	"123.206.30.254:8118",
	"183.129.207.86:14002",
	"60.205.229.126:80",
	"58.22.207.41:9000"]
	
	# @classmethod
	# def from_crawler(self):
	# 	pass
	
	def process_request(self,request,spider):
		# url_item = request.url
		# print("执行查询的URL是: " + url_item)
		# url_num = re.findall("currentPage=[0-9]*&",url_item)[0][12:-1]
		#
		# #print(url_num)
		# #print(request.headers['path'])
		# currentPage_num = re.findall("currentPage=[0-9]*&" , str(request.headers['path']))[0][12:-1]
		#
		# print("执行操作之前request的headers['path']: ------>"+str(currentPage_num))
		# request.headers['path'] = str(request.headers['path']).replace(re.findall("currentPage=[0-9]*&",str(request.headers['path']))[0],"currentPage="+str(url_num)+"&")
		# currentPage_num = re.findall("currentPage=[0-9]*&", str(request.headers['path']))[0][12:-1]
		# print("执行操作之后request的headers['path']: ------>" + str(currentPage_num))
		# request.headers['path'] = str(request.headers['path']).replace(re.findall("itemId=.*&",str(request.headers['path']))[0], re.findall("itemId=.*&",url_item)[0])
		# request.headers['path'] = str(request.headers['path']).replace(re.findall("spuId=.*&",str(request.headers['path']))[0], re.findall("spuId=.*&",url_item)[0])
		# request.headers['path'] = str(request.headers['path']).replace(re.findall("sellerId=.*&",str(request.headers['path']))[0], re.findall("sellerId=.*&",url_item)[0])
		#
		request.headers['path'] = request.url[22:]
		user_agent = random.choice(self.USER_AGENTS)
		request.headers['User-Agent'] = user_agent
		# ipproxy = random.choice(self.IPLISTS)
		# request.meta['proxy'] = "http://" + ipproxy
		
		return None
	
	def process_response(self, request, response, spider):
		# Called with the response returned from the downloader.
		
		# Must either;
		# - return a Response object
		# - return a Request object
		# - or raise IgnoreRequest
		# retries = request.meta.get('retry_times', 0) + 1
		if "retry_over_exception" in response.url:
			bad_ip = request.meta['proxy'][7:]
			self.IPLISTS.remove(bad_ip)
			ipproxy = random.choice(self.IPLISTS)
			request.meta['proxy'] = "http://" + ipproxy
			print("[ip为：%s 的代理执行访问httpbin.org/ip]: "
			      "返回非200状态页面 %s 次，出现访问error %s 次，将其视作无效ip，执行删除操作"
			      % (bad_ip, request.meta.get('response_retry', 0), request.meta.get('exception_retry', 0)))
			print("IPLISTS列表还存有 %s 条数据" % (len(self.IPLISTS)))
			return request
		
		return response


class TMallRetryMiddlewares(RetryMiddleware):
	# IOError is raised by the HttpCompression middleware when trying to
	# decompress an empty response
	EXCEPTIONS_TO_RETRY = (defer.TimeoutError, TimeoutError, DNSLookupError,
	                       ConnectionRefusedError, ConnectionDone, ConnectError,
	                       ConnectionLost, TCPTimedOutError, ResponseFailed,
	                       IOError, TunnelError)
	
	# def __init__(self, settings):
	#     if not settings.getbool('RETRY_ENABLED'):
	#         raise NotConfigured
	#     self.max_retry_times = settings.getint('RETRY_TIMES')
	#     self.retry_http_codes = set(int(x) for x in settings.getlist('RETRY_HTTP_CODES'))
	#     self.priority_adjust = settings.getint('RETRY_PRIORITY_ADJUST')
	
	@classmethod
	def from_crawler(cls, crawler):
		return cls(crawler.settings)
	
	def process_response(self, request, response, spider):
		if request.meta.get('dont_retry', False):
			return response
		if response.status in self.retry_http_codes:
			reason = response_status_message(response.status)
			res_retries = request.meta.get('response_retry', 0)
			res_retryreq = request.copy()
			res_retryreq.meta['response_retry'] = res_retries + 1
			return self._retry(res_retryreq, reason, spider) or response
		return response
	
	def process_exception(self, request, exception, spider):
		if isinstance(exception, self.EXCEPTIONS_TO_RETRY) and not request.meta.get('dont_retry', False):
			exc_retries = request.meta.get('exception_retry', 0)
			exc_retryreq = request.copy()
			exc_retryreq.meta['exception_retry'] = exc_retries + 1
			return self._retry(exc_retryreq, exception, spider)
	
	def _retry(self, request, reason, spider):
		response_retries = request.meta.get('response_retry', 0)
		exception_retries = request.meta.get('exception_retry', 0)
		print("response_retries is %s" % response_retries)
		print("exception_retries is %s" % exception_retries)
		retries = response_retries + exception_retries
		retry_times = self.max_retry_times
		
		if 'max_retry_times' in request.meta:
			retry_times = request.meta['max_retry_times']
		
		stats = spider.crawler.stats
		if retries <= retry_times:
			logger.debug("Retrying %(request)s (failed %(retries)d times): %(reason)s",
			             {'request': request, 'retries': retries, 'reason': reason},
			             extra={'spider': spider})
			retryreq = request.copy()
			retryreq.meta['retry_times'] = retries
			retryreq.dont_filter = True
			retryreq.priority = request.priority + self.priority_adjust
			
			if isinstance(reason, Exception):
				reason = global_object_name(reason.__class__)
			
			stats.inc_value('retry/count')
			stats.inc_value('retry/reason_count/%s' % reason)
			return retryreq
		else:
			stats.inc_value('retry/max_reached')
			logger.debug("Gave up retrying %(request)s (failed %(retries)d times): %(reason)s",
			             {'request': request, 'retries': retries, 'reason': reason},
			             extra={'spider': spider})
			# 如果主要是由于出现exception，则说明该ip地址很可能失效
			if exception_retries > response_retries:
				# 随意封装一个response，返回给靠近engin的middleware，也就是上面定义的MiddlewareIpagentDownloaderMiddleware
				response = HtmlResponse(url='retry_over_exception')
				return response
		# else:
		#     response = scrapy.http.HtmlResponse(url='retry_over_response')

































