# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.spiders import CrawlSpider

class ProxyipcnSpider(CrawlSpider):
    name = 'proxyipcn'
    allowed_domains = ['ipcn.org', 'baidu.com']
    test_url = 'http://www.baidu.com/favicon.ico'
    start_url = 'http://proxy.ipcn.org/proxylist.html'
    custom_settings = {
        'DOWNLOAD_DELAY': 1,
        'DOWNLOAD_TIMEOUT': 3,
        'COOKIES_DEBUG': True,
        'RETRY_TIMES': 1,
        'DOWNLOAD_TIMEOUT': 2,
        'REFERER_ENABLED': False,
        'FEED_FORMAT': 'json',
        'FEED_URI': 'ipcn.json',
    }

    def start_requests(self):
        start_url = self.start_url
        return [ scrapy.Request(url = start_url, callback = self.parse_proxylist) ]

    def parse_proxylist(self, response):
        pretext = response.xpath('/html/body/table/tr/td[1]/pre/text()').extract()
        self.logger.info('pretext = %s', len(pretext))
        alist = pretext[0].split('\n')
        p = re.compile('(\d*.\d*.\d*.\d*):(\d*)')
        for i, line in enumerate(alist):
            self.logger.info('%d: %s', i, line)
            m = p.match(line)
            if m:
                proxy = "http://" + m.group(0)
                self.logger.info('check proxy = %s, starting...', proxy)
                request = scrapy.Request(url = self.test_url + '?' + str(i), callback = self.check_proxy)
                request.meta['proxy'] = proxy
                yield request

    def check_proxy(self, response):
        proxy = response.meta['proxy']
        if response.status == 200 and response.headers['Content-Type'] == 'image/x-icon':
            self.logger.info('check proxy = %s, OK.', proxy)
            yield {"addr": proxy}
        else:
            self.logger.info('check proxy = %s, FAILED.', proxy)
