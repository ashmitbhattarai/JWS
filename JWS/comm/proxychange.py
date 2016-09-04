import random
import telnetlib
import time
import re
import base64
import logging


class ProxyMiddleware(object):
    def process_request(self, request, spider):
        request.meta['proxy'] = "http://127.0.0.1:80"
# PROXY_LIST = [
#             #     "http://165.139.179.225:8080",\
#             #     "https://103.10.22.242:3128",\
#             #     "http://113.204.212.50:3128",\
#             #     "http://200.48.4.148:80",\
#             #     "https://158.69.137.17:7808",\
#             #     "https://198.108.245.243:8080",\
#             #     "http://213.181.73.145:80",\
#             #     "http://89.108.165.37:8080",\
#             #     "https://82.117.158.241:8082",\
#             #     "http://188.165.141.151:80",\
#             # ]
