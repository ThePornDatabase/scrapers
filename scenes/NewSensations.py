import base64
import requests
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class NewSensationsSpider(BaseSceneScraper):
    name = 'NewSensations'
    network = 'New Sensations'

    start_urls = [
        'https://www.newsensations.com'

        # Sites that are included in scrape, though site names aren't given for scraping
        # Here for reference so we don't double scrape:
        # -------------------------------
        # https://familyxxx.com
        # https://hotwifexxx.com
        # https://parodypass.com
        # https://stretchedoutsnatch.com
        # https://tabutales.com
        # https://talesfromtheedge.com
        # https://thelesbianexperience.com
    ]

    selector_map = {
        'title': '//div[@class="indScene"]/*[self::h1 or self::h2 or self::h3]/text()',
        'description': '//div[@class="description"]/span/following-sibling::h2/text()',
        'date': '//div[@class="sceneDateP"]/span/text()',
        'image': '//span[@id="trailer_thumb"]//img/@src',
        'image_blob': '//span[@id="trailer_thumb"]//img/@src',
        'performers': '//div[@class="sceneTextLink"]//span[@class="tour_update_models"]/a/text()',
        'tags': '//meta[@name="keywords"]/@content',
        'external_id': 'tour_ns\\/updates\\/(.+)\\.html',
        'trailer': '',
        'pagination': '/tour_ns/categories/movies_%s_d.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="captions"]/h4/a/@href').getall()
        for scene in scenes:
            yield scrapy.Request(url=scene, callback=self.parse_scene)

    def get_site(self, response):
        if self.get_selector_map('tags'):
            taglist = self.process_xpath(response, self.get_selector_map('tags')).get()
            taglist = taglist.replace(" ", "")
            if "hotwifexxx" in taglist.lower():
                return "HotWifeXXX"
            if "thelesbianexperience" in taglist.lower():
                return "The Lesbian Experience"
            if "familyxxx" in taglist.lower():
                return "Family XXX"
            if "tabutales" in taglist.lower():
                return "Tabu Tales"
            if "stretchedoutsnatch" in taglist.lower():
                return "Stretched Out Snatch"
            if "talesfromtheedge" in taglist.lower():
                return "Tales From the Edge"
            if "parody" in taglist.lower():
                return "Parody Pass"
            return "New Sensations"

    def get_image(self, response):
        image = super().get_image(response)
        if image[-3:] == "%20":
            image = image[:-3]
        return image

    def get_image_blob(self, response):
        image = self.get_image(response)
        if image:
            image = self.format_link(response, image)
            return base64.b64encode(requests.get(image).content).decode('utf-8')
        return None

    def get_tags(self, response):
        performers = super().get_performers(response)
        site = self.get_site(response).strip().title()

        tags = super().get_tags(response)
        if len(tags) == 1 and "," in tags[0]:
            tags = tags[0].split(',')
            tags = list(map(lambda x: x.strip().title(), tags))
            for performer in performers:
                if performer in tags:
                    tags.remove(performer)
            if "Movies" in tags:
                tags.remove("Movies")
            if "4K" in tags:
                tags.remove("4K")
            if "New Sensations" in tags:
                tags.remove("New Sensations")
            if site in tags:
                tags.remove(site)
            tags2 = tags.copy()
            for tag in tags2:
                if "#" in tag:
                    tags.remove(tag)

        return tags
