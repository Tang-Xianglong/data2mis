# -*-coding:utf-8-*-

import pymssql
import shutil
import xlrd
import table


class Pro2mis:
    def __init__(self, ip, user, pwd, db):
        """

        :param ip: sql server ip
        :param user: sql server user
        :param pwd: sql server pwd
        :param db: sql server database,like "MIS"
        """
        self.pwd = pwd
        self.ip = ip
        self.user = user
        self.db = db
        self._connect_db()
        self.table_list = []

    def _connect_db(self):
        try:
            self.conn = pymssql.connect(user=self.user, password=self.pwd, host=self.ip,database=self.db)
            self.cur = self.conn.cursor()
            print "connected to sql server\n-----------------------\n"
            return 0
        except Exception, e:
            print "ERROR: fail to connect to sql server"
            print 'repr(e):\t', repr(e)
            return -1

    def read_tables(self, excel_file):
        try:
            book = xlrd.open_workbook(excel_file)
            sheet0 = book.sheet_by_index(0)
            for i in range(0, sheet0.nrows):
                table1 = table.Table()
                table1.name = sheet0.row_values(i)[0]
                table1.description = sheet0.row_values(i)[1]
                table1.source_file = sheet0.row_values(i)[2]
                table1.source_file_suffix = sheet0.row_values(i)[3]
                table1.is_have = sheet0.row_values(i)[4]
                table1.update_type = sheet0.row_values(i)[5]
                table1.ftp_area = sheet0.row_values(i)[6]
                table1.file_date_diff = sheet0.row_values(i)[7]
                table1.target_server = sheet0.row_values(i)[8]
                table1.db_name = sheet0.row_values(i)[9]
                self.table_list.append(table1)
            print "read %s table information:" % len(self.table_list)
            for item in self.table_list:
                sheet_name = item.name
                print sheet_name
                item.read_columns(excel_file, sheet_name)
            return 0
        except Exception, e:
            print "ERROR:read table information"
            print 'repr(e):\t', repr(e)
            return -1

    def get_fmt_files(self, col_delimiter, row_delimiter):
        try:
            for item in self.table_list:
                print "generate %s fmt file" % item.name
                item.get_fmt(col_delimiter, row_delimiter)
            return 0
        except Exception, e:
            print "ERROR:generate fmt file"
            print 'repr(e):\t', repr(e)
            return -1

    def get_alter_table_sql(self):
        for item in self.table_list:
            print "generate %s alter table file" % item.name
            item.get_create_table_sql()

    def __del__(self):
        self.cur.close()
        self.conn.close()

    def alter_table(self, sql_str):
        '''
        insert row, delete row, alter column
        :param sql_str:
        :return:
        '''
        pre_query = "use %s;" % self.db
        query = pre_query+sql_str
        try:
            self.cur.execute(query)
            self.conn.commit()
            return 0
        except Exception, e:
            print "ERROR:fail to alter table"
            print 'repr(e):\t', repr(e)
            return -1

    def query_table(self, sql_str):
        '''
        select table, select row
        :param sql_str:
        :return:
        '''
        pre_query = "use %s;" % self.db
        query = pre_query+sql_str
        try:
            self.cur.execute(query)
            result = self.cur.fetchall()
            for row in result:
                print row
            return 0
        except Exception, e:
            print "ERROR:fail to query table"
            print 'repr(e):\t', repr(0)
            return -1

    def copy_fmt(self, source, dest_dir):
        '''
        copy fmt file!
        :param source: r"E:\01\readme.fmt"
        :param dest_dir: r"E:\01\02\\"
        :return:
        '''
        try:
            shutil.copy(source, dest_dir)
            return 0
        except Exception, e:
            print "ERROR:copy fmt file"
            print 'repr(e):\t', repr(0)
            return -1


if __name__ == '__main__':
    proms = Pro2mis('127.0.0.1', 'misuser', '********', 'MIS')
    xlsfile = r'test.xls'
    proms.read_tables(xlsfile)
    proms.get_alter_table_sql()
