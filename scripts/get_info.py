#首先我们先导入requests这个包
import json,copy
import datetime
import requests
import bs4
import threading
from fyframe_v2.log.log import getLogger
from fyframe_v2.baselibrary.cfgparser import read_ini_file,write_ini_file
#我们来吧百度的index页面的html源码抓取到本地，并用r变量保存
#注意这里，网页前面的 http://一定要写出来，它并不能像真正的浏览器一样帮我们补全http协议
import logging
from logging.handlers import RotatingFileHandler
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='getinfo.txt',
                    filemode='a+')
Rthandler = RotatingFileHandler('getinfo.txt', maxBytes=10240*10240,backupCount=10)
Rthandler.setLevel(logging.DEBUG)
formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] [%(module)s:%(funcName)s]- %(message)s [%(module)s:%(funcName)s]')
Rthandler.setFormatter(formatter)
logging.getLogger('').addHandler(Rthandler)



try:
    congfig = read_ini_file('../ini/internetworm.ini')
    lastRunTime = congfig.get('DEFAULT','lastRunTime')
    if lastRunTime != 'FirstRun':
        lastRunTime= datetime.datetime.strptime(lastRunTime, '%Y-%m-%d %H:%M:%S')

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
    job_information2 = {}
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
        r_tmp = requests.get(more_link)
        soup_tmp=bs4.BeautifulSoup(r_tmp.text,'lxml')
        url_tmp = (soup_tmp.find('div',attrs={'id':'job_list'})).find_all('li',attrs={'class':"job-list-item"})
        for url_tmp_tmp in url_tmp:
            more_job_detail.append(url2+url_tmp_tmp.attrs['data-url'])
    more_job_detail = list(set(more_job_detail))
    dataurlSum = dataurl+more_job_detail
    dataurlSum = list(set(dataurlSum))
    job_end1= datetime.datetime.now()
    getLogger().info('寻找链接' + url2 +',链接总数' + str(len(dataurlSum)) + ',总时间为' + str((job_end1 - starttime).seconds) + 's')
    for dataurlDetail in dataurlSum:
        job_special2 = []
        sync_start2 = datetime.datetime.now()
        # getLogger().info(dataurlDetail)
        r_detial=requests.get(dataurlDetail)
        if r_detial.reason.lower() !='ok':
            job_information2[int(dataurlSum.index(dataurlDetail)+1)]={'job_desc':'网址打开失败，返回'+str(r_detial.reason.lower())+'状态码为'+str(r_detial.status_code),'job_url':dataurlDetail}
            getLogger().error('网址'+str(dataurlDetail)+'打开失败，返回'+str(r_detial.reason.lower())+'状态码为'+str(r_detial.status_code))
            continue
        soupDetail = bs4.BeautifulSoup(r_detial.text,'lxml')
        urlDe = (soupDetail.find('section',attrs={'class':'job-details-page'})).find('div',attrs={'class':'wrapper'})
        job_summary =(urlDe.find('div',attrs={'class':'content'}))
        job_time_dict = (((job_summary.find_all('p'))[1]).text.strip()).split(' ')
        job_time_dict2 = ((job_time_dict[0]).split('/'))
        lastindex = job_time_dict2.pop()
        job_time_dict2.insert(0, lastindex)
        job_time = '-'.join(job_time_dict2) + ' ' + job_time_dict[1]
        job_time_datetime = datetime.datetime.strptime(job_time, '%Y-%m-%d %H:%M:%S')
        if lastRunTime == 'FirstRun':
            getLogger().info('初次运行，所有信息都爬')
        elif job_time_datetime < lastRunTime:
            getLogger().info('此网址信息未更新，不用爬取')
            job_information2[int(dataurlSum.index(dataurlDetail) + 1)] = {'job_time': job_time,
                                                                          'job_desc': '工作信息未更新',
                                                                          'job_url': dataurlDetail}
            sync_stop3 = datetime.datetime.now()
            getLogger().info(
                '解析序号为' + str(dataurlSum.index(dataurlDetail) + 1) + '的url:' + dataurlDetail + '的时间为' + str(
                    (sync_stop3 - sync_start2).seconds) + 's')
            continue
        elif job_time_datetime >= lastRunTime:
            getLogger().info('信息更新，重新爬取')

        job_name_2 =job_summary.h1.contents[0]
        job_company=job_summary.h2.contents[0]
        jobsp = job_summary.find_all('p',recursive=False)

        for i in jobsp:
            ii = i.text.strip()
            job_special2.append(ii)
            # if len(str(ii).split(":"))==2:
            #     job_special[(ii.split(':'))[0]] = (ii.split(':'))[1]
        job_special2.pop(0)
        job_special2.pop(0)
        tip = job_summary.find_all('a',attrs={'class':'job-tag'})
        for tip_tmp in tip:
            job_special2.append(tip_tmp.text.strip())
        job_desc=job_summary.find('div',attrs={'class':'job-description'}).text.strip()
        job_apply=url2+((job_summary.find('div',attrs={'class':'apply-wrapper'})).find('a',attrs={'class':'btn btn-apply'})).attrs['href']
        sync_stop2 = datetime.datetime.now()
        job_information2[int(dataurlSum.index(dataurlDetail)+1)]={'job_name':job_name_2,'job_company':job_company,'job_time':job_time,'job_special':job_special2,'job_desc':job_desc,'job_apply':job_apply,'job_url':dataurlDetail}
        getLogger().info('解析序号为'+str(dataurlSum.index(dataurlDetail)+1)+'的url:'+dataurlDetail+'的时间为'+str((sync_stop2 - sync_start2).seconds)+'s')
    endtime_url2=datetime.datetime.now()
    getLogger().info('测试' + url2 + ',链接总数为:'+str(len(dataurlSum))+',总时间为:' + str((endtime_url2 - starttime).seconds) + 's,大概'+str('%.2f' % float(((endtime_url2 - starttime).seconds)/60.0))+'min')
    #将爬虫信息写入json文件
    if lastRunTime !='FirstRun':
        with open('D:\work\\factory\杂\\RemotiveGetInfo.json', 'r', encoding='UTF-8') as s:
            json_file = json.load(s)

        for k,l in job_information2.items():
            for m,n in json_file.items():
                if l['job_desc'] =='工作信息未更新':
                    continue
                else:
                    if l['job_url']==n['job_url']:
                        # s1 = json_file[k]
                        # s2 = job_information2[k]
                        json_file[m] = copy.deepcopy(job_information2[k])
                        # s11 = json_file[k]
                        # s21 = job_information2[k]
            else:
                if l['job_desc'] == '工作信息未更新':
                    pass
                else:
                    json_file[len(json_file)+1]=copy.deepcopy(job_information2[k])


        json_dicts2 = json.dumps(json_file, indent=4, ensure_ascii=False)
        with open('D:\work\\factory\杂\\RemotiveGetInfo.json', 'w', encoding="UTF-8") as f:
            f.write(json_dicts2)
    else:
        json_dicts2 = json.dumps(job_information2, indent=4, ensure_ascii=False)
        with open('D:\work\\factory\杂\\RemotiveGetInfo.json', 'w', encoding="UTF-8") as f:
            f.write(json_dicts2)

    starttime_url1=datetime.datetime.now()
    # index_start = len(job_information2)+1
    url1="https://weworkremotely.com"
    find_http_start = datetime.datetime.now()
    r = requests.get(url1)
    soup = bs4.BeautifulSoup(r.text,'lxml')
    #输出结果
    tag = (soup.find('div',attrs={'id':'job_list'})).find_all('a')
    jobLink = []
    jobcategry = []
    companyname = []
    job_special = []

    job_information ={}
    # job_information.update(job_information2)
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
    # getLogger().info(len(jobcategry))
    # getLogger().info(len(jobLink))

    jobLink_category = []
    for link in jobcategry:
        r_link = requests.get(link)
        soup_link = bs4.BeautifulSoup(r_link.text, 'lxml')
        # 输出结果
        tag_link = (soup_link.find('div', attrs={'id': 'job_list'})).find_all('a')
        jobLink_category_2,jobcategry_2 = getJobLink(tag_link)
        jobLink_category= jobLink_category+jobLink_category_2
        # print(jobcategry.index(link))

    # getLogger().info(len(jobLink_category))
    
    jobLink_sum = jobLink+jobLink_category
    jobLink_sum = list(set(jobLink_sum))
    # getLogger().info(len(jobLink_sum))

    find_http_stop = datetime.datetime.now()
    getLogger().info('寻找链接'+str(url1)+',链接总数'+str(len(jobLink_sum))+',的总时间为'+str((find_http_stop - find_http_start).seconds)+'s')

    for jj in jobLink_sum:
        link_analysis_start= datetime.datetime.now()
        job_special=[]
        r1 = requests.get(jj)
        if r1.reason.lower() != 'ok':
            job_information[int(jobLink_sum.index(jj))+1] = {'job_desc': '网址打开失败,返回值为'+str(r1.reason.lower())+'状态码'+str(r1.status_code),  'job_link': jj}
            getLogger().error('网址：'+jj+'打开失败,返回值为'+str(r1.reason.lower())+'状态码'+str(r1.status_code))
            # index_start = index_start + 1
            continue
        # getLogger().info(index_start)
        # getLogger().info(jj)
        soup1 = bs4.BeautifulSoup(r1.text,'lxml')
        job_time = (soup1.find('div', attrs={'class': 'listing-header-container'})).find('h3').contents[1].attrs[
            'datetime']
        job_time_datetime = datetime.datetime.strptime(job_time, '%Y-%m-%d %H:%M:%S')
        if lastRunTime == 'FirstRun':
            getLogger().info('初次运行，所有信息都爬')
        elif job_time_datetime < lastRunTime:
            getLogger().info('此网址信息未更新，不用爬取')
            job_information[int(jobLink_sum.index(jj) + 1)] = {'job_time': job_time,
                                                                          'job_desc': '工作信息未更新',
                                                                          'job_url': jj}
            sync_stop4 = datetime.datetime.now()
            getLogger().info(
                '解析序号为' + str(jobLink_sum.index(jj) + 1) + '的url:' + jj + '的时间为' + str(
                    (sync_stop4 - link_analysis_start).seconds) + 's')
            continue
        elif job_time_datetime >= lastRunTime:
            getLogger().info('信息更新，重新爬取')

        job_company2 = (soup1.find('div',attrs={'class':'company-card'})).h2.a.contents[0]
        job_sum1 = soup1.find('section',attrs={'id':'job-show'})
        job_desc = ((job_sum1.find('div',attrs={'id':'job-listing-show-container'})).contents)
        job_desc = map(str,job_desc)
        job_desc = ''.join(job_desc)
        job_applyLink= (job_sum1.find('a',attrs={'id':'job-cta-alt'})).attrs['href']

        job_sum2 = soup1.find('div',attrs={'class':'listing-header-container'})
        job_name = job_sum2.find('h1').text.strip()
        job_special_tmp = job_sum2.find_all('span',attrs={'class':'listing-tag'})
        for i in job_special_tmp:
            job_special.append(i.text.strip())
        job_information[int(jobLink_sum.index(jj))+1] = {'job_desc':job_desc,'job_time':job_time,'job_name':job_name,'job_special':job_special,'job_link':jj,'job_applyLink':job_applyLink}
        link_analysis_stop = datetime.datetime.now()
        getLogger().info('解析序号为'+str(int(jobLink_sum.index(jj))+1)+'的url:'+jj+'的时间为' + str((link_analysis_stop - link_analysis_start).seconds)+'s')
        # index_start=index_start+1
    # getLogger().info(job_desc)
    # getLogger().info(job_time)
    # getLogger().info(job_name)
    # getLogger().info(job_special)
    # getLogger().info(job_information)
    if lastRunTime !='FirstRun':
        with open('D:\work\\factory\杂\\RemotiveGetInfo.json', 'r', encoding='UTF-8') as s:
            json_file2 = json.load(s)

        for o,p in job_information.items():
            for q,r in json_file2.items():
                if p['job_desc'] =='工作信息未更新':
                    continue
                else:
                    if p['job_url']==r['job_url']:
                        # s1 = json_file2[q]
                        # s2 = job_information[o]
                        json_file2[q] = copy.deepcopy(job_information[o])
                        # s11 = json_file2[q]
                        # s21 = job_information[o]
            else:
                if p['job_desc'] == '工作信息未更新':
                    pass
                else:
                    json_file2[len(json_file2)+1]=copy.deepcopy(job_information[o])


        json_dicts = json.dumps(json_file2, indent=4, ensure_ascii=False)
        with open('D:\work\\factory\杂\WeworkremotelyGetInfo.json', 'w', encoding="UTF-8") as f:
            f.write(json_dicts)
    else:
        json_dicts = json.dumps(job_information, indent=4, ensure_ascii=False)
        with open('D:\work\\factory\杂\WeworkremotelyGetInfo.json', 'w', encoding="UTF-8") as f:
            f.write(json_dicts)

    # log_result_file.write(json_dicts)
    # log_result_file.close()
    endtime = datetime.datetime.now()
    getLogger().info('测试' + url1 +',链接总数：' + str(len(jobLink_sum)) + ',总时间为:' + str((endtime - starttime_url1).seconds) + 's,大概'+str('%.2f' % float(((endtime - starttime_url1).seconds)/60.0))+'min')
    starttime_string = starttime.strftime("%Y-%m-%d %H:%M:%S")
    congfig.set('DEFAULT','lastRunTime',starttime_string)
    write_ini_file(congfig)
    getLogger().info('爬虫结束，测试总时间为：'+str((endtime-starttime).seconds)+'s,大概'+str('%.2f' % float(((endtime - starttime).seconds)/60.0))+'min')
except Exception as e:
    getLogger().exception(e)