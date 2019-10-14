# -*- coding: utf-8 -*-

# Scrapy settings for tmall project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'tmall'

SPIDER_MODULES = ['tmall.spiders']
NEWSPIDER_MODULE = 'tmall.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'tmall (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
	'authority':'rate.tmall.com',
	'method':'GET',
	'path':'/list_detail_rate.htm?itemId=545129870941&spuId=722445115&sellerId=554185355&order=3&currentPage=1&append=0&content=1&tagId=&posi=&picture=&groupId=&_ksTS=1560173759587_1857&callback=jsonp1858',
	'scheme':'https',
	'accept':'*/*',
	'accept-encoding':'gzip, deflate, br',
	'accept-language':'zh-CN,zh;q=0.9',
	'referer': 'https://detail.tmall.com/item.htm?id=545129870941&ali_refid=a3_430620_1006:1103131728:N:uOOHZI7y/l/H5hoOESN8Tw==:c2e4b0a52190132666d07b23d56a4c20&ali_trackid=1_c2e4b0a52190132666d07b23d56a4c20&spm=a230r.1.14.1',
	'user-agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
	'cookie':'cna=G9o3EnTR1gACAd7JrYmmIIMw; lid=%E5%8A%AA%E5%8A%9B%E5%87%86%E5%A4%87%E7%9D%802015; hng=HK%7Czh-TW%7CHKD%7C344; OZ_1U_2061=vid=vcdd64e3c5b7cd.0&ctime=1558013507&ltime=1558013411; uss=""; t=fa6b0a03e4309ba87b25fc17dec57dba; tracknick=%5Cu52AA%5Cu529B%5Cu51C6%5Cu5907%5Cu77402015; lgc=%5Cu52AA%5Cu529B%5Cu51C6%5Cu5907%5Cu77402015; _tb_token_=ebe6336856a1e; cookie2=118c1957b1f8cf2f6605077ad68c93a4; uc1=cookie16=VFC%2FuZ9az08KUQ56dCrZDlbNdA%3D%3D&cookie21=V32FPkk%2FgPzW&cookie15=UtASsssmOIJ0bQ%3D%3D&existShop=false&pas=0&cookie14=UoTaGOn0V9mYgA%3D%3D&tag=8&lng=zh_CN; uc3=vt3=F8dBy3jdd1flu%2BnxCNo%3D&id2=UUtDWFO1lxqpRg%3D%3D&nk2=pjtAu9XGn9vj8eMIZ5Y%3D&lg2=V32FPkk%2Fw0dUvg%3D%3D; _l_g_=Ug%3D%3D; ck1=""; unb=2387741465; cookie1=VANCk8v%2FwA9kNgG%2BdmJgIZt33C15i9sl2Onc5UvVFKw%3D; login=true; cookie17=UUtDWFO1lxqpRg%3D%3D; _nk_=%5Cu52AA%5Cu529B%5Cu51C6%5Cu5907%5Cu77402015; csg=a6c114e2; skt=764dcc2e86c34f2c; x5sec=7b22726174656d616e616765723b32223a223039646438363530393232303530383632663836323138333561343062306564434966492b656346454b4c69335a3241316f754443426f4d4d6a4d344e7a63304d5451324e547378227d; l=bBSwYHDuvKqQxkJzBOfwCjoY0d_tyQAffsPy02LD3ICPOs6p1JeGWZTFQ_K9C3GVa6EwR3J4RKM8BxTULy4Eh; isg=BBIS3RRPmlMcnuMduN0cS9xZY9iAG5Ks54i04txpBkVv77TpxLKIzCBNXwv2n45V',
	'upgrade-insecure-requests':'1'
}

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'tmall.middlewares.TmallSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
   # 'tmall.middlewares.TmallDownloaderMiddleware': 543,
	"tmall.middlewares.UserAgentIpDownloaderMiddleware":548,
	"tmall.middlewares.TMallRetryMiddlewares":549,
	'scrapy.contrib.downloadermiddleware.retry.RetryMiddleware':None
}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   'tmall.pipelines.TmallPipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
RETRY_TIMES = 3

MYSQL_HOST = '39.106.86.218'
MYSQL_PORT = 3306
MYSQL_DBNAME = 'taobao'
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'hjy19960725'
MYSQL_ENCODING = 'utf8'

# MYSQL_HOST = 'localhost'
# MYSQL_PORT = 3306
# MYSQL_DBNAME = 'taobao'
# MYSQL_USER = 'root'
# MYSQL_PASSWORD = 'root'
# MYSQL_ENCODING = 'utf8'

