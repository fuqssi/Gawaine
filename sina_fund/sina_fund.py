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

PATH = os.path.join(sys.path[0],"config.cfg")
config=ConfigParser()
config.read(PATH)
req = session_rqst()
logger = LogRecorder()
DB_CTL = db_control()

SQL_INSERT_FUND_NET_WORTH = 'INSERT INTO tb_fund_net_worth (NET_WORTH_DATE,CODE,NET_WORTH,CUMULATIVE_NET_WORTH) VALUES %s;'
SQL_INSERT_FUND_NAME = 'INSERT INTO TB_FUND_NAME VALUES %s;'
SQL_FUND_LAST_UPDATE = 'UPDATE TB_FUND_NAME SET last_update=%s WHERE CODE =%s;'
SQL_INSERT_FUND_HOLDING = 'INSERT INTO tb_fund_holding (code,s_code,s_name,s_rate) VALUES %s;'


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
        return RESPONES



#==================================    
#
#插入基金基本信息（代码、名称、基金经理、净值更新日期）
#
#==================================  
def insert_fund_name():
    PAGE_NUM = 1
    TOTAL_RECORDS_NUM =get_fund_name(PAGE_NUM)['total_num']
    i = 0
    j = 0
    arr = []
    while i < TOTAL_RECORDS_NUM:
        #logger.info_log('======Starting Request Sina API From Page %s ======'%(PAGE_NUM))
        RECORDS = get_fund_name(PAGE_NUM)

        while j < len(RECORDS['data']):
            #logger.debug_log('【%s】-%s,%s'%(j,RECORDS['data'][j]['symbol'],RECORDS['data'][j]['name']))
            try:
                arr.append(tuple((RECORDS['data'][j]['symbol'],\
                        RECORDS['data'][j]['name'],\
                        RECORDS['data'][j]['jjjl'])))
            except Exception as e:
                logger.exception_log(e)
                i += 1
                j += 1
                continue
            else:
                i += 1
                j += 1

        PAGE_NUM += 1
        j = 0
    logger.info_log('======All of records are processed done !======')
    print(arr)
    DB_CTL.sql_list_insert(SQL_INSERT_FUND_NAME,arr)

def update_fund_stat(code):
    url  = f"http://stock.finance.sina.com.cn/fundfilter/api/openapi.php/XincaiFundFilterService.getFundInfo?symbol={code}&dpc=1"
    res = demjson.decode(req.get(url).text)

    logger.info_log(f'''UPDATE tb_fund_name set type1id={res["result"]["data"][0]["Type1Id"]},type2id={res["result"]["data"][0]["Type2Id"]},type3id={res["result"]["data"][0]["Type3Id"]},sgstat={res["result"]["data"][0]["SHStat"]},shstat={res["result"]["data"][0]["SHStat"]} WHERE CODE = '{code}';''')

    DB_CTL.sql_insert_excute(f'''UPDATE tb_fund_name set type1id='{res["result"]["data"][0]["Type1Id"]}',type2id='{res["result"]["data"][0]["Type2Id"]}',
        type3id='{res["result"]["data"][0]["Type3Id"]}',sgstat='{res["result"]["data"][0]["SHStat"]}',shstat='{res["result"]["data"][0]["SHStat"]}' WHERE CODE = '{code}';''')



#==================================    
#
#插入基金净值（日期、代码、净值、累计净值）
#
#==================================   
def insert_fund_value(FUND_CODE):
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

def select_all_code():
    res = DB_CTL.sql_select_excute('''SELECT * FROM TB_FUND_NAME WHERE (type2id = 'x2001'::bpchar OR type2id = 'x2002'::bpchar);''')
    return res

def update_fund_value(FUND_CODE,last_update):
    PAGE_NUM  = 1
    url = (config.get('sina_fund_worth','url')+'symbol=%s&page=%s')%(FUND_CODE,PAGE_NUM)
    RESPONES = req.get(url).json()
    arr = []          
    while len(RESPONES['result']['data']['data']) != 0:
        #==================================        
        #我发现新浪历史净值的记录总数不准，只好尽可能的翻页，如果返回的json item数量为0则跳出循环
        #更新tb_fund_name最后更新日期
        #================================== 
        url = (config.get('sina_fund_worth','url')+'symbol=%s&page=%s')%(FUND_CODE,PAGE_NUM)
        try:
            logger.info_log('GET %s'%(url))
            RESPONES = req.get(url).json()
        except Exception as e:
            #==================================    
            #如果调用接口时如果碰见超时则跳出循环再试一次，continue可确保页码计数不自增while不断重试
            #尽量确保记录不遗漏
            #================================== 
            logger.exception_log('%s %s'%(url,e))
            time.sleep(3)
            continue
        else:
            for record in RESPONES['result']['data']['data']:
                #{'fbrq': '2020-02-28 00:00:00', 'jjjz': '1.0023', 'ljjz': '1.0023'}
                logger.info_log(f"The {FUND_CODE} Last update:{last_update},current record is:{record['fbrq']}")

                if datetime.datetime.strptime(record['fbrq'],'%Y-%m-%d %H:%M:%S').date() > last_update \
                    and tuple((record['fbrq'],FUND_CODE,record['jjjz'],record['ljjz'])) not in arr:
                    arr.append(tuple((record['fbrq'],FUND_CODE,record['jjjz'],record['ljjz'])))
                else:
                    break
            if datetime.datetime.strptime(record['fbrq'],'%Y-%m-%d %H:%M:%S').date() > last_update:    
                PAGE_NUM += 1
                # time.sleep(2.5)
            elif not arr:
                break
            else:
                #DB_CTL.sql_list_insert(SQL_INSERT_FUND_NET_WORTH,arr)
                break
    DB_CTL.sql_list_insert(SQL_INSERT_FUND_NET_WORTH,arr)        
    logger.info_log(f"======All of {FUND_CODE} records are update done !======")

def update_fund_holding(FUND_CODE):
        url = (config.get('sina_fund_holding','url')+'symbol=%s')%(FUND_CODE)
        RESPONES = req.get(url).json()
        arr = []
        try:
            for i in RESPONES['result']['data']:
                arr.append(tuple((FUND_CODE,i['ESYMBOL'],i['NAME'],i['RATE'])))
            DB_CTL.sql_list_insert(SQL_INSERT_FUND_HOLDING,arr)  
            logger.info_log(f"======{FUND_CODE} Holdings are update done !======")
        except Exception as e:
            logger.exception_log('%s %s'%(FUND_CODE,e))
       

if __name__ == "__main__":
    # CODES = DB_CTL.sql_select_excute("SELECT code FROM TB_FUND_NAME t1 \
    #     WHERE (type2id = 'x2001'::bpchar OR type2id = 'x2002'::bpchar) and not exists \
    #     (select distinct(code) from tb_fund_holding t2 where t1.code = t2.code)")
    # TOTAL = len(CODES)
    # CURRENT = 1
    # for i in CODES:
    #     logger.info_log(f"【{CURRENT}/{TOTAL}】")
    #     print(i[0])
    #     update_fund_holding(i[0])
    #     CURRENT += 1
    #     time.sleep(2)

    #res = get_fund_name(1)
    

    #插入tb_fun_name表数据
    # insert_fund_name()

    #insert_fund_value('005312') #测试insert方法

# 更新基金状态
    # CODES = select_all_code()
    # TOTAL = len(CODES)
    # CURRENT = 1
    # for i in CODES:
    #     logger.info_log(f"【{CURRENT}/{TOTAL}】")
    #     update_fund_stat(i[0])
    #     time.sleep(2)

#根据tb_fund_name表中的code列插入历史净值
   CODES = select_all_code()
   TOTAL = len(CODES)
   CURRENT = 1
   for i in CODES:
       logger.info_log(f"【{CURRENT}/{TOTAL}】 {i}")
       update_fund_value(i[0],i[3])
       CURRENT += 1
       #time.sleep(2)
   DB_CTL.update_tb_name()
   DB_CTL.cursor_close()

    #update_fund_value('000809',datetime.datetime.strptime('2020-02-21','%Y-%m-%d').date())
    
 #插入晨星   
    # page = 1
    # url  = f"http://stock.finance.sina.com.cn/fundfilter/api/openapi.php/MoneyFinanceFundFilterService.getFundFilterAll?&page={page}&num=10&dpc=1"
    # #res = demjson.decode(req.get(url).text)
    # while len(res := demjson.decode(req.get(url).text))!=0:
    #     if res["result"]["data"]["data"]:
    #         for x in res["result"]["data"]["data"]:
    #             print (x['symbol'],x['cxpj'])
    #             DB_CTL.sql_insert_excute(f'''UPDATE tb_fund_name set cxpj='{x["cxpj"]}' WHERE CODE = '{x["symbol"]}';''')

    #         page += 1    
    #         url  = f"http://stock.finance.sina.com.cn/fundfilter/api/openapi.php/MoneyFinanceFundFilterService.getFundFilterAll?&page={page}&num=10&dpc=1"
    #     else:
    #         break
