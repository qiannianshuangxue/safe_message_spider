# -*- coding: UTF-8 -*-
import os
import sys
import getopt
import requests
import random
import re
import json
import time
import html2text
import traceback
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse
useragents = [
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
    ]
headers = {
    'User-Agent': random.choice(useragents)
}
s=requests.Session()
pro_dir="./anquanke/"
if not os.path.exists(pro_dir):# 判断目录是否存在，不存在则创建新的目录
    os.makedirs(pro_dir)
dirs=os.listdir(pro_dir)
#moban="<p><a href=\"{}\" class=\"highslide-img\" onclick=\"return hs.expand(this);\" target=\"_blank\"></a></p>"
moban="<p><img class=\"alignnone size-full wp-image-252058 aligncenter\" alt=\"\" width=\"760\" height=\"506\" data-original=\"{}\" src=\"{}\" style=\"\"></p>"
article_type=["knowledge","news","activity","tool","job"]
def change(matched):
    #print("changed")
    return moban.format(matched.group(1),matched.group(1))
def anquanke_spider(url):
    ## 获取网页主体
    html = s.get(url,headers=headers).text
    #print(html)
    soup = BeautifulSoup(html,'html.parser')
    pwd = os.getcwd() # 获取当前的文件路径
    dirpath = pwd + '/anquanke/'
    if not os.path.exists(dirpath):
        os.makedirs(dirpath) 
    try:
        title = soup.find_all('title')[0].get_text()
        article = str(soup.find_all("div",class_="article-content")[0])
        #print(article)
        #article =re.sub("<p><img class=\"aligncenter\" alt=\"\" data-original=\"(.*)\"/></p>", change, article)
        #article =re.sub("<p><img alt=\"\" class=\"aligncenter\" data-original=\"(.*)\"/></p>", change, article)
        article =re.sub("<p><img.*data-original=\"(.*)\"/?></p>", change, article)
        title=title.replace('?','-').replace('*','-').replace('|','-').replace('=','-').replace(':','-').replace('\'','-').replace('"','-').replace('：','-').replace('】','-').replace('【','-').replace('/','-').replace('\\','-').replace('[','').replace(']','').replace('<','').replace('>','').replace('!','').replace('_','').replace(' ','').replace('-','')[0:254]
        write2md(dirpath,title,article)
    #print(html)
    except Exception as e:
    	print('traceback.print_exc():', traceback.print_exc())
    	print("url :",url)
    	return


def write2md(dirpath,title,article):
    ## 创建转换器
    h2md = html2text.HTML2Text()
    h2md.ignore_links = False
    ## 转换文档
    #print(article)
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
def get_num(article_type_1):
    out_json=requests.get('https://api.anquanke.com/data/v1/search?c='+article_type_1).text
    out_json=json.loads(out_json)
    num=out_json["total_count"]
    return num//1000
def get_article_id():
    file_url=open("anquanke_url.txt","a")
    num=get_num(article_type[0])
    for i in range(1,num+2):
        #print(i)
        out_json=requests.get('https://api.anquanke.com/data/v1/search?c='+article_type[0]+'&page='+str(i)+'&size=1000').text
        out_json=json.loads(out_json)
        for i in out_json['data']:
            url="https://www.anquanke.com/post/id/"+i['id']
            file_url.write(url+"\n")
            print(url)
            #anquanke_spider(url)

    print("爬取博文完毕\n------------------\n开始更改图床")
    file_url.close()
def get_article_md(org_count):
    
    file = open("anquanke_url.txt","r") 
    thread_pool_list = []         
    thread_pool=ThreadPoolExecutor(max_workers=3)                                        
    p_count=0
    for line in file.readlines()[p_count:]:
        line=line.strip('\n')
        try:
            #print(line)
            #xianzhi_spider(line)
            obj = thread_pool.submit(anquanke_spider, line)
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
        pic_list=re.findall(r"!\[\]\(.+?\)", text) #找到了所有文件
        for pic in pic_list:
            pic_url=pic[4:].split('\)')[0].replace(")","")
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
    img_path="./anquanke/img"
    thread_pool_download_pic_list = []         
    thread_pool_download_pic=ThreadPoolExecutor(max_workers=3)                                        
    p_count=0
    if(os.path.exists(img_path)):
        print("./anquanke/img文件夹已经存在-请先删除文件夹哦\n")
    else:
        print("./anquanke/img文件夹不存在-新建文件夹中ing\n")
        os.makedirs(img_path)
        print("./anquanke/img文件夹已经存在-正在更换图床\n")
        starttime= time.time()  
        for file in dirs:
            obj = thread_pool_download_pic.submit(get_pic, file)
            thread_pool_download_pic_list.append(obj) 
        for future in as_completed(thread_pool_download_pic_list):
            data = future.result()   
        endtime=time.time()                                                                                    
        print(endtime-starttime)  
if __name__ == '__main__':
    get_article_id()#获取对应类型文章的链接
    get_article_md(7000)
    get_all_pic()