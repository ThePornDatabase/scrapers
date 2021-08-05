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
        'dorcelclub': 'c11g8qtdog2p7bhvf6ngr03iam',
        'u': '6106b2e6adfab1e2538',
        'disclaimer2': 'xx'
    }

    def get_scenes(self, response):
        scenes = response.css('div.scene a.thumb::attr(href)').getall()
        for scene in scenes:
            yield scrapy.Request(url=self.format_link(response, scene), cookies=self.cookies, callback=self.parse_scene, headers=self.headers)
