from configparser import ConfigParser
import psycopg2

class db_control:
    def __init__(self):
        config = ConfigParser()
        config.read('config.cfg')
        self.DBNAME = config.get('db','dbname')
        self.USERNAME = config.get('db','username')
        self.PASSWORD = config.get('db','password')
        self.HOST = config.get('db','host')
        self.CONN = psycopg2.connect(dbname=self.DBNAME,user= self.USERNAME,host=self.HOST,password=self.PASSWORD)


    def sql_select_excute(self,sql_string):
        try:
            CURSOR = self.CONN.cursor()            
        except Exception as e:
            print(e)
        else:
            CURSOR.execute(sql_string)
            RESULT = CURSOR.fetchall()
            return RESULT         

    def sql_insert_excute(self,sql_string,sql_param):
        try:
            CURSOR = self.CONN.cursor()
        except Exception as e:
            print(e)
        else:
            CURSOR.execute(sql_string,sql_param)
            self.CONN.commit()
            return None
    
    def cursor_close(self):
        self.CONN.close()
        return None




            
'''   
    def select_item(self,):
        conn = db_conn()
        if not conn:
            return
        cur = conn.cursor()
        cur.execute(SETLECT_FUND_NAME)
        print(cur.fetchone())
        db_close(conn)

    def insert_item():
        conn = db_conn()
        if not conn:
            return
        cur = conn.cursor()
        cur.execute(INSERT_FUND_NAME)
        print(cur.fetchone())
        db_close(conn)

if __name__ == "__main__":
    sql_select_excute(self,"SELECT * FROM TB_FUND_NAME;")
    
'''

