import os
import json
import time
from pathlib import Path
import random
import re
from curl_cffi import requests
from bs4 import BeautifulSoup

def fetch_walmart_seller_data(seller_id):
    url = f"https://www.walmart.com/global/seller/{seller_id}/cp/shopall"
    
    
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
    ]
    
    accept_languages = [
        'en-US,en;q=0.9',
        'zh-CN,zh;q=0.9,en;q=0.8',
        'en-GB,en;q=0.9',
        'fr-FR,fr;q=0.9,en;q=0.8',
        'de-DE,de;q=0.9,en;q=0.8'
    ]
    
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': random.choice(accept_languages),
        'Accept-Encoding': 'gzip, deflate, br',
        'Cache-Control': 'max-age=0',
        'User-Agent': random.choice(user_agents),
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1'
    }
    
    try:
        response = requests.get(url, headers=headers, impersonate="chrome110")
        response.raise_for_status()
        print(response.text)
        # Save the HTML response to a file for debugging
        debug_dir = Path("debug_html")
        debug_dir.mkdir(exist_ok=True)
        
        timestamp = int(time.time())
        debug_file = debug_dir / f"walmart_seller_{seller_id}_{timestamp}.html"
        
        with open(debug_file, "w", encoding="utf-8") as f:
            f.write(response.text)
            
        print(f"Saved HTML response to {debug_file}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract seller name
        seller_name = soup.select_one('[data-testid="seller-name"]')
        name = seller_name.text.strip() if seller_name else "Not found"
        
        # Extract address
        address = "Not found"
        di_elements = soup.select('.di')
        for element in di_elements:
            mb3 = element.select_one('.mb3')
            if mb3:
                address = mb3.text.strip()
                break
        
        # Extract phone
        phone = "Not found"
        for element in di_elements:
            phone_span = element.select_one('.ld-Phone + span')
            if phone_span and phone_span.text.strip():
                phone = phone_span.text.strip()
                break
        
        # Extract rating using regular expression
        rating = "Not found"
        rating_pattern = r'(\d+(\.\d+)?) out of \d+'
        rating_text = soup.text
        rating_match = re.search(rating_pattern, rating_text)
        if rating_match:
            rating = rating_match.group(1)
            
        # Extract ratings count
        ratings_count = "0"
        # Look for patterns like "1,504 ratings" in the text
        ratings_count_pattern = r'([\d,]+)\s+ratings'
        ratings_count_match = re.search(ratings_count_pattern, soup.text)
        if ratings_count_match:
            ratings_count = ratings_count_match.group(1)
            # Remove commas from the number
            ratings_count = ratings_count.replace(',', '')
            ratings_count = int(ratings_count[1:])
        
        # Extract reviews count
        reviews_count = "0"
        # Look for patterns like "267 reviews" in the text
        reviews_pattern = r'([\d,]+)\s+reviews'
        reviews_match = re.search(reviews_pattern, soup.text)
        if reviews_match:
            reviews_count = reviews_match.group(1)
            # Remove commas from the number
            reviews_count = reviews_count.replace(',', '')
        
        # Extract items count
        items_count = "0"
        items_count_element = soup.select_one('h2[style="color:undefined"]')
        if items_count_element:
            items_count = items_count_element.text.strip()
            # Extract only numeric characters and decimal point
            items_count = ''.join(c for c in items_count if c.isdigit() or c == '.')
            if not items_count:
                items_count = "0"
        
        seller_data = {
            "seller_id": seller_id,
            "name": name,
            "address": address,
            "phone": phone,
            "rating": rating,
            "items_count": items_count,
            "ratings_count": ratings_count,
            "reviews_count": reviews_count
        }

        if seller_data["name"] == "Not found":
            return None
        
        return seller_data
    except requests.RequestsError as e:
        print(f"Error fetching data for seller {seller_id}: {e}")
        return None

def process_seller(seller_id, data_dir):
    seller_data = fetch_walmart_seller_data(seller_id)
    
    if seller_data:
        file_path = os.path.join(data_dir, f"{seller_id}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(seller_data, f, ensure_ascii=False, indent=2)
        print(f"Saved data for seller {seller_id}")

def main():
    # Create data directory
    data_dir = "data/walmart"
    Path(data_dir).mkdir(parents=True, exist_ok=True)
    
    for seller_id in range(101100001, 101110000):
        # Check if file already exists
        process_seller(str(seller_id), data_dir)
        print(f"Processed seller {seller_id}")
        time.sleep(0.2)  # Wait 0.2 seconds between requests

if __name__ == "__main__":
    # main()
    print(fetch_walmart_seller_data(101138407))