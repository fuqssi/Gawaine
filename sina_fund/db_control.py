from configparser import ConfigParser
import psycopg2
from psycopg2.extras import execute_values
import os
import sys
from LogRecorder import *

class db_control:
    def __init__(self):
        self.logger = LogRecorder()
        self.PATH = os.path.join(sys.path[0],"config.cfg")
        config = ConfigParser()
        config.read(self.PATH)
        self.DBNAME = config.get('db','dbname')
        self.USERNAME = config.get('db','username')
        self.PASSWORD = config.get('db','password')
        self.HOST = config.get('db','host')
        self.CONN = psycopg2.connect(dbname=self.DBNAME,user= self.USERNAME,host=self.HOST,password=self.PASSWORD)


    def sql_select_excute(self,sql_string):
        try:
            CURSOR = self.CONN.cursor()
            CURSOR.execute(sql_string)
            RESULT = CURSOR.fetchall()            
        except Exception as e:
            self.logger.exception_log('【%s 】 %s'%(sql_string,e))
        else:
            return RESULT         

    def sql_insert_excute(self,sql_string):
        try:
            CURSOR = self.CONN.cursor()
            CURSOR.execute(sql_string)
        except Exception as e:
            self.logger.exception_log('【%s】 %s'%(sql_string,e))
        else:
            return None
        finally:
            self.CONN.commit()

    def sql_list_insert(self,sql_string,sql_param):
        try:
            CURSOR = self.CONN.cursor()
            execute_values(CURSOR,sql_string,sql_param)
        except Exception as e:
            self.logger.exception_log('【%s】 %s'%(sql_param,e))
        else:
            return None
        finally:
            self.CONN.commit()

    def update_tb_name(self):
        try:
            SQL_STR = '''update  tb_fund_name  set last_update=last_worth."net_worth_date" from 
            (SELECT * FROM
            (SELECT *,ROW_NUMBER()OVER(PARTITION BY CODE ORDER BY net_worth_date DESC)  AS RK from tb_fund_net_worth 
            WHERE Net_worth_date BETWEEN current_date - 180 AND current_date) T WHERE RK = 1) as last_worth 
            where last_worth.code=tb_fund_name.code;'''
            CURSOR = self.CONN.cursor()
            CURSOR.execute(SQL_STR)
        except Exception as e:
            self.logger.exception_log('【%s】'%(e))
        else:
            self.CONN.commit()
            return None
        finally:
            self.logger.info_log('======Database records are update done !======')

    
    def cursor_close(self):
        self.CONN.close()
        return None

if __name__ == "__main__":
    DB_CTL = db_control()
    DB_CTL.update_tb_name()
    DB_CTL.cursor_close()