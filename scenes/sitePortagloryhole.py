import re
import scrapy
import requests
from tpdb.BaseSceneScraper import BaseSceneScraper


class SitePortagloryholeSpider(BaseSceneScraper):
    name = 'PortaGloryhole'
    network = 'PortaGloryhole'
    parent = 'PortaGloryhole'
    site = 'PortaGloryhole'

    start_urls = [
        'https://www.portagloryhole.com',
    ]

    cookies = [{"name":"americancumdolls_locale","value":"en"},{"name":"device_view","value":"full"},{"name":"americancumdolls_adult_warning","value":"1"}]

    selector_map = {
        'description': '//h2[contains(@class, "description")]/text()',
        'performers': '//a[@class="tags" and contains(@href, "/models/")]/text()',
        'tags': '//a[@class="tags" and contains(@href, "search")]/text()',
        'trailer': '',
        'external_id': r'.*/(.*?)$',
        'pagination': '/videos?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "post_item")]')
        for scene in scenes:
            duration = scene.xpath('.//i[contains(@class, "fa-video")]/following-sibling::text()')
            if duration:
                meta['duration'] = self.duration_to_seconds(duration.get())

            scenedate = scene.xpath('.//span[contains(@class, "posted_on")]/text()')
            if scenedate:
                meta['date'] = self.parse_date(scenedate.get(), date_formats=['%b %d, %Y']).strftime('%Y-%m-%d')

            image = scene.xpath('.//div[contains(@class, "post_video")]//img[contains(@class, "cover")]/@src')
            if image:
                image = image.get()
                meta['image'] = image
                meta['image_blob'] = self.get_image_blob_from_link(image)

            title = scene.xpath('.//div[contains(@class, "post_video")]/a[1]/@title')
            if title:
                meta['title'] = self.cleanup_title(title.get())

            scene = scene.xpath('.//div[contains(@class, "post_video")]/a[1]/@href').get()

            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def parse_scene(self, response):
        meta = response.meta
        item = self.init_scene()
        item['title'] = meta['title']
        item['description'] = self.get_description(response)
        item['site'] = self.get_site(response)
        item['date'] = meta['date']
        item['duration'] = meta['duration']

        if 'image' in meta:
            item['image'] = meta['image']
        if 'image_blob' in meta:
            item['image_blob'] = meta['image_blob']
        if not item['image'] or not item['image_blob']:
            item['image'] = ''
            item['image_blob'] = ''
        item['performers'] = self.get_performers(response)
        item['tags'] = self.get_tags(response)
        item['id'] = self.get_id(response)
        item['url'] = self.get_url(response)

        item['network'] = self.network
        item['parent'] = self.get_parent(response)
        item['type'] = 'Scene'

        if item['date'] < "2018-12-31":
            if "check_date" in response.meta:
                check_date = response.meta['check_date']
                if item['date'] > check_date:
                    yield self.check_item(item, self.days)
            else:
                yield self.check_item(item, self.days)

    def get_image_from_link(self, image):
        if image and self.cookies:
            cookies = {cookie['name']:cookie['value'] for cookie in self.cookies}
            req = requests.get(image, cookies=cookies, verify=False)

            if req and req.ok:
                return req.content
        return None
