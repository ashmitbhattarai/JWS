# -*- coding: utf-8 -*-
import scrapy,sys,re,urlparse,time,os
from scrapy.spiders import CrawlSpider
from scrapy.selector import Selector
from scrapy.http import Request
from scrapy.utils.markup import remove_tags
from collections import defaultdict
from datetime import datetime
from lxml import html
import urlparse,json,re
reload(sys)
sys.setdefaultencoding('utf8')
url_list = []
urllist = []
# with open("1477-9234_Dalton Transactions.json","r+") as urljson:
    # url_list = json.load(urljson)
    # for each in url_list:
        # urllist.append(each["URL"])
urllist = open('uncrawled.txt','r+').read().split("\n")
def findemail(author,emaillist):
    email_dict = {}
    author1 = author.lower().replace(" ","")
    for email in emaillist:
        email1 = email.split("@")[0]
        email_dict[email]=lev_edit_dist(author1,email1)
    return sorted(email_dict.items(),key=lambda x: x[1])[0][0]
def lev_edit_dist(s1, s2):
    m=len(s1)+1
    n=len(s2)+1
    table = {}
    for i in range(m): table[i,0]=i
    for j in range(n): table[0,j]=j
    for i in range(1, m):
        for j in range(1, n):
            cost = 0 if s1[i-1] == s2[j-1] else 1
            table[i,j] = min(table[i, j-1]+1, table[i-1, j]+1, table[i-1, j-1]+cost)
    return table[i,j]
global article_count
article_count = 0
class journalscraper(CrawlSpider):
    name = "ncjc"
    rotate_user_agent=True
    start_urls = urllist[2:]

    def parse(self,response):
        global article_count
        result = {}
        authors = []
        authorss = []
        author_dict = {}
        main_author = []
        writers = []
        authors_dept = []
        writers_details = []
        try:
            writers = response.xpath('//meta[@name="citation_author"]/@content').extract()
            try:
                authors_dept = response.xpath('//meta[@name="citation_author_institution"]/@content').extract()
                for author in writers:
                    auth_index = writers.index(author)
                    semi_auth_dict = {}
                    semi_auth_dict[author] = {"department":authors_dept[auth_index]}    
                    authors.append(semi_auth_dict)
            except:
                for author in writers:
                    authors.append(author)
        except:
            authors = []
        result['authors'] = authors
        result['doi'] = response.xpath('//meta[@name="DC.Identifier"]/@content').extract()[0]
        # print json.dumps(result,indent=4)
        article_count+= 1
        filename = result['doi'].replace(".","_").replace("/","-")
        with open("RSC/"+filename+".json","w") as writefile:
            json.dump(result,writefile,indent=4)
        with open("records.txt","a") as recordwrite:
            recordwrite.write(result['doi']+"\t"+str(article_count)+"\n")