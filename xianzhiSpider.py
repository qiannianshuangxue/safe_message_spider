# -*- coding: UTF-8 -*-
import os
import sys
import getopt
import requests
import random
import re
import time
import html2text
from bs4 import BeautifulSoup
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
useragents = [
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
    ]
#初始化
print("------------------\n标准姿势python xianzhiSpider.py -s CTF -c 2 -p 1 \n表示查找CTF关键字（必须）+需要2篇文章（默认30）+需要本地图床（默认不需要为0）\n------------------\n")

ap = argparse.ArgumentParser()
#自定义参数（简写，全写，是否必需，说明）
ap.add_argument("-s","--search",required = False, help = "你要搜索的关键字",default='')
ap.add_argument("-c","--count",required = False, help = "你要搜索的文章数目。默认30",default='30')
ap.add_argument("-p","--is_need_pic",required = False, help = "是否需要图床",default=0)
#python demo.py -s CTF -c 2 -p 1
#获取所有的参数
args = vars(ap.parse_args())
print("------------------\n你要爬取的关键字是: "+args['search']+",数目是："+args['count'],end="")
serach_word=args['search']
org_count=int(args['count'])
page_count=int(org_count/30+1)
is_need_pic=int(args['is_need_pic'])
if is_need_pic==0 :
   print(", 而且你不需要本地图床~")
else:
   print(", 而且你需要本地图床~")
headers = {
    'User-Agent': random.choice(useragents),
    'Cookie': ""#浏览器F12粘贴
}
# print(serach_word)
# print(count)
# print(pic)
#下载对应的链接

#print("------------------\n开始爬取要下载的url存放在->url_list.txt\n")

s=requests.Session()

f=open("url_list.txt","w",encoding="utf-8")

for i in range(1,page_count+1):
    url="https://xz.aliyun.com/search?keyword="+serach_word+"&page="+str(i)
    print(url)
    html = s.get(url,headers=headers).text
    print(html)
    url_list = re.findall(r"\"topic-title\" href=\".+?\">", html)
    for i in url_list:
        rel_url="https://xz.aliyun.com"+i[20:].split('"')[0]
        print(rel_url)
        f.write(rel_url+"\n")
f.close()

print("爬取链接完毕\n------------------\n开始爬取博文")

def xianzhi_spider(url):
    ## 获取网页主体
    html = s.get(url,headers=headers).text
    soup = BeautifulSoup(html,'html.parser')
    pwd = os.getcwd() # 获取当前的文件路径
    dirpath = pwd + '/xianzhi/'
    if not os.path.exists(dirpath):
        os.makedirs(dirpath) 
    try:
	    title = soup.find_all('title')[0].get_text()
	    article = str(soup.find_all("div",class_="topic-content markdown-body")[0])
	    #print(article)
	    title=title.replace('?','-').replace('*','-').replace('|','-').replace('=','-').replace(':','-').replace('\'','-').replace('"','-').replace('：','-').replace('】','-').replace('【','-').replace('/','-').replace('\\','-').replace('[','').replace(']','').replace('<','').replace('>','').replace('!','').replace('_','').replace(' ','').replace('-','')[0:250]
	    write2md(dirpath,title,article)
    #print(html)
    except Exception as e:
    	print('发生错误')
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

file = open("url_list.txt") 
thread_pool_list = []         
thread_pool=ThreadPoolExecutor(max_workers=3)                                        
p_count=0
for line in file.readlines()[p_count:]:
    line=line.strip('\n')
    try:
        #print(line)
        #xianzhi_spider(line)
        obj = thread_pool.submit(xianzhi_spider, line)
        thread_pool_list.append(obj)
        p_count=p_count+1
        if p_count==org_count:
            break
    except Exception as e:
    	print("error")
file.close()

starttime= time.time()                                                                            
for future in as_completed(thread_pool_list):
    data = future.result()                                                                                    
endtime=time.time()                                                                                    
print(endtime-starttime)   


print("爬取博文完毕\n------------------\n开始更改图床")

pro_dir="./xianzhi/"
if not os.path.exists(pro_dir):# 判断目录是否存在，不存在则创建新的目录
    os.makedirs(pro_dir)
dirs=os.listdir(pro_dir)
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
            

if is_need_pic==0 :
    print("------------------\n你选择了不需要本地图床哦本次服务到此结束")
else:
    print("正在更换图床\n")
    img_path="./xianzhi/img"
    thread_pool_download_pic_list = []         
    thread_pool_download_pic=ThreadPoolExecutor(max_workers=3)                                        
    p_count=0
    if(os.path.exists(img_path)):
        print("./xianzhi/img文件夹已经存在-请先删除文件夹哦\n")
    else:
        print("./xianzhi/img文件夹不存在-新建文件夹中ing\n")
        os.makedirs(img_path)
        print("./xianzhi/img文件夹已经存在-正在更换图床\n")
        starttime= time.time()  
        for file in dirs:
            obj = thread_pool_download_pic.submit(get_pic, file)
            thread_pool_download_pic_list.append(obj) 
        for future in as_completed(thread_pool_download_pic_list):
            data = future.result()   
        endtime=time.time()                                                                                    
        print(endtime-starttime)  


os.remove("url_list.txt")