#首先我们先导入requests这个包
import json
import datetime
import requests
import bs4
import threading
from fyframe_v2.log.log import getLogger
#我们来吧百度的index页面的html源码抓取到本地，并用r变量保存
#注意这里，网页前面的 http://一定要写出来，它并不能像真正的浏览器一样帮我们补全http协议
import logging
from logging.handlers import RotatingFileHandler
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='getinfo.log',
                    filemode='a+')
Rthandler = RotatingFileHandler('getinfo.log', maxBytes=10240*10240,backupCount=10)
Rthandler.setLevel(logging.DEBUG)
formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] [%(module)s:%(funcName)s]- %(message)s [%(module)s:%(funcName)s]')
Rthandler.setFormatter(formatter)
logging.getLogger('').addHandler(Rthandler)
# sh = logging.StreamHandler()#往屏幕上输出
# sh.setFormatter(formatter) #设置屏幕上显示的格式

# mutex = threading.Lock()
# def setLogger(log):
#     global logger
#     logger = log
#
#
# def set_ser_log(log):
#     global ser_logger
#     ser_logger = log

# def getLogger(type='none',tag=''):
#     log = None
#     if type == 'ser':
#         if mutex.acquire():
#             if not ser_logger:
#                 log = logging
#             else:
#                 log = ser_logger
#             mutex.release()
#         return log
#     else:
#         if mutex.acquire():
#             if not logger:
#                 log = logging
#             else:
#                 log = logger
#             mutex.release()
#         return log

try:
    starttime = datetime.datetime.now()
    url2 = "http://remotive.io/"
    r2 = requests.get(url2)
    soup2=bs4.BeautifulSoup(r2.text,'lxml')
    tag2 = (soup2.find('div',attrs={'id':'job_list'})).find_all('li',attrs={'class':'category-list'})
    dataurl=[]
    dataurl_tag =[]
    more_job = []
    more_job_tag =[]
    more_job_detail=[]
    for tag2_tmp in tag2:
        if tag2_tmp.find_all('h2',attrs={'class':'category-title'})==[]:
            continue
        else:
            dataurl_tag.append(tag2_tmp.find_all('li',attrs={'class':'job-list-item'}))
            ss = tag2_tmp.find_all('a',attrs={'class':'more-jobs'})
            if ss !=[]:
                more_job_tag.append(ss)

    for dataurl_tag_tmp in dataurl_tag:
        for dataurl_tag_tmp_tmp in dataurl_tag_tmp:
            dataurl.append(url2+dataurl_tag_tmp_tmp.attrs['data-url'])

    for more_job_tag_tmp in more_job_tag:
        for more_job_tag_tmp_tmp in more_job_tag_tmp:
            more_job.append(url2+more_job_tag_tmp_tmp.attrs['href'])
    for more_link in more_job:
        more_job_detail=[]
        r_tmp = requests.get(url2)
        soup_tmp=bs4.BeautifulSoup(r_tmp.text,'lxml')
        url_tmp = (soup_tmp.find('div',attrs={'id':'job_list'})).find_all('li',attrs={'class':'job-list-item'})
        for url_tmp_tmp in url_tmp:
            more_job_detail.append(url_tmp_tmp.attrs['data-url'])
        more_job_detail = list(set(more_job_detail))
        print(1)

    url1="https://weworkremotely.com"
    r = requests.get(url1)
    soup = bs4.BeautifulSoup(r.text,'lxml')
    #输出结果
    tag = (soup.find('div',attrs={'id':'job_list'})).find_all('a')
    jobLink = []
    jobcategry = []
    companyname = []
    job_special = []

    job_information ={}

    find_http_start = datetime.datetime.now()

    def getJobLink(tag_tmp):
        jobLink_tmp =[]
        jobcategry_tmp=[]
        for tagi in tag_tmp:
            if 'href' in tagi.attrs.keys():
                contenets = tagi.contents
                for i in contenets:
                    if isinstance(i,bs4.element.Tag):
                        list_value = list(i.attrs.values())[:]
                        if ['company'] in list_value:
                            jobLink_tmp.append(url1+tagi.attrs['href'])
                    else:
                        continue

                if '/categories/' in tagi.attrs['href']:
                    if 'all' in str(tagi.contents[0]).lower():
                        jobcategry_tmp.append(url1+tagi.attrs['href'])
        return list(set(jobLink_tmp)),list(set(jobcategry_tmp))

    jobLink,jobcategry = getJobLink(tag)
    getLogger().info(len(jobcategry))
    getLogger().info(len(jobLink))

    jobLink_category = []
    for link in jobcategry:
        r_link = requests.get(link)
        soup_link = bs4.BeautifulSoup(r_link.text, 'lxml')
        # 输出结果
        tag_link = (soup_link.find('div', attrs={'id': 'job_list'})).find_all('a')
        jobLink_category_2,jobcategry_2 = getJobLink(tag_link)
        jobLink_category= jobLink_category+jobLink_category_2
        print(jobcategry.index(link))
        # for tagi_link in tag_link:
        #     if 'href' in tagi_link.attrs.keys():
        #         contenets = tagi_link.contents
        #         for i in contenets:
        #             if isinstance(i,bs4.element.Tag):
        #                 list_value = list(i.attrs.values())[:]
        #                 if ['company'] in list_value:
        #                     jobLink_category.append(url1+tagi_link.attrs['href'])
        #             else:
        #                 continue
    getLogger().info(len(jobLink_category))
    
    jobLink_sum = jobLink+jobLink_category
    jobLink_sum = list(set(jobLink_sum))
    getLogger().info(len(jobLink_sum))

    find_http_stop = datetime.datetime.now()
    getLogger().info('寻找链接的总时间为'+str((find_http_stop - find_http_start).seconds)+'s')

    for jj in jobLink_sum:
        link_analysis_start= datetime.datetime.now()
        job_special=[]
        r1 = requests.get(jj)
        getLogger().info(jobLink_sum.index(jj)+1)
        getLogger().info(jj)
        soup1 = bs4.BeautifulSoup(r1.text,'lxml')
        job_sum1 = soup1.find('section',attrs={'id':'job-show'})
        job_desc = ((job_sum1.find('div',attrs={'id':'job-listing-show-container'})).contents)
            # .text.strip()
        job_desc = map(str,job_desc)
        job_desc = ''.join(job_desc)
        job_applyLink= (job_sum1.find('a',attrs={'id':'job-cta-alt'})).attrs['href']

        job_sum2 = soup1.find('div',attrs={'class':'listing-header-container'})
        job_time = job_sum2.find('h3').contents[1].attrs['datetime']
        job_name = job_sum2.find('h1').text.strip()
        job_special_tmp = job_sum2.find_all('span',attrs={'class':'listing-tag'})
        for i in job_special_tmp:
            job_special.append(i.text.strip())
        job_information[int(jobLink_sum.index(jj))+1] = {'job_desc':job_desc,'job_time':job_time,'job_name':job_name,'job_special':job_special,'job_link':jj,'job_applyLink':job_applyLink}
        link_analysis_stop = datetime.datetime.now()
        getLogger().info('序号'+str(jobLink_sum.index(jj)+1)+'的链接解析需要的时间为' + str((link_analysis_stop - link_analysis_start).seconds)+'s')
        getLogger().info('')
    # getLogger().info(job_desc)
    # getLogger().info(job_time)
    # getLogger().info(job_name)
    # getLogger().info(job_special)
    # getLogger().info(job_information)
    json_dicts = json.dumps(job_information, indent=4, ensure_ascii=False)
    # log_result_file = open('D:\work\\factory\杂\get_info.json', 'a',encoding="UTF-8")
    with open('D:\work\\factory\杂\get_info.json', 'w',encoding="UTF-8") as f:
        f.write(json_dicts)
    # log_result_file.write(json_dicts)
    # log_result_file.close()
    endtime = datetime.datetime.now()
    getLogger().info('测试总时间为:'+str((endtime - starttime).seconds)+'s')
except Exception as e:
    getLogger().exception(e)
