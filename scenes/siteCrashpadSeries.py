import re
from requests import get
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteCrashpadSeriesSpider(BaseSceneScraper):
    name = 'CrashpadSeries'
    network = 'CrashpadSeries'
    parent = 'CrashpadSeries'
    site = 'CrashpadSeries'

    start_url = 'https://crashpadseries.com/queer-porn/episodes-all/'

    selector_map = {
        'title': '//div[@class="row"]//h2/text()',
        'description': '//div[@class="row"]//div[contains(@class, "ep-description")]//p[not(contains(text(), "following the results of the presidential election"))]/text()',
        'date': '//h4[contains(text(), "Date:")]/text()',
        're_date': r'(\w+ \d+\w{1,2}?, \d{4})',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//h3[contains(text(), "Starring")]/following-sibling::div//h4/text()',
        'tags': '//div[@class="row"]//a[contains(@class, "content-icon")]/@title',
        'duration': '',
        'trailer': '',
        'external_id': r'episode-(\d+)-',
        'pagination': '',
        'type': 'Scene',
    }

    def start_requests(self):
        ip = get('https://api.ipify.org').content.decode('utf8')
        print('My public IP address is: {}'.format(ip))

        yield scrapy.Request(self.start_url, callback=self.get_scenes, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//a[@class="epiLink"]')
        for scene in scenes:
            image = scene.xpath('.//img/@data-src')
            if image:
                meta['image'] = image.get()
                meta['image_blob'] = self.get_image_blob_from_link(meta['image'])
            scene = scene.xpath('./@href').get()

            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_image(self, response):
        image = response.xpath('//div[contains(@class, "col-video")]/div/iframe/@src')
        if image:
            image = image.get()
            image = re.search(r'.*/(.*?)\?auto', image)
            if image:
                image = image.group(1)
                image = f"https://vz-65913dd2-eef.b-cdn.net/{image}/thumbnail.jpg"
                return image
        return None
