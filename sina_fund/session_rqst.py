
import requests

class session_rqst(object):
    def __init__(self):
        self._headers = { 
                    "User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) \
                        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36",
                    "Accept-Language" : "zh-CN,zh;q=0.9,en;q=0.8",
                    "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,\
                        image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                    "Cache-Control" : "max-age=0"
                }
        self._timeout = 15
        self.s = requests.Session()
        self.adapter = requests.adapters.HTTPAdapter(pool_connections=10,pool_maxsize=100, max_retries=5)
        self.s.mount("http://",self.adapter)
        self.s.mount("https://",self.adapter)

    def get(self,url):
        return self.s.get(url,headers=self._headers,timeout=self._timeout)
