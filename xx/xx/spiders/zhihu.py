# -*- coding: utf-8 -*-
import scrapy
import json
from datetime import datetime

from xx.zhihu_people import ZhihuPeople

class ZhihuSpider(scrapy.Spider):
    name = "zhihu"
    allowed_domains = ["zhihu.com"]
    custom_settings = {
        'CONCURRENT_REQUESTS': 16,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 16,
        'CONCURRENT_REQUESTS_PER_IP': 16,
        'DOWNLOAD_DELAY': 2,
        'COOKIES_DEBUG': True,
        'FEED_FORMAT': 'json',
        'FEED_URI': 'zhihu.json',
        'MONGO_URI': 'syslog-1',
        'MONGO_DATABASE': 'test',
        'MONGO_COLLECTION': 'zhihu',
        'RETRY_TIMES': 3,
        'ITEM_PIPELINES': {
            'xx.mongodb.MongoPipeline': 300,
        },
        'DOWNLOADER_MIDDLEWARES': {
        #   'xx.randomproxy.RandomProxy': 300,
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': 333,
        }
    }

    def start_requests(self):
        self.logger.info('---CALL start_requests()---')

        login_url = 'http://www.zhihu.com/login/email'
        login_data = {'email': 'ch_etang@163.com', 'password': 'chetang'}
        return [ scrapy.FormRequest(url = login_url, 
                        formdata = login_data,
                        callback = self.parse_login) ]

    def parse_login(self, response):
        self.logger.info('---CALL parse_login()---')
        self.logger.info('---response.body = %s', response.body)

        start_url = 'http://www.zhihu.com/'
        request = scrapy.Request(url = start_url, callback = self.parse_start_page)
        yield request


    def parse_start_page(self, response):
        self.logger.info('---CALL parse_start_page()---')
        self.logger.info('---response.url = %s', response.url)

        people_url = 'https://www.zhihu.com/people/AOneAndATwo'
        request = scrapy.Request(url = people_url, callback = self.parse_people_page)
        yield request

    def parse_xpath(self, xpath, response):
        alist = response.xpath(xpath).extract()
        if len(alist):
            return alist[0]
        return None

    def parse_people_page(self, response):
        self.logger.info('---CALL parse_people_page()---')
        self.logger.info('---response.url = %s', response.url)

        people = ZhihuPeople()
        people['url'] = response.url
        people['name'] = self.parse_xpath('/html/body/div[3]/div[1]/div/div[1]/div[1]/div[1]/div/span[1]/text()', response)
        people['bio'] = self.parse_xpath('/html/body/div[3]/div[1]/div/div[1]/div[1]/div[1]/div/span[2]/text()', response)
        people['location'] = self.parse_xpath('/html/body/div[3]/div[1]/div/div[1]/div[1]/div[2]/div/div/div[1]/div[1]/span[1]/span[1]/a/text()', response)
        people['business'] = self.parse_xpath('/html/body/div[3]/div[1]/div/div[1]/div[1]/div[2]/div/div/div[1]/div[1]/span[1]/span[2]/text()', response)

        gender = response.xpath('/html/body/div[3]/div[1]/div/div[1]/div[1]/div[2]/div/div/div[1]/div[1]/span[1]/span[3]/i/@class').extract()
        if "female" in gender:
            people['gender'] = "female"
        elif "male" in gender:
            people['gender'] = "male"
        else:
            people['gender'] = "unknown"

        people['business'] = self.parse_xpath('/html/body/div[3]/div[1]/div/div[1]/div[1]/div[2]/div/div/div[1]/div[2]/span[1]/span[1]/text()', response)
        people['position'] = self.parse_xpath('/html/body/div[3]/div[1]/div/div[1]/div[1]/div[2]/div/div/div[1]/div[2]/span[1]/span[2]/text()', response)
        people['education'] = self.parse_xpath('/html/body/div[3]/div[1]/div/div[1]/div[1]/div[2]/div/div/div[1]/div[3]/span[1]/span[1]/a/text()', response)
        people['educationextra'] = self.parse_xpath('/html/body/div[3]/div[1]/div/div[1]/div[1]/div[2]/div/div/div[1]/div[3]/span[1]/span[2]/a/text()', response)
        people['content'] = self.parse_xpath('/html/body/div[3]/div[1]/div/div[1]/div[1]/div[2]/div/div/div[2]/span[1]/span[2]/span/text()', response)

        marked = self.parse_xpath('/html/body/div[3]/div[1]/div/div[1]/div[2]/a/text()', response)
        if marked:
            marked = marked.split(' ')[0]
        people['marked'] = marked
        
        people['useragree'] = self.parse_xpath('/html/body/div[3]/div[1]/div/div[1]/div[3]/div[1]/span[2]/strong/text()', response)
        people['userthanks'] = self.parse_xpath('/html/body/div[3]/div[1]/div/div[1]/div[3]/div[1]/span[3]/strong/text()', response)
        people['asks'] = self.parse_xpath('/html/body/div[3]/div[1]/div/div[1]/div[4]/a[2]/span/text()', response)
        people['answers'] = self.parse_xpath('/html/body/div[3]/div[1]/div/div[1]/div[4]/a[3]/span/text()', response)
        people['posts'] = self.parse_xpath('/html/body/div[3]/div[1]/div/div[1]/div[4]/a[4]/span/text()', response)
        people['collections'] = self.parse_xpath('/html/body/div[3]/div[1]/div/div[1]/div[4]/a[5]/span/text()', response)
        people['logs'] = self.parse_xpath('/html/body/div[3]/div[1]/div/div[1]/div[4]/a[6]/span/text()', response)
        people['followees'] = self.parse_xpath('/html/body/div[3]/div[2]/div[1]/a[1]/strong/text()', response)
        people['followers'] = self.parse_xpath('/html/body/div[3]/div[2]/div[1]/a[2]/strong/text()', response)

        columnsfollowed = self.parse_xpath('/html/body/div[3]/div[2]/div[2]/div/div[1]/a/strong/text()', response)
        if columnsfollowed:
            columnsfollowed = columnsfollowed.split(' ')[0]
        people['columnsfollowed'] = columnsfollowed

        topics = self.parse_xpath('/html/body/div[3]/div[2]/div[3]/div/div[1]/a/strong/text()', response)
        if topics:
            topics = topics.split(' ')[0]
        people['topics'] = topics

        people['browsers'] = self.parse_xpath('/html/body/div[3]/div[2]/div[5]/div/span/strong/text()', response)
        people['datetime'] = datetime.now()
        yield people

        people_url = response.url + '/followees'
        request = scrapy.Request(url = people_url, callback = self.parse_people_followees)
        yield request

        people_url = response.url + '/followers'
        request = scrapy.Request(url = people_url, callback = self.parse_people_followers)
        yield request

    def parse_people_followees(self, response):
        self.logger.info('---CALL parse_people_followees()---')
        self.logger.info('---response.url = %s', response.url)
        hrefs = response.xpath('//*[@id="zh-profile-follows-list"]/div/*/div[2]/h2/a/@href').extract()
        for i, href in enumerate(hrefs):
            people_url = href
            request = scrapy.Request(url = people_url, callback = self.parse_people_page)
            yield request

    def parse_people_followers(self, response):
        self.logger.info('---CALL parse_people_followers()---')
        self.logger.info('---response.url = %s', response.url)
        hrefs = response.xpath('//*[@id="zh-profile-follows-list"]/div/*/div[2]/h2/a/@href').extract()
        for i, href in enumerate(hrefs):
            people_url = href
            request = scrapy.Request(url = people_url, callback = self.parse_people_page)
            yield request

