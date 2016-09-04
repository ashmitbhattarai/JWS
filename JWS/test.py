# -*- coding: utf-8 -*-
import scrapy,sys,re,urlparse,time,os
from scrapy.spiders import CrawlSpider
from scrapy.selector import Selector
from scrapy.http import Request
from scrapy.utils.markup import remove_tags
from collections import defaultdict
from datetime import datetime
import urlparse,json,re,os
from lxml import html
reload(sys)
sys.setdefaultencoding('utf8')
urllist = []
default_url = "http://onlinelibrary.wiley.com"
urls = []
auth_list = []
# with open("/root/rsc.json","a") as rsdata:
for filelist in os.walk("/root/crawlers/JWS/JWS/journals/BiomedicalChromatography"):
    for files in filelist[-1]:
        filepath = os.path.join("/root/crawlers/JWS/JWS/journals/BiomedicalChromatography",files)
        filejson = open(filepath,"r+")
        filedata = json.load(filejson)
        print filedata
        # auth_list.append(filedata)
    # json.dump(auth_list,rsdata,indent=4)

# with open("jsons/1099-0801_Biomedical Chromatography.json") as jsonfile:
#     jsondata = json.load(jsonfile)
# for url in jsondata[:20]:
#     print "http://onlinelibrary.wiley.com/resolve/doi?DOI="+url['DOI']

# print re.findall(r"(10\..*?)$","http://onlinelibrary.wiley.com/resolve/reference/XREF?id=10.1016/j.jpba.2008.07.022")