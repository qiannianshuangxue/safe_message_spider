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
def freebuf_spider(url):
    ## 获取网页主体
    #print(url)
    html = s.get(url,headers=headers).text
    soup = BeautifulSoup(html,'html.parser')
    pwd = os.getcwd() # 获取当前的文件路径
    dirpath = pwd + '/freebuf/'
    if not os.path.exists(dirpath):
        os.makedirs(dirpath) 
    try:
	    title = soup.find_all('title')[0].get_text()
	    article = str(soup.find_all("div",id="tinymce-editor")[0])
	    #print(article)
	    title=title.replace('?','-').replace('*','-').replace('|','-').replace('=','-').replace(':','-').replace('\'','-').replace('"','-').replace('：','-').replace('】','-').replace('【','-').replace('/','-').replace('\\','-').replace('[','').replace(']','').replace('<','').replace('>','').replace('!','').replace('_','').replace(' ','').replace('-','')[0:254]
	    write2md(dirpath,title,article)
	    time.sleep(1)
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

def get_num(year):
    out_json=s.get("https://search.freebuf.com/search/find/?year="+str(year)+"&articleType=%E5%85%B6%E4%BB%96%2C%E5%AE%B9%E5%99%A8%E5%AE%89%E5%85%A8%2C%E7%BD%91%E7%BB%9C%E5%AE%89%E5%85%A8%2C%E6%95%B0%E6%8D%AE%E5%AE%89%E5%85%A8%2C%E5%B7%A5%E6%8E%A7%E5%AE%89%E5%85%A8%2C%E7%BB%88%E7%AB%AF%E5%AE%89%E5%85%A8%2C%E7%B3%BB%E7%BB%9F%E5%AE%89%E5%85%A8%2C%E4%BC%81%E4%B8%9A%E5%AE%89%E5%85%A8%2C%E6%97%A0%E7%BA%BF%E5%AE%89%E5%85%A8%2CWEB%E5%AE%89%E5%85%A8%2C%E6%BC%8F%E6%B4%9E%2C%E5%B7%A5%E5%85%B7&time=0&tabType=1&content=&page=1",headers=headers).text
    out_json=json.loads(out_json)
    totalPage=out_json['data']['totalPage']
    return totalPage
    
def get_article_id(year):
    file_url=open("freebuf_url.txt","a")
    num=get_num(year)
    print(num)
    for i in range(1,num+1):
        #print(i)
        out_json=s.get("https://search.freebuf.com/search/find/?year="+str(year)+"&articleType=%E5%85%B6%E4%BB%96%2C%E5%AE%B9%E5%99%A8%E5%AE%89%E5%85%A8%2C%E7%BD%91%E7%BB%9C%E5%AE%89%E5%85%A8%2C%E6%95%B0%E6%8D%AE%E5%AE%89%E5%85%A8%2C%E5%B7%A5%E6%8E%A7%E5%AE%89%E5%85%A8%2C%E7%BB%88%E7%AB%AF%E5%AE%89%E5%85%A8%2C%E7%B3%BB%E7%BB%9F%E5%AE%89%E5%85%A8%2C%E4%BC%81%E4%B8%9A%E5%AE%89%E5%85%A8%2C%E6%97%A0%E7%BA%BF%E5%AE%89%E5%85%A8%2CWEB%E5%AE%89%E5%85%A8%2C%E6%BC%8F%E6%B4%9E%2C%E5%B7%A5%E5%85%B7&time=0&tabType=1&content=&page="+str(i),headers=headers).text
        out_json=json.loads(out_json)
        for i in out_json['data']['list']:
            try:
                url=i['url']
                file_url.write(url+"\n")
            except:
                pass
        time.sleep(random.randint(0,3))
    print("爬取博文完毕\n------------------\n开始更改图床")
    file_url.close()

def get_article_md(org_count):
    
    file = open("freebuf_url.txt","r") 
    thread_pool_list = []         
    thread_pool=ThreadPoolExecutor(max_workers=2)                                        
    p_count=0
    for line in file.readlines()[p_count:]:
        line=line.strip('\n')
        try:
            #print(line)
            #xianzhi_spider(line)
            obj = thread_pool.submit(freebuf_spider, line)
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
    img_path="./freebuf/img"
    thread_pool_download_pic_list = []         
    thread_pool_download_pic=ThreadPoolExecutor(max_workers=3)                                        
    p_count=0
    if(os.path.exists(img_path)):
        print("./freebuf/img文件夹已经存在-请先删除文件夹哦\n")
    else:
        print("./freebuf/img文件夹不存在-新建文件夹中ing\n")
        os.makedirs(img_path)
        print("./freebuf/img文件夹已经存在-正在更换图床\n")
        starttime= time.time()  
        for file in dirs:
            obj = thread_pool_download_pic.submit(get_pic, file)
            thread_pool_download_pic_list.append(obj) 
        for future in as_completed(thread_pool_download_pic_list):
            data = future.result()   
        endtime=time.time()                                                                                    
        print(endtime-starttime)  

if __name__ == '__main__':
    get_article_id(2018)
    get_article_id(2019)
    get_article_id(2020)
    get_article_id(2021)
    pro_dir="./freebuf/"
    if not os.path.exists(pro_dir):# 判断目录是否存在，不存在则创建新的目录
        os.makedirs(pro_dir)
    dirs=os.listdir(pro_dir)
    
    get_article_md(8000)
    get_all_pic()
