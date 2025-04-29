from bs4 import BeautifulSoup
import requests
import re
from functools import wraps
from flask import Flask, jsonify, render_template, request
app = Flask(__name__)

card_list = []


   
@app.route("/scraper", methods=["GET", "POST"])
def load_page():
    
    if request.method == "POST":
        card_list.clear()
        brand = request.form.get('brand')
        sort_order = request.form.get('sort_order')

        if sort_order == "desc":
            tradera_url = "https://www.tradera.com/category/1001?af-car_brand="+brand+"&sortBy=HighestPrice"
            blocket_url = "https://www.blocket.se/bilar/sok?sortOrder=Dyrast&q="+brand+"&filter=%7B%22key%22%3A%22sellerType%22%2C%22values%22%3A%5B%22Privat%22%5D%7D"
        elif sort_order == "asc":
            tradera_url = "https://www.tradera.com/category/1001?af-car_brand="+brand+"&sortBy=LowestPrice"
            blocket_url = "https://www.blocket.se/bilar/sok?sortOrder=Billigast&q="+brand+"&filter=%7B%22key%22%3A%22sellerType%22%2C%22values%22%3A%5B%22Privat%22%5D%7D"
        
        blocket_result = requests.get(blocket_url)
        tradera_result = requests.get(tradera_url)

        blocket_doc = BeautifulSoup(blocket_result.text, "html.parser")
        tradera_doc = BeautifulSoup(tradera_result.text, "html.parser")

        blocket_priser = blocket_doc.find_all("div", class_="TextSubHeading__TextSubHeadingWrapper-sc-1c6hp2-0 doxbKq text-[17px] leading-6 flex flex-wrap items-center gap-1 justify-centers  group-[.is-gridview]:!max-h-36")
        print(blocket_priser)
        tradera_priser = tradera_doc.find_all("span", {"class": "text-nowrap font-weight-bold font-hansen pr-1"}) 
        
        

        
        for pris in blocket_priser:
            pris_text = pris.text.strip()
            print(pris_text)

            #klipper av "kr", "," och " "
            almost_clean_price = re.sub(r'\s+', '', pris_text.replace("kr", "").replace(",", ""))

            #klipper av reapriser inom parantes
            index = almost_clean_price.find('(')
            if index != -1:
                clean_price = almost_clean_price[:index]
            else: 
                clean_price = almost_clean_price
            print("3")
            #gör det till en int
            pris_int = int(clean_price)
            
            parent = pris.find_parent("a")
            print("1")
            title = pris.find_parent("a").find("h2").text.strip()

            if parent and parent.has_attr("href"):
                link = parent["href"]
                print("2")
                card_list.append({
                        "title": title,
                        "pris": pris_int,
                        "link": link
                    })
        for pris in tradera_priser:

            pris_text = pris.text.strip()

            #klipper av "kr", "," och " "
            almost_clean_price = re.sub(r'\s+', '', pris_text.replace("kr", "").replace(",", ""))

            #klipper av reapriser inom parantes
            index = almost_clean_price.find('(')
            if index != -1:
                clean_price = almost_clean_price[:index]
            else: 
                clean_price = almost_clean_price

            #gör det till en int
            #print(clean_price)
            pris_int = int(clean_price)

            parent = pris.find_parent("div", {"class": "item-card-inner-wrapper"}).find("a")
            
            if parent and parent.has_attr("href"):
                link = "https://www.tradera.com/" + parent["href"]
                title = parent["title"]
                
                card_list.append({
                        "title": title,
                        "pris": pris_int,
                        "link": link
                    })
    return render_template("scraper.html", title="scraper", card_list = card_list)
"""
@app.route("/scraper/<int:sort_id>", methods=["GET", "POST"])
def price_sorter(sort_id):

    if request.method == "POST":
        card_list.clear()
        brand = request.form.get('brand')

        tradera_url_mapping = {
            1: "https://www.tradera.com/category/1001?af-car_brand="+brand+"&sortBy=HighestPrice",  # URL for lowest-first
            2: "https://www.tradera.com/category/1001?af-car_brand="+brand+"&sortBy=LowestPrice",  # URL for highest-first
        }
        
        blocket_url_mapping = {
            1: "https://www.blocket.se/bilar/sok?q=BMW&filter=%7B%22key%22%3A%22sellerType%22%2C%22values%22%3A%5B%22Privat%22%5D%7D&filter=%7B%22key%22%3A%22make%22%2C%22values%22%3A%5B%22"+brand+"%22%5D%7D&sortOrder=Billigast",  # URL for lowest-first
            2: "https://www.blocket.se/bilar/sok?q=BMW&filter=%7B%22key%22%3A%22sellerType%22%2C%22values%22%3A%5B%22Privat%22%5D%7D&filter=%7B%22key%22%3A%22make%22%2C%22values%22%3A%5B%22"+brand+"%22%5D%7D&sortOrder=Dyrast"  # URL for highest-first
        }
        blocket_url = blocket_url_mapping.get(sort_id, "https://www.blocket.se/bilar/sok?filter=%7B%22key%22%3A%22make%22%2C%22values%22%3A%5B%22"+brand+"%22%5D%7D")
        tradera_url = tradera_url_mapping.get(sort_id, "https://www.tradera.com/category/1001?af-car_brand="+brand)
    
    
        
        #tradera_url = "https://www.tradera.com/category/1001?af-car_brand="+brand
        #blocket_url = "https://www.blocket.se/bilar/sok?filter=%7B%22key%22%3A%22make%22%2C%22values%22%3A%5B%22"+brand+"%22%5D%7D"
        

        blocket_result = requests.get(blocket_url)
        tradera_result = requests.get(tradera_url)

        blocket_doc = BeautifulSoup(blocket_result.text, "html.parser")
        tradera_doc = BeautifulSoup(tradera_result.text, "html.parser")

        blocket_priser = blocket_doc.find_all("div", {"class": "TextSubHeading__TextSubHeadingWrapper-sc-1c6hp2-0 doxbKq text-[17px] leading-6 flex flex-wrap items-center gap-1 justify-centers group-[.is-gridview]:!max-h-36"})
        tradera_priser = tradera_doc.find_all("span", {"class": "text-nowrap font-weight-bold font-hansen pr-1"}) 

        
        for pris in blocket_priser:
            pris_text = pris.text.strip()

            #klipper av "kr", "," och " "
            almost_clean_price = re.sub(r'\s+', '', pris_text.replace("kr", "").replace(",", ""))

            #klipper av reapriser inom parantes
            index = almost_clean_price.find('(')
            if index != -1:
                clean_price = almost_clean_price[:index]
            else: 
                clean_price = almost_clean_price

            #gör det till en int
            pris_int = int(clean_price)
            
            parent = pris.find_parent("a")
            title = pris.find_parent("a").find("h2").text.strip()

            if parent and parent.has_attr("href"):
                link = parent["href"]
                
                card_list.append({
                        "title": title,
                        "pris": pris_int,
                        "link": link
                    })
        for pris in tradera_priser:

            pris_text = pris.text.strip()
            print(pris_text)

            #klipper av "kr", "," och " "
            almost_clean_price = re.sub(r'\s+', '', pris_text.replace("kr", "").replace(",", ""))

            #klipper av reapriser inom parantes
            index = almost_clean_price.find('(')
            if index != -1:
                clean_price = almost_clean_price[:index]
            else: 
                clean_price = almost_clean_price

            #gör det till en int
            print(clean_price)
            pris_int = int(clean_price)

            parent = pris.find_parent("div", {"class": "item-card-inner-wrapper"}).find("a")
            print("1")

            if parent and parent.has_attr("href"):
                print("2")
                link = "https://www.tradera.com/" + parent["href"]
                title = parent["title"]
                
                card_list.append({
                        "title": title,
                        "pris": pris_int,
                        "link": link
                    })
    return render_template("scraper.html", title="scraper", card_list = card_list)
"""





#@app.route("/scraper/<int:sort_id>", methods=["GET"])
#def price_sorter(sort_id):
#    if sort_id == 1:
#        card_list.sort(key=lambda x: x["pris"]) 
#    elif sort_id == 2:
#        card_list.sort(key=lambda x: x["pris"], reverse=True)
#    return render_template("scraper.html", title="scraper", card_list=card_list)

#@app.route("/scraper/<int:sort_id>", methods=["GET"])
#def price_sorter(sort_id):
#    brand = ""
#    if sort_id == 1:
#        blocket_url = "https://www.blocket.se/bilar/sok?q=BMW&filter=%7B%22key%22%3A%22sellerType%22%2C%22values%22%3A%5B%22Privat%22%5D%7D&sortOrder=Billigast&filter=%7B%22key%22%3A%22make%22%2C%22values%22%3A%5B%22"+brand+"%22%5D%7D"
#        return render_template("scraper.html", title="scraper", card_list=card_list)
#    elif sort_id == 2:
#        blocket_url = "https://www.blocket.se/bilar/sok?q=BMW&filter=%7B%22key%22%3A%22sellerType%22%2C%22values%22%3A%5B%22Privat%22%5D%7D&filter=%7B%22key%22%3A%22make%22%2C%22values%22%3A%5B%22"+brand+"%22%5D%7D&sortOrder=Dyrast"
#        return render_template("scraper.html", title="scraper", card_list=card_list)
#    else:
#        blocket_url = "https://www.blocket.se/bilar/sok?filter=%7B%22key%22%3A%22make%22%2C%22values%22%3A%5B%22"+brand+"%22%5D%7D"



if __name__ == "__main__":
    app.run(debug= True, port=5502)





    