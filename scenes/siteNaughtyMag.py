import re
import scrapy
import string
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteNaughtyMagSpider(BaseSceneScraper):
    name = 'NaughtyMag'
    network = 'Score Pass'
    parent = 'Porn Mega Load"'

    start_urls = [
        'https://www.naughtymag.com',
        'https://www.18eighteen.com',
        'https://www.bootyliciousmag.com',
    ]

    selector_map = {
        'title': '//section//h1/text()',
        'description': '//div[contains(@class, "p-desc")]/text()',
        'date': '//span[@class="label" and contains(text(), "Date:")]/following-sibling::span[1]/text()',
        'image': '//style[contains(text(), "min-width: 1000px")]/text()',
        're_image': r'min-width: 1000px.*(http.*?)[\'\"]',
        'performers': '//span[@class="label" and contains(text(), "Featuring:")]/following-sibling::span[1]/a/text()',
        'tags': '//div[contains(@class, "p-desc")]/a[contains(@href, "-tag")]/text()',
        'duration': '//span[@class="label" and contains(text(), "Duration:")]/following-sibling::span[1]/text()',
        'trailer': '//div[contains(@class, "vp")]//video/source[contains(@src, "1280")]/@src',
        'external_id': r'.*/(\d+)/',
        'pagination': '/amateur-videos/?page=%s',
        'type': 'Scene',
    }

    custom_scraper_settings = {
        'CONCURRENT_REQUESTS': 1,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'CONCURRENT_REQUESTS_PER_IP': 1,
        # ~ 'DOWNLOAD_FAIL_ON_DATALOSS': True,
        'COMPRESSION_ENABLED': False,
        'RETRY_ENABLED': True,
        'RETRY_TIMES': 10,
        'RETRY_HTTP_CODES': [500, 503, 504, 400, 408, 307, 403],
        'HANDLE_HTTPSTATUS_LIST': [500, 503, 504, 400, 408, 307, 403],
    }

    def get_next_page_url(self, base, page):
        if "naughtymag" in base:
            pagination = '/amateur-videos/?page=%s'
        if "18eighteen" in base:
            pagination = '/xxx-teen-videos/?page=%s'
        if "bootylicious" in base:
            pagination = '/big-booty-videos/?page=%s'
        return self.format_url(base, pagination % page)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class,"li-item") and contains(@class, "video")]//div[contains(@class, "item-img")]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene) and "join." not in scene:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_image(self, response):
        imagetext = response.xpath('//style[contains(text(), "min-width: ") and not(contains(text(), "gradient"))]/text()')
        image = ""
        if imagetext:
            imagetext = imagetext.get()
            imagetext = imagetext.replace("\r", "").replace("\n", "").replace("\t", "")
            images = re.findall(r'(https:.*?\.jpg)', imagetext)
            if images:
                for res in ['_1280', '_800', '_xl', '_lg']:
                    for image_candidate in images:
                        if res in image_candidate and not image:
                            image = self.format_link(response, image_candidate)


        if not image:
            image = response.xpath('//meta[@property="og:image"]/@content')
            if image:
                image = self.format_link(response, image.get())

        return image

    def get_url(self, response):
        url = response.url
        if "?nats" in url:
            url = re.search(r'(.*)\?nats', url).group(1)
        return url

    def get_duration(self, response):
        duration = response.xpath('//span[@class="label" and contains(text(), "Duration:")]/following-sibling::span[1]/text()')
        if duration:
            duration = duration.get().strip()
            duration = re.sub(r'[^0-9:]+', '1', duration)
            return self.duration_to_seconds(duration)

    def get_performers(self, response):
        perflist = response.xpath('//span[@class="label" and contains(text(), "Featuring:")]/following-sibling::span[1]/a')
        performers = []
        if perflist:
            for perf in perflist:
                performer = perf.xpath('./text()').get()
                performer = string.capwords(performer.strip())
                if " " not in performer:
                    perf_href = perf.xpath('./@href').get()
                    perf_id = re.search(r'/(\d+)/', perf_href).group(1)
                    performer = performer + " " + perf_id
                performers.append(performer)
        return performers
