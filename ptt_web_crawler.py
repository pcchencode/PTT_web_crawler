import re
import requests
from bs4 import BeautifulSoup #install bs4, install lxml
import pandas as pd
import datetime as dt
import random
import time 
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import argparse


def get_post_data(post_url):
    payload={
    'from':'/bbs/'+ 'Gossiping' +'/index.html',
    'yes':'yes' 
    }

    #破除18歲的限制
    rs = requests.session()
    req = rs.post('https://www.ptt.cc/ask/over18',verify = False, data = payload)
    req = rs.get('https://www.ptt.cc/bbs/'+ 'Gossiping' +'/index.html',verify = False)
    req = rs.get(post_url, verify=False)

    if req.status_code==200:
        web_content = req.text
        #以美味湯解析html
        soup = BeautifulSoup(web_content, 'lxml')
        main_content = soup.find('div',id="main-content")
        metas = main_content.select('div.article-metaline')

        author = metas[0].select('span.article-meta-value')[0].text
        title = metas[1].select('span.article-meta-value')[0].text
        post_date = metas[2].select('span.article-meta-value')[0].text
        author_ID = author.split('(',1)[0].replace(' ','')
        author_name = author.split('(',1)[1].replace(')','')

        #content篩選出文章內文
        content = soup.find(id="main-content").text
        target_content=u'※ 發信站: 批踢踢實業坊(ptt.cc),'
        content = content.split(target_content)
        date = soup.select('.article-meta-value')[3].text
        content = content[0].split(date)
        content = content[1].replace('\n', '  ').replace('\t', '  ')

        #note = soup.select('span.f2')
        #org_url = note[1].text.replace('※ 文章網址: ','')
        createdTime = dt.datetime.today().strftime("%d/%m/%Y %H:%M:%S")
        post_info = []
        post_info.append({'authorId':author_ID, 'authorName':author_name, 'title':title, 'publishedTime':post_date
                          , 'content':content, 'canonicalUrl':post_url, 'createdTime':createdTime})
        post_info = pd.DataFrame(post_info)

        pushes = main_content.find_all('div', class_='push')
        messages = []
        for push in pushes:
            push_tag = push.find('span', 'push-tag').string.strip(' \t\n\r')
            push_userid = push.find('span', 'push-userid').string.strip(' \t\n\r')
            # if find is None: find().strings -> list -> ' '.join; else the current way
            push_content = push.find('span', 'push-content').strings
            push_content = ' '.join(push_content)[1:].strip(' \t\n\r')  # remove ':'
            push_ipdatetime = push.find('span', 'push-ipdatetime').string.strip(' \t\n\r')    
            messages.append( {'canonicalUrl':post_url, 'push_tag': push_tag, 'commentId': push_userid
                              , 'commentContent': push_content, 'commentTime': push_ipdatetime} )

        messages = pd.DataFrame(messages)

        #post_data = pd.merge(post_info, messages, how='left', on='canonicalUrl')

        return post_info, messages

    else:
        return "404"

def get_href_from_page(board_name, scrap_page):
    payload={
    'from':'/bbs/'+ str(board_name) +'/index.html',
    'yes':'yes' 
    }

    #破除18歲的限制
    rs = requests.session()
    req = rs.post('https://www.ptt.cc/ask/over18',verify = False, data = payload)
    req = rs.get('https://www.ptt.cc/bbs/'+ str(board_name) +'/index.html',verify = False)
    if req.status_code==200:
        web_content = req.text
        #以美味湯解析html
        soup = BeautifulSoup(web_content, 'lxml')
        pre_num = soup.select('div.btn-group > a')[3]['href'].replace('/bbs/'+board_name+'/index','') ##
        pre_num = pre_num.replace('.html','')
        total_page_index = pd.to_numeric(pre_num)+1

        url_list = []
        for i in range(total_page_index, total_page_index-scrap_page, -1):
            req = rs.post('https://www.ptt.cc/ask/over18',verify = False, data = payload)
            req = rs.get('https://www.ptt.cc/bbs/'+ str(board_name) +'/index'+str(i)+'.html',verify = False)
            web_content = req.text
            #以美味湯解析html
            soup = BeautifulSoup(web_content, 'lxml')
            post_list = soup.find_all('div',class_="title")
            for item in post_list:
                try:
                    url_list.append('https://www.ptt.cc'+item.select_one("a").get("href"))
                except: #刪文抓不到href
                    pass         
        return url_list
    
    else:
        return "404"



def main(Board_Name, Scrap_Page):
	print(get_href_from_page(board_name=Board_Name, scrap_page=Scrap_Page))


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-Board_Name', action='store')
	parser.add_argument('-Scrap_Page', action='store')
	args = parser.parse_args()
	main(args.Board_Name, args.Scrap_Page)
