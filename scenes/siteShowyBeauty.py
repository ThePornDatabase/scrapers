import re
import string
import requests
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from scrapy import Selector


class SiteShowyBeautySpider(BaseSceneScraper):
    name = 'ShowyBeauty'
    network = 'Amour Angels'
    parent = 'Showy Beauty'
    site = 'Showy Beauty'

    start_urls = [
        'http://www.showybeauty.com',
    ]

    selector_map = {
        'title': '//div[@class="short"]/strong/text()',
        'description': '',
        'date': '//div[@class="short"]//text()[contains(., "Added")]',
        're_date': r'(\d{4}-\d{2}-\d{2})',
        'date_formats': ['%Y-%m-%d'],
        'image': '//div[contains(@class, "cover-video")]/div[@class="view"]/img/@src',
        'performers': '',  # '//div[@class="see-model-info"]//a[contains(@href, "model")]/text()', is the actual code, but first name only and multiple models of the same name
        'tags': '',
        'external_id': r'.*_(\d+).html',
        'trailer': '',
        'pagination': '/videos_%s.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="body"]/div[@class="item"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_tags(self, response):
        return ['Teen', 'Erotica', 'Art', 'Barely Legal']

    def get_next_page_url(self, base, page):
        pagination = self.get_selector_map('pagination') % page
        if page == 1:
            pagination = "/videos.html"
        return self.format_url(base, pagination)

    def get_performers(self, response):
        performer_list = []
        performers = response.xpath('//div[@class="see-model-info"]//a[contains(@href, "model")]')
        if performers:
            for performer in performers:
                performer_name = performer.xpath('./text()').get()
                performer_id = performer.xpath('./@href').get()
                if performer_id:
                    performer_id = re.search(r'model_(\d+).html', performer_id)
                    if performer_id:
                        performer_id = performer_id.group(1)
                if performer and performer_id:
                    performer_list.append(string.capwords(performer_name + " " + performer_id))
        return performer_list

    def get_description(self, response):
        model_link = response.xpath('//div[@class="see-model-info"]//a[contains(@href, "model")]/@href')
        if model_link:
            model_link = self.format_link(response, model_link.get())
            model = requests.get(model_link)
            sel = Selector(text=model.content)
            description = sel.xpath('//div[@class="description"]/p[@class="short"]/text()')
            if description:
                return description.get().replace("\n", "").strip()
        return ""

    def get_title(self, response):
        title = super().get_title(response)
        title = string.capwords(title.lower().replace("<b>", "").replace("</b>", ""))
        title = re.sub(r'( Video)$', '', title)
        return string.capwords(title)
