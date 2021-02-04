from db_control import *
import time
import datetime

DB_CTL = db_control()

def time_increase(begin_time,days):
	ts = time.strptime(str(begin_time),"%Y-%m-%d")
	ts = time.mktime(ts)
	dateArray = datetime.datetime.utcfromtimestamp(ts)
	date_increase = (dateArray+datetime.timedelta(days=days)).strftime("%Y-%m-%d")
	return  date_increase



def buy_fund(bought_date,code,bought_value,trade_rank):
    transactionRate=0.002
    #sql_If_bought = f"SELECT * FROM tb_trade_records WHERE CODE = '{code}' AND sold_date is null;"
    #sql_Insert_transaction = f"INSERT INTO tb_trade_records \
    #(bought_date,code,bought_value,trade_rank) VALUES \
    #('{bought_date}','{code}',{round((bought_value*transactionRate)+bought_value,4)},'{trade_rank}');"

    if not DB_CTL.sql_select_excute(f"SELECT * FROM tb_trade_records WHERE CODE = '{code}' AND sold_date is null;"):
        DB_CTL.sql_insert_excute(f"INSERT INTO tb_trade_records \
    (bought_date,code,bought_value,trade_rank) VALUES \
    ('{bought_date}','{code}',{round((bought_value*transactionRate)+bought_value,4)},'{trade_rank}');")
    else:
        pass




def sale_fund(sale_date,code,sale_value):
    transactionRate=0.001
    #sql_If_bought = f"SELECT * FROM tb_trade_records WHERE CODE = '{code}' AND sold_date is null;"
    if (res := DB_CTL.sql_select_excute(f"SELECT * FROM tb_trade_records WHERE CODE = '{code}' AND sold_date is null;")):
        dateDalta = (datetime.datetime.strptime(sale_date,'%Y-%m-%d').date()-res[0][1]).days
        if dateDalta < 7:
            print(f"{sale_date}-{code} bought time less than 7 days")
            pass
        else:
            sql_Update_transaction = f"UPDATE tb_trade_records SET \
            sold_date='{sale_date}',sold_value={round((sale_value*transactionRate)+sale_value,4)},\
            rate_of_return={round((sale_value-res[0][4])/res[0][4]*100,2)} \
            WHERE CODE='{code}' AND sold_date is null;"
            DB_CTL.sql_insert_excute(sql_Update_transaction)


#==================================    
#
#监控tb_trade_records未被卖出的基金，检查20日均价与现价之比是否已小于2%
#
#==================================   
def monitor_fund(curren_Date):  #curren_Date
    #sql_If_bought = "SELECT code FROM tb_trade_records WHERE sold_date is null;"
    #already_Bought = tuple(x[0] for x in DB_CTL.sql_select_excute(sql_If_bought))
    #if len(already_Bought) == 1:
    #    already_Bought = f"('{already_Bought[0]}')"
    sql_rate_With_avg_price = f'''
    WITH T1 AS (SELECT ROW_NUMBER()OVER(PARTITION BY tw.CODE ORDER BY tw.net_worth_date DESC) AS RK,
			tw.net_worth_date,tw.code,fn.name,tw.cumulative_net_worth
			from tb_fund_net_worth as tw,tb_fund_name as fn
	WHERE Net_worth_date BETWEEN to_date('{curren_Date}','yyyy-mm-dd') - 15
			AND to_date('{curren_Date}','yyyy-mm-dd') and tw.code = fn.code AND fn.shstat=false 
			AND (fn.type2id='x2001' or fn.type2id='x2002')),
	T2 AS (
		SELECT * FROM T1 WHERE RK = 1
	),
	T3 AS (
		SELECT * FROM T1 WHERE RK = 2
	),
	T4 AS (
		SELECT * FROM T1 WHERE RK = 3
	),
	T5 AS (
		SELECT * FROM T1 WHERE RK = 7
	),
	day2 AS (
		SELECT T2.NET_WORTH_DATE,T2.CODE,T2.NAME,T2.CUMULATIVE_NET_WORTH AS CURRENT,T3.CUMULATIVE_NET_WORTH AS Historical,
	ROUND(CAST((T2.CUMULATIVE_NET_WORTH-T3.CUMULATIVE_NET_WORTH)/T3.CUMULATIVE_NET_WORTH*100 AS numeric),4) AS PERCENTAGE FROM T2,T3
	WHERE T2.CODE = T3.CODE ORDER BY PERCENTAGE DESC
	),
	day3 AS (
		SELECT T2.NET_WORTH_DATE,T2.CODE,T2.NAME,T2.CUMULATIVE_NET_WORTH AS CURRENT,T4.CUMULATIVE_NET_WORTH AS Historical,
	ROUND(CAST((T2.CUMULATIVE_NET_WORTH-T4.CUMULATIVE_NET_WORTH)/T4.CUMULATIVE_NET_WORTH*100 AS numeric),4) AS PERCENTAGE FROM T2,T4
	WHERE T2.CODE = T4.CODE ORDER BY PERCENTAGE DESC
	),
	day7 as (
		SELECT T2.NET_WORTH_DATE,T2.CODE,T2.NAME,T2.CUMULATIVE_NET_WORTH AS CURRENT,T5.CUMULATIVE_NET_WORTH AS Historical,
	ROUND(CAST((T2.CUMULATIVE_NET_WORTH-T5.CUMULATIVE_NET_WORTH)/T5.CUMULATIVE_NET_WORTH*100 AS numeric),4) AS PERCENTAGE FROM T2,T5
	WHERE T2.CODE = T5.CODE ORDER BY PERCENTAGE DESC
	)
	SELECT TR.CODE,day2.name,day2.current,day2.rk2,day3.rk3,day7.rk7 FROM tb_trade_records AS TR,
	(SELECT ROW_NUMBER()OVER() AS RK2,day2.* FROM day2) as day2,
	(SELECT ROW_NUMBER()OVER() AS RK3,day3.* FROM day3) as day3,
	(SELECT ROW_NUMBER()OVER() AS RK7,day7.* FROM day7) as day7
    where TR.CODE = day2.code AND TR.CODE = day3.code and TR.CODE = day7.code 
	AND TR.sold_date is null 
	and tr.code not in (select code from day7  limit 3000)
    '''
    #print(sql_rate_With_avg_price)
    rate_With_avg_price = DB_CTL.sql_select_excute(sql_rate_With_avg_price)
    if rate_With_avg_price:
        for x in rate_With_avg_price:
            print(f"[sell]-----{curren_Date}----{x[0]}----{x[1]}----RARNK1:{x[3]}/RARNK3:{x[4]}/RARNK7:{x[5]}/")
            sale_fund(curren_Date,x[0],x[2])
    else:
        pass
    
    


#==================================    
#
#根据历史净值计算是否有基金10日均价与现价之比超过3%，并且进入了1、3、5日收益排行前300名
#
#================================== 
def discover_fund_trend(startDate):
    while datetime.datetime.strptime(startDate,'%Y-%m-%d') < datetime.datetime.today():
        SQL_STR = f'''
        WITH T1 AS (SELECT ROW_NUMBER()OVER(PARTITION BY tw.CODE ORDER BY tw.net_worth_date DESC) AS RK,
			tw.net_worth_date,tw.code,fn.name,tw.cumulative_net_worth
			from tb_fund_net_worth as tw,tb_fund_name as fn
        WHERE Net_worth_date BETWEEN to_date('{startDate}','yyyy-mm-dd') - 15
                AND to_date('{startDate}','yyyy-mm-dd') and tw.code = fn.code AND fn.sgstat=false 
                AND (fn.type2id='x2001' or fn.type2id='x2002') AND FN.CXPJ > 0),
        T2 AS (
            SELECT * FROM T1 WHERE RK = 1
        ),
        T3 AS (
            SELECT * FROM T1 WHERE RK = 2
        ),
        T4 AS (
            SELECT * FROM T1 WHERE RK = 3
        ),
        T5 AS (
            SELECT * FROM T1 WHERE RK = 7
        ),
        day2 AS (
            SELECT T2.NET_WORTH_DATE,T2.CODE,T2.NAME,T2.CUMULATIVE_NET_WORTH AS CURRENT,T3.CUMULATIVE_NET_WORTH AS Historical,
        ROUND(CAST((T2.CUMULATIVE_NET_WORTH-T3.CUMULATIVE_NET_WORTH)/T3.CUMULATIVE_NET_WORTH*100 AS numeric),4) AS PERCENTAGE FROM T2,T3
        WHERE T2.CODE = T3.CODE ORDER BY PERCENTAGE DESC
        ),
        day3 AS (
            SELECT T2.NET_WORTH_DATE,T2.CODE,T2.NAME,T2.CUMULATIVE_NET_WORTH AS CURRENT,T4.CUMULATIVE_NET_WORTH AS Historical,
        ROUND(CAST((T2.CUMULATIVE_NET_WORTH-T4.CUMULATIVE_NET_WORTH)/T4.CUMULATIVE_NET_WORTH*100 AS numeric),4) AS PERCENTAGE FROM T2,T4
        WHERE T2.CODE = T4.CODE ORDER BY PERCENTAGE DESC
        ),
        day7 as (
            SELECT T2.NET_WORTH_DATE,T2.CODE,T2.NAME,T2.CUMULATIVE_NET_WORTH AS CURRENT,T5.CUMULATIVE_NET_WORTH AS Historical,
        ROUND(CAST((T2.CUMULATIVE_NET_WORTH-T5.CUMULATIVE_NET_WORTH)/T5.CUMULATIVE_NET_WORTH*100 AS numeric),4) AS PERCENTAGE FROM T2,T5
        WHERE T2.CODE = T5.CODE ORDER BY PERCENTAGE DESC
        )
        select day2.code,day2.name,day2.current,day2.rk2,day3.rk3,day7.rk7 from 
        (SELECT ROW_NUMBER()OVER() AS RK2,day2.* FROM day2) as day2,
        (SELECT ROW_NUMBER()OVER() AS RK3,day3.* FROM day3) as day3,
        (SELECT ROW_NUMBER()OVER() AS RK7,day7.* FROM day7) as day7
        where day2.code = day3.code and day2.code = day7.code 
        and day3.rk3 <= 30
        and day7.rk7 <= 500
        and not exists
        (SELECT * FROM tb_trade_records WHERE sold_date is null and code = day2.code)
        '''
        res = DB_CTL.sql_select_excute(SQL_STR)
        if res:
            for x in res:
                print(f"[buy]-----{startDate}-----fund name{x[0]}{x[1]}-----RANK1:{x[3]}/RANK3:{x[4]}/RANK7:{x[5]}")
                buy_fund(startDate,x[0],x[2],f"{x[3]}/{x[4]}/{x[5]}")
                #print(startDate,res)
        else:
            print(f"{startDate} is null")
        monitor_fund(startDate)
        startDate=time_increase(startDate,2)


if __name__ == "__main__":
    #time_increase('{curren_Date}',4)
    discover_fund_trend('2020-03-07')
    #monitor_fund('2020-03-')
    #buy_fund('2020-01-05','001480',1.31)
    #sale_fund('2020-01-22','333333',1.1)
    #monitor_fund()