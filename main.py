import requests
from bs4 import BeautifulSoup
import os
import json
import time
from pathlib import Path


def fetch_walmart_seller_data(seller_id):
    url = f"https://www.walmart.com/global/seller/{seller_id}"
    
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,ja;q=0.6',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Cache-Control': 'max-age=0',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
        'Sec-Ch-Ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"macOS"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
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
        
        seller_data = {
            "seller_id": seller_id,
            "name": name,
            "address": address,
            "phone": phone
        }
        
        return seller_data
    except requests.exceptions.RequestException as e:
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
    
    for seller_id in range(1, 19093):
        # Check if file already exists
        file_path = os.path.join(data_dir, f"{seller_id}.json")
        if not os.path.exists(file_path):
            process_seller(str(seller_id), data_dir)
            time.sleep(0.2)  # Wait 0.2 seconds between requests

if __name__ == "__main__":
    main()