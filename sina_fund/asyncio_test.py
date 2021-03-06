from configparser import ConfigParser
import time
import os
import sys
import datetime
import re
import json
import demjson
from db_control import *
from LogRecorder import *
from session_rqst import *
import psycopg2

PATH = os.path.join(sys.path[0],"config.cfg")
config=ConfigParser()
print(PATH)
config.read(PATH)
SQL_INSERT_FUND_NET_WORTH = 'INSERT INTO tb_fund_net_worth (NET_WORTH_DATE,CODE,NET_WORTH,CUMULATIVE_NET_WORTH) VALUES (%s,%s,%s,%s)'
SQL_INSERT_FUND_NAME = 'INSERT INTO TB_FUND_NAME VALUES (%s,%s,%s)'
SQL_FUND_LAST_UPDATE = 'UPDATE TB_FUND_NAME SET last_update=%s WHERE CODE =%s'
req = session_rqst()
logger = LogRecorder()


#==================================    
#
# 新浪基金接口返回字符串整形规则
#
#==================================    

def fund_rank_resp_fmt(TEXT):
    TEXT = re.sub(r'^//.*\s','',TEXT)
    TEXT = re.sub(r'^IO.{21}','',TEXT)
    TEXT = re.sub(r'].exec.*',']}',TEXT)
    return TEXT    


#==================================    
#
# 获取新浪基金接口信息
# 交给fund_rank_resp_fmt()和demjson.decode()进行json格式化
#
#==================================       

def get_fund_name(page_num):
    SINA_FUND_URL = (config.get('sina_fund','url')\
        +'page=%s&num='+config.get('sina_fund','num')\
        +'&sort='+config.get('sina_fund','sort')\
        +'&asc='+config.get('sina_fund','asc')\
        +'&ccode='+config.get('sina_fund','ccode')\
        +'type2='+config.get('sina_fund','type2')\
        +'&type3='+config.get('sina_fund','type3'))\
        %(page_num)
    try:
        RESPONES = fund_rank_resp_fmt(req.get(SINA_FUND_URL).text)
        RESPONES = demjson.decode(RESPONES)
    except  Exception  as  e:
        logger.exception_log('Get %s %s'%(SINA_FUND_URL,e))
    else:
        print(RESPONES)
        return RESPONES



#==================================    
#
#插入基金基本信息（代码、名称、基金经理、净值更新日期）
#
#==================================  
def insert_fund_name():
    DB_CTL = db_control()
    RECORDS_PER_PAGE = int(config.get('sina_fund','num'))
    TOTAL_RECORDS_NUM = get_fund_name(1)['total_num']
    PAGE_NUM = 1
    i = 0
    j = 0
    while i < TOTAL_RECORDS_NUM:
        logger.info_log('======Starting Request Sina API From Page %s ======'%(PAGE_NUM))
        RECORDS = get_fund_name(PAGE_NUM)

        while j < RECORDS_PER_PAGE:
            logger.debug_log('INSERT INTO TB_FUND_NAME VALUES (%s,%s)'%(RECORDS['data'][j]['symbol'],RECORDS['data'][j]['name']))
            try:
                DB_CTL.sql_insert_excute(SQL_INSERT_FUND_NAME,(RECORDS['data'][j]['symbol'],\
                        RECORDS['data'][j]['name'],RECORDS['data'][j]['jjjl']))
            except Exception as e:
                logger.exception_log(e)
                i += 1
                j += 1
                continue
            else:
                i += 1
                j += 1
                if i == TOTAL_RECORDS_NUM:
                    logger.info_log('======All of records are processed done !======')
                    break
                
        PAGE_NUM += 1
        j = 0
    DB_CTL.cursor_close()


#==================================    
#
#插入基金净值（日期、代码、净值、累计净值）
#
#==================================   
def insert_fund_value(FUND_CODE):
    DB_CTL = db_control()
    PAGE_NUM  = 1
    url = (config.get('sina_fund_worth','url')+'symbol=%s&page=%s')%(FUND_CODE,PAGE_NUM)
    RESPONES = req.get(url).json()
    TOTAL_RECORDS_NUM = RESPONES['result']['data']['total_num']
    i = 0
    j = 0
    arr = []        
    while len(RESPONES['result']['data']['data']) != 0:
        #==================================    
        #       
        #我发现新浪历史净值的记录总数不准，只好尽可能的翻页，如果返回的json item数量为0则跳出循环
        #更新tb_fund_name最后更新日期
        #================================== 
        url = (config.get('sina_fund_worth','url')+'symbol=%s&page=%s')%(FUND_CODE,PAGE_NUM)
        try:
            logger.info_log('GET %s'%(url))
            RESPONES = req.get(url).json()
        except Exception as e:
            #==================================    
            #       
            #如果调用接口时如果碰见超时则跳出循环再试一次，continue可确保页码计数不自增while不断重试
            #尽量确保记录不遗漏
            #
            #================================== 
            logger.exception_log('%s %s'%(url,e))
            time.sleep(3)
            continue
        else:
            while j < len(RESPONES['result']['data']['data']):
                logger.info_log('Current fund had records:%s,Now:%s'%(TOTAL_RECORDS_NUM,i+1))
                try:
                    arr.append(tuple((RESPONES['result']['data']['data'][j]['fbrq'],\
                        FUND_CODE,RESPONES['result']['data']['data'][j]['jjjz'],\
                        RESPONES['result']['data']['data'][j]['ljjz'])))
                except Exception as e:
                    logger.exception_log(e)
                    i += 1
                    j += 1
                    continue
                else:
                    i += 1
                    j += 1
            j = 0
            PAGE_NUM += 1
    
    logger.info_log('======All of records are processed done !======')
    DB_CTL.sql_list_insert(SQL_INSERT_FUND_NET_WORTH,arr)
    DB_CTL.sql_insert_excute(SQL_FUND_LAST_UPDATE,(datetime.date.today(),FUND_CODE))
    DB_CTL.cursor_close()

def select_all_code():
    DB_CTL = db_control()
    res = DB_CTL.sql_select_excute('select * from tb_fund_name;')
    DB_CTL.cursor_close()
    return res
    

if __name__ == "__main__":

    #res = get_fund_name(1)
    

    #插入tb_fun_name表数据
    #insert_fund_name()

    #insert_fund_value('005312') #测试insert方法

    #根据tb_fund_name表中的code列插入历史净值
    CODES = select_all_code()
    for i in CODES:
        logger.info_log(i)
        insert_fund_value(i[0])