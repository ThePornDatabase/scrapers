import re
import string
import requests
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from scrapy import Selector


class SiteAmourAngelsSpider(BaseSceneScraper):
    name = 'AmourAngels'
    network = 'Amour Angels'
    parent = 'Amour Angels'
    site = 'Amour Angels'

    start_urls = [
        'http://www.amourangels.com',
    ]

    selector_map = {
        'title': '//comment()[contains(.,"Info and Buttons")]/following-sibling::table//tr/td/p[1]/b/text()',
        'description': '',
        'date': '//comment()[contains(.,"Info and Buttons")]/following-sibling::table//text()[contains(., "Added")]',
        're_date': r'(\d{4}-\d{2}-\d{2})',
        'date_formats': ['%Y-%m-%d'],
        'image': '//comment()[contains(.,"Cover")]/following-sibling::table//img/@src',
        'performers': '',  # '//comment()[contains(.,"Info and Buttons")]/following-sibling::table//a[contains(@href, "model")]/b/text()', is the actual code, but first name only and multiple models of the same name
        'tags': '',
        'external_id': r'.*_(\d+).html',
        'trailer': '',
        'pagination': '/videos2_%s.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//a[@class="sethref"]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_tags(self, response):
        return ['Teen', 'Erotica', 'Art']

    def get_next_page_url(self, base, page):
        pagination = self.get_selector_map('pagination') % page
        if page == 1:
            pagination = "/videos2.html"
        return self.format_url(base, pagination)

    def get_title(self, response):
        title = super().get_title(response)
        title = string.capwords(title.lower().replace("<b>", "").replace("</b>", ""))
        title = re.sub(r'( Video)$', '', title)
        return string.capwords(title)

    def get_performers(self, response):
        performer_list = []
        performers = response.xpath('//comment()[contains(.,"Info and Buttons")]/following-sibling::table//a[contains(@href, "model")]')
        if performers:
            for performer in performers:
                performer_name = performer.xpath('./b/text()').get()
                performer_id = performer.xpath('./@href').get()
                if performer_id:
                    performer_id = re.search(r'model_(\d+).html', performer_id)
                    if performer_id:
                        performer_id = performer_id.group(1)
                if performer and performer_id:
                    performer_list.append(string.capwords(performer_name + " " + performer_id))
        return performer_list

    def get_description(self, response):
        model_link = response.xpath('//comment()[contains(.,"Info and Buttons")]/following-sibling::table//a[contains(@href, "model")]/@href')
        if model_link:
            model_link = self.format_link(response, model_link.get())
            model = requests.get(model_link)
            sel = Selector(text=model.content)
            description = sel.xpath('//td[@class="modelinfo-bg"]//p[contains(@style, "margin-left")][1]/text()')
            if description:
                return description.get().replace("\n", "").strip()
        return ""
