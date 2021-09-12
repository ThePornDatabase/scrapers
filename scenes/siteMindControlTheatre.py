import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class MindControlTheatreScraper(BaseSceneScraper):
    name = 'MindControlTheatre'
    network = 'MindControlTheatre'
    parent = 'MindControlTheatre'

    start_urls = [
        'https://mindcontroltheatre.com'
    ]

    cookies = {
        'age': 'yes',
    }

    selector_map = {
        'title': "//h1/text()",
        'description': "//div[@id='description']/p/text()",
        'date': "//p[@id='data']/text()",
        're_date': r'(\d{1,2} .*? \d{4})',
        'image': '//video/@poster',
        'performers': "//div[@id='cast']/a/text()",
        'tags': "",
        'external_id': r'.*\/(.*?)$',
        'trailer': '',
        'pagination': '/movies?page=%s'
    }

    max_pages = 1

    def start_requests(self):
        url = "https://mindcontroltheatre.com/movies"
        yield scrapy.Request(url, callback=self.get_scenes,
                             meta={'page': self.page},
                             headers=self.headers,
                             cookies=self.cookies)

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="movielist"]/div[1]/a/@href').getall()
        for scene in scenes:
            if "movie" in scene:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        return "Mind Control Theatre"

    def get_parent(self, response):
        return "Mind Control Theatre"
