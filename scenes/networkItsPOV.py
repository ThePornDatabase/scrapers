import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkItsPOVSpider(BaseSceneScraper):
    name = 'ItsPOV'
    network = 'Its POV'

    url = 'https://itspov.com/'

    paginations = [
        '/collection/officepov/more?lang=en&page=%s&sorting=new',
        '/collection/backdoorpov/more?lang=en&page=%s&sorting=new',
        '/collection/intimatepov/more?lang=en&page=%s&sorting=new',
        '/collection/feetishpov/more?lang=en&page=%s&sorting=new',
        '/collection/academypov/more?lang=en&page=%s&sorting=new',
        '/collection/steppov/more?lang=en&page=%s&sorting=new',
        '/collection/petitepov/more?lang=en&page=%s&sorting=new',
        '/collection/morepov/more?lang=en&page=%s&sorting=new',
        '/collection/ilovepov/more?lang=en&page=%s&sorting=new',
    ]

    headers = {
        'x-requested-with': 'XMLHttpRequest',
    }

    # ~ custom_settings = {'CONCURRENT_REQUESTS': '1',
    # ~ 'AUTOTHROTTLE_ENABLED': 'True',
    # ~ 'AUTOTHROTTLE_DEBUG': 'False',
    # ~ 'DOWNLOAD_DELAY': '2',
    # ~ 'CONCURRENT_REQUESTS_PER_DOMAIN': '1',

    # ~ 'ITEM_PIPELINES': {
    # ~ 'tpdb.pipelines.TpdbApiScenePipeline': 400,
    # ~ },
    # ~ 'DOWNLOADER_MIDDLEWARES': {
    # ~ 'tpdb.middlewares.TpdbSceneDownloaderMiddleware': 543,
    # ~ }
    # ~ }

    selector_map = {
        'title': '//h1[@class="title"]/text()',
        'description': '//div[contains(@class,"content-description")]//span[@class="full"]/p/span/text()',
        'date': '//div[@class="right"]/span[@class="publish_date"]/text()',
        'date_formats': ['%B %d, %Y'],
        'performers': '//h1[@class="title"]/following-sibling::div[@class="actress"]/a/text()',
        'type': 'Scene',
        'external_id': r'/(\d+)/',
    }

    def get_next_page_url(self, base, page, pagination):
        return self.format_url(base, pagination % page)

    def start_requests(self):
        yield scrapy.Request("https://itspov.com/en/", callback=self.start_requests2, headers=self.headers, cookies=self.cookies)

    def start_requests2(self, response):
        for pagination in self.paginations:
            meta = {}
            meta['page'] = self.page
            meta['pagination'] = pagination
            meta['check_date'] = "2023-10-03"
            url = self.get_next_page_url(response.url, meta['page'], meta['pagination'])
            yield scrapy.Request(url, method='POST', callback=self.get_scenes, meta=meta, headers=self.headers, cookies=self.cookies)

    def parse(self, response, **kwargs):
        print(response.text)
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
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page'], meta['pagination']), method='POST', callback=self.parse, meta=meta, headers=self.headers)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class,"scene thumbnail")]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_site(self, response):
        meta = response.meta
        return re.search(r'collection/(.*?)/', meta['pagination']).group(1)

    def get_parent(self, response):
        meta = response.meta
        return re.search(r'collection/(.*?)/', meta['pagination']).group(1)

    def get_image(self, response):
        images = response.xpath('//div[@class="player_container"]/span[@class="thumb-ratio"]//source/@data-srcset')
        final_image = ""
        if images:
            images = images.getall()
            for image in images:
                image = re.search(r',.*?(http.*?)\s', image)
                if image:
                    image = image.group(1)
                    if not final_image:
                        final_image = image
                    else:
                        final_res = re.search(r'(\d+)_\d+_crop', final_image)
                        image_res = re.search(r'(\d+)_\d+_crop', image)
                        if final_res and image_res:
                            final_res = final_res.group(1)
                            image_res = image_res.group(1)
                            if int(image_res) > int(final_res):
                                final_image = image
        return final_image

    def get_tags(self, response):
        return ['POV']

    def get_duration(self, response):
        duration = response.xpath('//div[@class="right"]/span[@class="duration"]/text()')
        if duration:
            duration = duration.get()
            duration = re.search(r'(\d+)m(\d+)', duration.lower())
            if duration:
                minutes = int(duration.group(1)) * 60
                seconds = int(duration.group(2))
                return str(minutes + seconds)
        return None
