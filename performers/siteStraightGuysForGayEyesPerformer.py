import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper
from scrapy.utils.project import get_project_settings


class PerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@class="profile_details"]/h3/text()',
        'image': '//div[@class="profile_img"]/img/@src0_1x',
        'image_blob': True,
        'bio': '',
        'gender': '',
        'astrology': '//li[contains(@class, "model_profile_sign")]/span/text()',
        'birthday': '',
        'birthplace': '',
        'cupsize': '',
        'ethnicity': '',
        'eyecolor': '//li[contains(text(), "EYE COLOR")]/span/text()',
        'fakeboobs': '',
        'haircolor': '//li[contains(text(), "HAIR COLOR")]/span/text()',
        'height': '//li[contains(text(), "HEIGHT")]/span/text()',
        'measurements': '',
        'nationality': '',
        'piercings': '',
        'tattoos': '',
        'weight': '//li[contains(text(), "WEIGHT")]/span/text()',

        'pagination': '',
        'external_id': r'model/(.*)/'
    }

    name = 'StraightGuysForGayEyesPerformer'
    network = 'Straight Guys For Gay Eyes'

    url = "https://www.straightguysforgayeyes.com"

    paginations = [
        '/tour/models/%s/latest/?gender=female',
        '/tour/models/%s/latest/?gender=male',
    ]

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

        for pagination in self.paginations:
            link = self.url
            meta['pagination'] = pagination
            yield scrapy.Request(url=self.get_next_page_url(link, self.page, pagination),
                                 callback=self.parse,
                                 meta=meta,
                                 headers=self.headers,
                                 cookies=self.cookies)

    def parse(self, response):
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
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page'], meta['pagination']),
                                     callback=self.parse,
                                     meta=meta,
                                     headers=self.headers,
                                     cookies=self.cookies)

    def get_next_page_url(self, base, page, pagination):
        return self.format_url(base, pagination % page)

    def get_gender(self, response):
        if "female" in response.meta['pagination']:
            return 'Female'
        return "Male"

    def get_performers(self, response):
        meta = response.meta
        performers = response.xpath('//div[contains(@class, "sexyman_img")]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, cookies=self.cookies, headers=self.headers, meta=meta)

    def get_image(self, response):
        if 'image' in self.get_selector_map():
            image = self.get_element(response, 'image', 're_image')
            image = "https://www.straightguysforgayeyes.com/tour/" + image
            return image.replace(' ', '%20')
        return ''
