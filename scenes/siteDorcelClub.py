import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
true = True
false = False

class DorcelClubSpider(BaseSceneScraper):
    name = 'DorcelClub'
    network = 'Dorcel Club'
    parent = 'Dorcel Club'

    start_urls = [
        'https://www.dorcelclub.com'
    ]

    headers = {
        'Accept-Language': 'en-US,en',
        'x-requested-with': 'XMLHttpRequest',
        'referer': 'https://www.dorcelclub.com/en/news-videos-x-marc-dorcel?sorting=new',
    }

    selector_map = {
        'title': '//h1/text()',
        'description': '///span[@class="full"]/p/text()',
        'image': 'picture img.thumbnail::attr(data-src)',
        'performers': '//div[@class="actress"]/a/text()',
        'date': '//span[@class="publish_date"]/text()',
        'tags': '',
        'external_id': 'scene/(\\d+)',
        'trailer': '',
        'pagination': '/en/news-videos-x-marc-dorcel?sorting=new&page=%s'
    }

    cookies = {
        'disclaimer2': 'xx',
        'gen_disclaimer': '1',
        'gen_cookies': 'ta'
    }

    def start_requests(self):
        yield scrapy.Request("https://www.dorcelclub.com/en/", callback=self.start_requests_2, headers=self.headers, cookies=self.cookies)

    def start_requests_2(self, response):
        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, self.page), callback=self.parse, meta={'page': self.page})

    def get_scenes(self, response):
        scenes = response.css('div.scene a.thumb::attr(href)').getall()
        for scene in scenes:
            yield scrapy.Request(url=self.format_link(response, scene), cookies=self.cookies, callback=self.parse_scene)

    def get_image(self, response):
        image = super().get_image(response)
        trash = '_' + image.split('_', 3)[-1].rsplit('.', 1)[0]
        image = image.replace(trash, '', 1)
        return image
