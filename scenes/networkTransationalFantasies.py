import re

import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkTransationalFantasiesSpider(BaseSceneScraper):
    name = 'TransationalFantasies'
    network = 'Transational Fantasies'
    parent = 'Transational Fantasies'

    start_urls = [
        'https://www.transationalfantasies.com',
    ]

    # The site runs on the AdultEmpire platform, which bounces every request to
    # /AgeConfirmation until this cookie is set -- that is why the crawl saw HTTP
    # 200 and parsed nothing.  With the cookie the old
    # /watch-...-free-trailers.html listing does load, but its grid-item cards link
    # to movie/product pages; the scene listing is /streaming-video-by-scene.html,
    # whose default order is oldest-first, so sort=released is added.
    cookies = [{"name": "ageConfirmed", "value": "true"}]

    custom_scraper_settings = {
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 60,
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 2,
    }

    selector_map = {
        'title': '//h1[@class="description"]/text()',
        'description': '',
        'date': '//div[@class="release-date"]/span[contains(text(), "eleased:")]/following-sibling::text()',
        'date_formats': ['%b %d, %Y'],
        'image': '//meta[@property="og:image"]/@content',
        # the cast is a strip of headshot tiles, each carrying the name in its own div
        'performers': '//div[contains(@class, "video-performer-container")]//div[@class="performer-name"]/text()',
        # only the visible run is taken -- the "View More" modal repeats it and adds
        # per-performer body attributes that are not scene tags
        'tags': '//strong[contains(text(), "Attributes")]/following-sibling::a/text()',
        'trailer': '',
        'external_id': r'/(\d+)/',
        'pagination': '/streaming-video-by-scene.html?page=%s&sort=released',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        scenes = response.xpath(
            '//article[contains(@class, "scene-widget")]//a[contains(@class, "scene-img")]/@href').getall()
        for scene in dict.fromkeys(scenes):
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene,
                                     headers=self.headers, cookies=self.cookies)

    def get_trailer(self, response):
        """The preview stream is assembled by the page's hover-preview script from
        the master id and the scene id rather than being linked anywhere."""
        master = response.xpath('//*[@data-master-id]/@data-master-id').get()
        scene = re.search(self.get_selector_map('external_id'), response.url)
        if master and scene:
            return f"https://video.adultempire.com/hls/previewscene/{master.strip()}/{scene.group(1)}/index-f1-v1.m3u8"
        return ''

    def get_duration(self, response):
        duration = response.xpath('//div[@class="release-date"]/span[contains(text(), "ength:")]/following-sibling::text()')
        if duration:
            duration = re.search(r'(\d+) min', duration.get())
            if duration:
                return str(int(duration.group(1)) * 60)
        return None

    def get_site(self, response):
        site = response.xpath('//div[@class="studio"]/span[2]/text()|//div[@class="studio"]/a/text()')
        if site:
            return self.cleanup_title(site.get())
        return "Transational Fantasies"

    def get_parent(self, response):
        return "Transational Fantasies"
