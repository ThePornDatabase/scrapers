import re
import string
import scrapy
from scrapy.utils.project import get_project_settings
from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class NetworkAVRevenuePerformerSpiderPerformers(BasePerformerScraper):
    name = 'AVRevenuePerformer'
    network = 'AV Revenue'

    start_urls = [
        'https://baberotica.com/feed/models?limit=9999',
        'https://baberoticavr.com/feed/models?limit=9999',
        'https://japanhdv.com/feed/models?limit=9999',
        'https://tenshigao.com/feed/models?limit=9999',
    ]

    selector_map = {
        'external_id': '(\\d+)$',
        'pagination': '/en/videos?page=%s'
    }

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

        for link in self.start_urls:
            yield scrapy.Request(link, callback=self.get_models, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_models(self, response):
        models = response.xpath('//model')
        for performer in models:
            item = PerformerItem()
            item['network'] = 'AV Revenue'
            item['name'] = string.capwords(self.get_field(performer, './name/text()'))
            url = performer.xpath('.//text()').getall()
            url = " ".join(url)
            url = url.replace("\n", "").replace("  ", " ")
            url = re.search(r'(http.*?model.*?)\s', url).group(1).strip()
            item['url'] = url

            item['image'] = self.get_field(performer, './image/text()')
            if item['image']:
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
            else:
                item['image_blob'] = None
            item['bio'] = ''
            item['gender'] = 'Female'
            item['birthday'] = self.get_field(performer, './personal/birthdate/text()')
            item['astrology'] = ''
            item['birthplace'] = ''
            item['nationality'] = self.get_field(performer, './personal/country/text()')
            breast = self.get_field(performer, './appearance/breast/text()')
            waist = self.get_field(performer, './appearance/waist/text()')
            hips = self.get_field(performer, './appearance/hips/text()')
            cupsize = self.get_field(performer, './appearance/cup/text()')
            if breast and waist and hips:
                item['measurements'] = f'{breast}{cupsize}-{waist}-{hips}'.upper()
            else:
                item['measurements'] = ''
            item['tattoos'] = self.get_field(performer, './appearance/tattoos/text()')
            item['piercings'] = self.get_field(performer, './appearance/piercings/text()')
            if breast and cupsize:
                item['cupsize'] = f'{breast}{cupsize}'.upper()
            else:
                item['cupsize'] = ''
            item['ethnicity'] = self.get_field(performer, './personal/ethnicity/text()')
            item['fakeboobs'] = ''
            item['haircolor'] = self.get_field(performer, './appearance/hair/text()')
            item['eyecolor'] = self.get_field(performer, './appearance/eye/text()')
            item['weight'] = self.get_field(performer, './appearance/weight/text()')
            item['height'] = self.get_field(performer, './appearance/height/text()')
            yield item

    def get_field(self, scene, xpath):
        field = scene.xpath(xpath)
        if field:
            return field.get().strip()
        return None

    def get_fields(self, scene, xpath):
        fields = scene.xpath(xpath)
        if fields:
            return fields.getall()
        return None
