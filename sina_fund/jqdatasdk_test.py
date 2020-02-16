from jqdatasdk import *
import matplotlib.pyplot as plt

auth('18966808664','Yxl59078108')


'''#获取基金时间段大于20200101的净值
q=query(finance.FUND_NET_VALUE)\
    .filter(finance.FUND_NET_VALUE\
    ,finance.FUND_NET_VALUE.day>'2020-01-01')\
    .order_by(finance.FUND_NET_VALUE.day.desc()).limit(10)
df=finance.run_query(q)
print(df)'''

'''print(df.info())
print(df.head())
dfcs=df[['net_value']]
print (dfcs)
plt.plot(dfcs)
plt.show()'''

'''
#获取基金重仓股
q=query(finance.FUND_PORTFOLIO_STOCK).filter(finance.FUND_PORTFOLIO_STOCK.code=="519005").order_by(finance.FUND_PORTFOLIO_STOCK.pub_date.desc()).limit(10)
df=finance.run_query(q)
print(df)
'''
q=finance.run_query(query(finance.FUND_MAIN_INFO))
   
df=finance.run_query(q)
print(df)