import scrapy
from tpdb.BasePerformerScraper import BasePerformerScraper


class SitePascalsSubslutsPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@id="individual-description"]//h3/text()',
        'image': '//div[@id="individual-description"]//img/@src',
        'bio': '//div[@class="twocolumns"]/p/text()',
        'height': '//li/strong[contains(text(), "Height")]/following-sibling::text()',
        'haircolor': '//li/strong[contains(text(), "Hair")]/following-sibling::text()',
        'nationality': '//li/strong[contains(text(), "Nationality")]/following-sibling::text()',
        'astrology': '//li/strong[contains(text(), "Zodiac")]/following-sibling::text()',
        'pagination': '/submissive/sluts.php?p=%s',
        'external_id': r'model/(.*)/'
    }

    name = 'PascalsSubslutsPerformer'
    network = 'Pascals Subsluts'

    start_urls = [
        'https://www.pascalssubsluts.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[contains(@class, "subMargin")]/a/@href').getall()
        for performer in performers:
            performer = performer.replace('./', 'submissive/')
            if "-and-" not in performer and "-lockdown=" not in performer:
                yield scrapy.Request(
                    url=self.format_link(response, performer),
                    callback=self.parse_performer
                )

    def get_bio(self, response):
        bio_xpath = self.process_xpath(response, self.get_selector_map('bio'))
        if bio_xpath:
            if len(bio_xpath) > 1:
                bio = list(map(lambda x: x.strip(), bio_xpath.getall()))
                bio = ' '.join(bio)
            else:
                bio = bio_xpath.get()
            return bio

        return ''
