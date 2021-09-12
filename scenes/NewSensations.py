import dateparser
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
        'date': "//div[contains(@class, 'stat')]//span[contains(text(),'Date:')]/following-sibling::span/text()",
        'image': '//span[@id="trailer_thumb"]//img/@src',
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

    def get_date(self, response):
        date = response.xpath(
            '//div[@class="sceneDateP"]/span/text()').get().strip(',').strip()
        return dateparser.parse(date).isoformat()

    def get_tags(self, response):
        return []

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
