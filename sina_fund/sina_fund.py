from configparser import ConfigParser
import requests
import re
import json
import demjson
from logging import *
from db_control import *
from LogRecorder import *

config=ConfigParser()
config.read('/Users/yanxl/OneDrive/Code/Gawaine/sina_fund/config.cfg')
SQL_INSERT_FUND_NET_WORTH = 'INSERT INTO tb_fund_net_worth (NET_WORTH_DATE,CODE,NET_WORTH,CUMULATIVE_NET_WORTH) VALUES (%s,%s,%s,%s)'
SQL_INSERT_FUND_NAME = 'INSERT INTO TB_FUND_NAME VALUES (%s,%s,%s)'

logger = LogRecorder()


def fund_rank_resp_fmt(TEXT):
    TEXT = re.sub(r'^//.*\s','',TEXT)
    TEXT = re.sub(r'^IO.{21}','',TEXT)
    TEXT = re.sub(r'].exec.*',']}',TEXT)
    return TEXT    

def get_fund_name(page_num):
    SINA_FUND_URL = (config.get('sina_fund','url')\
        +'page=%s&num='+config.get('sina_fund','num')\
        +'&sort='+config.get('sina_fund','sort')\
        +'&asc='+config.get('sina_fund','asc')\
        +'&ccode='+config.get('sina_fund','ccode')\
        +'type2='+config.get('sina_fund','type2')\
        +'&type3='+config.get('sina_fund','type3'))\
        %(page_num)

    RESPONES = fund_rank_resp_fmt(requests.get(SINA_FUND_URL).text)
    RESPONES = demjson.decode(RESPONES)
    return RESPONES


def insert_fund_name():
    DB_CTL = db_control()
    RECORDS_PER_PAGE = int(config.get('sina_fund','num'))
    TOTAL_RECORDS_NUM = get_fund_name(1)['total_num']
    PAGE_NUM = 14
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
                #利用遍历基金信息的顺便就用insert_fund_value()把基金历史净值入库了
                insert_fund_value(RECORDS['data'][j]['symbol'])
            except Exception as e:
                logger.exception_log(e)
                i += 1
                j += 1
                continue
            else:
                i += 1
                j += 1
                if i == TOTAL_RECORDS_NUM:
                    break
                
        PAGE_NUM += 1
        j = 0
    DB_CTL.cursor_close()

def insert_fund_value(FUND_CODE):
    DB_CTL = db_control()
    PAGE_NUM  = 1
    url = (config.get('sina_fund_worth','url')+'symbol=%s&page=%s')%(FUND_CODE,PAGE_NUM)
    RESPONES = requests.get(url).json()
    TOTAL_RECORDS_NUM = RESPONES['result']['data']['total_num']
    i = 0
    j = 0
    while i < int(TOTAL_RECORDS_NUM):
        url = (config.get('sina_fund_worth','url')+'symbol=%s&page=%s')%(FUND_CODE,PAGE_NUM)
        RESPONES = requests.get(url).json()

        while j < len(RESPONES['result']['data']['data']):
            try:
                DB_CTL.sql_insert_excute(\
                    SQL_INSERT_FUND_NET_WORTH,(\
                    RESPONES['result']['data']['data'][j]['fbrq'],\
                    FUND_CODE,\
                    RESPONES['result']['data']['data'][j]['jjjz'],\
                    RESPONES['result']['data']['data'][j]['ljjz']))
            except Exception as e:
                logger.exception_log(e)
                i += 1
                j += 1
                continue
            else:
                i += 1
                j += 1
                if j == TOTAL_RECORDS_NUM:
                    break
        j = 1
        PAGE_NUM += 1
    DB_CTL.cursor_close()

def select_all_code():
    DB_CTL = db_control()
    res = DB_CTL.sql_select_excute('select code from tb_fund_name;')
    print(res)
    DB_CTL.cursor_close()

if __name__ == "__main__":
    insert_fund_name()
    #insert_fund_value('005312')
    #select_all_code()