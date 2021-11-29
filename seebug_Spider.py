# -*- coding: UTF-8 -*-
import os
import sys
import getopt
import requests
import random
import re
import time
import json
import html2text
from bs4 import BeautifulSoup
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse
useragents = [ "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
        "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0);",
        "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)",
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
        "Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
        "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11",
        "Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; TencentTraveler 4.0)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; The World)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Avant Browser)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36"
        "Mozilla/5.0 (X11; Linux x86_64; rv:76.0) Gecko/20100101 Firefox/76.0"]

headers = {'User-Agent': random.choice(useragents)}
s=requests.Session()
def seebug_spider(url):
    ## 获取网页主体
    #print(url)
    html = s.get(url,headers=headers).text
    soup = BeautifulSoup(html,'html.parser')
    pwd = os.getcwd() # 获取当前的文件路径
    dirpath = pwd + '/seebug/'
    if not os.path.exists(dirpath):
        os.makedirs(dirpath) 
    try:
	    title = soup.find_all('title')[0].get_text()
	    article = str(soup.find_all("section",class_="post-content")[0])
	    #print(article)
	    title=title.replace('?','-').replace('*','-').replace('|','-').replace('=','-').replace(':','-').replace('\'','-').replace('"','-').replace('：','-').replace('】','-').replace('【','-').replace('/','-').replace('\\','-').replace('[','').replace(']','').replace('<','').replace('>','').replace('!','').replace('_','').replace(' ','').replace('-','')[0:254]
	    write2md(dirpath,title,article)
	    #time.sleep(1)
    #print(html)
    except Exception as e:
    	raise e
    	return


def write2md(dirpath,title,article):
    ## 创建转换器
    h2md = html2text.HTML2Text()
    h2md.ignore_links = False
    ## 转换文档
    article = h2md.handle(article)
    ## 写入文件
    if not os.path.exists(dirpath):# 判断目录是否存在，不存在则创建新的目录
        os.makedirs(dirpath)
    # 创建md文件
    with open(dirpath+title+'.md','w',encoding="utf8") as f:
        lines = article.splitlines()
        for line in lines:
            if line.endswith('-'):
                f.write(line)
            else:
                f.write(line+"\n")
    print(title+"下载完成....")


    
def get_article_id():
    file_url=open("seebug_url.txt","a")
    for i in range(26,1741):
        try:
            file_url.write("https://paper.seebug.org/"+str(i)+"/"+"\n")
        except:
            pass
        #time.sleep(random.randint(0,3))
    print("爬取博文完毕\n------------------\n开始更改图床")
    file_url.close()

def get_article_md(org_count):
    
    file = open("seebug_url.txt","r") 
    thread_pool_list = []         
    thread_pool=ThreadPoolExecutor(max_workers=3)                                        
    p_count=0
    for line in file.readlines()[p_count:]:
        line=line.strip('\n')
        try:
            #print(line)
            #xianzhi_spider(line)
            obj = thread_pool.submit(seebug_spider, line)
            thread_pool_list.append(obj)
            p_count=p_count+1
            if p_count==org_count:
                break
        except Exception as e:
            print('traceback.print_exc():', traceback.print_exc())
    file.close()

    starttime= time.time()                                                                            
    for future in as_completed(thread_pool_list):
        data = future.result()                                                                                    
    endtime=time.time()                                                                                    
    print(endtime-starttime)   
    print("爬取博文完毕\n------------------\n开始更改图床")

def model_picture_download(model_picture_url, file_dir,text,new_pic):
    headers = {
        'User-Agent': random.choice(useragents)
    }
    model_picture_downloaded = False
    err_status = 0
    while model_picture_downloaded is False and err_status < 10:
        try:
            html_model_picture = s.get(
                model_picture_url,headers=headers, timeout=1)
            with open(file_dir, 'wb') as file:
                file.write(html_model_picture.content)
                model_picture_downloaded = True
                text=text.replace(model_picture_url,"./img/"+new_pic)
                print('下载成功！图片 = ')
                return text
        except Exception as e:
            err_status += 1
            random_int = 1
            time.sleep(random_int)
            print(e)
            print('出现异常！睡眠 ' + str(random_int) + ' 秒')
            return text
        continue
    return text

def get_pic(file):
    if file!="img":
        f=open(pro_dir+file,"r+",encoding='utf-8')
        text=f.read()
        f.close()
        print(file)
        #print(text)
        pic_list=re.findall(r"!\[.*\]\(.+?\)", text) #找到了所有文件
        for pic in pic_list:
            #pic_url=pic[4:].split('\)')[0].replace(")","")
            #pic_url=pic.split('(')[1].replace(")","")
            pic_url=re.match(r"!\[.*\]\((.+?)\)",pic)
            pic_url=pic_url.group(1)
            print(pic_url)
            if pic_url.startswith("./img/")==0:
                new_pic=str(hash(pic_url))+'.png'
                new_pic=new_pic.replace("-","")
                try:
                    text=model_picture_download(pic_url, pro_dir+'img/'+new_pic,text,new_pic)
                    print(pic_url)
                    print(new_pic)
                except Exception as e:
                    pass
                continue
         
        f=open(pro_dir+file,"w+",encoding='utf-8')
        f.write(text)
        f.close()

def get_all_pic():
    print("正在更换图床\n")
    img_path="./seebug/img"
    thread_pool_download_pic_list = []         
    thread_pool_download_pic=ThreadPoolExecutor(max_workers=3)                                        
    p_count=0
    if(os.path.exists(img_path)):
        print("./seebug/img文件夹已经存在-请先删除文件夹哦\n")
    else:
        print("./seebug/img文件夹不存在-新建文件夹中ing\n")
        os.makedirs(img_path)
        print("./seebug/img文件夹已经存在-正在更换图床\n")
        starttime= time.time()  
        for file in dirs:
            obj = thread_pool_download_pic.submit(get_pic, file)
            thread_pool_download_pic_list.append(obj) 
        for future in as_completed(thread_pool_download_pic_list):
            data = future.result()   
        endtime=time.time()                                                                                    
        print(endtime-starttime)  

if __name__ == '__main__':
    get_article_id()
    pro_dir="./seebug/"
    if not os.path.exists(pro_dir):# 判断目录是否存在，不存在则创建新的目录
        os.makedirs(pro_dir)
    dirs=os.listdir(pro_dir)
    
    get_article_md(2000)
    get_all_pic()
