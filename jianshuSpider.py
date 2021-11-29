import os
import sys
import getopt
import requests
import random
import re
import json
import time
import html2text
import argparse
from bs4 import BeautifulSoup

useragents = [
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
    ]
print("------------------\n标准姿势python jianshuSpider.py -s CTF -c 2 -p 1 \n表示查找CTF关键字（必须）+需要2篇文章（默认5）+需要本地图床（默认不需要为0）\n------------------\n")

ap = argparse.ArgumentParser()
#自定义参数（简写，全写，是否必需，说明）
ap.add_argument("-s","--search",required = False, help = "你要搜索的关键字",default='CTF')
ap.add_argument("-c","--count",required = False, help = "你要搜索的文章数目。默认5",default='5')
ap.add_argument("-p","--is_need_pic",required = False, help = "是否需要图床",default=0)
#python demo.py -s CTF -c 2 -p 1
#获取所有的参数
args = vars(ap.parse_args())
print("------------------\n你要爬取的关键字是: "+args['search']+",数目是："+args['count'],end="")
serach_word=args['search']
org_count=int(args['count'])
page_count=int(org_count/10+1)
is_need_pic=int(args['is_need_pic'])
if is_need_pic==0 :
   print(", 而且你不需要本地图床~")
else:
   print(", 而且你需要本地图床~")


def jianshu(url):
    ## 浏览器头部
    headers = {
        'Host': 'www.jianshu.com',
        'Referer': 'https://www.jianshu.com/',
        'User-Agent': random.choice(useragents)
    }
    ## 获取网页主体
    html = requests.get(url,headers=headers).text

    ## bs4
    soup = BeautifulSoup(html,"html.parser")
    try:
        title = soup.find_all("title")[0].get_text()
        #print("title:"+title)
        article = str(soup.find_all("script", id='__NEXT_DATA__')[0].get_text())
        article_json = json.loads(article)
        ## 替图片的src加上https://方便访问
        #print(type(article_json))
        new_article=str(article_json["props"]["initialState"]["note"]["data"]["free_content"])
        new_article = re.sub('(src=")|(data-original-src=")','src="https:',new_article)
        new_article="# "+title+"\n"+new_article
        ## 写入文件
        pwd = os.getcwd() # 获取当前的文件路径
        dirpath = pwd + '/jianshu/'
        title=title.replace('*','?').replace('*','-').replace('|','-').replace('=','-').replace(':','-').replace('\'','-').replace('"','-').replace('：','-').replace('】','-').replace('【','-').replace('/','-').replace('\\','-').replace('[','').replace(']','').replace('<','').replace('>','').replace('!','').replace('_','').replace(' ','').replace('-','')[0:30]
        write2md(dirpath,title,new_article)
    except Exception as e:
        print("error")


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


def get_page_url(question,page_id):
    global x
    ses = requests.Session()
    headers = {
        'Host': 'www.jianshu.com',
        'Referer': 'https://www.jianshu.com/',
        'User-Agent': random.choice(useragents),
    }
    #url="https://www.jianshu.com/search/do?q="+question+"&type=note&page="+str(page_id)+"&order_by=default"
    url="https://www.jianshu.com/search/do?q="+question+"&type=note&page="+str(page_id)+"&order_by=default"
    one_text=ses.get("https://www.jianshu.com/search?q="+question+"&page="+str(page_id)+"&type=note",headers=headers)
    #print(one_text.text)
    ## 浏览器头部
    s=ses.post(url,headers=headers)
    #print(s.text)
    text=s.content.decode('utf-8')
    tmp = json.loads(text)
    obj_url=''
    try:
        print("搜索的url:+"+url)
        for i in range(0,10):
            #print(tmp)
            obj_num=tmp['entries'][i]['slug']
            obj_url='https://www.jianshu.com/p/'+obj_num
            print("第"+str(page_id)+"页的"+"第"+str(i+1)+"篇文章的page_url： "+ obj_url)
            #print("------写入文件开始---------")
            f=open("url_list.txt","a+")
            f.write(obj_url+"\n")
            f.close()
            #time.sleep(1)
        x=x+1
    except KeyError as e:
        #raise e
        print('暂时被ban了~继续搜冲就完事了>_<\n')
    except IndexError as e:
        print('索引错误')
    except TypeError as e:
        print('类型错误')
    except ValueError as e:
        print('值的类型错误')
    except Exception as e:
        print('错误')
    return obj_url
def model_picture_download(model_picture_url, file_dir,text,new_pic,pic_url):
    headers = {
        'User-Agent': random.choice(useragents)
    }
    model_picture_downloaded = False
    err_status = 0
    while model_picture_downloaded is False and err_status < 10:
        try:
            html_model_picture = requests.get(
                model_picture_url,headers=headers, timeout=1)
            with open(file_dir, 'wb') as file:
                file.write(html_model_picture.content)
                model_picture_downloaded = True
                text=text.replace(pic_url,"./img/"+new_pic)
                print('下载成功！图片 = ')
                return text
        except Exception as e:
            err_status += 1
            random_int = 4
            time.sleep(random_int)
            print(e)
            print('出现异常！睡眠 ' + str(random_int) + ' 秒')
            return text
        continue
    return text

x=1
def main():
    print("\n-------------------开始爬取链接-------------------")
    f=open("url_list.txt","w")
    f.close()
    global x
    global page_count
    global org_count
    global serach_word
    while x<page_count+1:
        get_page_url(serach_word,x)
        #time.sleep(2)
    print("\n-------------------开始爬取文章内容-------------------")
    file = open("url_list.txt") 
    p_count=0
    for line in file.readlines():
        line=line.strip('\n')
        try:
            #print(line)
            jianshu(line)
            p_count=p_count+1
            if p_count==org_count:
                break
        except Exception as e:
            print("error")
    file.close()
    pro_dir="./jianshu/"
    dirs=os.listdir(pro_dir)
    if is_need_pic==0 :
       print("------------------\n你选择了不需要本地图床哦本次服务到此结束")
    else:
       print("正在更换图床\n")
       img_path="./jianshu/img"
       if(os.path.exists(img_path)):
          print("./jianshu/img文件夹已经存在-请先删除文件夹哦\n")
       else:
          print("./jianshu/img文件夹不存在-新建文件夹中ing\n")
          os.makedirs(img_path)
          print("./jianshu/img文件夹已经存在-正在更换图床\n")
          for file in dirs:
             if file!="img":
                f=open(pro_dir+file,"r+",encoding='utf-8')
                text=f.read()
                f.close()
                print(file)
                #print(text)
                pic_list=re.findall(r"!\[\]\(.+?\)", text) #找到了所有文件
                for pic in pic_list:
                   pic_url=pic[4:].split('\)')[0].replace(")","")
                   #print(pic_url)
                   new_pic=str(hash(pic_url))+'.png'
                   new_pic=new_pic.replace("-","")
                   try:
                      text=model_picture_download(pic_url, pro_dir+'img/'+new_pic,text,new_pic,pic_url)
                      print(pic_url)
                      print(new_pic)
                   except Exception as e:
                      print(e)
                   continue
                   
                f=open(pro_dir+file,"w+",encoding='utf-8')
                f.write(text)
                f.close()
    os.remove("url_list.txt")

if __name__ == "__main__":
    main()