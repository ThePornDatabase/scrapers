import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteForbiddenFruitsFilmsSpider(BaseSceneScraper):
    name = 'ForbiddenFruitsFilms'
    network = 'Forbidden Fruits Films'
    parent = 'Forbidden Fruits Films'
    site = 'Forbidden Fruits Films'

    start_urls = [
        'https://forbiddenfruitsfilms.com',
    ]

    # The site runs on the AdultEmpire platform, which bounces every request to
    # /AgeConfirmation until this cookie is present.  Without it the listing and
    # every scene page returned the same age-gate shell, so the crawl saw HTTP 200
    # and parsed nothing.
    cookies = [{"name": "ageConfirmed", "value": "true"}]

    selector_map = {
        'title': '//h1[@class="description"]/text()',
        'description': '',
        'date': '//div[@class="release-date"]/span[contains(text(), "eleased:")]/following-sibling::text()',
        'date_formats': ['%b %d, %Y'],
        'image': '//meta[@property="og:image"]/@content',
        # The old span.video-performer-name markup is gone; the cast is now a strip
        # of headshot tiles, each carrying the name in its own div.
        'performers': '//div[contains(@class, "video-performer-container")]//div[@class="performer-name"]/text()',
        # div.tags was replaced by the "Attributes:" run.  Only the visible run is
        # taken -- the "View More" modal repeats it and adds per-performer body
        # attributes (hair colour, ethnicity) that are not scene tags.
        'tags': '//strong[contains(text(), "Attributes")]/following-sibling::a/text()',
        'trailer': '',
        'external_id': r'/(\d+)/',
        # The default listing order is oldest-first, so a date-limited crawl never saw a
        # new scene; sort=released puts the newest release at the top.
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
            duration = duration.get()
            duration = re.search(r'(\d+) min', duration)
            if duration:
                return str(int(duration.group(1)) * 60)
        return None
