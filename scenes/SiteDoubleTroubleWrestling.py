import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteDoubleTroubleWrestlingSpider(BaseSceneScraper):
    name = 'DoubleTroubleWrestling'
    network = 'DoubleTroubleWrestling'
    parent = 'DoubleTroubleWrestling'
    site = 'DoubleTroubleWrestling'

    start_urls = [
        'https://shop.dtwrestling.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//h2[contains(text(), "Description")]/following-sibling::p[1]//text()',
        'image': '//div[@class="woocommerce-product-gallery__wrapper"]/div[1]/a[contains(@href, "jpg")]/@href',
        'performers': '//span[contains(@class, "posted_in")]/a[contains(@href, "wrestler")]/text()',
        'external_id': r'.*/(.*?)/',
        'pagination': '/index.php/product-category/dl/page/%s/',
        'type': 'Scene',
    }

    async def start(self):
        # The first hit on this host answers 200 with an empty body, a PHPSESSID
        # cookie and a "Refresh: 0" header -- an HTTP-header refresh, which Scrapy
        # does not follow (MetaRefreshMiddleware only reads the meta tag, and there
        # is no body to read it from). So the root is fetched once to pick up the
        # session, and the listing is requested after that.
        yield scrapy.Request(url=self.start_urls[0], callback=self.start_after_session,
                             meta={'page': self.page}, headers=self.headers,
                             cookies=self.cookies, dont_filter=True)

    def start_after_session(self, response):
        meta = self.copy_meta(response)
        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, self.page), callback=self.parse,
                                 meta=meta, headers=self.headers, dont_filter=True)

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        scenes = response.xpath('//ul[contains(@class, "products")]/li/a[1]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_duration(self, response):
        # The runtime is written "25 Min - Standard Download". The old XPath tested
        # contains(text(), "min"), and XPath contains() is case-sensitive, so the
        # capitalised "Min" never matched and every scene came back with no runtime.
        candidates = response.xpath('//div[contains(@class, "short-description")]//p//text()').getall()
        candidates += response.xpath('//p//text()[contains(., "Time:")]').getall()
        for candidate in candidates:
            match = re.search(r'(\d+)\s*min', candidate, re.IGNORECASE)
            if match:
                return str(int(match.group(1)) * 60)
        return None

    def get_tags(self, response):
        return ['Sports', 'Wrestling']

    def get_image(self, response):
        image = super().get_image(response)
        if image in response.url:
            image = ""
        return image
