from datetime import date, timedelta
import tldextract
import requests
import scrapy
import re
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


def match_site(argument):
    match = {
        'backroomcastingcouch': "Backroom Casting Couch",
        'bbcsurprise': "BBC Surprise",
        'exploitedcollegegirls': "Exploited College Girls",
        'ikissgirls': "I Kiss Girls",
        'interracialpass': "Interracial Pass",
    }
    return match.get(argument, '')


class InterracialPassSpider(BaseSceneScraper):
    name = 'InterracialPass'
    network = 'ExploitedX'
    handle_httpstatus_list = [500]

    start_urls = [
        'https://www.interracialpass.com',
        'https://www.backroomcastingcouch.com',
        'https://bbcsurprise.com',
        'https://exploitedcollegegirls.com',
        # 'https://www.ikissgirls.com'
    ]

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        "HTTPERROR_ALLOWED_CODES": [500],
        "RETRY_ENABLED": False
    }

    cookies = [{
                        "name": "warn",
                        "value": "true"
                    }, {
                        "name": "numheader",
                        "value": "1"
                    }
                ]

    selector_map = {
        'title': '//div[@class="video-player"]/div[@class="title-block"]/h3[@class="section-title"]/text()|//div[@class="video-player"]/div[@class="title-block"]/h2[@class="section-title"]/text()',
        'description': '//div[@class="update-info-block"]/h3[contains(text(),"Description")]/following-sibling::text()',
        'date': '//div[@class="update-info-row"]/text()',
        'image': '//div[@class="player-thumb"]//img/@src0_1x | //img[contains(@class,"main-preview")]/@src',
        'performers': '//div[contains(@class, "models-list-thumbs")]//li//span/text()',
        'duration': '//strong[contains(text(), "Runtime:")]/following-sibling::text()',
        're_duration': r'(\d{1,2}\:?\d{1,2}\:\d{1,2})',
        'tags': '//ul[@class="tags"]//li//a/text()',
        'external_id': 'trailers/(.+)\\.html',
        'trailer': '',
        'type': 'Scene'
    }

    def get_scenes(self, response):
        meta = response.meta
        meta['handle_httpstatus_list'] = [500]
        scenes = response.xpath('//div[contains(@class, "item-video")]')
        for scene in scenes:
            link = scene.css('a::attr(href)').get()
            image = scene.xpath('.//img/@src0_1x')
            if image:
                meta['image'] = self.format_link(response, image.get())
                meta['image_blob'] = self.get_image_blob_from_link(meta['image'])
            if link:
                yield scrapy.Request(url=self.format_link(response, link), callback=self.parse_scene, meta=meta)

    def get_next_page_url(self, base, page):
        selector = '/t1/categories/movies_%s_d.html'

        if 'exploitedcollegegirls' in base:
            selector = '/categories/movies_%s_d.html'
        elif 'ikissgirls' in base:
            selector = '/categories/movies_%s_d.html'
        elif 'bbcsurprise' in base:
            selector = '/categories/movies_%s_d.html'
        elif 'backroomcastingcouch' in base:
            selector = '/categories/movies_%s_d.html'

        return self.format_url(base, selector % page)

    def get_date(self, response):
        date = self.process_xpath(
            response, self.get_selector_map('date')).extract()
        return self.parse_date(date[1].strip()).isoformat()

    def get_image(self, response):
        meta = response.meta
        image = self.process_xpath(response, self.get_selector_map('image'))
        if image:
            image = self.get_from_regex(image.get(), 're_image')

            if image:
                image = self.format_link(response, image)
                return image.replace(" ", "%20")
        else:
            if 'image' in meta:
                return self.format_link(response, meta['image'])
        return ''

    def get_site(self, response):
        site = tldextract.extract(response.url).domain
        site = match_site(site)
        return site

    def get_parent(self, response):
        parent = tldextract.extract(response.url).domain
        parent = match_site(parent)
        return parent

    def get_id(self, response):
        return super().get_id(response).lower()

    def get_description(self, response):
        description = super().get_description(response)
        if not description:
            alt_description = response.xpath('//div[@class="update-info-block"]/h3[contains(text(),"Description")]/following-sibling::p[contains(@class, "descriptionFull")]/text()')
            if alt_description:
                description = alt_description.getall()
                description = " ".join(description)
                description = description.replace('\r', ' ').replace('\t', ' ').replace('\n', ' ')
                description = re.sub(r'\s+', ' ', description)
                description = self.cleanup_description(description.strip())
            else:
                alt_description = response.xpath('//div[@class="update-info-block"]/h3[contains(text(),"Description")]/following-sibling::p[contains(@class, "description")]/text()')
                if alt_description:
                    description = alt_description.getall()
                    description = " ".join(description)
                    description = self.cleanup_description(description.strip())
        return description

    def get_image_from_link(self, image):
        if image and self.cookies:
            cookies = {cookie['name']:cookie['value'] for cookie in self.cookies}
            req = requests.get(image, cookies=cookies, verify=False)

            if req and req.ok:
                return req.content
        return None
