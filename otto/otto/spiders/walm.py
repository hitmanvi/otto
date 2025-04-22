import scrapy
import json
from pathlib import Path
import re

class WalmSpider(scrapy.Spider):
    name = "walm"
    allowed_domains = ["www.walmart.com"]
    start_urls = [f"https://www.walmart.com/global/seller/{i}/cp/shopall" for i in range(5001, 20000)]
    
    def __init__(self, *args, **kwargs):
        super(WalmSpider, self).__init__(*args, **kwargs)
        self.output_file = Path('walmart_sellers.json')
        if self.output_file.exists():
            self.output_file.unlink()
    
    def parse(self, response):
        if 'Robot or human?' in response.text:
            yield scrapy.Request(response.url, callback=self.parse_seller)
            return
        # Extract seller details
        seller_name = response.css('[data-testid="seller-name"]::text').get()
        name = seller_name.strip() if seller_name else "Not found"
        
        # Extract address
        address = "".join(response.css('.mb2.mr5.flex.flex-row').css('::text').getall())
        
        # Extract phone
        phone = response.css('[link-identifier="callBusinessClick"]::text').get()
        
        # Extract rating using regular expression
        rating = "Not found"
        rating_pattern = r'(\d+(\.\d+)?) out of \d+'
        rating_text = response.text
        rating_match = re.search(rating_pattern, rating_text)
        if rating_match:
            rating = rating_match.group(1)
        

        # Extract ratings count
        ratings_count = "0"
        # Look for patterns like "1,504 ratings" in the text
        ratings_count_pattern = r'([\d,]+)\s+ratings'
        ratings_count_match = re.search(ratings_count_pattern, response.text)
        if ratings_count_match:
            ratings_count = ratings_count_match.group(1)
            # Remove commas from the number
            ratings_count = ratings_count.replace(',', '')
            
        # Extract reviews count
        reviews_count = "0"
        # Look for patterns like "267 reviews" in the text
        reviews_pattern = r'([\d,]+)\s+reviews'
        reviews_match = re.search(reviews_pattern, response.text)
        if reviews_match:
            reviews_count = reviews_match.group(1)
            # Remove commas from the number
            reviews_count = reviews_count.replace(',', '')
        
        # Extract items count
        items_count = "0"
        items_count_element = response.css('h2[style="color:undefined"]::text').get()
        if items_count_element:
            items_count = items_count_element.strip()
            # Extract only numeric characters and decimal point
            items_count = ''.join(c for c in items_count if c.isdigit() or c == '.')
            if not items_count:
                items_count = "0"

        
        # Extract seller_id from the URL with the new format
        # https://www.walmart.com/global/seller/{i}/cp/shopall
        url_parts = response.url.split('/')
        seller_index = url_parts.index('seller') if 'seller' in url_parts else -1
        seller_id = url_parts[seller_index + 1] if seller_index != -1 else "shopall"
        
        result = {
            'seller_id': seller_id,
            'name': name,
            'address': address,
            'phone': phone,
            'rating': rating,
            'items_count': items_count,
            'ratings_count': ratings_count,
            'reviews_count': reviews_count
        }
        
        # Save to JSON file
        with open(self.output_file, 'a', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False)
            f.write('\n')
        
        yield result
