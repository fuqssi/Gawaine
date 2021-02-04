SELECT tr.id,tr.bought_date,tr.sold_date,tr.code,fn.name,tr.bought_value,tr.sold_value,
tr.rate_of_return,SUMMARY.cumulative_net_worth
FROM tb_trade_records tr,tb_fund_name fn,
(WITH SUMMARY AS 
(SELECT *,ROW_NUMBER()OVER(PARTITION BY CODE ORDER BY net_worth_date DESC)  AS RK 
FROM tb_fund_net_worth
WHERE Net_worth_date BETWEEN current_date - 15 AND current_date)
SELECT * FROM SUMMARY WHERE SUMMARY.RK = 1) AS SUMMARY
where tr.code = fn.code AND TR.CODE = SUMMARY.CODE AND TR.SOLD_VALUE IS NULL--AND TR.CODE = '519674' 
order by tr.bought_date

select fn.code,fn.name,sum(tr.rate_of_return) from tb_trade_records tr,tb_fund_name fn,
(WITH SUMMARY AS 
(SELECT *,ROW_NUMBER()OVER(PARTITION BY CODE ORDER BY net_worth_date DESC)  AS RK 
FROM tb_fund_net_worth
WHERE Net_worth_date BETWEEN current_date - 15 AND current_date)
SELECT * FROM SUMMARY WHERE SUMMARY.RK = 1) AS SUMMARY
where tr.code = fn.code AND TR.CODE = SUMMARY.CODE
group by fn.name,fn.code order by sum(tr.rate_of_return) desc


