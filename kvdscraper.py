from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import requests
import time

card_list = []

def scroll_to_load_all_cards(driver, pause_time=1, step=300, max_scrolls=200):
    last_height = driver.execute_script("return document.body.scrollHeight")
    total_scrolled = 0
    scrolls = 0

    while scrolls < max_scrolls:
        driver.execute_script(f"window.scrollBy(0, {step});")
        time.sleep(pause_time)

        total_scrolled += step
        scrolls += 1

        new_height = driver.execute_script("return document.body.scrollHeight")
        if total_scrolled >= new_height:
            break
def kvd_scrape_simple(brand):
    options = Options()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options) 
    
    kvd_url = f"https://www.kvd.se/begagnade-bilar?terms={brand}"
    driver.get(kvd_url)
    #kvd_result = requests.get(kvd_url)
    
    time.sleep(1)
    try:
        cookie_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"))  # or adjust selector
        )
        cookie_button.click()
        print("Cookie consent accepted.")
    except:
        print("No cookie popup appeared or it was already handled.")

    time.sleep(2)

    scroll_to_load_all_cards(driver, pause_time=0.05, step=300, max_scrolls=100)
    


    soup = BeautifulSoup(driver.page_source, "html.parser")

    card_list = []

    cards = soup.find_all("a", {"data-testid": "product-card"})

    for card in cards:
        title_tag = card.find("p", {"class": "Title__Container-sc-1pnhtgy-0 dUjCyV"})
        subtitle_tag = card.find("p", {"class": "Subtitle__Container-sc-mtvkrl-0 dQIixS"})
        #price_tag = card.find("span", {"class": "FinancingRowItem__PriceValue-sc-t6ke1g-2 epRKgX"})
        price_tag = card.find("span", string=lambda s: s and "kr" in s)
        img_tag = card.find("img", {"class" : "styles__LazyImg-sc-1tncjpw-2 bEPGnb media__image"})
        img_url = None
        if img_tag:
            img_url = img_tag.get("src") or img_tag.get("data-src")
  

        if not (title_tag and subtitle_tag and price_tag and img_tag):
            continue  # Skip incomplete cards

        img_url = img_tag.get("src")
        link = "https://www.kvd.se" + card.get("href")

        card_list.append({
            "title": title_tag.text + ", " + subtitle_tag.text,
            "pris": price_tag.text.strip(),
            "link": link,
            "img": img_url
        })
    driver.quit()
    return card_list

def kvd_scrape_advanced(make_search, fuel_search, price_low, price_high):
    options = Options()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options) 

    if fuel_search.lower() == "bensin":
        fuel_search = "petrol"
    if fuel_search.lower() == "el":
        fuel_search = "electric"
    price_low = str(price_low)
    price_high = str(price_high)


    kvd_url = "https://www.kvd.se/begagnade-bilar?brand="+make_search+"&fuel="+fuel_search+"&cardealerPriceFrom="+price_low+"&cardealerPriceTo="+price_high
    driver.get(kvd_url)
    #kvd_result = requests.get(kvd_url)
    time.sleep(1)
    try:
        cookie_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"))  # or adjust selector
        )
        cookie_button.click()
        print("Cookie consent accepted.")
    except:
        print("No cookie popup appeared or it was already handled.")

    time.sleep(2)

    scroll_to_load_all_cards(driver, pause_time=0.05, step=300, max_scrolls=100)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    cards = soup.find_all("a", {"data-testid": "product-card"})

    for card in cards:
        title_tag = card.find("p", {"class": "Title__Container-sc-1pnhtgy-0 dUjCyV"})
        subtitle_tag = card.find("p", {"class": "Subtitle__Container-sc-mtvkrl-0 dQIixS"})
        #price_tag = card.find("span", {"class": "FinancingRowItem__PriceValue-sc-t6ke1g-2 epRKgX"})
        price_tag = card.find("span", string=lambda s: s and "kr" in s)
        img_tag = card.find("img", {"class" : "styles__LazyImg-sc-1tncjpw-2 bEPGnb media__image"})
        img_url = None
        if img_tag:
            img_url = img_tag.get("src") or img_tag.get("data-src")

        if not (title_tag and subtitle_tag and price_tag and img_tag):
            continue  # Skip incomplete cards

        img_url = img_tag.get("src")
        link = "https://www.kvd.se" + card.get("href")

        card_list.append({
            "title": title_tag.text + ", " + subtitle_tag.text,
            "pris": price_tag.text.strip(),
            "link": link,
            "img": img_url
        })
    driver.quit()
    return card_list