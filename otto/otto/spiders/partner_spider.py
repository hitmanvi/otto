import scrapy
from pathlib import Path
import redis
import os

class PartnerSpider(scrapy.Spider):
    name = 'partner'
    allowed_domains = ['otto.de']
    base_url = 'https://www.otto.de'
    
    def __init__(self, *args, **kwargs):
        super(PartnerSpider, self).__init__(*args, **kwargs)
        # Create data directory
        Path("data").mkdir(exist_ok=True)
        
        # Connect to Redis
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        
    def _is_completed(self, partner_id):
        return bool(self.redis_client.sismember('completed_partners', partner_id))
        
    def _mark_completed(self, partner_id):
        self.redis_client.sadd('completed_partners', partner_id)
    
    def start_requests(self):
        # Generate partner IDs from 1000000 to 2000000
        for partner_id in range(1000001, 2000001):
            # Skip if already processed
            if self._is_completed(partner_id):
                self.logger.info(f'Partner {partner_id} already processed - skipping')
                continue
                
            # Skip if file exists
            filename = f"data/{partner_id}.html"
            if Path(filename).exists():
                self.logger.info(f'File {filename} already exists - skipping')
                continue
                
            url = f"{self.base_url}/partner-details/partner/{partner_id}/section/imprint"
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                cb_kwargs={'partner_id': partner_id},
                dont_filter=True
            )
    
    def parse(self, response, partner_id):
        if '1995 bis 2025 OTTO' in response.text:
            self.logger.info('Found copyright text - stopping spider')
            raise scrapy.exceptions.CloseSpider(f'Found copyright text for partner {partner_id}')
            
        if response.status == 404:
            self.logger.info(f'Got 404 for partner {partner_id} - marking as completed')
            self._mark_completed(partner_id)
            return
            
        if '1995 bis 2025 OTTO' not in response.text:
            # Save response content
            filename = f"data/{partner_id}.html"
            with open(filename, 'wb') as f:
                f.write(response.body)
            self.logger.info(f'Saved partner {partner_id} info to {filename}')
            
            # Mark as completed
            self._mark_completed(partner_id)