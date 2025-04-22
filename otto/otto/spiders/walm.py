import scrapy
import json
from pathlib import Path
import re
import os
from scrapy.exceptions import CloseSpider

class WalmSpider(scrapy.Spider):
    name = "walm"
    allowed_domains = ["www.walmart.com"]
    
    def __init__(self, *args, **kwargs):
        super(WalmSpider, self).__init__(*args, **kwargs)
        # 创建数据存储目录
        self.data_dir = Path('seller_data')
        self.data_dir.mkdir(exist_ok=True)
        
        # 创建已爬取卖家ID的记录文件
        self.crawled_file = Path('crawled_sellers.txt')
        if not self.crawled_file.exists():
            self.crawled_file.touch()
        
        # 读取已爬取的卖家ID
        with open(self.crawled_file, 'r') as f:
            self.crawled_sellers = set(f.read().splitlines())
    
    def start_requests(self):
        # 生成起始URL，跳过已爬取的卖家
        for seller_id in range(5001, 10000):
            if str(seller_id) not in self.crawled_sellers:
                url = f"https://www.walmart.com/global/seller/{seller_id}/cp/shopall"
                yield scrapy.Request(url, callback=self.parse, meta={'seller_id': seller_id})
    
    def parse(self, response):
        seller_id = response.meta['seller_id']
        
        # 检查是否是307重定向
        if response.status == 307:
            self.logger.error(f"Received 307 redirect for seller {seller_id}, stopping spider...")
            raise CloseSpider('Received 307 redirect')
        
        # 检查是否是机器人验证页面
        if 'Robot or human?' in response.text:
            self.logger.info(f"Received robot check for seller {seller_id}, skipping...")
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
        ratings_count_pattern = r'([\d,]+)\s+ratings'
        ratings_count_match = re.search(ratings_count_pattern, response.text)
        if ratings_count_match:
            ratings_count = ratings_count_match.group(1)
            ratings_count = ratings_count.replace(',', '')
        
        # Extract reviews count
        reviews_count = "0"
        reviews_pattern = r'([\d,]+)\s+reviews'
        reviews_match = re.search(reviews_pattern, response.text)
        if reviews_match:
            reviews_count = reviews_match.group(1)
            reviews_count = reviews_count.replace(',', '')
        
        # Extract items count
        items_count = "0"
        items_count_element = response.css('h2[style="color:undefined"]::text').get()
        if items_count_element:
            items_count = items_count_element.strip()
            items_count = ''.join(c for c in items_count if c.isdigit() or c == '.')
            if not items_count:
                items_count = "0"
        
        result = {
            'seller_id': str(seller_id),
            'name': name,
            'address': address,
            'phone': phone,
            'rating': rating,
            'items_count': items_count,
            'ratings_count': ratings_count,
            'reviews_count': reviews_count
        }
        
        # 保存到单独的文件
        output_file = self.data_dir / f'seller_{seller_id}.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        # 记录已爬取的卖家ID
        with open(self.crawled_file, 'a') as f:
            f.write(f"{seller_id}\n")
        
        yield result
