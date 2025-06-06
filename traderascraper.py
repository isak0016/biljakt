from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from db import generate_token_tradera, save_new_token_if_unseen
import requests

card_list = []

def get_location(link): 
    try:
        loc_link = requests.get(link)
        loc_soup = BeautifulSoup(loc_link.text, "html.parser")
        location_tag = loc_soup.find("p", {"class": "text_reset__qhVLr text_wrapper__g8400 size-paris text-gray-600 font-medium text-truncate my-auto"}).text
        return location_tag if location_tag else "Unknown"
    except Exception as e:
        return "Unknown"

def tradera_scrape(brand):
    card_list.clear()

    tradera_url = "https://www.tradera.com/category/1001?af-car_brand="+brand+"&sortBy=HighestPrice"
    tradera_result = requests.get(tradera_url)
    soup = BeautifulSoup(tradera_result.text, "html.parser")

    tradera_priser = soup.find_all("span", {"class": "text-nowrap font-weight-bold font-hansen pr-1"}) 
    items = []
    
    for pris in tradera_priser:
        
        
        
        parent = pris.find_parent("div", {"class": "item-card-inner-wrapper"}).find("a")
        pris_clean = pris.text 
        img_tag = parent.find("source", {"type": "image/webp"})
        srcset = img_tag.get("srcset", "")
        img_url = srcset.split(",")[0].strip().split(" ")[0] if srcset else ""
        link = "https://www.tradera.com" + parent["href"]
        title = parent["title"]
        token = generate_token_tradera(pris_clean, title)
        print(token + "tradera")
        items.append({
                "title": title,
                "pris": pris_clean,
                "link": link,
                "img": img_url,
                "token": token
            })
        save_new_token_if_unseen(token, title, link)

    with ThreadPoolExecutor(max_workers=20) as executor:
        locations = list(executor.map(lambda item: get_location(item["link"]), items))

    for item, loc in zip(items, locations):
        item["location"] = loc
        card_list.append(item)

    return card_list

def tradera_scrape_single_thread(brand):
    card_list.clear()

    tradera_url = "https://www.tradera.com/category/1001?af-car_brand="+brand+"&sortBy=HighestPrice"
    tradera_result = requests.get(tradera_url)
    soup = BeautifulSoup(tradera_result.text, "html.parser")

    tradera_priser = soup.find_all("span", {"class": "text-nowrap font-weight-bold font-hansen pr-1"}) 
    
    
    for pris in tradera_priser:
        
        
        

        parent = pris.find_parent("div", {"class": "item-card-inner-wrapper"}).find("a")
        pris_clean = pris.text 
        img_tag = parent.find("source", {"type": "image/webp"})
        srcset = img_tag.get("srcset", "")
        img_url = srcset.split(",")[0].strip().split(" ")[0] if srcset else ""
        link = "https://www.tradera.com" + parent["href"]
        title = parent["title"]
        
        token = generate_token_tradera(pris_clean, title)

        loc_link = requests.get(link)
        loc_soup = BeautifulSoup(loc_link.text, "html.parser")
        location = loc_soup.find("p", {"class": "text_reset__qhVLr text_wrapper__g8400 size-paris text-gray-600 font-medium text-truncate my-auto"}).text
    
        card_list.append({
                "title": title,
                "pris": pris_clean,
                "link": link,
                "img": img_url,
                "location": location,
                "token": token
            })
        save_new_token_if_unseen(token, title, link)
    return card_list



    