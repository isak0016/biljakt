from bs4 import BeautifulSoup
import requests

card_list = []

def kvd_scrape_simple(brand):

    kvd_url = "https://www.kvd.se/begagnade-bilar?terms="+brand

    kvd_result = requests.get(kvd_url)

    soup = BeautifulSoup(kvd_result.text, "html.parser")

    kvd_priser = soup.find_all("span", {"class": "FinancingRowItem__PriceValue-sc-t6ke1g-2 epRKgX"})

    for pris in kvd_priser:
        parent = pris.find_parent("a")
        pris_clean = pris.text
        
        if parent and parent.has_attr("href"):
            link = "https://www.kvd.se" + parent["href"]
            title = parent.find("p", {"class": "Title__Container-sc-1pnhtgy-0 dUjCyV"}).text
            subtitle = parent.find("p", {"class": "Subtitle__Container-sc-mtvkrl-0 dQIixS"}).text
            card_list.append({
                    "title": title + ", " + subtitle,
                    "pris": pris_clean,
                    "link": link
                })
    return card_list

def kvd_scrape_advanced(make_search, fuel_search, price_low, price_high):

    if fuel_search.lower() == "bensin":
        fuel_search = "petrol"
    if fuel_search.lower() == "el":
        fuel_search = "electric"
    price_low = str(price_low)
    price_high = str(price_high)


    kvd_url = "https://www.kvd.se/begagnade-bilar?brand="+make_search+"&fuel="+fuel_search+"&cardealerPriceFrom="+price_low+"&cardealerPriceTo="+price_high
    print(kvd_url)
    kvd_result = requests.get(kvd_url)

    soup = BeautifulSoup(kvd_result.text, "html.parser")

    kvd_priser = soup.find_all("span", {"class": "FinancingRowItem__PriceValue-sc-t6ke1g-2 epRKgX"})
    print(kvd_priser)
    for pris in kvd_priser:
        parent = pris.find_parent("a")
        pris_clean = pris.text
        
        if parent and parent.has_attr("href"):
            link = "https://www.kvd.se" + parent["href"]
            title = parent.find("p", {"class": "Title__Container-sc-1pnhtgy-0 dUjCyV"}).text
            subtitle = parent.find("p", {"class": "Subtitle__Container-sc-mtvkrl-0 dQIixS"}).text
            card_list.append({
                    "title": title + ", " + subtitle,
                    "pris": pris_clean,
                    "link": link
                })
    return card_list