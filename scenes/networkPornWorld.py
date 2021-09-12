import re
import dateparser

import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class PornWorldScraper(BaseSceneScraper):
    name = 'PornWorld'
    network = 'ddfnetwork'

    start_urls = [
        'https://1by-day.com/',
        'https://ddfbusty.com/',
        'https://eurogirlsongirls.com/',
        'https://euroteenerotica.com/',
        'https://fuckinhd.com',
        'https://handsonhardcore.com/',
        'https://hotlegsandfeet.com/',
        'https://houseoftaboo.com/',
        'https://onlyblowjob.com/',
    ]

    selector_map = {
        'title': "//div[@id='video-specs']/h1/text()",
        'description': "//div[@class='descr-box']//p/text()",
        'date': "//meta[@itemprop='uploadDate']/@content",
        'image': '//meta[@itemprop="thumbnailUrl"]/@content',
        'performers': "//div[contains(@class,'pornstar-card')]//meta[@itemprop='name']/@content",
        'tags': "ul.tags a::text",
        'external_id': r'videos\\/[A-Z-_a-z0-9+]+\\/(\\d+)',
        'trailer': '//meta[@itemprop="contentUrl"]/@content',
        'pagination': '/videos/search/latest/ever/allsite/-/%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath(
            "//*[@id='scenesAjaxReplace']//a/@href").getall()
        for scene in scenes:
            if re.match(r'.*\d{4}-\d{2}-\d{2}$', scene):
                scene = re.search(r'(.*)\d{4}-\d{2}-\d{2}$', scene).group(1)
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_date(self, response):
        date = self.process_xpath(response, self.get_selector_map('date')).get()
        if date:
            date.replace('Released:', '').replace('Added:', '').strip()
            return dateparser.parse(date.strip()).isoformat()
        date = response.xpath('//div[@id="video-specs"]/div/div/div[contains(@class, "d-inline-flex")]/p/text()').get()
        if re.match(r'\d{2}.\d{2}.\d{4}', date):
            return dateparser.parse(date.strip()).isoformat()

    def get_description(self, response):

        title = self.process_xpath(
            response, self.get_selector_map('title')).get().strip()
        if not title:
            title = response.xpath('//meta[@itemprop="name"]/@content').group(1).strip()

        description = self.process_xpath(
            response, self.get_selector_map('description')).get()

        if not description:
            description = response.xpath('//meta[@itemprop="description"]/@content').get()

        if not description:
            description = title

        return description.replace("\\", "").strip()

    def get_title(self, response):
        title = self.process_xpath(
            response, self.get_selector_map('title')).get()
        if not title:
            title = response.xpath('//meta[@itemprop="name"]/@content').group(1).strip()
        return title

    def get_image(self, response):
        image = self.process_xpath(response, self.get_selector_map('image')).get()
        if not image:
            image = response.xpath('//div[@class="video-box"]/div/img/@src').get()
        if not image:
            image = response.xpath('//div[contains(@class,"video-join-box")]/img/@src').get()
        if image:
            image = image.strip()
        if not image:
            image = ''

        return self.format_link(response, image)
