#首先我们先导入requests这个包
import json

import requests
import bs4

#我们来吧百度的index页面的html源码抓取到本地，并用r变量保存
#注意这里，网页前面的 http://一定要写出来，它并不能像真正的浏览器一样帮我们补全http协议
url1="https://weworkremotely.com"
r = requests.get(url1)

soup = bs4.BeautifulSoup(r.text,'lxml')
#输出结果
# tagppp = soup.find_all('li',attrs={'class':'feature'})
tag=soup.find_all('a')
jobLink = []
jobcategry = []
companyname = []
job_special = []

job_information ={}
for tagi in tag:
    if 'href' in tagi.attrs.keys():
        # if '/remote-jobs/new' in tagi.attrs['href']:
        #     continue
        contenets = tagi.contents
        for i in contenets:
            p = type(i)
            print(type(i))
            print(isinstance(i,bs4.element.Tag))
            if isinstance(i,bs4.element.Tag):
                list_value = list(i.attrs.values())[:]
                if ['company'] in list_value:
                    jobLink.append(url1+tagi.attrs['href'])
                    companyname.append(i.contents[0])
            else:
                continue

        if '/categories/' in tagi.attrs['href']:
            if 'view all' in str(tagi.contents[0]).lower():
                jobcategry.append(url1+tagi.attrs['href'])
# print(list(set(jobLink)))
# print(len(list(set(jobLink))))
# print(list(set(companyname)))
# print(len(list(set(companyname))))
# print(jobcategry)
# print(len(jobcategry))


jobLink_real = list(set(jobLink))

for jj in jobLink_real:
    r1 = requests.get(jj)
    # print(jobLink_real[0])
    soup1 = bs4.BeautifulSoup(r1.text,'lxml')
    job_desc=(soup1.find('div',attrs={'id':'job-listing-show-container'})).text.strip()

    job_sump = soup1.find('div',attrs={'class':'listing-header-container'})
    job_time = job_sump.find('h3').contents[1].attrs['datetime']
    job_name = job_sump.find('h1').text.strip()
    job_special_tmp = job_sump.find_all('span',attrs={'class':'listing-tag'})
    for i in job_special_tmp:
        job_special.append(i.text.strip())
    job_information[job_name] = {'job_desc':job_desc,'job_time':job_time,'job_name':job_name,'job_special':job_special}

# print(job_desc)
# print(job_time)
# print(job_name)
# print(job_special)
print(job_information)
json_dicts = json.dumps(job_information, indent=4, ensure_ascii=False)
log_result_file = open('D:\work\\factory\杂\get_info.json', 'a',encoding="UTF-8")
log_result_file.write(json_dicts)
log_result_file.close()