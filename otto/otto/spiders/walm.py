import scrapy


class WalmSpider(scrapy.Spider):
    name = "walm"
    allowed_domains = ["www.walmart.com"]
    start_urls = ["https://www.walmart.com/ip/BCZHQQ-First-Aid-Box-Organizer-Empty-8-5-Inch-Blue-Vintage-First-Aid-Kit-Tin-Metal-Medical-Box-First-Aid-Storage-Box-Container-Bins-Dividers-Removabl/5609670746?athcpid=5609670746&athpgid=DiscoveryPageSeller&athcgid=null&athznid=mtsi&athieid=v0&athstid=CS020&athguid=tAySOfs_AuNEWnfIKQ6y1-XgCTikUDWmpzfd&athancid=null&athena=true&selectedSellerId=101538196"]

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
        # Extract seller details
        name = response.css('[data-testid="seller-name"]::text').get()
        # Get all text from elements with class 'di'
        info_texts = response.css('.di::text').getall()
        
        yield {
            'url': response.url,
            'name': name,
            'info_texts': info_texts
        }
