import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteBoxTruckSexSpider(BaseSceneScraper):
    name = 'BoxTruckSex'
    network = 'Box Truck Sex'
    parent = 'Box Truck Sex'

    start_urls = [
        'https://www.boxtrucksex.com',
    ]

    selector_map = {
        'title': '//h2/text()',
        'description': '//div[@class="desc"]/p/text()',
        'date': '//strong[contains(text(),"Date Added")]/following-sibling::text()',
        'date_formats': ['%b %d, %Y'],
        'image': '//div/img[contains(@class,"fp-splash")]/@data-orig-src',
        'performers': '//h5/a[contains(@href,"/models/")]/text()',
        'tags': '//h5/a[contains(@href,"/categories/")]/text()',
        'external_id': r'.*/(.*).html',
        'trailer': '',
        'pagination': '/tour/categories/videos_%s_d.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//li/a[contains(@href,"/trailers")]')
        for scene in scenes:
            image = scene.xpath('./img/@src0_3x').get()
            if image:
                image = "https://www.boxtrucksex.com/" + image.strip()
            else:
                image = ''

            performers = scene.xpath('.//i[contains(@class,"icon-female")]/following-sibling::text()').get()
            if performers:
                if "," in performers:
                    performers = performers.split(",")
                else:
                    performers = [performers]

            if performers:
                performers = list(map(lambda x: x.strip().title(), performers))
            else:
                performers = []

            scene = scene.xpath('./@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta={'image': image, 'performers': performers})

    def get_site(self, response):
        return "Box Truck Sex"

    def get_parent(self, response):
        return "Box Truck Sex"

    def get_trailer(self, response):
        if 'trailer' in self.get_selector_map() and self.get_selector_map('trailer'):
            trailer = self.process_xpath(response, self.get_selector_map('trailer'))
            if trailer:
                trailer = self.get_from_regex(trailer.get(), 're_trailer')
                return trailer.replace(" ", "%20").replace("\\", "")

        return ''
