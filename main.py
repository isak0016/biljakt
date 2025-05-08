from traderascraper import tradera_scrape, tradera_scrape_single_thread
from blocketscraper import blocket_scrape_advanced, blocket_scrape_simple
from kvdscraper import kvd_scrape_simple, kvd_scrape_advanced
from flask import Flask, jsonify, render_template, request
from db import init_car_db, init_user_db, save_new_user_if_unseen, auto_service_get_user, auto_service_get_car, CAR_DB_PATH
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from email.mime.text import MIMEText
import smtplib
import sqlite3
import time
import re
import os
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()
init_car_db()
init_user_db()
card_list = []

def add_unique_results(results, target_list):
    for result in results:
        if not any(card['link'] == result['link'] for card in target_list):
            target_list.append(result)

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
    if request.method == "POST":
        s_search = request.form.get('simple_search')
        price_low = int(request.form.get('min_input', 0))
        price_high = int(request.form.get('max_input', 10**9))

        card_list[:] = run_combined_search(s_search, price_low, price_high)

    return render_template("scraper.html", title="scraper", card_list=card_list)

@app.route("/scraper/mail-list", methods=["POST"])
def add_user_to_mail_list():
    if request.method ==  "POST":
        user_email = request.form.get("email_input")
        user_search_words = request.form.get("user_search_words")
        valid = re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', user_email)
        if valid: 
            save_new_user_if_unseen(user_email, user_search_words)

    return render_template("scraper.html", title="scraper", card_list = card_list)

def run_combined_search(s_search, price_low, price_high):
    temp_card_list = []

    blocket_results = blocket_scrape_simple(s_search)
    tradera_results = tradera_scrape(s_search)
    kvd_results = kvd_scrape_simple(s_search)

    add_unique_results(blocket_results, temp_card_list)
    add_unique_results(tradera_results, temp_card_list)
    add_unique_results(kvd_results, temp_card_list)

    for card in temp_card_list:
        card["pris"] = clean_price_to_int(card["pris"])

    return price_limit_cutoff(price_low, price_high, temp_card_list)

def auto_service():
    users = auto_service_get_user()

    for user in users:
        user_email = user[0]
        search_words = user[1]
        last_seen = datetime.fromisoformat(user[2])

        results = run_combined_search(search_words, 0, 10**6)
        new_items_for_user = []

        for card in results:
            
            conn = sqlite3.connect(CAR_DB_PATH)
            c = conn.cursor()
            c.execute("SELECT seen_at FROM seen_items WHERE token = ?", (card["token"],))
            row = c.fetchone()
            conn.close()

            if row:
                seen_at = datetime.fromisoformat(row[0])
                if seen_at > last_seen:
                    new_items_for_user.append(card)
        if new_items_for_user:
            send_email(user_email, new_items_for_user)

            # Update user_seen_at in user DB
            #conn = sqlite3.connect(USER_DB_PATH)
            #c = conn.cursor()
            #c.execute("UPDATE mail_list SET user_seen_at = ? WHERE email = ?", (datetime.now().isoformat(), user_email))
            #conn.commit()
            #conn.close()
def send_email(user_email, new_items_for_user):

    EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")

    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        raise ValueError("EMAIL_ADDRESS or EMAIL_PASSWORD is not set in environment.")

    content = "New cars found:\n\n"
    for card in new_items_for_user:
        content += f"{card['title']} - {card['pris']} SEK\n{card['link']}\n\n"
        
    msg = MIMEText(content)
    msg['Subject'] = "New car listings"
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = user_email

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        print(f"Email sent to {user_email}")
    except Exception as e:
            print(f"Failed to send email: {e}")

scheduler = BackgroundScheduler()
scheduler.add_job(auto_service, 'cron', hour=14, minute=30)
scheduler.start()
if __name__ == "__main__":
    app.run(debug= True, port=5502)