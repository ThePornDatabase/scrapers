import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class DorcelClubSpider(BaseSceneScraper):
    name = 'DorcelClub'
    network = 'Dorcel Club'
    parent = 'Dorcel Club'

    start_urls = [
        'https://www.dorcelclub.com'
    ]

    headers = {
        'Accept-Language': 'en-US,en',
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
        'pagination': '/scene/list/more/?lang=en&page=%s&sorting=new'
    }

    cookies = {
        # ~ 'dorcelclub': 'jjp5ajprrugqqp7j04ibtugdlp',
        # ~ 'u': '61836d0b0c409b94e77',
        'disclaimer2': 'xx'
    }

    def start_requests(self):
        yield scrapy.Request("https://www.dorcelclub.com/en/", callback=self.start_requests_2,
                             headers=self.headers,
                             cookies=self.cookies)

    def start_requests_2(self, response):
        if not hasattr(self, 'start_urls'):
            raise AttributeError('start_urls missing')

        if not self.start_urls:
            raise AttributeError('start_urls selector missing')

        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, self.page),
                                 callback=self.parse,
                                 meta={'page': self.page},
                                 headers=self.headers,
                                 cookies=self.cookies)

    def get_scenes(self, response):
        scenes = response.css('div.scene a.thumb::attr(href)').getall()
        for scene in scenes:
            yield scrapy.Request(url=self.format_link(response, scene), cookies=self.cookies, callback=self.parse_scene, headers=self.headers)
