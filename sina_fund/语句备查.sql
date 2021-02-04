--explain 查询最新的净值记录
select DISTINCT on (code) net_worth_date,code,
 cumulative_net_worth
from tb_fund_net_worth
order by code,net_worth_date desc

-- explain 根据净值记录更新基金信息中的更新日期
update  tb_fund_name  set last_update=last_worth."net_worth_date" from 
(SELECT * FROM 
(SELECT *,ROW_NUMBER()OVER(PARTITION BY CODE ORDER BY net_worth_date DESC)  AS RK from tb_fund_net_worth
WHERE Net_worth_date BETWEEN current_date - 15 AND current_date) T WHERE RK = 1) as last_worth
where last_worth.code=tb_fund_name.code;    


-- explain 查询一段时间内的增幅
CREATE OR REPLACE VIEW public.view_rate_of_return_by_365day AS
WITH T1 AS (SELECT ROW_NUMBER()OVER(PARTITION BY tw.CODE ORDER BY tw.net_worth_date DESC) AS RK,
			tw.net_worth_date,tw.code,fn.name,tw.cumulative_net_worth
			from tb_fund_net_worth as tw,tb_fund_name as fn
	WHERE Net_worth_date BETWEEN current_date - 380
			AND current_date and tw.code = fn.code AND fn.sgstat=false 
			AND (fn.type2id='x2001' or fn.type2id='x2002')),
	T2 AS (
		SELECT * FROM T1 WHERE RK = 1
	),
	T3 AS (
		SELECT * FROM T1 WHERE RK = 365
	),
	T4 AS (
	SELECT T2.NET_WORTH_DATE,T2.CODE,T2.NAME,T2.CUMULATIVE_NET_WORTH AS CURRENT,T3.CUMULATIVE_NET_WORTH AS Historical,
	ROUND(CAST((T2.CUMULATIVE_NET_WORTH-T3.CUMULATIVE_NET_WORTH)/T2.CUMULATIVE_NET_WORTH*100 AS numeric),4) AS PERCENTAGE FROM T2,T3
	WHERE T2.CODE = T3.CODE ORDER BY PERCENTAGE DESC
	)
SELECT ROW_NUMBER()OVER(),T4.* FROM T4;

--一段时间内基金当时的累计净值和均值
SELECT * FROM 
(SELECT T1.net_worth_date,T1.code,T1.cumulative_net_worth,
ROUND(CAST((T1.cumulative_net_worth+T2.cumulative_net_worth)/2 AS NUMERIC),4) AS AVG_PRICE
FROM 
(SELECT *,ROW_NUMBER()OVER(PARTITION BY CODE ORDER BY net_worth_date DESC)  AS RK from tb_fund_net_worth
WHERE Net_worth_date BETWEEN current_date - 1000 AND current_date AND CODE = '519674') T1
LEFT JOIN 
(SELECT *,ROW_NUMBER()OVER(PARTITION BY CODE ORDER BY net_worth_date DESC)  AS RK from tb_fund_net_worth
WHERE Net_worth_date BETWEEN current_date - 1000 AND current_date AND CODE = '519674') T2
ON
T1.RK = T2.RK-20 ORDER BY T1.net_worth_date DESC LIMIT 400) AS A ORDER BY A.net_worth_date;



--删除重复记录
delete from tb_fund_net_worth t where exists (select * from tb_fund_net_worth r where t.code=r.code and t.net_worth_date = r.net_worth_date and t.ctid > r.ctid);

--所有索引
SELECT VIEWNAME FROM PG_VIEWS WHERE SCHEMaNAME='public';


---测试语句
--排名查询 
SELECT * FROM tb_fund_name WHERE 
CODE IN  (SELECT CODE FROM view_rate_of_return_by_1day LIMIT 30) AND
CODE IN  (SELECT CODE FROM view_rate_of_return_by_3days LIMIT 30) AND
CODE IN  (SELECT CODE FROM view_rate_of_return_by_7days LIMIT 30);



--均价计算
CREATE OR REPLACE VIEW VIEW_RATE_OF_AVERAGE_BY_5DAYS AS
select 
    t.code,
    t.average_price,
    round(cast((t."cumulative_net_worth"-t.average_price)/t.average_price*100 as numeric),4 ) as rate_of_return 
from
    (select Current."code",Current."cumulative_net_worth", 
    round(cast(((Current."cumulative_net_worth")+(Historical."cumulative_net_worth"))/2 as numeric),4) as average_price
    from 
        (SELECT * FROM 
        (SELECT *,ROW_NUMBER()OVER(PARTITION BY CODE ORDER BY net_worth_date DESC)  AS RK from tb_fund_net_worth
        WHERE Net_worth_date BETWEEN current_date - 15 AND current_date) T WHERE RK = 1) as Current,
        (SELECT * FROM 
        (SELECT *,ROW_NUMBER()OVER(PARTITION BY CODE ORDER BY net_worth_date DESC)  AS RK from tb_fund_net_worth
        WHERE Net_worth_date BETWEEN current_date - 60 AND current_date) T WHERE RK = 5) as Historical
        where Current.code = Historical.code) t;



 drop view view_rate_of_average_by_5days;
 drop view view_rate_of_average_by_10days;
 drop view view_rate_of_average_by_20days;


---一句话看清近期涨幅超过5日均价5%的且进入7天内排名30的基金，且显示排名情况
select t1.code,t2.name,t1.average_price,t1.rate_of_return,t3.rank as RANK_WITH_1DAY,
t4.rank AS RANK_WITH_5DAYS,t5.rank AS RANK_WITH_7DAYS
from VIEW_RATE_OF_AVERAGE_BY_5days t1,tb_fund_name t2,view_rate_of_return_by_1day t3,
view_rate_of_return_by_3days t4,view_rate_of_return_by_7days t5
where t1.code=t2.code and  t1.code = t3.code and t1.code=t4.code and t1.code = t5.code and 
t1.rate_of_return > 5 and
t1.CODE IN  (SELECT CODE FROM view_rate_of_return_by_1day LIMIT 30) AND
t1.CODE IN  (SELECT CODE FROM view_rate_of_return_by_3days LIMIT 30) AND
t1.CODE IN  (SELECT CODE FROM view_rate_of_return_by_7days LIMIT 30)
ORDER BY RANK_WITH_7DAYS;


SELECT T1.CODE,T4.NAME,T1.rate_of_return AS DAY5,T2.rate_of_return AS DAY10,T3.rate_of_return AS DAY20 
FROM view_rate_of_average_by_5days T1,
view_rate_of_average_by_10days T2,
view_rate_of_average_by_20DAYS T3,
tb_fund_name T4
WHERE T1.CODE = T2.CODE AND T1.CODE = T3.CODE AND T1.CODE = T4.CODE
AND T1.CODE IN ('002844','257070','519005','001480');


select t1.code,t2.name,t1.average_price,t1.rate_of_return,t3.rank as RANK_WITH_1DAY,
t4.rank AS RANK_WITH_5DAYS,t5.rank AS RANK_WITH_7DAYS
from VIEW_RATE_OF_AVERAGE_BY_5days t1,tb_fund_name t2,view_rate_of_return_by_1day t3,
view_rate_of_return_by_3days t4,view_rate_of_return_by_7days t5
where t1.code=t2.code and  t1.code = t3.code and t1.code=t4.code and t1.code = t5.code and 
t1.CODE IN ('002844','257070','519005','001480') and
t1.CODE IN  (SELECT CODE FROM view_rate_of_return_by_1day LIMIT 30) AND
t1.CODE IN  (SELECT CODE FROM view_rate_of_return_by_3days LIMIT 30) AND
t1.CODE IN  (SELECT CODE FROM view_rate_of_return_by_7days LIMIT 30)
ORDER BY RANK_WITH_7DAYS;






--------数据分析起点，根据5日均价排名查找收益率排名靠前的基金

SELECT T1.CODE,T5.NAME,
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
            WHERE Net_worth_date BETWEEN to_date('{startDate}','yyyy-mm-dd') - 60 AND to_date('{startDate}','yyyy-mm-dd')) T WHERE RK = 5) as Historical
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
    select ROW_NUMBER()OVER(ORDER BY s.percent desc) AS RANK,s.* from summary as s LIMIT 50) AS T2,
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
    select ROW_NUMBER()OVER(ORDER BY s.percent desc) AS RANK,s.* from summary as s LIMIT 50) AS T3,
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
    select ROW_NUMBER()OVER(ORDER BY s.percent desc) AS RANK,s.* from summary as s LIMIT 50) AS T4,
    /*
    关联基金基本信息tb_fund_name
    */
    tb_fund_name AS T5 
    WHERE T1.CODE = T2.CODE AND T1.CODE = T3.CODE AND T1.CODE = T4.CODE AND T1.CODE = T5.CODE AND T1.rate_of_return >={rateOfavg}
    ORDER BY RATE_WITH_AVG_PRICE DESC;

-- 根据近日涨幅排名聚合重仓股
select s_name,count(s_code) from tb_fund_holding t1 where exists 
(select * from public.view_rate_of_return_by_7day t2 where t1.code = t2.code limit 500 )
group by s_name order by count(s_code) desc