import scrapy


class WalmSpider(scrapy.Spider):
    name = "walm"
    allowed_domains = ["www.walmart.com"]
    start_urls = [f"https://www.walmart.com/global/seller/{i}" for i in range(5001, 20000)]

    def parse(self, response):
        # Extract all product links from the page
        links = response.css('a::attr(href)').getall()
        
        # Filter for seller profile links
        seller_links = [link for link in links if '/seller/' in link]
        
        # Process each seller link
        for link in seller_links:
            # Ensure absolute URL
            if not link.startswith('http'):
                link = response.urljoin(link)
            yield scrapy.Request(link, callback=self.parse_seller)
    
    def parse_seller(self, response):
        if 'Robot or human?' in response.text:
            yield scrapy.Request(response.url, callback=self.parse_seller)
            return
        # Extract seller details
        seller_name = response.css('[data-testid="seller-name"]::text').get()
        name = seller_name.strip() if seller_name else "Not found"
        
        # Extract address
        address = "Not found"
        di_elements = response.css('.di')
        for element in di_elements:
            mb3 = element.css('.mb3::text').get()
            if mb3:
                address = mb3.strip()
                break
        
        # Extract phone
        phone = "Not found"
        for element in di_elements:
            phone_span = element.css('.ld-Phone + span::text').get()
            if phone_span and phone_span.strip():
                phone = phone_span.strip()
                break
        
        # Extract rating using regular expression
        rating = "Not found"
        rating_pattern = r'(\d+(\.\d+)?) out of \d+'
        rating_text = response.text
        import re
        rating_match = re.search(rating_pattern, rating_text)
        if rating_match:
            rating = rating_match.group(1)
        
        seller_id = response.url.split('/')[-1]
        
        yield {
            'seller_id': seller_id,
            'name': name,
            'address': address,
            'phone': phone,
            'rating': rating
        }
