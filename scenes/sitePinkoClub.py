import re
import base64
import requests
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SitePinkoClubSpider(BaseSceneScraper):
    name = 'PinkoClub'
    network = 'Pinko Club'
    parent = 'Pinko Club'
    site = 'Pinko Club'

    start_urls = [
        'https://www.pinkoclub.com',
    ]

    selector_map = {
        'title': '//meta[@property="og:title"]/@content',
        'description': '//meta[@property="og:description"]/@content',
        'date': '',
        'image': '//meta[@property="og:image"]/@content',
        'image_blob': '//meta[@property="og:image"]/@content',
        'performers': '//h4/a/text()',
        'tags': '',
        'external_id': r'.*/(\d+.*?)\.php',
        'trailer': '',
        'pagination': '/new-video.php?next=%s'
    }

    def get_scenes(self, response):
        cookies = response.headers.getlist("Set-Cookie")
        scenes = response.xpath('//div[@class="contorno01"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta={'mycookies': cookies})

    def get_tags(self, response):
        return []

    def get_description(self, response):
        description = super().get_description(response)
        description = description.replace("\n", "").replace("\r", "").strip()
        return self.cleanup_description(description)

    def get_image_blob(self, response):
        phpsessid = re.search(r'PHPSESSID=(.*?);', str(response.meta['mycookies']))
        if phpsessid:
            cookies_dict = {'PHPSESSID': phpsessid.group(1)}
        else:
            cookies_dict = ''

        header_dict = {'Referer': 'https://www.pinkoclub.com/'}

        image = self.process_xpath(response, self.get_selector_map('image_blob'))
        if image:
            image = self.get_from_regex(image.get(), 're_image_blob')
            if image:
                image = self.format_link(response, image)
                return base64.b64encode(requests.get(image, headers=header_dict, cookies=cookies_dict).content).decode('utf-8')
        return None
