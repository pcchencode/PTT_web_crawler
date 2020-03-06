import requests
from bs4 import BeautifulSoup # install bs4, install lxml
import pandas as pd
import datetime as dt
import logging
#from datetime import datetime, timedelta
import traceback
import os
import random
import time 
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import argparse


''' log_file setting '''
ct8 = dt.datetime.now() #+ datetime.timedelta(hours=8)
# file_path_dict = lbt.check_folder()

logger = logging.getLogger()
logger.setLevel(logging.NOTSET)

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s: - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')
try:
    os.mkdir('/work_dir/log')
except FileExistsError:
    pass

log_path = os.path.join("/work_dir/log", 'ptt_web_crawler{}.txt'.format(
    dt.datetime.strftime(ct8, "%Y-%m-%d-%H%M%S"))) ##路徑名稱自己改，'.'代表當下路徑

fh = logging.FileHandler(log_path)
fh.setLevel(logging.WARNING)
fh.setFormatter(formatter)

ch = logging.StreamHandler()
ch.setLevel(logging.WARNING)
ch.setFormatter(formatter)

logger.addHandler(ch)
logger.addHandler(fh)

def get_post_data(post_url):
    payload={
    'from':'/bbs/'+ 'Gossiping' +'/index.html',
    'yes':'yes' 
    }

    # 有些版有年齡限制，點選確定滿18歲
    rs = requests.session()
    req = rs.post('https://www.ptt.cc/ask/over18', verify = False, data = payload)
    req = rs.get('https://www.ptt.cc/bbs/'+ 'Gossiping' +'/index.html', verify = False)
    req = rs.get(post_url, verify=False)

    if req.status_code == 200:
        web_content = req.text
        # 使用lxml解析html、速度較快
        soup = BeautifulSoup(web_content, 'lxml')
        main_content = soup.find('div', id="main-content")
        metas = main_content.select('div.article-metaline')

        author = metas[0].select('span.article-meta-value')[0].text
        title = metas[1].select('span.article-meta-value')[0].text
        post_date = metas[2].select('span.article-meta-value')[0].text
        author_ID = author.split('(', 1)[0].replace(' ', '')
        author_name = author.split('(', 1)[1].replace(')', '')

        # content篩選出文章內文
        content = soup.find(id="main-content").text
        target_content = u'※ 發信站: 批踢踢實業坊(ptt.cc),'
        content = content.split(target_content)
        date = soup.select('.article-meta-value')[3].text
        content = content[0].split(date)
        content = content[1].replace('\n', '  ').replace('\t', '  ')

        # note = soup.select('span.f2')
        # org_url = note[1].text.replace('※ 文章網址: ','')
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

        # post_data = pd.merge(post_info, messages, how='left', on='canonicalUrl')

        return post_info, messages

    else:
        return 404

def get_href_from_page(board_name, scrap_page):
    payload={
    'from':'/bbs/'+ str(board_name) +'/index.html',
    'yes':'yes' 
    }

    
    rs = requests.session()
    req = rs.post('https://www.ptt.cc/ask/over18',verify = False, data = payload)
    req = rs.get('https://www.ptt.cc/bbs/'+ str(board_name) +'/index.html',verify = False)
    if req.status_code==200:
        web_content = req.text
        
        soup = BeautifulSoup(web_content, 'lxml')
        pre_num = soup.select('div.btn-group > a')[3]['href'].replace('/bbs/'+board_name+'/index','') ##
        pre_num = pre_num.replace('.html','')
        total_page_index = pd.to_numeric(pre_num)+1

        url_list = []
        for i in range(total_page_index, total_page_index-scrap_page, -1):
            time.sleep(random.uniform(0,2)) #爬取每頁網址所有文章時sleep，避免IP被擋
            req = rs.post('https://www.ptt.cc/ask/over18',verify = False, data = payload)
            req = rs.get('https://www.ptt.cc/bbs/'+ str(board_name) +'/index'+str(i)+'.html',verify = False)
            web_content = req.text
            
            soup = BeautifulSoup(web_content, 'lxml')
            post_list = soup.find_all('div',class_="title")
            for item in post_list:
                try:
                    url_list.append('https://www.ptt.cc'+item.select_one("a").get("href"))
                except: #刪文抓不到href
                    pass         
        return url_list
    
    else:
        return 404




def main(Board_Name, Scrap_Page):
    post_list = get_href_from_page(board_name=str(Board_Name), scrap_page=int(Scrap_Page))
    all_post_info = get_post_data(post_list[0])[0] 
    for i in range(1, len(post_list)):
        try:
            all_post_info = all_post_info.append(get_post_data(post_list[i])[0])
        except:
            pass

    all_msg = get_post_data(post_list[0])[1] 
    for i in range(1, len(post_list)):
        try:
            all_msg = all_msg.append(get_post_data(post_list[i])[1])    
        except:
            pass
    all_post_info.to_csv('/work_dir/all_post_info.csv')
    all_msg.to_csv('/work_dir/all_msg.csv')
        
    return 

	#print(get_href_from_page(board_name=str(Board_Name), scrap_page=int(Scrap_Page)))


if __name__ == '__main__':

	parser = argparse.ArgumentParser()
	parser.add_argument('-Board_Name', action='store')
	parser.add_argument('-Scrap_Page', action='store')
	args = parser.parse_args()
	logging.warning('start')
	main(args.Board_Name, args.Scrap_Page)
	logging.warning('end')
