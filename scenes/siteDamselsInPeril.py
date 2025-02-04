import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteDamselsInPerilSpider(BaseSceneScraper):
    name = 'DamselsInPeril'
    network = 'Damsels In Peril'
    parent = 'Damsels In Peril'
    site = 'Damsels In Peril'

    start_urls = [
        'https://damselsinperil.com',
    ]

    selector_map = {
        'title': '//div[@class="info"]/h2[@class="name"]/text()',
        'description': '',
        'date': '//div[@class="date"]/text()',
        're_date': r'(\w+ \d+, \d{4})',
        'image': '//div[@class="playerholder"]//img/@src',
        'performers': '//div[@class="modelstop"]/div/a/following-sibling::text()',
        'tags': '//div[@class="extrainfo"]//a[contains(@href, "search")]/text()',
        'duration': '',
        'trailer': '',
        'external_id': r'.*/(\d+)/',
        'pagination': '/show.php?a=247_%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="itemv"]')
        for scene in scenes:
            title = scene.xpath('.//div[@class="nm-name"]/p[1]/text()')
            if title:
                meta['title'] = self.cleanup_title(title.get())

            scenedate = scene.xpath('.//text()[contains(., "Added:")]')
            if scenedate:
                scenedate = scenedate.get().replace("\r", "").replace("\n", "").replace("\t", "").strip()
                scenedate = re.search(r'(\w+ \d+, \d{4})', scenedate)
                if scenedate:
                    meta['date'] = self.parse_date(scenedate.group(1)).strftime('%Y-%m-%d')

            duration = scene.xpath('.//span[contains(text(), "mins")]/text()')
            if duration:
                duration = duration.get()
                duration = re.search(r'([0-9\.]+)min', duration)
                if duration:
                    duration = duration.group(1)
                    duration = float(duration) * 60
                    meta['duration'] = str(int(duration))

            scene = scene.xpath('./a/@href').get()
            meta['id'] = re.search(r'lid=(\d+)', scene).group(1)
            if meta['id']:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_duration(self, response):
        duration = response.xpath('//strong[contains(text(), "Running")]/text()')
        if duration:
            duration = duration.get()
            duration = re.search(r'([0-9\.]+)min', duration)
            if duration:
                duration = duration.group(1)
                duration = float(duration) * 60
                return str(int(duration))
            return None

    def get_image(self, response):
        image = super().get_image(response)
        if image in response.url:
            image = response.xpath('//div[@class="tourpreview"]/p[1]//img/@src')
            if image:
                image = image.get()
                image = self.format_link(response, image)
        if image:
            return image
        return ""

    def get_performers(self, response):
        performers = super().get_performers(response)
        if not performers:
            performers = response.xpath('//h2/a/text()')
            if performers:
                performers = performers.getall()
        if performers:
            return performers
        return []

    def get_description(self, response):
        description = super().get_description(response)
        if not description:
            description = response.xpath('//h2/following-sibling::p/text()')
            if description:
                description = description.get()
        if description:
            return description
        return ""
