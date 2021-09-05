import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class NetworkTwoWebMediaSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h1[@class="page_title"]/text()',
        'image': '//div[@class="wpb_wrapper"]/a/@data-src|//div[@class="wpb_wrapper"]/a/@href',
        'cupsize': '//h5/strong[contains(text(),"Measurement")]/following-sibling::text()',
        'weight': '//h5/strong[contains(text(),"Weight")]/following-sibling::text()',
        'height': '//h5/strong[contains(text(),"Height")]/following-sibling::text()',
        'ethnicity': '//h5/strong[contains(text(),"Race")]/following-sibling::text()',
        'eyecolor': '//h5/strong[contains(text(),"Eyes")]/following-sibling::text()',
        'haircolor': '//h5/strong[contains(text(),"Hair")]/following-sibling::text()',
        'bio': '//div[@class="post_excerpt"]/p/text()',
        'external_id': r'models\/(.*).html',
        'pagination': '/modelentry/page/%s/'
    }

    start_urls = [
        'https://www.boppingbabes.com',
        'https://www.downblousejerk.com',
        'https://www.upskirtjerk.com',
        'https://www.wankitnow.com',
    ]

    paginations = {
        '/tour/models/%s/latest/?g=f',
        '/tour/models/%s/latest/?g=m',
    }

    name = 'TwoWebMediaPerformer'
    network = "Two Web Media"

    def get_next_page_url(self, base, page):
        if "boppingbabes" in base:
            pagination = '/v2/modelentry/page/%s/'
        else:
            pagination = '/modelentry/page/%s/'
        return self.format_url(base, pagination % page)

    def get_performers(self, response):
        performers = response.xpath('//div[contains(@class,"loop_content")]//h2/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer
            )

    def get_gender(self, response):
        return "Female"

    def get_cupsize(self, response):
        cupsize = super().get_cupsize(response)
        cupsize = re.search(r'(\w) .*', cupsize)
        if cupsize:
            return cupsize.group(1).strip().upper()
        return ''
