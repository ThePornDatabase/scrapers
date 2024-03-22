import re
import dateparser
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class CherryPimpsSpider(BaseSceneScraper):
    name = 'CherryPimps'
    network = 'Cherry Pimps'

    start_urls = [
        'https://www.cherrypimps.com',
        'https://www.wildoncam.com',
        # ~ 'https://www.cherryspot.com',
    ]

    selector_map = {
        'title': '//*[@class="trailer-block_title"]/text() | //h1/text()',
        'description': '//div[@class="info-block"]//p[@class="text"]/text() | //div[@class="update-info-block"]//p/text()',
        'image': '//img[contains(@class, "update_thumb")]/@src | //img[contains(@class, "update_thumb")]/@src0_1x',
        'performers': '//div[contains(@class, "model-list-item")]//a/span/text() | //p[contains(text(), "Featuring")]/a/text()',
        'tags': '//ul[@class="tags"]/li/a/text() | //p[@class="text" and contains(text(),"Categories")]/a/text()',
        'duration': '//div[@class="update-info-row"]/i[contains(@class, "play-circle")]/following-sibling::text()[1]',
        're_duration': r'(\d{1,2}:\d{2}(?::\d{2})?)',
        'external_id': 'trailers/(.+)\\.html',
        'trailer': '',
        'pagination': '/categories/movies_%s.html'
    }

    def get_scenes(self, response):
        meta = response.meta
        """ Returns a list of scenes
        @url https://cherrypimps.com/categories/movies.html
        @returns requests 10 50
        """
        if "cherrypimps" in response.url:
            scenexpath = '//div[contains(@class,"item-update") and not(contains(@class,"item-updates"))]'
        if "wildoncam" in response.url:
            scenexpath = '//div[contains(@class,"video-thumb")]'
        scenes = response.xpath(scenexpath)
        for scene in scenes:
            image = scene.xpath('.//img[contains(@class, "update_thumb")]/@src0_1x|.//img[contains(@class, "video_placeholder")]/@src')
            if image:
                meta['origimage'] = image.get()

            site = scene.xpath('.//div[@class="item-sitename"]/a/text() | ./p[contains(@class, "text-thumb")]/a/@data-elx_site_name')
            if site:
                site = site.get().strip()
            else:
                site = False
            meta['site'] = site

            if "cherrypimps" in response.url:
                urlxpath = './div[@class="item-footer"]/div/div[@class="item-title"]/a/@href'
            else:
                urlxpath = './div[contains(@class, "videothumb")]/a/@href | ./a/@href'
            scenelink = scene.xpath(urlxpath).get()

            if "/signup/" not in scenelink:
                yield scrapy.Request(url=scenelink, callback=self.parse_scene, meta=meta)

    def get_date(self, response):
        selector = '//div[@class="info-block_data"]//p[@class="text"]/text() | //div[@class="update-info-row"]/text()'
        if "wildoncam" in response.url or "cherryspot" in response.url:
            date = response.xpath(selector).extract()[0]
        else:
            date = response.xpath(selector).extract()[1]
        date = date.split('|')[0].replace('Added', '').replace(':', '').strip()
        return dateparser.parse(date).isoformat()

    def get_site(self, response):
        return response.css('.series-item-logo::attr(title)').get().strip()

    def get_parent(self, response):
        meta = response.meta
        if meta['site']:
            return meta['site']
        return super().get_parent(response)

    def get_duration(self, response):
        duration = self.get_element(response, 'duration', 're_duration')
        if duration:
            return self.duration_to_seconds(duration)
        if not duration:
            duration = response.xpath('//p[@class="text" and contains(text(), "min")]/text()')
            if duration:
                duration = duration.get()
                duration = re.search(r'(\d+).?min', duration)
                if duration:
                    return str(int(duration.group(1)) * 60)
        return None

    def get_image(self, response):
        meta = response.meta
        image = super().get_image(response)
        if "content" not in image and "cdn" not in image:
            return meta['origimage']
        return image
