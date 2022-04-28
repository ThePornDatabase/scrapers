import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteFootFetishDailyPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@class="main_column"]/div[@class="section_titles"]/strong/text()',
        're_name': r'(.*) Feet',
        'image': '//div[@class="main_column"]/div/img/@src',
        'image_blob': True,
        'cupsize': '//div[@class="main_column"]/p/text()',
        're_cupsize': r'Bra Size: (.*)[\s{2,10}\n]',
        'ethnicity': '//div[@class="main_column"]/p/text()',
        're_ethnicity': r'Ethnicity: (.*)[\s{2,10}\n]',
        'astrology': '//div[@class="main_column"]/p/text()',
        're_astrology': r'Sign: (.*)[\s{2,10}\n]',
        'height': '//div[@class="main_column"]/p/text()',
        're_height': r'Height: (.*)[\s{2,10}\n]',
        'bio': '//div[@class="profile-about"]/p/text()',
        'pagination': '/guest/models/page/%s',
        'external_id': r'models\/(.+).html$'
    }

    name = 'FootFetishDailyPerformer'
    network = "Foot Fetish Daily"
    parent = "Foot Fetish Daily"

    start_urls = [
        'https://footfetishdaily.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="model_spacings"]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer
            )

    def get_height(self, response):
        if 'height' in self.selector_map:
            height = self.process_xpath(response, self.get_selector_map('height'))
            if height:
                height = " ".join(height.getall())
                height = self.get_from_regex(height, 're_height')
                if height and "Dom" not in height:
                    return self.cleanup_text(height).title()

        return ''

    def get_cupsize(self, response):
        if 'cupsize' in self.selector_map:
            cupsize = self.process_xpath(response, self.get_selector_map('cupsize'))
            if cupsize:
                cupsize = " ".join(cupsize.getall())
                cupsize = self.get_from_regex(cupsize, 're_cupsize')
                if cupsize and "Dom" not in cupsize:
                    return self.cleanup_text(cupsize).title()

        return ''

    def get_ethnicity(self, response):
        if 'ethnicity' in self.selector_map:
            ethnicity = self.process_xpath(response, self.get_selector_map('ethnicity'))
            if ethnicity:
                ethnicity = " ".join(ethnicity.getall())
                ethnicity = self.get_from_regex(ethnicity, 're_ethnicity')
                if ethnicity and "Dom" not in ethnicity:
                    return self.cleanup_text(ethnicity).title()

        return ''

    def get_astrology(self, response):
        if 'astrology' in self.selector_map:
            astrology = self.process_xpath(response, self.get_selector_map('astrology'))
            if astrology:
                astrology = " ".join(astrology.getall())
                astrology = self.get_from_regex(astrology, 're_astrology')
                if astrology and "Dom" not in astrology:
                    return self.cleanup_text(astrology).title()

        return ''
