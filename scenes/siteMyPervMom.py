# This is a filler script since it's also pulled from TeamSkeet.  There's actually more information
# on this page, but I'm not sure if everything is here
import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteMyPervMomSpider(BaseSceneScraper):
    name = 'MyPervMom'
    network = 'Team Skeet'
    parent = 'Perv Mom'
    site = 'Perv Mom'

    start_urls = [
        'https://mypervmom.com',
    ]

    selector_map = {
        'title': '//h2/text()',
        'description': '//strong[contains(text(), "Description")]/following-sibling::text()',
        'date': '//div[@id="title-single"]/span/img[@id="time-single"]/following-sibling::text()',
        'date_formats': ['%B %d, %Y'],
        'image': '//div[@class="entry"]//video/@poster',
        'performers': '//strong[contains(text(), "Starring")]/following-sibling::a/text()',
        'tags': '//span[@class="update_tags"]/a/text()',
        'external_id': r'.*/(.*?)/',
        'trailer': '//div[@class="entry"]//video/source/@src',
        'pagination': '/page/%s/'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@id,"post")]//h2/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene) and "/join/" not in scene:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)
