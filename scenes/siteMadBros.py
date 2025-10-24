import re
import requests
import string
from scrapy.selector import Selector
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
true = True
false = False


class SiteMadBrosSpider(BaseSceneScraper):
    name = 'MadBros'
    site = 'MadBros'
    parent = 'MadBros'
    network = 'MadBros'

    start_urls = [
        'https://madbrosx.com'
    ]

    cookies = [{"domain":".madbrosx.com","hostOnly":false,"httpOnly":false,"name":"sbjs_migrations","path":"/","sameSite":"unspecified","secure":false,"session":true,"storeId":"0","value":"1418474375998%3D1"},{"domain":".madbrosx.com","hostOnly":false,"httpOnly":false,"name":"sbjs_current_add","path":"/","sameSite":"unspecified","secure":false,"session":true,"storeId":"0","value":"fd%3D2025-05-01%2020%3A25%3A28%7C%7C%7Cep%3Dhttps%3A%2F%2Fmadbrosx.com%2Fvideos%2F%7C%7C%7Crf%3D%28none%29"},{"domain":".madbrosx.com","hostOnly":false,"httpOnly":false,"name":"sbjs_first_add","path":"/","sameSite":"unspecified","secure":false,"session":true,"storeId":"0","value":"fd%3D2025-05-01%2020%3A25%3A28%7C%7C%7Cep%3Dhttps%3A%2F%2Fmadbrosx.com%2Fvideos%2F%7C%7C%7Crf%3D%28none%29"},{"domain":".madbrosx.com","hostOnly":false,"httpOnly":false,"name":"sbjs_current","path":"/","sameSite":"unspecified","secure":false,"session":true,"storeId":"0","value":"typ%3Dtypein%7C%7C%7Csrc%3D%28direct%29%7C%7C%7Cmdm%3D%28none%29%7C%7C%7Ccmp%3D%28none%29%7C%7C%7Ccnt%3D%28none%29%7C%7C%7Ctrm%3D%28none%29%7C%7C%7Cid%3D%28none%29%7C%7C%7Cplt%3D%28none%29%7C%7C%7Cfmt%3D%28none%29%7C%7C%7Ctct%3D%28none%29"},{"domain":".madbrosx.com","hostOnly":false,"httpOnly":false,"name":"sbjs_first","path":"/","sameSite":"unspecified","secure":false,"session":true,"storeId":"0","value":"typ%3Dtypein%7C%7C%7Csrc%3D%28direct%29%7C%7C%7Cmdm%3D%28none%29%7C%7C%7Ccmp%3D%28none%29%7C%7C%7Ccnt%3D%28none%29%7C%7C%7Ctrm%3D%28none%29%7C%7C%7Cid%3D%28none%29%7C%7C%7Cplt%3D%28none%29%7C%7C%7Cfmt%3D%28none%29%7C%7C%7Ctct%3D%28none%29"},{"domain":".madbrosx.com","hostOnly":false,"httpOnly":false,"name":"sbjs_udata","path":"/","sameSite":"unspecified","secure":false,"session":true,"storeId":"0","value":"vst%3D1%7C%7C%7Cuip%3D%28none%29%7C%7C%7Cuag%3DMozilla%2F5.0%20%28Windows%20NT%2010.0%3B%20Win64%3B%20x64%29%20AppleWebKit%2F537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome%2F135.0.0.0%20Safari%2F537.36%20Edg%2F135.0.0.0"},{"domain":"madbrosx.com","hostOnly":true,"httpOnly":false,"name":"age_gate","path":"/","sameSite":"no_restriction","secure":true,"session":true,"storeId":"0","value":"18"},{"domain":"madbrosx.com","expirationDate":1746218035.77515,"hostOnly":true,"httpOnly":true,"name":"client_ipv4","path":"/","sameSite":"unspecified","secure":true,"session":false,"storeId":"0","value":"169.150.204.36"},{"domain":".madbrosx.com","expirationDate":1746133563,"hostOnly":false,"httpOnly":false,"name":"sbjs_session","path":"/","sameSite":"unspecified","secure":false,"session":false,"storeId":"0","value":"pgs%3D9%7C%7C%7Ccpg%3Dhttps%3A%2F%2Fmadbrosx.com%2Fvideos%2F"}]

    selector_map = {
        'title': '//div[@class="mx-heading-h4"]/text()',
        'description': '//div[contains(@class, "mx-single-video-info-excerpt")]/p/text()',
        'date': '//div[contains(@class, "info-meta-date")]/text()[contains(., "date")]',
        're_date': r'(\d{1,2}/\d{1,2}/\d{4})',
        'date_formats': ['%d/%m/%Y'],
        'performers': '//div[contains(text(), "Featuring")]/a/text()',
        'type': 'Scene',
        'external_id': r'.*/(.*?)/$',
        'pagination': '/videos/page/%s/',
    }

    custom_scraper_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.62',
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 120,
        'CONCURRENT_REQUESTS': 1,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'CONCURRENT_REQUESTS_PER_IP': 1,
    }

    def get_next_page_url(self, base, page):
        if int(page) == 1:
            return "https://madbrosx.com/videos/"
        return self.format_url(base, self.get_selector_map('pagination') % page)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="wpb_wrapper"]/div[@class="mx-video-item"]')
        for scene in scenes:
            duration = scene.xpath('.//div[@class="video-duration"]/text()')
            if duration:
                duration = re.sub(r'[^0-9:]+', '', duration.get())
                meta['duration'] = self.duration_to_seconds(duration)

            # ~ image = scene.xpath('.//img/@src')
            # ~ if image:
                # ~ meta['image'] = image.get()
                # ~ meta['image_blob'] = self.get_image_blob_from_link(meta['image'])

            meta['trailer'] = scene.xpath('./div[1]/@data-preview-src').get()

            scene = scene.xpath('./div[1]/a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_image(self, response):
        image = response.xpath('//div[contains(@class, "mx-single-video")]//iframe/@src')
        if image:
            image = image.get()
            req = requests.get(image)
            if req.status_code == 200:
                selector = Selector(text=req.text)
                image = selector.xpath('//meta[@property="og:image"]/@content')
                return image.get()

        return None

    def get_tags(self, response):
        tags = []
        taglist = response.xpath('//div[@class="mx-video-tags-list"]/a/text()').getall()
        for tagentry in taglist:
            tagentry = string.capwords(tagentry.replace("#", ""))
            tags.append(tagentry)
        return tags
