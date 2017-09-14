#持久化工具类

'''
问题：
    bug1:不能保存字符串中带有英文双引号的值
    2017年08月27日14:05:58
    bug1:已解决
    2017年09月14日10:58:15

'''

import pymysql


class Store(object):

    @staticmethod
    def insert_mysql(url,user,password,db_name,table_name,data):
        try:
            db = pymysql.connect(url ,user ,password ,db_name ,use_unicode=True ,charset='utf8')
            cursor = db.cursor()
            fields = ','.join(data.keys())
            values = ','.join(['%s'] * len(data))
            sql = 'INSERT INTO {table}({fields}) VALUES({values}) ON DUPLICATE KEY UPDATE '.format(table = table_name,fields = fields,values = values)
            update = ','.join([' {key} = %s'.format(key = key) for key in data])
            sql += update
            # print(sql)
            try:
                cursor.execute(sql,tuple(data.values()) * 2)
                db.commit()
                result = 'Success'
            except pymysql.err.Error as e:
                db.rollback()
                result = repr(e)
            finally:
                db.close()
            return result
        except Exception as e2:
            return repr(e2)


