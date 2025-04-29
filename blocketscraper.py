from blocket_api import BlocketAPI, Region
api = BlocketAPI("356c0349b77b33f46479ed2cf0145bd838692942")
card_list = []
def blocket_scrape_advanced(make_search, fuel_search, chassi_search, price_low, price_high):
    search_result = api.motor_search(
            make=[make_search],
            fuel=[fuel_search],
            chassi=[chassi_search],
            price=(price_low, price_high),
            page=1
            )
        

    for x in search_result['cars']:
        title = x.get('heading', '')
        pris = x.get('price', {}).get('amount', '')
        link = x.get('link', '')
        card_list.append({
            "title": title,
            "pris": pris,
            "link": link
        })
    return card_list

def blocket_scrape_simple(s_search):
    search_results = api.custom_search(s_search)

    for x in search_results['data']:
        title = x.get('subject', '')
        pris = x.get('price', {}).get('value', '')
        link = x.get('share_url', '')
        card_list.append({
            "title": title,
            "pris": pris,
            "link": link
        })

    return card_list