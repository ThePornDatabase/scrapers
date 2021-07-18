import re
import scrapy
import dateparser

from tpdb.BaseSceneScraper import BaseSceneScraper


class sitePeeOnHerSpider(BaseSceneScraper):
    name = 'PeeOnHer'
    network = "VIPissy Cash"
    parent = "Pee On Her"

    start_urls = [
        'https://www.peeonher.com',
    ]

    selector_map = {
        'title': '//h1[@class="page_title"]/text()',
        'description': '//strong[@class="title"]/following-sibling::p/text()',
        'date': '//strong[@class="title" and contains(text(),"Published")]/following-sibling::text()',
        'image': '//div[@class="update_box"]/img/@src',
        'performers': '//strong[contains(text(),"Starring")]/following-sibling::a/text()',
        'tags': '//strong[contains(text(),"Tags")]/following-sibling::a/text()',
        'external_id': '.*\/(.*?)\/$',
        'trailer': '//div[@id="videoplayer"]//video/source/@src',
        'pagination': '/updates/page-%s/'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class,"item")]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)
        
    def get_site(self, response):
        return "Pee On Her"


    def get_description(self, response):
        description = self.process_xpath(response, self.get_selector_map('description')).getall()
        if description:
            description = list(map(lambda x: x.replace("&nbsp;", "").strip(), description))
            description = " ".join(description)
            return description.strip()

        return ''

    def get_date(self, response):
        date = self.process_xpath(response, self.get_selector_map('date')).get()
        if date:
            return dateparser.parse(date).isoformat()

        return None
