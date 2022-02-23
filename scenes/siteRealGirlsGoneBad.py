import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteRealGirlsGoneBadSpider(BaseSceneScraper):
    name = 'RealGirlsGoneBad'
    network = 'Real Girls Gone Bad'
    parent = 'Real Girls Gone Bad'
    site = 'Real Girls Gone Bad'

    start_urls = [
        'https://www.realgirlsgonebad.com',
    ]

    cookies = {'rggbwarning_13': 'accepted'}

    selector_map = {
        'title': '//div[@class="epiTitle"]/text()',
        'description': '//div[@class="eachB"]/p/text()',
        'date': '//div[@class="eachB"]//strong[contains(text(), "Added")]/following-sibling::text()',
        'date_formats': ['%d %B, %Y'],
        'image': '//script[contains(text(), "poster")]/text()',
        'performers': '',
        'tags': '//div[@class="eachB"]//span[@class="tagsC"]/a/text()',
        'external_id': r'.*/(.*?).html',
        'trailer': '//script[contains(text(), "poster")]/text()',
        'pagination': '/tour/categories/videos_%s_d.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//h3/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, cookies=self.cookies)

    def get_image(self, response):
        image = response.xpath(self.get_selector_map('image'))
        if image:
            image = image.get()
            image = re.search(r'poster=\"(.*?.jpg)', image)
            if image:
                return "https://www.realgirlsgonebad.com" + image.group(1)
        return ''

    def get_trailer(self, response):
        trailer = response.xpath(self.get_selector_map('trailer'))
        if trailer:
            trailer = trailer.get()
            trailer = re.search(r'video src=\"(.*?.mp4)', trailer)
            if trailer:
                return "https://www.realgirlsgonebad.com" + trailer.group(1)
        return ''
