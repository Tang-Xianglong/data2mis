# -*-coding:utf-8-*-
import xlrd
import logging


class Column:
    def __init__(self):
        self.name = None
        self.type = None
        self.length = None
        self.scale = None
        self.description = None


class Table:
    def __init__(self):
        self.column_list = []
        self.name = ''
        self.update_type = ''  # 增量，全量还是Merge
        self.is_have = ''  # 扩档还是新增
        self.ftp_area = ''
        self.target_server = ''
        self.insert_dt = ''
        self.file_date_diff = ''
        self.description = ''
        self.source_file = ''
        self.source_file_suffix = ''
        self.columns_num = ''
        self.db_name = ''

    def read_columns(self, excel_file, sheet_name):
        '''
        从版本表中读取字段信息
        :param excel_file: 整个版本要处理的表信息文件
        :param sheet_name: 某个表的名称
        :return:
        '''
        try:
            book = xlrd.open_workbook(excel_file)
            sheet0 = book.sheet_by_name(sheet_name)
            for i in range(1, sheet0.nrows):
                column = Column()
                column.name = sheet0.row_values(i)[0]
                column.type = sheet0.row_values(i)[1]
                column.length = int(sheet0.row_values(i)[2])
                column.scale = int(sheet0.row_values(i)[3])
                column.description = sheet0.row_values(i)[4]
                self.column_list.append(column)
            logging.info('read ' + self.name + ' columns success')
        except Exception, e:
            logging.error('fail to read ' + self.name + 'column info')
            logging.error(repr(e))

    def get_table_sql(self, flag=0):
        '''
        :param flag: =0 生成create table语句
                     =1 生成alter table语句
        '''
        pre_create_table = '\n'+'create table %s (\n' % self.name
        end_create_table = ');\n'
        pre_alter_table = '\n'+'alter %s add column:\n' % self.name
        end_alter_table = ';\n'
        table_sql_str = ''
        sql_file_name = r'./sql/' + self.name + r'.sql'
        sql_file = open(sql_file_name, 'w')
        if flag == 0:
            table_sql_str += pre_create_table
        else:
            table_sql_str += pre_alter_table
        if len(self.column_list) == 0:
            logging.warning('column list is null!')
            return
        for i in range(0, len(self.column_list)):
            column_type = self.column_list[i].type
            column_sql = ''
            if column_type in ('VARCHAR', 'varchar'):
                column_sql = self.column_list[i].name + ' ' + self.column_list[i].type + '(' \
                                       + str(self.column_list[i].length) + '),\n'
            elif column_type in ("DECIMAL", "decimal"):
                column_sql = self.column_list[i].name + ' ' + self.column_list[i].type + '(' \
                             + str(self.column_list[i].length + self.column_list[i].scale) + ', ' \
                             + str(self.column_list[i].scale) + '),\n'
            elif column_type in ('INT', 'int', 'DATETIME', 'datetime', 'DATE', 'date'):
                column_sql = self.column_list[i].name + ' ' + self.column_list[i].type + ',\n'
            else:
                logging.error('wrong type of column:' + self.column_list[i].name)
            table_sql_str += column_sql
        if flag == 0:
            table_sql_str += end_create_table
        else:
            table_sql_str += end_alter_table
        sql_file.write(table_sql_str)
        sql_file.close()
        logging.info('generate table ' + self.name + ' sql success, sql:'+table_sql_str)

    def get_fmt(self, col_delimiter, row_delimiter, flag=0):
        """
        :param col_delimiter: 列分隔符
        :param row_delimiter: 行分隔符
        :param flag: =0 非定长,不屏蔽filler
                     =1 非定长,屏蔽filler
                     =2 定长
        """
        row_del = row_delimiter
        col_del = col_delimiter
        str1 = "    SQLCHAR    0    0    \""
        str2 = "\"    "
        str3 = "        Chinese_PRC_Stroke_CI_AS\n"
        fmt_file_name = r'./fmt/' + self.name + r'.fmt'
        fmt_file = open(fmt_file_name, 'w')
        fmt_file.write('8.0\n')
        fmt_file.write(str(len(self.column_list)) + '\n')
        logging.info(self.name+'.fmt:')
        logging.info('8.0')
        logging.info(len(self.column_list))
        if flag == 0:
            for i in range(0, len(self.column_list) - 1):
                fmt_line = str(i + 1) + str1 + col_del + str2 + str(i + 1) + "        " + \
                           self.column_list[i].name + str3
                logging.info(fmt_line)
                fmt_file.write(fmt_line+'\n')
            fmt_final_line = str(len(self.column_list)) + str1 + row_del + str2 + str(len(self.column_list)) \
                             + "        " + self.column_list[-1].name + str3
            fmt_file.write(fmt_final_line + '\n')
            logging.info(fmt_final_line)
        elif flag == 1:
            for i in range(0, len(self.column_list) - 1):
                print str(i + 1) + str1 + col_del + str2 + str(i + 1) + "        " + self.column_list[i].name \
                      + str3
            print str(len(self.column_list)) + str1 + row_del + str2 + str(len(self.column_list)) + "        " \
                  + self.column_list[-1].name + str3
        elif flag == 2:
            for i in range(0, len(self.column_list) - 1):
                print str(i + 1) + str1 + col_del + str2 + str(i + 1) + "        " + self.column_list[i].name \
                      + str3
            print str(len(self.column_list)) + str1 + row_del + str2 + str(len(self.column_list)) + "        " \
                  + self.column_list[-1].name + str3
        fmt_file.close()
