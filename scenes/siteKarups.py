import re
import scrapy
import string
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.helpers.http import Http
true = True
false = False

def match_site(argument):
    match = {
        'kpc': 'karupspc',
        'kha': 'karupsha',
        'kow': 'karupsow',
    }
    return match.get(argument.lower(), argument)


class SiteKarupsSpider(BaseSceneScraper):
    name = 'Karups'
    network = "Karups"

    start_urls = [
        'https://www.karups.com/'
    ]

    cookies = [{"domain":"www.karups.com","hostOnly":true,"httpOnly":false,"name":"warningHidden","path":"/","sameSite":"unspecified","secure":false,"session":true,"storeId":"0","value":"hide"}]

    selector_map = {
        'title': '//span[@class="title"]/text()',
        'description': '',
        'date': '//span[@class="date"]/span[@class="content"]/text()',
        'image': '//video/@poster',
        'performers': '//span[@class="models"]/span[@class="content"]/a/text()',
        'tags': '',
        'trailer': '//video//source/@src',
        'external_id': r'.*?(\d+)\.htm',
        'pagination': '/videos/page%s.html'
    }

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        scenes = response.xpath('//div[@class="item-inside"]')
        for scene in scenes:
            site = scene.xpath('.//span[contains(@class, "site") and not(contains(@class, "date"))]/text()').get()
            meta['site'] = match_site(site)
            meta['parent'] = "Karups"
            meta['network'] = "Karups"

            image = scene.xpath('.//img/@src').get()
            if image:
                meta['orig_image'] = image.strip()

            sceneurl = scene.xpath('./a/@href').get()
            sceneid = re.search(r'.*?(\d+)\.htm', sceneurl)

            if sceneid:
                yield scrapy.Request(url=self.format_link(response, sceneurl), callback=self.parse_scene, meta=meta)

    def get_description(self, response):
        return ''

    def get_site(self, response):
        site = response.xpath('//span[@class="sup-title"]/span[contains(@class,"site")]/text()').get()

        if site:
            site = site.strip()
            return site
        return ''

    def get_image(self, response):
        meta = self.copy_meta(response)
        image = self.process_xpath(response, self.get_selector_map('image')).get()

        if not image:
            image = response.xpath('//div[@class="video-poster"]/img/@src').get()

        if image and image != 'https://media.karups.com/thumbs_pg/':
            image = self.format_link(response, image)
            return image
        else:
            # print("Image not found, trying to get from scene list: " + str(meta['orig_image']))
            return meta['orig_image']

    def get_image_from_link(self, image):
        if image:
            req = Http.get(image)
            if req and req.is_success:
                return req.content
        return None    

    def get_performers(self, response):
        perf_list = response.xpath('//span[@class="models"]/span[@class="content"]/a')
        performers = []
        for perf in perf_list:
            perf_name = perf.xpath('./text()').get()
            perf_url = perf.xpath('./@href').get()
            perf_id = re.search(r'-(\d+)', perf_url).group(1)
            if " " not in perf_name:
                perf_name = perf_name + " " + perf_id
            performers.append(string.capwords(perf_name.strip()))
        return performers