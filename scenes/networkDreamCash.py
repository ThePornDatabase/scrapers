import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


def match_site(argument):
    match = {
        'lesarchive': 'Lesarchive',
        'teen-depot': 'Teen Depot',
        'teendreams': 'Teen Dreams',
    }
    return match.get(argument, '')


class NetworkDreamCashSpider(BaseSceneScraper):
    name = 'DreamCash'
    network = 'Dream Cash'

    start_urls = [
        # ~ 'https://www.lesarchive.com',
        'https://www.teendreams.com',
        # ~ 'https://www.teen-depot.com',
    ]

    selector_map = {
        'title': '//meta[@name="twitter:title"]/@content',
        'description': '//p[@class="description"]/text()',
        'date': '//div[@class="content-date"]/span/text()',
        're_date': r'(\d{4}-\d{2}-\d{2})',
        'date_formats': ['%Y-%m-%d'],
        'image': '//script[contains(text(), "poster")]/text()',
        'image_blob': True,
        're_image': r'poster=\"(.*?)\"',
        'performers': '//h3[@class="item-name"]',
        'tags': '',
        'external_id': r'.*/(.*?).html',
        'trailer': '//script[contains(text(), "video_content")]/text()',
        're_trailer': r'video src=\"(.*?\.mp4)',
        'pagination': '/t4/categories/movies_%s_d.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="content-item"]/div/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_performers(self, response):
        performers = response.xpath('//img[contains(@class, "category_model_thumb")]/ancestor::div[contains(@class, "col-3-inner")]')
        performer_list = []
        if performers:
            performer_name = performers.xpath('.//div[@class="half-col-item"]//span/text()')
            if performer_name:
                performer_name = performer_name.get()
                normalized = performer_name.lower().replace(" and ", "&")
                if "&" in normalized:
                    performer_list = [string.capwords(p.strip()) + "-99999" for p in normalized.split("&")]
                elif " " in normalized:
                    performer_list = [string.capwords(normalized.strip())]
                else:
                    perf_url = performers.xpath('./div[1]/a/@href')
                    if perf_url:
                        perf_url = perf_url.get()
                        perf_url = re.search(r'-(\d+)\.htm', perf_url)
                        if perf_url:
                            performer_list = [string.capwords(normalized.strip()) + "-" + "{:04}".format(int(perf_url.group(1)))]
                        else:
                            performer_list = [string.capwords(normalized.strip()) + "-0000"]

        if not performer_list:
            performer_list = []
        return performer_list

    def get_tags(self, response):
        if "teen" in response.url:
            return ['Teen']
        if "lesarchive" in response.url:
            return ['Lesbian']
        return []

    def get_site(self, response):
        return match_site(super().get_site(response))

    def get_parent(self, response):
        return match_site(super().get_parent(response))

    def get_image(self, response):
        image = super().get_image(response)
        if not image or "content" not in image:
            image = response.xpath('//div[contains(@class, "player-window")]/following-sibling::img[contains(@class, "update_thumb")]/@src0_1x')
            if image:
                image = image.get()
                image = self.format_link(response, image)
        if "-1x" in image:
            image = image.replace("-1x", "-full")
        return image

    def get_performers_data(self, response):
        performers = self.get_performers(response)
        performers_data = []
        for performer in performers:
            perf = {}
            perf['name'] = performer
            perf['site'] = self.get_site(response)
            perf['network'] = "Dream Cash"
            perf['extra'] = {}
            perf['extra']['gender'] = "Female"

            image = response.xpath('//img[contains(@class, "category_model_thumb")]/@src0_1x')
            if image:
                image = self.format_link(response, image.get())
                perf['image'] = image
                perf['image_blob'] = self.get_image_blob_from_link(image)

            performers_data.append(perf)
        return performers_data
