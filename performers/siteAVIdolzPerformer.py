import scrapy
from scrapy.utils.project import get_project_settings
from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteAVIdolzPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '',
        'image': '',
        'image_blob': True,
        'bio': '',
        'gender': '',
        'astrology': '',
        'birthday': '',
        'birthplace': '',
        'cupsize': '',
        'ethnicity': '',
        'eyecolor': '',
        'fakeboobs': '',
        'haircolor': '',
        'height': '',
        'measurements': '',
        'nationality': '',
        'piercings': '',
        'tattoos': '',
        'weight': '',

        'pagination': '',
        'external_id': r'model/(.*)/'
    }

    name = 'AVIdolzPerformer'
    network = 'AVIdolz'

    start_urls = [
        'https://avidolz.com/jav-models/',
    ]

    def get_gender(self, response):
        return 'Female'


    def start_requests(self):
        settings = get_project_settings()

        meta = {}
        meta['page'] = self.page
        if 'USE_PROXY' in settings.attributes.keys():
            use_proxy = settings.get('USE_PROXY')
        else:
            use_proxy = None

        if use_proxy:
            print(f"Using Settings Defined Proxy: True ({settings.get('PROXY_ADDRESS')})")
        else:
            try:
                if self.proxy_address:
                    meta['proxy'] = self.proxy_address
                    print(f"Using Scraper Defined Proxy: True ({meta['proxy']})")
            except Exception:
                print("Using Proxy: False")

        url = "https://avidolz.com/jav-models/"
        yield scrapy.Request(url, callback=self.get_performers, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_performers(self, response):
        performers = response.xpath('//div[@class="rel"]')
        for performer in performers:
            item = PerformerItem()

            item['name'] = self.cleanup_title(performer.xpath('.//h3/text()').get())
            item['image'] = self.format_link(response, performer.xpath('./a/img/@src').get())
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['bio'] = ''
            item['gender'] = ''
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
            item['network'] = 'AVIdolz'
            item['url'] = self.format_link(response, performer.xpath('./a/@href').get())

            yield item
