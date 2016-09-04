# -*- coding: utf-8 -*-
import scrapy,sys,re,urlparse,time,os
from scrapy.spiders import CrawlSpider
from scrapy.selector import Selector
from scrapy.http import Request
from scrapy.utils.markup import remove_tags
from collections import defaultdict
from datetime import datetime
import urlparse,json,re
from lxml import html
reload(sys)
sys.setdefaultencoding('utf8')
urllist = []
default_url = "http://onlinelibrary.wiley.com"
def findemail(authorlist,email):
	author_dict = {}
	emailz = email[0].replace(" ","").split("@")[0]
	for author in authorlist:
		author1 = author.lower().replace(" ","").replace(",","").replace("‐","")
		author_dict[author]=lev_edit_dist(author,emailz)
	return sorted(author_dict.items(),key=lambda x: x[1])[0][0]
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
with open("jsons/1099-0801_Biomedical Chromatography.json") as jsonfile:
	jsondata = json.load(jsonfile)
for url in jsondata:
	urllist.append("http://onlinelibrary.wiley.com/resolve/doi?DOI="+url['DOI'])

global counter
counter = 15
class jspider(CrawlSpider):
	name = 'crawl1'
	start_urls = urllist[:10]
	# start_urls = ["http://onlinelibrary.wiley.com/resolve/doi?DOI=10.1002/bmc.797"]

	def parse(self,response):
		a = 1
		meta_dict = {
					'doi':'citation_doi','issn':'citation_issn','issue_number':'citation_issue','keywords':'citation_keywords',
					'journal_name':'citation_journal_title','pdf_url':'citation_pdf_url',
					'pub_date':'citation_publication_date','publisher':'citation_publisher',
					'volume':'citation_volume','firstpage':'citation_firstpage','lastpage':'citation_lastpage'
					}
		result = {}
		for name,content in meta_dict.items():
			try:	
				if name == "keywords":
					result[name] = response.xpath("//meta[@name='{0}']/@content".format(content)).extract()
				else:
					result[name] = response.xpath("//meta[@name='{0}']/@content".format(content)).extract()[0]
			except:
				result[name] = ""
		##########################XPATH EXPRESSIONS IN HERE##################################################
		result['page'] = result['firstpage']+"-"+result['lastpage']
		del result['firstpage'],result['lastpage']
		result['url'] = response.url.split(";")[0]
		# authors_data = response.xpath("//ul[@class='article-header__authors_list js-module']/li/div/ol/li[1]").extract()
		author_dict = {}
		authors_data = response.xpath("//ul[@class='article-header__authors_list js-module']/li").extract()
		for author in authors_data:
			semi_author_dict = {}
			author_data = html.fromstring(author)
			author_name= author_data.xpath("//@data-author-name")[0]
			try:
				semi_author_dict["email"]= remove_tags(html.tostring(author_data.xpath("//a[@class='article-header__authors-item-email']")[0]))
			except:	
				a=1
			try:
				semi_author_dict["department"]= remove_tags(html.tostring(author_data.xpath("//div/ol/li")[0]))
			except:
				a=1
			author_dict[author_name] = semi_author_dict
		result["authors"] = author_dict
		### Add abstract and the required tags to save the html tags too
		try:
			abstract = response.xpath("//div[@id='en_main_abstract']/p").extract()[0].replace("<small>"," %small%").replace("</small>"," %/small%").replace("<sub>"," %sub%").replace("</sub>"," %/sub%").replace("<sup>"," %sup%").replace("</sup>"," %/sup%").replace("<em>"," %em%").replace("</em>"," %/em%")
			result["abstract"] = remove_tags(abstract.replace("<strong>"," %strong%").replace("</strong>"," %/strong%").replace("\n"," ").replace("  ","").strip()).replace(u"\u2013","-")
		except:
			result["abstract"] = ""
		try:
			title = response.xpath("//h1[@class='article-header__title']").extract()[0].replace("<small>"," %small%").replace("</small>"," %/small%").replace("<sub>"," %sub%").replace("</sub>"," %/sub%").replace("<sup>"," %sup%").replace("</sup>"," %/sup%").replace("<em>"," %em%").replace("</em>"," %/em%")
			result["title"] = remove_tags(title.replace("<strong>"," %strong%").replace("</strong>"," %/strong%").replace("\n"," ").replace("  ","").strip()).replace(u"\u2013","-")
		except:
			title = ""
		#################citing urls here####################################
		citing_list = []
		cite_datas = response.xpath("//div[@id='js-citations__section']/div[@class='modal__scrollable']/ol[@class='article-section__citation-list']/li").extract()
		for cite_data in cite_datas:
			vol_data = []
			semi_cite_dict = {}
			cite_name = html.fromstring(cite_data)
			semi_cite_dict['authors'] = [author.strip() for author in cite_name.xpath("//cite/span[@class='author']/text()")]
			cite_text = cite_name.xpath("//cite/text()")
			try:
				semi_cite_dict['title'] = "".join(cite_text[:-2]).replace(", ","").replace(u"\u2013","-")
			except:
				semi_cite_dict['title'] = ""
			journal_detail = {}
			try:
				journal_detail['journal'] = remove_tags(html.tostring(cite_name.xpath("//span[@class='journalTitle']")[0])).replace(",","").strip()
			except:
				journal_detail['journal'] = ""
			try:	
				journal_detail['pub_info'] = remove_tags(html.tostring(cite_name.xpath("//span[@class='pubYear']")[0])).replace(",","").strip()
			except:
				journal_detail['pub_info'] = ""
			try:
				vol_data = remove_tags(html.tostring(cite_name.xpath("//span[@class='vol']")[0])).replace(",","").strip().split(" ")
				if vol_data != []:
					if len(vol_data)>2:
						journal_detail['volume'] = vol_data[0]
						journal_detail['issue_number'] = vol_data[1]
						journal_detail['pages'] = vol_data[2]
					elif len(vol_data)>1:
						journal_detail['volume'] = vol_data[0]
						journal_detail['issue_number'] = vol_data[1]
					else:
						journal_detail['volume'] = vol_data[0]
			except:
				journal_detail['volume'] = ""
			semi_cite_dict['details']=journal_detail
			try:
				cite_link = cite_name.xpath("//a[@class='article-section__citation-link']/@href")[0]
				semi_cite_dict["doi"] = re.findall(r"(10\..*?)$",cite_link)[0]
			except:
				semi_cite_dict['doi'] = ""
			citing_list.append(semi_cite_dict)
		result['citing_articles'] = citing_list
		rel_url = "http://onlinelibrary.wiley.com/advanced/search/results?articleDoi="+result['doi']+"&scope=allContent&start=1&resultsPerPage=20"
		rel_method = Request(url=rel_url,callback=self.rel_articles)
		rel_method.meta['result'] = result
		yield rel_method

	def rel_articles(self,response):
		global counter
		rel_method = response.meta['result']
		rel_list = []
		try:
			rel_datas  = response.xpath("//div[@id='searchResultsList']/ol[@class='articles']/li/div[@class='citation article']").extract()
			for rel_data in rel_datas:
				tag = ""
				title_rel = ""
				semi_rel_dict = {}
				jour_det = {}
				rel_data = rel_data.decode("utf-8")
				# print rel_data
				tag = html.fromstring(rel_data)
				### add tags in title tooo, similar to the HTML ones
				title_rel = html.tostring(tag.xpath("//a[1]")[0]).replace("<small>"," %small%").replace("</small>"," %/small%").replace("<sub>"," %sub%").replace("</sub>"," %/sub%").replace("<sup>"," %sup%").replace("</sup>"," %/sup%").replace("<em>"," %em%").replace("</em>"," %/em%")
				semi_rel_dict["title"]= remove_tags(title_rel.replace("<strong>"," %strong%").replace("</strong>"," %/strong%").replace("\n"," ").replace("  ","").strip())
				semi_rel_dict['url']= urlparse.urljoin(default_url,tag.xpath("//a[1]/@href")[0])
				jour_det['journal_name'] =  tag.xpath("//h3/text()")[0]
				jour_details = tag.xpath("//p[1]/text()")[0].split(",")
				if "Volume" in jour_details[0]:
					jour_det['volume'] = jour_details[0].replace("Volume ","")
				else:
					jour_det['volume'] = ""
				if "Issue" in jour_details[1]:
					jour_det['issue_no'] = jour_details[1].replace("Issue ","")
				else:
					jour_det['issue_no'] = ""
				if "Pages" in jour_details[3]:
					jour_det['pages'] = jour_details[3].replace("Pages:","").replace(u"\u2013","-").strip()
				else:
					jour_det['pages'] = ""
				jour_det['pub_info'] = jour_details[2].strip()
				####PROBLEM TO GET THE DAMNED AUTHORS
				rel_auth_data = ",".join(jour_details[4:]).replace("and",",").split(",")
				if rel_auth_data!=[" "]:
					jour_det['authors'] = ",".join(jour_details[4:]).replace("and",",").split(", ")
				else:
					jour_det['authors'] = []
				semi_rel_dict['details'] = jour_det
				rel_pub_details = tag.xpath("//p[2]/text()")[0].split(",")
				semi_rel_dict["doi"] = rel_pub_details[-1].replace("DOI:","").replace(u"\u00a0","").strip()
				rel_list.append(semi_rel_dict)
		except Exception as e:
			print e
		rel_method['related_articles'] = rel_list
		doi = rel_method['doi']
		rel_method["crawled_date"] = str(datetime.now().date())
		doi_file = doi.replace("/","-").replace(".","_")
		with open("journals/BiomedicalChromatography/"+doi_file+".json","w") as jsondata:
			json.dump(rel_method,jsondata,indent=4,encoding="utf-8",ensure_ascii=False)
		counter +=1
		with open("records/BiomedicalChromatography.txt","a") as writerecord:
			writerecord.write(str(counter)+"\t"+str(rel_method["url"])+"\t"+doi+"\n")