import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteHeatwaveSceneSpider(BaseSceneScraper):
    name = 'HeatwaveScene'
    network = 'Heatwave'
    parent = 'Heatwave'
    site = 'Heatwave'

    start_urls = [
        'http://www.heatwavepass.com',
    ]

    selector_map = {
        'title': '//h1[@class="title"]/text()',
        'description': '',
        'date': '//div[contains(@id,"info_container")]//span[contains(text(), "Added")]/following-sibling::text()',
        'date_formats': ['%B %d, %Y'],
        'image': '//div[@id="promo-shots"]/div[1]/@style',
        're_image': r'(http.*?)\)',
        'performers': '//div[@class="cast"]//div[@class="name"]/a/text()',
        'tags': '//span[contains(text(), "Tags")]/following-sibling::a/text()',
        'trailer': '',
        'external_id': r'.*-(\d+)\.htm',
        'pagination': '/scenes.html?p=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//ul[contains(@class,"scene-list")]/li/h3/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_duration(self, response):

        duration = response.xpath('//span[contains(text(), "Duration")]/following-sibling::text()')
        if duration:
            duration = duration.get().lower().replace(" ", "")
            hours = ''
            minutes = ''
            if "h" in duration:
                hours = (int(re.search(r'(\d{1,2})h', duration).group(1)) * 3600)
            else:
                hours = 0
            if "m" in duration:
                minutes = (int(re.search(r'(\d{1,2})m', duration).group(1)) * 60)
            else:
                minutes = 0
            if "s" in duration:
                seconds = int(re.search(r'(\d{1,2})s', duration).group(1))
            else:
                seconds = 0
            tot_duration = str(hours + minutes + seconds)
        else:
            tot_duration = None

        return tot_duration

    def get_date(self, response):
        scenedate = super().get_date(response)
        if not scenedate:
            scenedate = "2012-01-01"
        return scenedate

    def get_image(self, response):
        image = super().get_image(response)
        if "/images/" in image:
            image = image.replace("/images/", "/sc/")
        return image
