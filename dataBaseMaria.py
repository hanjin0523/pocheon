import pymysql

class DatabaseMaria:

    def __init__(self, host, port, user, password, db, charset):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db = db
        self.charset = charset
    
    def connect_db(self):
        conn = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            db=self.db,
            charset=self.charset
        )
        return conn
    
    def operationCheckOn(self,):
        try:
            with self.connect_db() as conn:
                with conn.cursor() as cur:
                    sql = '''
                    INSERT INTO 
                        operationStatus 
                            (operation_start)
                    value (CURTIME())
                    '''
                    cur.execute(sql,)
                    conn.commit()
        except Exception as e:
            print("예외  :  ", str(e))

    def operationCheckOff(self,):
        try:
            with self.connect_db() as conn:
                with conn.cursor() as cur:
                    sql = '''
                    UPDATE 
                    operationStatus 
                    SET
                    operation_end = CURDATE();
                    '''
                    cur.execute(sql,)
                    conn.commit()
        except Exception as e:
            print("예외  :  ", str(e))