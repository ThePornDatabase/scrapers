import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class NetworkDungeonCorpPerformerSpider(BasePerformerScraper):
    name = 'DungeonCorpPerformer'
    network = 'Dungeon Corp'

    start_urls = {
        'http://dungeoncorp.com',
    }

    selector_map = {
        'name': '//div[@class="prhead"]/a[1]/following-sibling::text()|//div[@class="prhead"]/span[1]/following-sibling::text()',
        'image': '//div[@class="prhead"]/following-sibling::img/@src',
        'pagination': '',
        'external_id': r'girls/(.+)/?$'
    }

    def start_requests(self):

        url = "http://dungeoncorp.com/index.php?p=models"
        yield scrapy.Request(url, callback=self.get_performers,
                             meta={'page': self.page},
                             headers=self.headers,
                             cookies=self.cookies)

    def get_performers(self, response):
        performers = response.xpath('//span[contains(text(), "Alphabetical")]/following-sibling::table[1]//a/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer, meta={'gender': 'Female'}
            )

        maleperformers = response.xpath('//span[contains(text(), "Alphabetical")]/following-sibling::table[2]//a/@href').getall()
        for maleperformer in maleperformers:
            yield scrapy.Request(
                url=self.format_link(response, maleperformer),
                callback=self.parse_performer, meta={'gender': 'Male'}
            )

    def get_name(self, response):
        return self.process_xpath(response, self.get_selector_map('name')).get().replace("-", "").replace("  ", " ").strip()
