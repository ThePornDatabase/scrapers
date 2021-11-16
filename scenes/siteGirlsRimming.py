import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteGirlsRimmingSpider(BaseSceneScraper):
    name = 'GirlsRimming'
    network = 'Girls Rimming'
    parent = 'Girls Rimming'

    start_urls = [
        'https://www.girlsrimming.com'
    ]

    selector_map = {
        'title': '',
        'description': '//meta[@name="description"]/@content',
        'performers': '',
        'date': '',
        'image': '//img[contains(@class,"player-thumb-img")]/@src0_4x|//img[contains(@class,"player-thumb-img")]/@src0_3x|//img[contains(@class,"player-thumb-img")]/@src0_2x|//img[contains(@class,"player-thumb-img")]/@src0_1x',
        'tags': '//meta[@name="keywords"]/@content',
        'trailer': '',
        'external_id': r'.*/(.*?).html',
        'pagination': '/tour/categories/movies/%s/latest/'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="update_details"]')
        for scene in scenes:
            meta = {}
            meta['site'] = "Girls Rimming"
            meta['parent'] = "Girls Rimming"
            meta['network'] = "Girls Rimming"

            title = scene.xpath('./comment()[contains(.,"Title")]/following-sibling::a/text()')
            if title:
                meta['title'] = self.cleanup_title(title.get())
            else:
                meta['title'] = ''

            performers = scene.xpath('./span[@class="update_models"]/a/text()').getall()
            if performers:
                meta['performers'] = list(map(lambda x: x.strip().title(), performers))
            else:
                meta['performers'] = []

            image = scene.xpath('./a/img/@src1_4x').get()
            if not image:
                image = scene.xpath('./a/img/@src1_3x').get()
            if not image:
                image = scene.xpath('./a/img/@src1_2x').get()
            if not image:
                image = scene.xpath('./a/img/@src1_1x').get()

            if image:
                meta['image'] = image.strip()

            date = scene.xpath('.//div[@class="cell update_date"]/comment()/following-sibling::text()').get()
            if date:
                meta['date'] = self.parse_date(date.strip()).isoformat()

            scene = scene.xpath('./comment()[contains(.,"Title")]/following-sibling::a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene) and meta['title']:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        meta = response.meta
        if self.get_selector_map('tags'):
            tags = self.process_xpath(response, self.get_selector_map('tags')).get()
            if tags:
                tags = tags.split(",")
                if meta['performers']:
                    for performer in meta['performers']:
                        if performer in tags:
                            tags.remove(performer)
                        if "" in tags:
                            tags.remove("")
                tags2 = tags.copy()
                for tag in tags2:
                    matches = [' id ', '...', 'pornstar', 'ramon', 'updates', 'movies', 'anita', 'girlsriming', 'models', 'tags', 'photos', 'girlsrimming', '(id:', 'tony', 'totti']
                    if any(x in tag.lower() for x in matches):
                        tags.remove(tag)
                tags = list(map(lambda x: x.strip().title(), tags))
                if 'Rimming' not in tags:
                    tags.append('Rimming')

                return tags

        return []

    def get_id(self, response):
        extern_id = super().get_id(response)
        return extern_id.lower()
