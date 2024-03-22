import scrapy
from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteIFeelMyselfPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/public/main.php?page=view&mode=all&offset=%s',
        'external_id': r'model/(.*)/'
    }

    name = 'IFeelMyselfPerformer'
    network = 'Feck Erotica'

    start_urls = [
        'https://ifeelmyself.com',
    ]

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
            yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page']),
                                 callback=self.parse,
                                 meta=meta,
                                 headers=self.headers,
                                 cookies=self.cookies)

    def get_performers(self, response):
        performers = response.xpath('//table[@class="DispResults"]')
        for performer in performers:
            item = self.init_performer()

            item['name'] = self.cleanup_title(performer.xpath('.//a[contains(@href, "artist_bio")]/text()').get())
            image = performer.xpath('.//img/@src')
            if image:
                item['image'] = self.format_link(response, image.get())
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
            else:
                item['image'] = ""
                item['image_blob'] = ""
            item['gender'] = 'Female'
            item['network'] = 'Feck Erotica'
            item['url'] = self.format_link(response, performer.xpath('.//a[contains(@href, "artist_bio")]/@href').get())

            yield item

    def get_next_page_url(self, base, page):
        page = str((int(page) - 1) * 12)
        return self.format_url(base, self.get_selector_map('pagination') % page)
