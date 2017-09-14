#2017年08月19日16:18:20
#liuxn
#博客园个人博客列表


import urllib.request
import re
import time
import hashlib
import configparser

import store

class Bky_blog_list(object):

    def __init__(self,username):
        self.username = username
        #http://www.cnblogs.com/用户名/default.html?page=1
        self.base_url = "http://www.cnblogs.com/%s/default.html?page=" % username
        self.enable = True
        self.page_num = 0
        self.article_num = 0
        self.fail_num = 0

        #读取配置文件
        conf = configparser.ConfigParser()
        conf.read('SETTING.conf')
        self.db_url = conf.get('db','db_url')
        self.db_user = conf.get('db','db_user')
        self.db_password = conf.get('db','db_password')
        self.db_name = conf.get('db','db_name')
        self.table_name = conf.get('db','table_name')
        self.crawl_delay = conf.getint('constants','crawl_delay')


    def download(self,url):
        response = urllib.request.urlopen(url)
        resp_str = response.read().decode('utf-8')
        return resp_str

    def get_page(self,url):
        resp_str = self.download(url)
        print("获取url:%s页面完成" % url)
        #(文章url，文章title,发布时间，阅读数量，评论数量)
        pattern = re.compile('<div class="postTitle">.*?class="postTitle2" href="(.*?)">(.*?)</a>.*?<div class="postDesc">.*?posted @ (.*?) %s 阅读\((.*?)\) 评论\((.*?)\)' % self.username,re.S)
        # print(pattern)
        find_results = re.findall(pattern,resp_str)
        print("解析文章数据完成！")
        print("解析出的文章个数 %d" % len(find_results))
        next_p = re.compile(r'<div class="topicListFooter".*?<a href="(.*?)">下一页</a>',re.S)
        next_r = re.search(next_p,resp_str)
        print("解析下一页数据完成！")
        # print(next_r)
        if not next_r:
            print("检测无下一页")
            self.enable = False

        for item in find_results:
            # print(item)
            md5 = hashlib.md5()
            md5.update(item[0].encode('utf-8'))
            self.article_num += 1
            data = {
                'hd':md5.hexdigest(),
                'title_url':item[0],
                'title':item[1],
                'post_date':item[2],
                'view_num':item[3],
                'comment_num':item[4],
                'username':self.username
            }
            result = store.Store.insert_mysql(self.db_url,self.db_user,self.db_password,self.db_name,self.table_name,data)
            if result and result == 'Success':
                print("文章 '{title}' 保存成功！" .format(title=data.get('title')))
            else:
                print("文章 '{title}' 保存失败！，失败原因为：{reason}" .format(title=data.get('title'),reason=result))
                self.fail_num += 1


    def begin(self):
        print("开始爬取，用户名为：%s" % self.username)
        while True:
            if self.enable:
                self.page_num += 1
                url = self.base_url + str(self.page_num)
                print("正在爬取第%d页，爬取的url为：%s" % (self.page_num,url))
                self.get_page(url)
                time.sleep(self.crawl_delay)
            else:
                print("无下一页！爬取的总页数为:%d ， 文章总数为：%d, 保存失败个数：%d" % (self.page_num,self.article_num,self.fail_num))
                break
        print("爬取结束！")



if __name__ == "__main__":
    username = input("请输入博客用户名：")
    bky_user_blog_list = Bky_blog_list(username)
    bky_user_blog_list.begin()
    print("程序结束！")