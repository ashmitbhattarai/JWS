#!/bin/bash
cd /root/crawlers/JWS/JWS/
PATH=$PATH:/usr/local/bin
export PATH
scrapy crawl ncjc
