import re
import html
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteAPOVStorySpider(BaseSceneScraper):
    name = 'APOVStory'
    network = 'A POV Story'

    start_urls = [
        'https://www.apovstory.com',
    ]

    selector_map = {
        'title': '//div[contains(@class,"topSpace")]/div/h3/text()',
        'description': '//div[@class="trailerContent"]/p//text()',
        'date': '//div[@class="videoContent"]/ul/li/span[contains(text(),"RELEASE")]/following-sibling::text()',
        'image': '//div[@class="player-thumb"]/img/@src0_3x',
        'performers': '//div[@class="videoContent"]/ul/li/span[contains(text(),"FEATURING")]/following-sibling::a/text()',
        'tags': '//div[@class="videoContent"]/ul/li/span[contains(text(),"CATEGORIES")]/following-sibling::a/text()',
        'external_id': r'.*/(.*?).html',
        'trailer': '//script[contains(text(), "trailers")]/text()',
        're_trailer': r'src=\"(.*\.mp4)\"',
        'pagination': '/categories/movies_%s_d.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="updateDetails"]/div/div[contains(@class,"title")]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        return "A POV Story"

    def get_parent(self, response):
        return "A POV Story"

    def get_description(self, response):
        description = self.process_xpath(response, self.get_selector_map('description'))
        if description:
            description = description.getall()
            description = list(map(lambda x: x.strip(), description))
            description = " ".join(description)
            return html.unescape(description.strip())
        return ''
