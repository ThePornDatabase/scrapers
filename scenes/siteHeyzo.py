import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteHeyzoSpider(BaseSceneScraper):
    name = 'Heyzo'
    network = 'Heyzo'
    parent = 'Heyzo'
    site = 'Heyzo'

    start_urls = [
        'https://en.heyzo.com',
    ]

    selector_map = {
        'title': '//div[@id="movie"]/h1[1]/text()',
        'description': '',
        'date': '//td[contains(text(), "Released")]/following-sibling::td[1]/text()',
        'performers': '//td[contains(text(), "Actress")]/following-sibling::td[1]/a/text()',
        'tags': '//td[contains(text(), "Type")]/following-sibling::td[1]/a/text()|//td[contains(text(), "Sex Styles")]/following-sibling::td[1]/a/text()|//td[contains(text(), "Theme")]/following-sibling::td[1]/a/text()',
        'duration': '',
        'external_id': r'moviepages/(\d+)/',
        'pagination': '/listpages/all_%s.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "movie")]')
        for scene in scenes:
            scenedate = scene.xpath('.//p[contains(text(), "Release")]/text()')
            if scenedate:
                scenedate = scenedate.get()
                if re.search(r'(\d{4}-\d{2}-\d{2})', scenedate):
                    meta['date'] = re.search(r'(\d{4}-\d{2}-\d{2})', scenedate).group(1)
            scene = scene.xpath('./a[1]/@href').get()
            meta['sceneid'] = re.search(self.get_selector_map('external_id'), scene).group(1)
            if meta['sceneid']:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_title(self, response):
        title = super().get_title(response)
        title = re.sub(' +', ' ', title.replace("\n", "").replace("\r", "").replace("\t", ""))
        return title

    def get_trailer(self, response):
        sceneid = response.meta['sceneid']
        return f'https://www.heyzo.com/contents/3000/{sceneid}/sample_low.mp4'

    def get_image(self, response):
        sceneid = response.meta['sceneid']
        return f'https://en.heyzo.com/contents/3000/{sceneid}/images/player_thumbnail_en.jpg'

    def get_date(self, response):
        scenedate = response.xpath('//td[contains(text(), "Released")]/following-sibling::td[1]/text()')
        if scenedate:
            scenedate = scenedate.get()
            scenedate = scenedate.strip()
            if re.search(r'(\d{4}-\d{2}-\d{2})', scenedate):
                return re.search(r'(\d{4}-\d{2}-\d{2})', scenedate).group(1)
        return None

    def get_id(self, response):
        return "HEYZO-" + response.meta['sceneid']
