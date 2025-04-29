from blocket_api import BlocketAPI, Region
from scrapetest import tradera_scrape

api = BlocketAPI("356c0349b77b33f46479ed2cf0145bd838692942")
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

card_list = []
@app.route("/scraper", methods=["GET", "POST"])
def api_test_search():
    card_list.clear()
    
    if request.method ==  "POST":
        make_pre_cap = request.form.get('brand')
        fuel_pre_cap = request.form.get('fuel')
        chassi_pre_cap = request.form.get('chassi')
        price_low = int(request.form.get('price_low'))
        price_high = int(request.form.get('price_high'))
        if make_pre_cap.upper() != "BMW" or "BYD" or "DFSK" or "DS" or "GMC" or "LEVC" or "MAN" or "MG" or "NIO" or "SEAT" or "XPENG" or "AMC" or "DKW" or "VW" or "ABT":
            make_search = make_pre_cap.capitalize()
        else: 
            make_search = make_pre_cap.upper()
        fuel_search = fuel_pre_cap.capitalize()
        chassi_search = chassi_pre_cap.capitalize()
        
        search_result = api.motor_search(
            make=[make_search],
            fuel=[fuel_search],
            chassi=[chassi_search],
            price=(price_low, price_high),
            page=1
        #    make=["Audi", "Ford"],
        #    fuel=["Diesel"],
        #    chassi=["Cab"],
        #    price=(50000, 100000),
        #    page=1,
            )
        

        for x in search_result['cars']:
                #print(x)
            title = x.get('heading', '')
            pris = x.get('price', {}).get('amount', '')
            link = x.get('link', '')
            card_list.append({
                                "title": title,
                                "pris": pris,
                                "link": link
                                })
            
        tradera_results = tradera_scrape(make_search)
        card_list.extend(tradera_results)

    return render_template("scraper.html", title="scraper", card_list = card_list)

if __name__ == "__main__":
    app.run(debug= True, port=5502)