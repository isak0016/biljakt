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
        
    try:
        for x in search_result['cars']:
            
            title = x.get('heading', '')
            pris = x.get('price', {}).get('amount', '')
            link = x.get('link', '')
            images = x.get('car', {}).get('images', [])
            img = images[0].get('image', '') if images else x.get('thumbnail', '')

            card_list.append({
                "title": title,
                "pris": pris,
                "link": link,
                "img": img
            })
            
    except:
        print("no matches on blocket for this search")

    return card_list

def blocket_scrape_simple(s_search):
    search_results = api.custom_search(s_search)

    for x in search_results['data']:
        title = x.get('subject', '')
        pris = x.get('price', {}).get('value', '')
        link = x.get('share_url', '')

        images = x.get('images', [])
        img = images[0].get('url', '') if images else ''

        card_list.append({
            "title": title,
            "pris": pris,
            "link": link,
            "img": img
        })

        
    return card_list