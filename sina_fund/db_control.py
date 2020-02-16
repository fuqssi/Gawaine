from configparser import ConfigParser
import psycopg2
from LogRecorder import *

class db_control:
    def __init__(self):
        self.logger = LogRecorder()
        config = ConfigParser()
        assert config.read('/Users/yanxl/OneDrive/Code/Gawaine/sina_fund/config.cfg')
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
            self.logger.exception_log(e)
        else:
            return RESULT         

    def sql_insert_excute(self,sql_string,sql_param):
        try:
            CURSOR = self.CONN.cursor()
            CURSOR.execute(sql_string,sql_param)
            self.CONN.commit()
        except Exception as e:
            self.logger.exception_log(e)
        else:
            return None
    
    def cursor_close(self):
        self.CONN.close()
        return None

if __name__ == "__main__":
    DB_CTL = db_control()
    res = DB_CTL.sql_select_excute('select code from tb_fund_name;')
    print(res)
    DB_CTL.cursor_close()