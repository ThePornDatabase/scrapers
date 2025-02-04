import re
import scrapy
from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class MovieHeatwavePassPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/pornstars.html?p=%s',
        'external_id': r'model/(.*)/'
    }

    paginations = {
        '/pornstars.html?fs[0]=f&p=%s',
        '/pornstars.html?fs[0]=m&p=%s',
        '/pornstars.html?fs[0]=t&p=%s',
    }

    name = 'MovieHeatwavePassPerformer'

    start_url = 'http://www.heatwavepass.com'

    def get_next_page_url(self, base, page, pagination):
        return self.format_url(base, pagination % page)

    def start_requests(self):
        meta = {}
        meta['page'] = self.page

        for pagination in self.paginations:
            meta['pagination'] = pagination
            link = self.start_url
            yield scrapy.Request(url=self.get_next_page_url(link, self.page, meta['pagination']), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)


    def parse(self, response, **kwargs):
        performers = self.get_performers(response)
        count = 0
        for performer in performers:
            count += 1
            yield performer

        if count:
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                meta = response.meta
                meta['page'] = meta['page'] + 1
                print('NEXT PAGE: ' + str(meta['page']))
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page'], meta['pagination']), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_performers(self, response):
        meta = response.meta
        performers = response.xpath('//ul[contains(@class,"pornstar-list-large")]/li')
        for performer in performers:
            item = PerformerItem()

            item['name'] = self.cleanup_title(performer.xpath('.//h3/a/text()').get())
            image = performer.xpath('./a[1]/@style')
            if image:
                image = image.get()
                image = re.search(r'(http.*?)\)', image).group(1)
                item['image'] = self.format_link(response, image)
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
            else:
                item['image'] = ""
                item['image_blob'] = ""
            item['bio'] = ''
            if "=f" in meta['pagination']:
                item['gender'] = 'Female'
            elif "=m" in meta['pagination']:
                item['gender'] = 'Male'
            elif "=t" in meta['pagination']:
                item['gender'] = 'Trans Female'
            item['astrology'] = ''
            item['birthday'] = ''
            item['birthplace'] = ''
            item['cupsize'] = ''
            item['ethnicity'] = ''
            item['eyecolor'] = ''
            item['fakeboobs'] = ''
            item['haircolor'] = ''
            item['height'] = ''
            item['measurements'] = ''
            item['nationality'] = ''
            item['piercings'] = ''
            item['tattoos'] = ''
            item['weight'] = ''
            item['network'] = 'Heatwave'
            item['url'] = self.format_link(response, performer.xpath('./a[1]/@href').get())

            yield item
