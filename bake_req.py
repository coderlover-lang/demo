import requests 
from bs4 import BeautifulSoup
import os 
from utils.info import * 

max_page  = 100
wokd_dir = "./year_output/"


for i in range(len(urls)):
    demo = urls[i]
    base_save_path = f"./海口/{demo[1]}/"
    if not os.path.exists(base_save_path):
        os.mkdir(base_save_path)
    for i in ["base", "footprint", "profile", "track"]:
        if (not os.path.exists(base_save_path + i)):
            os.mkdir(base_save_path + i)
    for page in range(1, max_page + 1):
        try:
            base_url = demo[0] + f"&page={page}"
            print("current url : ", base_url)
            
            req = requests.get(base_url, headers=headers)
            parser = HTMLParser()
            bs = BeautifulSoup(req.text)
            childrenNodes = None
            parentNode = bs.find("ul", class_ = "tripsList")
            childrenNodes = parentNode.find_all("li")[1:-1]
            print("base")
            base_path = base_save_path + f"base/base-{page}.csv"
            user_path = base_save_path + f"profile/user-{page}.csv"
            aft = ""
            base = getBase_info(childrenNodes, base_path)
            print("track")
            get_track_info(base, base_save_path, aft)
            print("footprint")
            get_foot_print_info(base, base_save_path, aft)
            print("user")
            get_user_info(base, user_path)
        except Exception as e:
            print(e)
            print(demo[1] + "finished ! total page : ", page)
            break