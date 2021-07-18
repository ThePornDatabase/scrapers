import re
import scrapy
import tldextract
import html

from tpdb.BaseSceneScraper import BaseSceneScraper


class siteFisterTwisterSpider(BaseSceneScraper):
    name = 'FisterTwister'
    network = "VIPissy Cash"
    parent = "Fister Twister"

    start_urls = [
        'https://www.fistertwister.com',
    ]

    selector_map = {
        'title': '//div[@class="jumbotron"]/h2[1]/text()[1]',
        'description': '//div[contains(@class,"video-info")]/p/text()',
        'date': '//ul/li[contains(text(),"Released")]/strong/text()',
        'date_formats': ['%b %d, %Y'],
        'image': '//div[@class="player"]//video/@poster',
        'performers': '//ul/li[contains(text(),"Featuring")]/strong/a/text()',
        'tags': '//div[contains(@class,"video-info")]/p/a[contains(@href,"tag")]/text()',
        'external_id': '.*\/(.*?)\/$',
        'trailer': '//div[@class="player"]//video/source/@src',
        'pagination': '/videos/page-%s/?tag=&site=&model=all&sort=recent&pussy=all'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//li[contains(@class,"col-xxs-12")]/a[contains(@href,"/videos/")]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)
        
    def get_site(self, response):
        return "Fister Twister"


    def get_description(self, response):
        description = self.process_xpath(response, self.get_selector_map('description')).getall()
        if description:
            description = list(map(lambda x: x.replace("&nbsp;", "").strip(), description))
            description = " ".join(description)
            return description.strip()

        return ''
