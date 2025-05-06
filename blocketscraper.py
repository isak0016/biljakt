from blocket_api import BlocketAPI, Region
from db import generate_token, save_new_token_if_unseen
from dotenv import load_dotenv
import os
load_dotenv()
BLOCKET_API = os.getenv("BLOCKET_API", "")
api = BlocketAPI(BLOCKET_API)
card_list = []
def blocket_scrape_advanced(make_search, fuel_search, chassi_search, price_low, price_high):
    card_list.clear()
    search_result = api.motor_search(
            make=[make_search],
            fuel=[fuel_search],
            chassi=[chassi_search],
            price=(price_low, price_high),
            page=1
            )
        
    try:
        for x in search_result['cars']:
            token = generate_token(x)
            
            title = x.get('heading', '')
            pris = x.get('price', {}).get('amount', '')
            link = x.get('link', '')
            images = x.get('car', {}).get('images', [])
            img = images[0].get('image', '') if images else x.get('thumbnail', '')

            

            loc = x.get('car', {}).get('location', {})
            region = loc.get('region', '')
            municipality = loc.get('municipality', '')
            location_str = ", ".join(part for part in [region, municipality] if part)
           

            card_list.append({
                "title": title,
                "pris": pris,
                "link": link,
                "img": img,
                "location": location_str,
                "token": token
            })

            save_new_token_if_unseen(token, title, link)
            
    except:
        print("no matches on blocket for this search")

    return card_list

def blocket_scrape_simple(s_search):
    card_list.clear()
    search_results = api.custom_search(s_search)

    for x in search_results['data']:
        token = generate_token(x)

        title = x.get('subject', '')
        pris = x.get('price', {}).get('value', '')
        link = x.get('share_url', '')

        images = x.get('images', [])
        img = images[0].get('url', '') if images else ''

        location_list = x.get('location', [])
        location_str = ", ".join(loc.get('name', '') for loc in location_list)

        card_list.append({
            "title": title,
            "pris": pris,
            "link": link,
            "img": img,
            "location": location_str,
            "token": token
        })

        save_new_token_if_unseen(token, title, link)

        
    return card_list