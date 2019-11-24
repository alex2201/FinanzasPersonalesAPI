import pyodbc


class SQLServerDBConn:
    def __enter__(self):
        # self.cnxn = pyodbc.connect(
        #     'DRIVER={ODBC Driver 17 for SQL Server};'
        #     'SERVER=appsmx-development.database.windows.net;'
        #     'DATABASE=PersonalFinance;'
        #     'UID=AppsMxMaster;'
        #     'PWD=appsmx.1234')

        self.cnxn = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=tcp:192.168.1.98,49172;'
            'DATABASE=PersonalFinance;'
            'UID=sa;'
            'PWD=admin.1234')

        return self.cnxn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cnxn.close()


__all__ = ['SQLServerDBConn']
