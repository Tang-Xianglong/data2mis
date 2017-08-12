# -*-coding:utf-8-*-
import xlrd


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
        self.name = None
        self.update_type = None  # 增量，全量还是Merge
        self.is_have = None  # 扩档还是新增
        self.ftp_area = None
        self.target_server = None
        self.insert_dt = None
        self.file_date_diff = None
        self.description = None
        self.source_file = None
        self.source_file_suffix = None
        self.columns_num = None
        self.db_name = None

    # def read_tables(self, excel_file):
    #     book = xlrd.open_workbook(excel_file)
    #     sheet0 = book.sheet_by_index(0)
    #     row_data = sheet0.row_values(0)

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
            print "read %s columns success" % self.name
        except Exception, e:
            print "ERROR:read column information"
            print 'repr(e):\t', repr(e)

    def get_create_table_sql(self):
        for i in range(0, len(self.column_list)):
            if self.column_list[i].type == 'VARCHAR':
                print self.column_list[i].name + ' ' + self.column_list[i].type + '(' \
                      + str(self.column_list[i].length) + '),'
            elif self.column_list[i].type == 'INT':
                print self.column_list[i].name + ' ' + self.column_list[i].type + ','

    def get_fmt(self, col_delimiter, row_delimiter):
        row_del = row_delimiter
        col_del = col_delimiter
        str1 = "    SQLCHAR    0    0    \""
        str2 = "\"    "
        str3 = "        Chinese_PRC_Stroke_CI_AS\n"
        print '8.0'
        print len(self.column_list)
        for i in range(0, len(self.column_list) - 1):
            print str(i + 1) + str1 + col_del + str2 + str(i + 1) + "        " + self.column_list[i].name \
                  + str3
        print str(len(self.column_list)) + str1 + row_del + str2 + str(len(self.column_list)) + "        " \
              + self.column_list[-1].name + str3


if __name__ == '__main__':
    xlsfile = r'test.xls'
    table = Table()
    table.read_columns(xlsfile)
    # table.get_create_table_sql()
    table.get_fmt('!&', '\\n')
