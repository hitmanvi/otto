import scrapy
import json
import csv
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
            
        # 创建CSV文件并写入表头
        # 根据 start id 和 end id 创建CSV文件名
        start_id = getattr(self, 'start_id', 10000)
        end_id = getattr(self, 'end_id', 20000)
        self.csv_file = Path(f'seller_data/sellers_{start_id}_to_{end_id}.csv')
        csv_exists = self.csv_file.exists()
        
        self.csv_fieldnames = [
            'seller_id', 'name', 'address', 'phone', 
            'rating', 'items_count', 'ratings_count', 'reviews_count'
        ]
        
        if not csv_exists:
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.csv_fieldnames)
                writer.writeheader()
    
    def start_requests(self):
        # 生成起始URL，跳过已爬取的卖家
        # 从配置中获取爬取范围
        start_id = getattr(self, 'start_id', 10000)
        end_id = getattr(self, 'end_id', 20000)
        
        # 确保是整数类型
        start_id = int(start_id)
        end_id = int(end_id)
        
        for seller_id in range(start_id, end_id):
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
        items_count = response.css('.f6.f5-m.fw3.ml1.mt1-xl.gray.normal.self-center::text').get()
        if items_count:
            # Extract only the numeric part from items_count
            numeric_pattern = r'([\d,]+)'
            numeric_match = re.search(numeric_pattern, items_count)
            if numeric_match:
                items_count = numeric_match.group(1)
                items_count = items_count.replace(',', '')
        else:
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
        
        # 直接写入CSV文件
        with open(self.csv_file, 'a', newline='', encoding='utf-8') as f:
            if result['name'] != "Not found":   
                writer = csv.DictWriter(f, fieldnames=self.csv_fieldnames)
                writer.writerow(result)
        
        # # 保存到单独的文件
        # output_file = self.data_dir / f'seller_{seller_id}.json'
        # with open(output_file, 'w', encoding='utf-8') as f:
        #     json.dump(result, f, ensure_ascii=False, indent=2)
        
        # 记录已爬取的卖家ID
        with open(self.crawled_file, 'a') as f:
            f.write(f"{seller_id}\n")
        
        yield result
