# -*-coding:utf-8-*-

import pymssql
import shutil
import xlrd
import table
import logging


class Pro2mis:
    def __init__(self, ip, user, pwd, db):
        """
        :param ip: sql server ip
        :param user: sql server user
        :param pwd: sql server pwd
        :param db: sql server database,like "MIS"
        """
        self._log()
        self.pwd = pwd
        self.ip = ip
        self.user = user
        self.db = db
        self.table_list = []
        # self._connect_db()

    def _log(self):
        # 第一步，创建一个logger
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)  # Log等级总开关

        # 第二步，创建一个handler，用于写入日志文件
        self.logfile = r'./log/logger.txt'
        fh = logging.FileHandler(self.logfile, mode='w')
        fh.setLevel(logging.DEBUG)  # 输出到file的log等级的开关

        # 第三步，再创建一个handler，用于输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(logging.WARNING)  # 输出到console的log等级的开关

        # 第四步，定义handler的输出格式
        formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        # 第五步，将logger添加到handler里面
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    def _connect_db(self):
        try:
            self.conn = pymssql.connect(user=self.user, password=self.pwd, host=self.ip, database=self.db)
            self.cur = self.conn.cursor()
            self.logger.info('connected to sql server;')
        except Exception, e:
            self.logger.error('fail to connect to sql server:')
            self.logger.error(repr(e))

    def read_tables(self, excel_file):
        try:
            book = xlrd.open_workbook(excel_file)
            sheet0 = book.sheet_by_index(0)
            # print sheet0.nrows
            for i in range(1, sheet0.nrows):
                table1 = table.Table()
                table1.name = sheet0.row_values(i)[0]
                self.logger.info('reading ' + table1.name + ' info......')
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
            self.logger.info('total read ' + str(len(self.table_list)) + ' tables info;')
            self.logger.info('**************************************************')
            # print "read %s table information:" % len(self.table_list)
            for item in self.table_list:
                sheet_name = item.name
                try:
                    self.logger.info('reading ' + sheet_name + ' column info......')
                    item.read_columns(excel_file, sheet_name)
                    self.logger.info('read ' + sheet_name + ' column info success')
                except Exception, e:
                    self.logger.error('read ' + sheet_name + ' column info!')
        except Exception, e:
            self.logger.error('read table info!')
            self.logger.error(repr(e))

    def get_fmt_files(self, col_delimiter, row_delimiter, flag=0):
        for item in self.table_list:
            try:
                self.logger.info('**************************************************')
                self.logger.info('begin generate ' + item.name + ' fmt file.......')
                item.get_fmt(col_delimiter, row_delimiter, flag)
                self.logger.info('generate ' + item.name + '.fmt file success;')
            except Exception, e:
                self.logger.error('generate ' + item.name + '.fmt file;')
                self.logger.error(repr(e))

    def get_alter_table_sql(self, flag=0):
        for item in self.table_list:
            try:
                self.logger.info('**************************************************')
                self.logger.info('generate ' + item.name + ' sql str;')
                item.get_table_sql(flag)
                # self.logger.info('generate ' + item.name + ' sql str success;')
            except Exception, e:
                self.logger.error('generate ' + item.name + ' sql str!')
                self.logger.error(repr(e))

    # def __del__(self):
    #     self.logger.info('disconnect to sql server ......')
    #     self.cur.close()
    #     self.conn.close()
    #     self.logger.info('disconnected to sql server!')

    def alter_table(self, sql_str):
        '''
        insert row, delete row, alter column
        :param sql_str:
        :return:
        '''
        pre_query = "use %s;" % self.db
        query = pre_query + sql_str
        try:
            self.cur.execute(query)
            self.conn.commit()
            return 0
        except Exception, e:
            self.logger.error("fail to alter_table!")
            self.logger.error(repr(e))
            return -1

    def query_table(self, sql_str):
        '''
        select table, select row
        :param sql_str:
        :return:
        '''
        pre_query = "use %s;" % self.db
        query = pre_query + sql_str
        try:
            self.cur.execute(query)
            result = self.cur.fetchall()
            for row in result:
                print row
            return 0
        except Exception, e:
            self.logger.error('fail to query_table!')
            self.logger.error(repr(e))
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
            self.logger.error('fail to copy fmt file!')
            self.logger.error(repr(e))
            return -1


if __name__ == '__main__':
    proms = Pro2mis('127.0.0.1', 'misuser', '********', 'MIS')
    xlsfile = r'./xlsx/test.xlsx'
    proms.read_tables(xlsfile)
    proms.get_alter_table_sql(0)
    proms.get_fmt_files('!&', '\\n', 0)
