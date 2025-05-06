from traderascraper import tradera_scrape, tradera_scrape_single_thread
from blocketscraper import blocket_scrape_advanced, blocket_scrape_simple
from kvdscraper import kvd_scrape_simple, kvd_scrape_advanced
from flask import Flask, jsonify, render_template, request
from db import init_db
import re




app = Flask(__name__)

card_list = []
init_db()

def add_unique_results(results):
    for result in results:
        if not any(card['link'] == result['link'] for card in card_list):
            card_list.append(result)

def clean_price_to_int(price):
    price = str(price)
    cleaned = re.sub(r"[^\d]", "", price)
    return int(cleaned) if cleaned else 0

def price_limit_cutoff(price_low, price_high, card_list):
    return [
        card for card in card_list
        if price_low <= card['pris'] <= price_high
    ]

@app.route("/scraper/sort", methods=["GET", "POST"])
def card_list_sorter():
    if request.form.get("sort_order") == 'asc':
        card_list.sort(key=lambda x: x["pris"])
    elif request.form.get("sort_order") == 'desc':
        card_list.sort(key=lambda x: x["pris"], reverse=True)

    return render_template("scraper.html", card_list = card_list)

@app.route("/scraper", methods=["GET", "POST"])
def advanced_search():
    card_list.clear()
    
    if request.method ==  "POST":
        card_list.clear()

        make_pre_cap = request.form.get('brand')
        fuel_pre_cap = request.form.get('fuel')
        chassi_pre_cap = request.form.get('chassi')
        price_low = int(request.form.get('min_input'))
        price_high = int(request.form.get('max_input'))
        if make_pre_cap.upper() != "BMW" or "BYD" or "DFSK" or "DS" or "GMC" or "LEVC" or "MAN" or "MG" or "NIO" or "SEAT" or "XPENG" or "AMC" or "DKW" or "VW" or "ABT":
            make_search = make_pre_cap.capitalize()
        else: 
            make_search = make_pre_cap.upper()
        fuel_search = fuel_pre_cap.capitalize()
        chassi_search = chassi_pre_cap.capitalize()
        
        blocket_results = blocket_scrape_advanced(make_search, fuel_search, chassi_search, price_low, price_high)
        tradera_results = tradera_scrape(make_search)
        kvd_results = kvd_scrape_advanced(make_search, fuel_search, price_low, price_high)
        add_unique_results(blocket_results)
        add_unique_results(tradera_results)
        add_unique_results(kvd_results)

        for card in card_list:
            card["pris"] = clean_price_to_int(card["pris"])

        card_list[:] = price_limit_cutoff(price_low, price_high, card_list)

    return render_template("scraper.html", title="scraper", card_list = card_list)

@app.route("/scraper/simple-search", methods=["GET", "POST"])
def simple_search():
    card_list.clear()
    if request.method ==  "POST":
        card_list.clear()
        s_search = request.form.get('simple_search')
        price_low = int(request.form.get('min_input'))
        price_high = int(request.form.get('max_input'))
        
        blocket_results = blocket_scrape_simple(s_search)
        tradera_results = tradera_scrape(s_search)
        #tradera_results = tradera_scrape_single_thread(s_search)
        kvd_results = kvd_scrape_simple(s_search)
        add_unique_results(blocket_results)
        add_unique_results(tradera_results)
        add_unique_results(kvd_results)

        for card in card_list:
            card["pris"] = clean_price_to_int(card["pris"])

        card_list[:] = price_limit_cutoff(price_low, price_high, card_list)

        
    return render_template("scraper.html", title="scraper", card_list = card_list)

if __name__ == "__main__":
    app.run(debug= True, port=5502)