import tldextract
import requests
import scrapy
import string
import re
from tpdb.BaseSceneScraper import BaseSceneScraper


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
        ### 'https://www.ikissgirls.com'
    ]

    custom_settings = {
        "HTTPERROR_ALLOWED_CODES": [500],
        "RETRY_ENABLED": True,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.62',
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 10,
        'CONCURRENT_REQUESTS': 1,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,        
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
        'title': '//div[@class="video-player"]/div[@class="title-block"]/h3[@class="section-title"]/text()|//div[@class="video-player"]/div[@class="title-block"]/h2[@class="section-title"]/text()|//h1[@class="h3"]/text()',
        'description': '//div[@class="update-info-block"]/h3[contains(text(),"Description")]/following-sibling::text()|//p[contains(@class, "descriptionFull")]//text()',
        'date': '//div[@class="update-info-row"]/text()|//strong[contains(text(), "Released:")]/following-sibling::text()[contains(., ",")]',
        'image': '//div[@class="player-thumb"]//img/@src0_1x | //img[contains(@class,"main-preview")]/@src',
        'performers': '//div[contains(@class, "models-list-thumbs")]//li//span/text()|//section[@id="model-bio"]//h3/text()',
        'duration': '//strong[contains(text(), "Runtime:")]/following-sibling::text()',
        're_duration': r'(\d{1,2}\:?\d{1,2}\:\d{1,2})',
        'tags': '//ul[@class="tags"]//li//a/text()',
        'external_id': 'trailers/(.+)\\.html',
        'trailer': '',
        'type': 'Scene'
    }

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        meta['handle_httpstatus_list'] = [500]
        scenes = response.xpath('//div[contains(@class, "item-video")]')
        for scene in scenes:
            link = scene.css('a::attr(href)').get()
            if "bbcsurprise" in response.url or "backroomcastingcouch" in response.url:
                image = scene.xpath('.//video/@poster')
            else:
                image = scene.xpath('.//img[contains(@class, "update_thumb")]/@src0_1x')
            if image:
                meta['orig_image'] = self.format_link(response, image.get())
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

    def get_image(self, response):
        meta = self.copy_meta(response)
        image = self.process_xpath(response, self.get_selector_map('image'))
        if image:
            image = self.get_from_regex(image.get(), 're_image')
        
        if not image:
            if 'orig_image' in meta:
                image = meta['orig_image']
        
        if image:
            if "exploitedcollegegirls" not in response.url:
                if "-1x" in image:
                    image = image.replace("-1x", "-4x")
                if "-2x" in image:
                    image = image.replace("-2x", "-4x")
            image = self.format_link(response, image)
            image = image.replace(" ", "%20")
            return image
        
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
            cookies = {cookie['name']: cookie['value'] for cookie in self.cookies}
            req = requests.get(image, cookies=cookies, verify=False)
            if req and req.ok:
                return req.content
        return None

    def get_performers_data(self, response):
        list_id = 1
        performers = response.xpath('//section[@id="model-bio"]//div[@class="card"]')
        if not performers:
            performers = response.xpath('//div[contains(@class, "models-list-thumbs")]/ul/li')
            list_id = 2

        performers_data = []
        if len(performers):
            for performer in performers:
                perf = {}
                perf_id = performer.xpath('.//img/@id').get()
                perf_id = re.search(r'-(\d+)', perf_id).group(1)

                if list_id == 1:
                    perf_name = performer.xpath('.//h3/text()').get().strip()
                if list_id == 2:
                    perf_name = performer.xpath('.//span/text()').get().strip()

                if perf_name and " " not in perf_name.strip():
                    perf_name = f"{perf_name} {perf_id}"

                perf['name'] = string.capwords(perf_name)

                perf['extra'] = {}
                perf['extra']['gender'] = "Female"
                perf['site'] = self.get_site(response)
                image = performer.xpath('.//img/@src0_3x')
                if image:
                    image = image.get()
                    if "content" in image:
                        image = self.format_link(response, image)
                        perf['image'] = image
                        # perf['image_blob'] = self.get_image_blob_from_link(image)
                        if "?" in perf['image']:
                            perf['image'] = re.search(r'(.*?)\?', perf['image']).group(1)

                height = performer.xpath('.//strong[contains(text(), "Height:")]/following-sibling::text()')
                if height:
                    height = height.get()
                    height = re.sub(r'[^0-9\'\"]', '', height)
                    if re.search(r'(\d+)\'', height):
                        perf['extra']['height'] = self.convert_height(height)

                measurements = performer.xpath('.//strong[contains(text(), "Measurements:")]/following-sibling::text()')
                if measurements:
                    perf['extra']['measurements'] = self.convert_measurements(measurements.get())

                performers_data.append(perf)
        return performers_data
    
    def get_performers(self, response):
        performers = []
        list_id = 1
        perf_list = response.xpath('//section[@id="model-bio"]//div[@class="card"]')
        if not perf_list:
            perf_list = response.xpath('//div[contains(@class, "models-list-thumbs")]/ul/li')
            list_id = 2

        if perf_list:
            for perf in perf_list:
                perf_id = perf.xpath('.//img/@id').get()
                perf_id = re.search(r'-(\d+)', perf_id).group(1)
                if list_id == 1:
                    perf_name = perf.xpath('.//h3/text()').get().strip()
                if list_id == 2:
                    perf_name = perf.xpath('.//span/text()').get().strip()
                if perf_name and " " not in perf_name.strip():
                    perf_name = f"{perf_name} {perf_id}"
                performers.append(perf_name)
            return performers
        return []

    def convert_measurements(self, measurements):
        measurements = re.search(r'(\d+\w+).*?(\d+).*?(\d+)', measurements)
        if measurements:
            measurements = f"{measurements.group(1)}-{measurements.group(2)}-{measurements.group(3)}"
            return measurements.upper()
        return None

    def convert_height(self, height):
        if not height:
            return None

        height = height.strip()

        pattern = re.compile(
            r"""
            ^\s*
            (?P<feet>\d+)
            (?:\s*'\s*
                (?P<inches>\d+)
            )?
            \s*"?\s*$
            """,
            re.VERBOSE
        )

        match = pattern.match(height)
        if not match:
            return None

        feet = int(match.group("feet"))
        inches = int(match.group("inches")) if match.group("inches") else 0

        if feet > 8 or inches >= 12:
            return None

        cm = feet * 30.48 + inches * 2.54
        return f"{int(cm)}cm" if cm > 0 else None

