from blocket_api import BlocketAPI, Region
from traderascraper import tradera_scrape
from blocketscraper import blocket_scrape_advanced, blocket_scrape_simple

api = BlocketAPI("356c0349b77b33f46479ed2cf0145bd838692942")
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

card_list = []
@app.route("/scraper", methods=["GET", "POST"])
def advanced_search():
    card_list.clear()
    
    if request.method ==  "POST":
        card_list.clear()
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
        
        blocket_results = blocket_scrape_advanced(make_search, fuel_search, chassi_search, price_low, price_high)
        tradera_results = tradera_scrape(make_search)
        card_list.extend(blocket_results)
        card_list.extend(tradera_results)

    return render_template("scraper.html", title="scraper", card_list = card_list)

@app.route("/scraper/simple-search", methods=["GET", "POST"])
def simple_search():
    card_list.clear()
    if request.method ==  "POST":
        card_list.clear()
        s_search = request.form.get('simple_search')
        
        blocket_results = blocket_scrape_simple(s_search)
        tradera_results = tradera_scrape(s_search)
        card_list.extend(blocket_results)
        card_list.extend(tradera_results)
        
    return render_template("scraper.html", title="scraper", card_list = card_list)






if __name__ == "__main__":
    app.run(debug= True, port=5502)