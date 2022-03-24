import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class NubilesPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '.model-profile-desc h2::text',
        'image': ".model-profile img::attr(src)",
        'bio': '.model-bio::text',
        'nationality': '//div[contains(@class, "model-profile-desc")]//p[1]/text()',
        'height': '//div[contains(@class, "model-profile-desc")]//p[3]/text()',
        'astrology': '//div[contains(@class, "model-profile-desc")]//p[4]/text()',
        'measurements': '//div[contains(@class, "model-profile-desc")]//p[5]/text()',
        'pagination': '/model/gallery/%s',
        'external_id': r'profile/\d+/.+$'
    }

    custom_settings = {'DOWNLOADER_MIDDLEWARES': {'tpdb.mymiddlewares.CustomProxyMiddleware': 350, 'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 400}}

    name = 'NubilesPerformer'
    network = "Nubiles"
    parent = "Nubiles"

    start_urls = [
        'https://nubiles.net/',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.css('.Performer .img-wrapper a::attr(href)').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer
            )

    def get_next_page_url(self, base, page):
        page = (page - 1) * 10
        return self.format_url(
            base, self.get_selector_map('pagination') % page)
