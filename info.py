import requests
from html.parser import HTMLParser
from bs4 import BeautifulSoup
import json 
import numpy as np 
import re 
import time
import pandas as pd 
import os 

# if query Hainan change 22 to 1 and set keyword=海南
urls = [
    ['http://www.foooooot.com/search/trip/sightseeing/22/all/occurtime/descent/?keyword=',
  '观光旅行'],
 ['http://www.foooooot.com/search/trip/hiking/22/all/occurtime/descent/?keyword=',
  '徒步'],
 ['http://www.foooooot.com/search/trip/mountaineering/22/all/occurtime/descent/?keyword=',
  '登山'],
 ['http://www.foooooot.com/search/trip/biking/22/all/occurtime/descent/?keyword=',
  '骑行'],
 ['http://www.foooooot.com/search/trip/driving/22/all/occurtime/descent/?keyword=',
  '自驾车'],
 ['http://www.foooooot.com/search/trip/running/22/all/occurtime/descent/?keyword=',
  '跑步'],
 ['http://www.foooooot.com/search/trip/photography/22/all/occurtime/descent/?keyword=',
  '摄影'],
 ['http://www.foooooot.com/search/trip/cross_country/22/all/occurtime/descent/?keyword=',
  '越野跑'],
 ['http://www.foooooot.com/search/trip/gps_drawing/22/all/occurtime/descent/?keyword=',
  'Gps作画'],
 ['http://www.foooooot.com/search/trip/mountain_biking/22/all/occurtime/descent/?keyword=',
  '山地骑行'],
 ['http://www.foooooot.com/search/trip/motorcycling/22/all/occurtime/descent/?keyword=',
  '摩托车'],
 ['http://www.foooooot.com/search/trip/geocaching/22/all/occurtime/descent/?keyword=',
  '寻宝'],
 ['http://www.foooooot.com/search/trip/skiing/22/all/occurtime/descent/?keyword=',
  '滑雪'],
 ['http://www.foooooot.com/search/trip/sailing/22/all/occurtime/descent/?keyword=',
  '航海'],
 ['http://www.foooooot.com/search/trip/paragliding/22/all/occurtime/descent/?keyword=',
  '滑翔伞'],
 ['http://www.foooooot.com/search/trip/skateboard/22/all/occurtime/descent/?keyword=',
  '滑板'],
 ['http://www.foooooot.com/search/trip/water/22/all/occurtime/descent/?keyword=',
  '涉水'],
 ['http://www.foooooot.com/search/trip/other/22/all/occurtime/descent/?keyword=',
  '其他'],
 ['http://www.foooooot.com/search/trip/import/22/all/occurtime/descent/?keyword=',
  '导入']
 ]

headers = {
    "Cookie":"Hm_lvt_eecac55989041e0555b5b1376f9b1c2f=1693805329,1693805600,1693980315; csrftoken=ac1135562386fb9b19af889b802c2b20; sessionid=a4bf93c14d1b5d44472ebc423085c34f; Hm_lpvt_eecac55989041e0555b5b1376f9b1c2f=1693980364" ,  
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    "Referer":"http://www.foooooot.com/search/trip/all/1/all/time/descent/?keyword=%E6%B5%B7%E5%8D%97"
}

# base_save_path = './year_output/'
sleep_count = 0

def getBase_info(childrenNodes, save_path):
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
            pass
    base_info = pd.DataFrame(dic)
    base_info.to_csv(save_path)
    return base_info

def get_track_info(base_info, base_save_path, save_path_aft):
    for i in range(base_info.shape[0]):
        try:
            req_json_demo = base_info.loc[i, "trip_id"]
            json_url = f"http://www.foooooot.com/v4/api/trip/{req_json_demo}/trackjson"
            json_req = requests.get(json_url, headers=headers, timeout=30)
            time.sleep(sleep_count)
            json_arr = json.loads(json_req.text)
            json_data_frame = pd.DataFrame(np.array(json_arr[0]), columns=["timestamp", "latitude", "longtitude","altitude", "speed", "meleage"])
            json_data_frame.to_csv(base_save_path + "track/" + req_json_demo + "-" + save_path_aft + ".csv")
            # print("tracks id in this page: ", i)
        except Exception as e:
            pass
    
def get_foot_print_info(base_info, base_save_path, save_path_aft):
    for i in range(base_info.shape[0]):
        req_json_demo = base_info.loc[i, "trip_id"]
        foot_print_json_url = f"http://www.foooooot.com/trip/{req_json_demo}/footprintsjson/"
        json_req = requests.get(foot_print_json_url, headers=headers, timeout=20)
        time.sleep(sleep_count)
        try:
            fot_print_df = pd.DataFrame(json.loads(json_req.text))
            fot_print_df = fot_print_df.iloc[:, [0, 1, 2, 4, 11]]
            fot_print_df.columns = ["TimeStamp", "latitude", "longtitude", "rank", "detail_id"]
            fot_print_df.to_csv(base_save_path + "footprint/" + req_json_demo + "-" + save_path_aft + ".csv")
            # print("footprint id in this page: ", i)
        except:
            pass 
        

def get_user_info(base_info, save_path):
    dic = {k :[] for k in ['经验', '等级', '威望', '银两', '金币', '注册时间', '最后登陆', 'user_id']}
    for user_demo in base_info["user_id"].values.tolist():
        try:
            user_req_url = f"http://www.foooooot.com/userindex/{user_demo}/"
            user_req = requests.get(user_req_url, headers=headers)
            bs = BeautifulSoup(user_req.text)
            text_lis = np.array([i.lstrip().rstrip().split("：") for i in bs.find("div", class_ = "u_info_content").text.split("\n")[1:-1]])[:, 1].tolist()
            # dic['user_id'].append()
            text_lis.append(user_demo)
            for (i, k) in enumerate(dic.keys()):
                dic[k].append(text_lis[i])
            time.sleep(sleep_count)
        except Exception as e:
            pass
    user_profile = pd.DataFrame(dic)
    # user_profile["user_id"] = base_info["user_id"].values.tolist()
    user_profile = user_profile.drop_duplicates(subset=["user_id"])
    user_profile.to_csv(save_path)