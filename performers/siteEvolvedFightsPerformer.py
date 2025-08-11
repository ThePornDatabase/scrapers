import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteEvolvedFightsPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h1/text()',
        'image': '//div[@class="modelInfo"]//img/@src0_4x',
        'height': '//span[contains(text(), "Height")]/following-sibling::text()',
        'weight': '//span[contains(text(), "Weight")]/following-sibling::text()',

        'pagination': '/models/models_%s_n.html?g=f',
        'external_id': r'model/(.*)/'
    }

    paginations = [
        '/models/models_%s_n.html?g=f',
        '/models/models_%s_n.html?g=m'
    ]

    name = 'EvolvedFightsPerformer'
    network = 'Evolved Fights'

    start_url = 'https://www.evolvedfights.com'

    def get_next_page_url(self, base, page, pagination):
        return self.format_url(base, pagination % page)

    def start_requests(self):
        meta = {}
        meta['page'] = self.page
        for pagination in self.paginations:
            meta['pagination'] = pagination
            yield scrapy.Request(url=self.get_next_page_url(self.start_url, self.page, meta['pagination']), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def parse(self, response, **kwargs):
        performers = self.get_performers(response)
        count = 0
        for performer in performers:
            count += 1
            yield performer

        if 'page' in response.meta and response.meta['page'] < self.limit_pages:
            meta = response.meta
            meta['page'] = meta['page'] + 1
            print('NEXT PAGE: ' + str(meta['page']))
            yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page'], meta['pagination']), callback=self.parse, meta=meta)

    def get_gender(self, response):
        if "g=m" in response.meta['pagination']:
            return 'Male'
        else:
            return 'Female'

    def get_performers(self, response):
        meta = response.meta
        performers = response.xpath('//div[contains(@class, "modelBlock")]//h4/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, cookies=self.cookies, headers=self.headers, meta=meta)

    def get_weight(self, response):
        weight = response.xpath('//div[@class="modelInfo"]//li[contains(text(), "Weight")]/text()')
        if weight:
            weight = weight.getall()
            weight = "".join(weight)
            weight = re.search(r'(\d+)', weight)
            if weight:
                return str(int(int(weight.group(1)) * .453592)) + "kg"
        return None

    def get_height(self, response):
        height = response.xpath('//div[@class="modelInfo"]//li[contains(text(), "Height")]/text()')
        if height:
            height = height.getall()
            height = "".join(height)
            height = re.sub(r'[^0-9\']+', '', height)
            height = re.search(r'(\d+?\'\d+)', height)
            if height:
                height = height.group(1)
                tot_inches = 0
                if re.search(r'(\d+)[\'\"]', height):
                    feet = re.search(r'(\d+)\'', height)
                    if feet:
                        feet = feet.group(1)
                        tot_inches = tot_inches + (int(feet) * 12)
                    inches = re.search(r'\d+?\'(\d+)', height)
                    if inches:
                        inches = inches.group(1)
                        inches = int(inches)
                        tot_inches = tot_inches + inches
                    height = str(int(tot_inches * 2.54)) + "cm"
                    return height
        return None
