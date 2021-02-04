import matplotlib.pyplot as plt
import matplotlib.dates as mdate
from matplotlib.pyplot import MultipleLocator
from db_control import *
import pandas as pd 
import datetime as dt

db = db_control()
date = []
net_Worth = []
avg_Price = []
code = "006751"

def transaction_point(operation,trans_date,trans_value):
    print(operation,trans_date,trans_value)
    ax = plt.gca()
    if operation == "buy":
        an = ax.annotate(f"{operation}",
                xy = (trans_date,trans_value),
                xytext = (trans_date,round((trans_value*1.1),1)),
                weight = 'regular',
                color = 'red',#注释文本的颜色
                fontsize = 15,#注释文本的字体大小
                arrowprops = {
                    'arrowstyle': '->',#箭头类型
                    'connectionstyle': 'arc3',#连接类型
                    'color': 'r'#箭头颜色
                })
    elif operation == "sell":
        an = ax.annotate(f"{operation}",
                xy = (trans_date,trans_value),
                xytext = (trans_date,round((trans_value/1.1),1)),
                weight = 'regular',
                color = 'g',#注释文本的颜色
                fontsize = 15,#注释文本的字体大小
                arrowprops = {
                    'arrowstyle': '->',#箭头类型
                    'connectionstyle': 'arc3',#连接类型
                    'color': 'g'#箭头颜色
                })
    else:
        raise "trans opration Input err"
    
    return an

SQL = f'''
SELECT * FROM 
(SELECT T1.net_worth_date,T1.code,T1.cumulative_net_worth,
ROUND(CAST((T1.cumulative_net_worth+T2.cumulative_net_worth)/2 AS NUMERIC),4) AS AVG_PRICE
FROM 
(SELECT *,ROW_NUMBER()OVER(PARTITION BY CODE ORDER BY net_worth_date DESC)  AS RK from tb_fund_net_worth
WHERE Net_worth_date BETWEEN current_date - 1000 AND current_date AND CODE = '{code}') T1
LEFT JOIN 
(SELECT *,ROW_NUMBER()OVER(PARTITION BY CODE ORDER BY net_worth_date DESC)  AS RK from tb_fund_net_worth
WHERE Net_worth_date BETWEEN current_date - 1000 AND current_date AND CODE = '{code}') T2
ON
T1.RK = T2.RK-90 ORDER BY T1.net_worth_date DESC LIMIT 400) AS A ORDER BY A.net_worth_date;
'''

sql_Trans = f'''SELECT tr.id,tr.bought_date,tr.sold_date,tr.code,fn.name,tr.bought_value,tr.sold_value,tr.rate_of_return,SUMMARY.cumulative_net_worth
FROM tb_trade_records tr,tb_fund_name fn,
(WITH SUMMARY AS 
(SELECT *,ROW_NUMBER()OVER(PARTITION BY CODE ORDER BY net_worth_date DESC)  AS RK 
FROM tb_fund_net_worth
WHERE Net_worth_date BETWEEN current_date - 15 AND current_date)
SELECT * FROM SUMMARY WHERE SUMMARY.RK = 1) AS SUMMARY
where tr.code = fn.code AND TR.CODE = SUMMARY.CODE AND TR.CODE = '{code}'
order by tr.bought_date
'''
res = db.sql_select_excute(SQL)

for record in res:
    date.append(record[0])
    net_Worth.append(record[2])
    avg_Price.append(record[3])


plt.rcParams['font.sans-serif']=['SimHei']#用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False#用来正常显示负号
fig = plt.figure(figsize=(19,9))
ax = fig.add_subplot(1,1,1)
ax.xaxis.set_major_formatter(mdate.DateFormatter('%Y%m%d'))#设置时间标签显示格式
ax.xaxis.set_major_locator(MultipleLocator(30))
ax.yaxis.set_major_locator(MultipleLocator(0.1))
ax.set_title(f"{code}")
ax.plot(date, net_Worth)
ax.plot(date, avg_Price,color='red')
plt.xticks(rotation=45)#旋转45度显示
plt.xlabel = ("Date")
plt.ylabel = ("value")
legend = ax.legend(loc='lower center', shadow=False)

res = db.sql_select_excute(sql_Trans)
for record in res:
    print(record[1],record[5])
    print(record[2],record[6])

    transaction_point("buy",record[1],record[5])
    if record[2]:
        transaction_point("sell",record[2],record[6])
    else:
        pass



plt.show() 