import re
import requests
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteThatFetishGirlSpider(BaseSceneScraper):
    name = 'ThatFetishGirl'
    network = 'That Fetish Girl'
    site = 'That Fetish Girl'
    parent = 'That Fetish Girl'

    start_urls = [
        'https://thatfetishgirl.com',
    ]

    selector_map = {
        'title': '//h4/comment()[contains(., "Title")]/following-sibling::text()[normalize-space()]',
        'description': '//div[contains(@class, "vidImgContent ")]/p//text()',
        'date': '//div[contains(@class,"latestUpdateBinfo")]/ul[@class="videoInfo"]/li[@class="text_med"]//text()[contains(., "/")]',
        'date_formats': ['%m/%d/%Y'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[contains(@class,"latestUpdateBinfo")]//a[contains(@href, "/models/")]/text()',
        'tags': '//div[contains(@class,"latestUpdateBinfo")]//div[contains(@class, "blogTags")]//a/text()',
        'external_id': r'.*/(.*?)(?:_vids)?\.htm',
        'pagination': '/categories/movies_%s.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        scenes = response.xpath('//div[@class="videoPic"]/div/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_duration(self, response):
        duration = response.xpath('//div[contains(@class,"latestUpdateBinfo")]/ul[@class="videoInfo"]/li[@class="text_med"]//text()[not(contains(., "/"))]')
        if duration:
            duration = duration.get()
            duration = duration.replace("\r", "").replace("\n", "").replace("\t", "").replace("&nbsp;", " ").replace("\xa0", " ").replace(" ", "").lower()
            duration = re.search(r'(\d+)min', duration)
            if duration:
                duration = duration.group(1)
                return str(int(duration) * 60)
        return None

    def get_id(self, response):
        sceneid = super().get_id(response)
        return sceneid.lower()

    def get_image(self, response):
        image = super().get_image(response)
        if image:
            image = self.find_best_image(response, image)
            return image
        return None

    def image_exists(self, url):
        try:
            r = requests.head(url, allow_redirects=True, timeout=5)
            return r.status_code == 200
        except requests.RequestException:
            return False

    def find_best_image(self, response, original_url):
        # Original URL may already be -1x, -2x, etc. Substitute whichever -Nx marker
        # is present so we can try each size.
        for suffix in ("-4x", "-3x", "-2x", "-1x"):
            candidate = re.sub(r'-\dx(?=\.\w+(?:\?|$))', suffix, original_url)
            candidate = self.format_link(response, candidate).replace(" ", "%20")
            if self.image_exists(candidate):
                return candidate
        return None
