import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class NubilesPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '.model-profile-desc h2::text',
        'image': ".model-profile img::attr(src)",
        'bio': '.model-bio::text',
        'nationality': '//p[contains(text(), "Location")]/following-sibling::p[1]/text()',
        'height': '//p[contains(text(), "Height")]/following-sibling::p[1]/text()',
        'astrology': '//p[contains(text(), "Zodiac")]/following-sibling::p[1]/text()',
        'measurements': '//p[contains(text(), "Figure")]/following-sibling::p[1]/text()',
        'cupsize': '//p[contains(text(), "Figure")]/following-sibling::p[1]/text()',
        're_cupsize': r'(\d{1,3}\w+?)-\d',
        'pagination': '/model/gallery/%s',
        'external_id': r'profile/\d+/.+$'
    }

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
