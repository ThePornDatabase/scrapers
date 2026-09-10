import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


def match_site(argument):
    match = {
        'pornstarbts': "Pornstar BTS",
        'sissypov': "Sissy POV",
    }
    return match.get(argument, argument)


class CXWowSpiderAlt(BaseSceneScraper):
    name = 'CXWowAlt'
    network = 'CX Wow'

    start_urls = [
        'https://pornstarbts.com',
        'https://sissypov.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//h4/following-sibling::p//text()',
        'performers': '//h5[contains(text(), "Featuring")]/following-sibling::ul/li/a/text()',
        'tags': '//h5[contains(text(), "Tags")]/following-sibling::ul/li/a/text()',
        'trailer': '',
        'external_id': '/trailers/(.*).html',
        'pagination': '/tour/categories/movies_%s_d.html',

    }

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        scenes = response.xpath('//div[@class="iLatestScene"]')
        for scene in scenes:
            scenedate = scene.xpath('.//i[contains(@class, "calendar")]/following-sibling::text()')
            if scenedate:
                scenedate = scenedate.get().strip()
                meta['date'] = self.parse_date(scenedate, date_formats=['%b %d, %Y']).strftime('%Y-%m-%d')

            duration = scene.xpath('.//i[contains(@class, "clock")]/following-sibling::text()')
            if duration:
                duration = duration.get()
                duration = re.search(r'((?:\d{1,2}\:)?\d{2}\:\d{2})', duration)
                if duration:
                    meta['duration'] = self.duration_to_seconds(duration.group(1))

            image = scene.xpath('.//img/@src0_4x')
            if image:
                image = image.get()
                meta['image'] = self.format_link(response, image)

            sceneid = scene.xpath('.//img/@id')
            if sceneid:
                sceneid = sceneid.get()
                meta['id'] = re.search(r'target-(\d+)', sceneid).group(1)

            scene = scene.xpath('./div/a/@href').get()
            if meta['date'] > "2024-01-28" and meta['id']:
                if self.check_item(meta, self.days):
                    meta['image_blob'] = self.get_image_blob_from_link(meta['image'])
                    yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_site(self, response):
        return match_site(super().get_site(response))

    def get_parent(self, response):
        return match_site(super().get_parent(response))

    def get_performers(self, response):
        performers = super().get_performers(response)
        performers.append("Christian XXX")
        return performers
