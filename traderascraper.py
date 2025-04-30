from bs4 import BeautifulSoup
import requests

card_list = []

def tradera_scrape(brand):
    
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
        if parent and parent.has_attr("href"):
            link = "https://www.tradera.com" + parent["href"]
            title = parent["title"]
            
            card_list.append({
                    "title": title,
                    "pris": pris_clean,
                    "link": link,
                    "img": img_url
                })
    return card_list





    