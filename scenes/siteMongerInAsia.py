import scrapy
import re
import dateparser
import html
import tldextract

from tpdb.BaseSceneScraper import BaseSceneScraper

class siteMongerInAsiaSpider(BaseSceneScraper):
    name = 'MongerInAsia'
    network = 'Monger In Asia'

    start_urls = [
        'https://mongerinasia.com',
    ]

    selector_map = {
        'title': '//div[@class="scene-title-wrap"]/h1/text()',
        'description': '//div[@class="description_content"]/text()',
        'date': '',
        'image': '//video/@poster',
        'performers': '//div[@class="div-model-info-in-desc"]//h2/text()',
        'tags': '',
        'external_id': 'trailers\/(.*)',
        'trailer': '//video/source/@src',
        'pagination': '/categories/monger-in-asia_%s_d'
    }

    def get_scenes(self, response):
        meta = {}
        scenes = response.xpath('//div[contains(@class,"videoBlock")]')
        for scene in scenes:
            date = scene.xpath('./div[@class="scene-icons"]//img[contains(@class,"calendar")]/following-sibling::span/text()')
            if date:
                date = date.get()
                meta['date'] = dateparser.parse(date.strip()).isoformat()
            tag = scene.xpath('.//a[@class="site_link"]/span/text()')
            if tag:
                meta['tags'] = [tag.get().strip()]
            
            scene = scene.xpath('./div/a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
        

    def get_description(self, response):
        description = self.process_xpath(response, self.get_selector_map('description')).getall()
        if description:
            description = " ".join(description)
            return html.unescape(description.strip())

        return ''

    def get_date(self, response):
        return dateparser.parse('today').isoformat()

    def get_site(self, response):
        return "Monger in Asia"

    def get_network(self, response):
        return "Monger in Asia"

    def get_parent(self, response):
        return "Monger in Asia"
