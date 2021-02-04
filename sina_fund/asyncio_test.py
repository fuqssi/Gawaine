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
        print(f"BUY SQL EXCUTE SELECT * FROM tb_trade_records WHERE CODE = '{code}' AND sold_date is null")
        DB_CTL.sql_insert_excute(f"INSERT INTO tb_trade_records \
    (bought_date,code,bought_value,trade_rank) VALUES \
    ('{bought_date}','{code}',{round((bought_value*transactionRate)+bought_value,4)},'{trade_rank}');")
        print(f"insert trade message INSERT INTO tb_trade_records \
    (bought_date,code,bought_value,trade_rank) VALUES \
    ('{bought_date}','{code}',{round((bought_value*transactionRate)+bought_value,4)},'{trade_rank}')")
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
            print(f"{sale_date}-{code} sold out")
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
    sql_rate_With_avg_price = f'''select 
    t.code,
    t.cumulative_net_worth,
    t.average_price,
    round(cast((t."cumulative_net_worth"-t.average_price)/t.average_price*100 as numeric),4 ) as rate_of_return 
from
    (select Current."code",
            Current."cumulative_net_worth", 
            round(cast(((Current."cumulative_net_worth")+(Historical."cumulative_net_worth"))/2 as numeric),4) as average_price
    from 
            (SELECT * FROM 
                (SELECT *,ROW_NUMBER()OVER(PARTITION BY CODE ORDER BY net_worth_date DESC)  AS RK 
                from tb_fund_net_worth
                WHERE Net_worth_date BETWEEN to_date('{curren_Date}','yyyy-mm-dd') - 15 AND to_date('{curren_Date}','yyyy-mm-dd')) T 
    WHERE RK = 1) as Current,
        (SELECT * FROM 
        (SELECT *,ROW_NUMBER()OVER(PARTITION BY CODE ORDER BY net_worth_date DESC)  AS RK from tb_fund_net_worth
        WHERE Net_worth_date BETWEEN to_date('{curren_Date}','yyyy-mm-dd') - 180 AND to_date('{curren_Date}','yyyy-mm-dd')) T WHERE RK = 20) as Historical
        where Current.code = Historical.code) t 
        WHERE exists (SELECT code FROM tb_trade_records WHERE sold_date is null and tb_trade_records.code = t.code );
    '''
    #print(sql_rate_With_avg_price)
    rate_With_avg_price = DB_CTL.sql_select_excute(sql_rate_With_avg_price)
    if rate_With_avg_price:
        for x in rate_With_avg_price:
            print(curren_Date,x)
            if x[3] < 2:
                sale_fund(curren_Date,x[0],x[1])
            else:
                pass
    
    


#==================================    
#
#根据历史净值计算是否有基金10日均价与现价之比超过3%，并且进入了1、3、5日收益排行前300名
#
#================================== 
def discover_fund_trend(startDate):
    rateOfavg = 3
    #i = 1
    #从传入的起始日期往后推780天
    #while i <= 430:
    while datetime.datetime.strptime(startDate,'%Y-%m-%d') < datetime.datetime.today():
        SQL_STR = f'''SELECT T1.CODE,T5.NAME,
            T1.cumulative_net_worth AS CURRENT_WORTH,
            T1.average_price AS AVG_PRICE_5DAYS,
            T1.rate_of_return AS RATE_WITH_AVG_PRICE,
            T2.RANK AS RANK_BY_1DAY,
            T3.RANK AS RANK_BY_3DAYS,
            T4.RANK AS RANK_BY_5DAYS 
    FROM 
    /*
    【5日均价/现价和均价收益率】
    取时间段内tb_fund_net_worth记录，根据日期加ROW_NUMBER()取1-5条记录
    */
    (select 
        t.code,
        t.cumulative_net_worth,
        t.average_price,
        round(cast((t."cumulative_net_worth"-t.average_price)/t.average_price*100 as numeric),4 ) as rate_of_return 
    from
        (select Current."code",
                Current."cumulative_net_worth", 
                round(cast(((Current."cumulative_net_worth")+(Historical."cumulative_net_worth"))/2 as numeric),4) as average_price
        from 
                (SELECT * FROM 
                    (SELECT *,ROW_NUMBER()OVER(PARTITION BY CODE ORDER BY net_worth_date DESC)  AS RK 
                    from tb_fund_net_worth
                    WHERE Net_worth_date BETWEEN to_date('{startDate}','yyyy-mm-dd') - 15 AND to_date('{startDate}','yyyy-mm-dd')) T 
        WHERE RK = 1) as Current,
            (SELECT * FROM 
            (SELECT *,ROW_NUMBER()OVER(PARTITION BY CODE ORDER BY net_worth_date DESC)  AS RK from tb_fund_net_worth
            WHERE Net_worth_date BETWEEN to_date('{startDate}','yyyy-mm-dd') - 180 AND to_date('{startDate}','yyyy-mm-dd')) T WHERE RK = 10) as Historical
            where Current.code = Historical.code) t) AS T1,
    /*
    【当日收益率排名】
    取时间段内tb_fund_net_worth记录，根据日期加ROW_NUMBER()取1-2条记录用作计算，使用LIMIT筛选前几名
    */
    (with summary as (
        select Current."net_worth_date",Current."code",Current."cumulative_net_worth" as CURRENT,Historical."cumulative_net_worth" as Historical,
    round(cast(((Current."cumulative_net_worth")-(Historical."cumulative_net_worth"))/(Historical."cumulative_net_worth")*100 as numeric),2) as percent
    from 
    (SELECT * FROM 
    (SELECT *,ROW_NUMBER()OVER(PARTITION BY CODE ORDER BY net_worth_date DESC)  AS RK from tb_fund_net_worth
    WHERE Net_worth_date BETWEEN to_date('{startDate}','yyyy-mm-dd') - 15 AND to_date('{startDate}','yyyy-mm-dd')) T WHERE RK = 1) as Current,
    (SELECT * FROM 
    (SELECT *,ROW_NUMBER()OVER(PARTITION BY CODE ORDER BY net_worth_date DESC)  AS RK from tb_fund_net_worth
    WHERE Net_worth_date BETWEEN to_date('{startDate}','yyyy-mm-dd') - 15 AND to_date('{startDate}','yyyy-mm-dd')) T WHERE RK = 2) as Historical
    where Current.code = Historical.code order by percent desc
    )
    select ROW_NUMBER()OVER(ORDER BY s.percent desc) AS RANK,s.* from summary as s LIMIT 300) AS T2,
    /*
    【3日收益率排名】
    取时间段内tb_fund_net_worth记录，根据日期加ROW_NUMBER()取1-3条记录用作计算，使用LIMIT筛选前几名
    */
    (with summary as (
        select Current."net_worth_date",Current."code",Current."cumulative_net_worth" as CURRENT,Historical."cumulative_net_worth" as Historical,
    round(cast(((Current."cumulative_net_worth")-(Historical."cumulative_net_worth"))/(Historical."cumulative_net_worth")*100 as numeric),2) as percent
    from 
    (SELECT * FROM 
    (SELECT *,ROW_NUMBER()OVER(PARTITION BY CODE ORDER BY net_worth_date DESC)  AS RK from tb_fund_net_worth
    WHERE Net_worth_date BETWEEN to_date('{startDate}','yyyy-mm-dd') - 15 AND to_date('{startDate}','yyyy-mm-dd')) T WHERE RK = 1) as Current,
    (SELECT * FROM 
    (SELECT *,ROW_NUMBER()OVER(PARTITION BY CODE ORDER BY net_worth_date DESC)  AS RK from tb_fund_net_worth
    WHERE Net_worth_date BETWEEN to_date('{startDate}','yyyy-mm-dd') - 15 AND to_date('{startDate}','yyyy-mm-dd')) T WHERE RK = 3) as Historical
    where Current.code = Historical.code order by percent desc
    )
    select ROW_NUMBER()OVER(ORDER BY s.percent desc) AS RANK,s.* from summary as s LIMIT 300) AS T3,
    /*
    【5日收益率排名】
    取时间段内tb_fund_net_worth记录，根据日期加ROW_NUMBER()取1-5条记录用作计算，使用LIMIT筛选前几名
    */
    (with summary as (
        select Current."net_worth_date",Current."code",Current."cumulative_net_worth" as CURRENT,Historical."cumulative_net_worth" as Historical,
    round(cast(((Current."cumulative_net_worth")-(Historical."cumulative_net_worth"))/(Historical."cumulative_net_worth")*100 as numeric),2) as percent
    from 
    (SELECT * FROM 
    (SELECT *,ROW_NUMBER()OVER(PARTITION BY CODE ORDER BY net_worth_date DESC)  AS RK from tb_fund_net_worth
    WHERE Net_worth_date BETWEEN to_date('{startDate}','yyyy-mm-dd') - 15 AND to_date('{startDate}','yyyy-mm-dd')) T WHERE RK = 1) as Current,
    (SELECT * FROM 
    (SELECT *,ROW_NUMBER()OVER(PARTITION BY CODE ORDER BY net_worth_date DESC)  AS RK from tb_fund_net_worth
    WHERE Net_worth_date BETWEEN to_date('{startDate}','yyyy-mm-dd') - 15 AND to_date('{startDate}','yyyy-mm-dd')) T WHERE RK = 5) as Historical
    where Current.code = Historical.code order by percent desc
    )
    select ROW_NUMBER()OVER(ORDER BY s.percent desc) AS RANK,s.* from summary as s LIMIT 300) AS T4,
    /*
    关联基金基本信息tb_fund_name
    */
    tb_fund_name AS T5 
    WHERE T1.CODE = T2.CODE AND T1.CODE = T3.CODE AND T1.CODE = T4.CODE AND T1.CODE = T5.CODE AND 
	(T5.type2id='x2001' or T5.type2id='x2002') AND T5.sgstat=false AND T1.rate_of_return >={rateOfavg}
    ORDER BY RATE_WITH_AVG_PRICE DESC;'''
        res = DB_CTL.sql_select_excute(SQL_STR)
        if res:
            for x in res:
                print(f"{startDate}---fund name{x[0]}{x[1]}---RANK1:{x[5]}/RANK3:{x[6]}/RANK5:{x[7]}")
                buy_fund(startDate,x[0],x[2],f"{x[5]}/{x[6]}/{x[7]}")
            print(startDate,res)
        else:
            print(f"{startDate} is null")
        monitor_fund(startDate)
        startDate=time_increase(startDate,2)


if __name__ == "__main__":
    #time_increase('2020-01-01',4)
    discover_fund_trend('2020-03-01')
    #buy_fund('2020-01-05','001480',1.31)
    #sale_fund('2020-01-22','333333',1.1)
    #monitor_fund()