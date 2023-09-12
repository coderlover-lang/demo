import requests
from html.parser import HTMLParser
from bs4 import BeautifulSoup
import json 
import numpy as np 
import re 
import time
import pandas as pd 
import os 

headers = {
    "Cookie":"Hm_lvt_eecac55989041e0555b5b1376f9b1c2f=1693805329,1693805600,1693980315; csrftoken=ac1135562386fb9b19af889b802c2b20; sessionid=a4bf93c14d1b5d44472ebc423085c34f; Hm_lpvt_eecac55989041e0555b5b1376f9b1c2f=1693980364" ,  
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    "Referer":"http://www.foooooot.com/search/trip/all/1/all/time/descent/?keyword=%E6%B5%B7%E5%8D%97"
}

base_save_path = "./total_output/"
# for i in ["base", "footprint", "profile", "track"]:
#     if (not os.path.exists(i)):
#         os.mkdir(base_save_path + i)
    
# 请求base url
page = 2
print("current page : ", page)
base_url = f"http://www.foooooot.com/search/trip/all/1/all/occurtime/descent/?page={page}&keyword=%E6%B5%B7%E5%8D%97"
req = requests.get(base_url, headers=headers)
parser = HTMLParser()
bs = BeautifulSoup(req.text)

parentNode = bs.find("ul", class_ = "tripsList")
childrenNodes = parentNode.find_all("li")[1:-1]

dic  = {
    "trip_id" : [],
    "trip_title" : [],
    "user_id" : [], 
    "user_name" : [], 
    "submit_time" : [], 
    "trip_way" : [], 
    "total_kilometers" : [] , 
    "difficult_ranks" : [], 
    "start_time" : [], 
    "spend_time" : [], 
    "start_place" : [], 
    "end_place" : [], 
    "view" : [], 
    "comment" : [], 
    "download" : [], 
    "love" : []
}
for i in range(len(childrenNodes)):
    demo = childrenNodes[i]
    try:
        profile_info, count_info = [i.text.replace("\n", "").lstrip().rstrip() for i in demo.find_all("tr")][:2]
        trip_id = demo.find("p", class_ = "trip-title").find("a").get_attribute_list("href")[0].split("/")[-2]
        trip_title = demo.find("p", class_ = "trip-title").find("a").text
        profiles = list(demo.find("dd"))
        user_id = profiles[1].get_attribute_list("href")[0].split("/")[-2]
        user_name = profiles[1].text.lstrip().rstrip()
        submit_time = profiles[2].replace("\n", "").replace("\xa0", "").lstrip().rstrip().replace("上传", "")
        trip_way = profiles[3].text
        total_kilometers, difficult_ranks = [i.lstrip().rstrip() for i in profiles[4].replace("\n", "").split("\xa0")[1:]]
        dls = list(demo.find("dl"))
        _, start_time, _, spend_time = [i.replace("\n", "").lstrip().rstrip() for i in dls[5].text.split("\xa0")]
        start_place, end_place = dls[7].text.replace("\n", "").replace("\xa0", "").lstrip().rstrip().split("-")
        trs = demo.find("div", class_ = "trip-icon-summaries").find("tr").findAll("td")
        views, comments, downloads, love = [trs[i].text.replace("\n", "").replace("\t", "").lstrip().rstrip() for i in range(4)]
        dic["trip_id"].append(trip_id)
        dic["trip_title"].append(trip_title)
        dic["user_id"].append(user_id)
        dic["user_name"].append(user_name)
        dic["submit_time"].append(submit_time)
        dic["trip_way"].append(trip_way)
        dic["total_kilometers"].append(total_kilometers)
        dic["difficult_ranks"].append(difficult_ranks)
        dic["start_time"].append(start_time)
        dic["spend_time"].append(spend_time)
        dic["start_place"].append(start_place)
        dic["end_place"].append(end_place)
        dic["view"].append(views)
        dic["comment"].append(comments)
        dic["download"].append(downloads)
        dic["love"].append(love)
    except Exception as e:
        print(e)

# 整理出base info
base_info = pd.DataFrame(dic)

print("current page : ", page, " request for the track json ...")

for i in range(len(childrenNodes)):
    try:
        req_json_demo = base_info.loc[i, "trip_id"]
        json_url = f"http://www.foooooot.com/v4/api/trip/{req_json_demo}/trackjson"
        json_req = requests.get(json_url, headers=headers)
        time.sleep(5)
        json_arr = json.loads(json_req.text)
        json_data_frame = pd.DataFrame(np.array(json_arr[0]), columns=["timestamp", "latitude", "longtitude","altitude", "speed", "meleage"])
        json_data_frame.to_csv(base_save_path + "track/" + req_json_demo + "-" + str(page) + ".csv")
        print("tracks id in this page: ", i)
    except Exception as e:
        print(e)

print("current page : ", page, " request for the footprint json ...")

        
for i in range(len(childrenNodes)):
    req_json_demo = base_info.loc[i, "trip_id"]
    foot_print_json_url = f"http://www.foooooot.com/trip/{req_json_demo}/footprintsjson/"
    json_req = requests.get(foot_print_json_url, headers=headers)
    time.sleep(5)
    try:
        fot_print_df = pd.DataFrame(json.loads(json_req.text))
        fot_print_df = fot_print_df.iloc[:, [0, 1, 2, 4, 11]]
        fot_print_df.columns = ["TimeStamp", "latitude", "longtitude", "rank", "detail_id"]
        fot_print_df.to_csv(f'{base_save_path}footprint/{req_json_demo}-{page}.csv')
        print("footprint id in this page: ", i)
    except:
        pass 


dic = {k :[] for k in ['经验', '等级', '威望', '银两', '金币', '注册时间', '最后登陆']}
for user_demo in base_info["user_id"].values.tolist():
    try:
        user_req_url = f"http://www.foooooot.com/userindex/{user_demo}/"
        user_req = requests.get(user_req_url, headers=headers)
        bs = BeautifulSoup(user_req.text)
        text_lis = np.array([i.lstrip().rstrip().split("：") for i in bs.find("div", class_ = "u_info_content").text.split("\n")[1:-1]])[:, 1].tolist()
        for (i, k) in enumerate(dic.keys()):
            dic[k].append(text_lis[i])
        time.sleep(5)
    except Exception as e:
        print(e)

user_profile = pd.DataFrame(dic)
user_profile["user_id"] = base_info["user_id"].values.tolist()
user_profile = user_profile.drop_duplicates(subset=["user_id"])
user_profile.to_csv(f'{base_save_path}/profile/user-{page}.csv')
base_info.to_csv(f'{base_save_path}/base/base-{page}.csv')