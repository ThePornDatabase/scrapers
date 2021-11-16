import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteCospuriSpider(BaseSceneScraper):
    name = 'Cospuri'
    network = 'Cospuri'
    parent = 'Cospuri'
    site = 'Cospuri'

    url = 'https://www.cospuri.com/'

    paginations = [
        '/samples?channel=cosplay&page=%s',
        '/samples?channel=bukkake&page=%s',
        '/samples?channel=schoolgirl&page=%s',
        '/samples?channel=harajuku&page=%s',
    ]

    selector_map = {
        'title': '//div[@class="sample-model"]/a/text()',
        'description': '//div[@class="description"]/text()',
        'date': '//div[@class="date"]/text()',
        'image': '//div[@class="vid cosplay"]/div/@style',
        're_image': r'\((http.*.jpg)\)',
        'performers': '//div[@class="sample-model"]/a/text()',
        'tags': '//div[@class="tags"]/a/text()',
        'external_id': 'id=(.*)',
        'trailer': '//script[contains(text(),"sources")]/text()',
        're_trailer': r'(https.*\.mp4)',
        'pagination': '/samples?channel=cosplay&page=%s'
    }

    def start_requests(self):
        for pagination in self.paginations:
            yield scrapy.Request(url=self.get_next_page_url(self.url, self.page, pagination),
                                 callback=self.parse,
                                 meta={
                'page': self.page, 'pagination': pagination},
                headers=self.headers,
                cookies=self.cookies)

    def parse(self, response, **kwargs):
        if response.status == 200:
            scenes = self.get_scenes(response)
            count = 0
            for scene in scenes:
                count += 1
                yield scene

            if count:
                if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                    meta = response.meta
                    meta['page'] = meta['page'] + 1
                    print('NEXT PAGE: ' + str(meta['page']))
                    yield scrapy.Request(url=self.get_next_page_url(self.url, meta['page'], meta['pagination']),
                                         callback=self.parse,
                                         meta=meta,
                                         headers=self.headers,
                                         cookies=self.cookies)

    def get_next_page_url(self, url, page, pagination):
        return self.format_url(url, pagination % page)

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="scene cosplay"]/div/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_date(self, response):
        date = self.process_xpath(response, self.get_selector_map('date')).get()
        if date:
            dates = re.search(r'(\d{4}).*?(\d{2}).*?(\d{2})', date)
            if dates:
                year = dates.group(1)
                month = dates.group(2)
                day = dates.group(3)
                date = year + month + day

            return self.parse_date(date, date_formats=['%Y%m%d']).isoformat()

        return None
