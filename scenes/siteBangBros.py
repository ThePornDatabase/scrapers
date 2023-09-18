import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class BangBrosSpider(BaseSceneScraper):
    name = 'BangBros'
    network = 'Bang Bros'
    parent = 'Bang Bros'

    start_urls = [
        # ~ 'https://bangbros.com/' # Moved to ProjectOneService
    ]

    custom_settings = {
        'USER_AGENT':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.62',
        'AUTOTHROTTLE_ENABLED': True,
        # ~ 'AUTOTHROTTLE_START_DELAY': 1,
        # ~ 'AUTOTHROTTLE_MAX_DELAY': 120,
        'CONCURRENT_REQUESTS': 1,
        # ~ 'DOWNLOAD_DELAY': 60,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'CONCURRENT_REQUESTS_PER_IP': 1,
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 522, 524, 408, 429, 403, 302],

        }

    selector_map = {
        'title': "//div[@class='ps-vdoHdd']//h1/text()",
        'description': "//div[@class='vdoDesc']/text()",
        'date': "",
        'image': '//img[@id="player-overlay-image"]/@src',
        'performers': "//div[@class='vdoAllDesc']//div[@class='vdoCast']//a[position()>1]/text()",
        'tags': "//div[@class='vdoTags']//a/text()",
        'external_id': r'/([A-Za-z0-9-_+=%]+)$',
        'trailer': '//video//source[contains(@src, "mp4") and not(contains(@src, "mpd")) and not(contains(@src, "m3u8"))]/@src',
        'pagination': '/videos/page/%s'
    }

    def get_scenes(self, response):
        meta = response.meta
        meta={'dont_redirect': True}
        scenes = response.xpath("//div[@class='videosPopGrls']//div[@class='echThumb']")
        for scene in scenes:
            date = scene.xpath(".//span[contains(@class, 'thmb_mr_cmn')][2]//span[@class='faTxt']/text()")
            if date:
                meta['date'] = self.parse_date(date.get(), date_formats=['%b %d, %Y']).isoformat()
            else:
                meta['date'] = self.parse_date('today').isoformat()

            duration = scene.xpath('.//b[@class="tTm"]/text()')
            if duration:
                meta['duration'] = self.duration_to_seconds(duration.get())

            link = self.format_link(response, scene.css('a::attr(href)').get())
            if "mobile." in link:
                link = link.replace("mobile.", "")
            yield scrapy.Request(url=link, callback=self.parse_scene, meta=meta)

    def get_site(self, response):
        site = response.xpath("//div[@class='vdoAllDesc']//div[@class='vdoCast']//a[1]/text()").get()
        if 'casting' in site:
            return 'Bang Bros Casting'
        if 'party of 3' in site.lower():
            return 'Party of Three'
        return site

    def get_id(self, response):
        external_id = response.xpath('//img[@id="player-overlay-image"]/@src')
        if external_id:
            external_id = re.search(r'shoots/(.*?)/', external_id.get())
            if external_id:
                return external_id.group(1)
        return super().get_id(response)

    def get_image(self, response):
        image = response.xpath(self.get_selector_map('image'))
        if image:
            image = image.get()
            image = image.strip('//')
            return "https://" + image.replace("//", "/")
        return ''
