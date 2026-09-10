import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class Site1111CustomsXXXSpider(BaseSceneScraper):
    name = '1111CustomsXXX'
    site = '1111CustomsXXX'
    parent = '1111CustomsXXX'
    network = '1111CustomsXXX'

    start_urls = [
        'https://www.1111customsxxx.com',
    ]

    # The site left its Elevated X tour behind: the listing is /videos and scenes
    # live at /video/<slug>.  The scene page has the title, cast, categories and a
    # trailer but no release date of its own (the dates on it belong to the related
    # videos), so the date comes from the card's <time> element.
    selector_map = {
        'title': '//h1//text()',
        'description': '',
        'date': '',
        'date_formats': ['%m/%d/%Y'],
        'image': '',
        'performers': '//a[contains(@href, "/model/")]/text()',
        'tags': '//a[contains(@href, "/category/") or contains(@href, "/categories/")]/text()',
        # the player lists a 4K and a 2K source; take one or get_trailer gets a list
        'trailer': '//video[1]/source[1]/@src',
        'external_id': r'/video/(.+?)/?$',
        'pagination': '/videos?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        for card in response.xpath('//article[contains(@class, "flex flex-col overflow-hidden")]'):
            link = card.xpath('.//h3/a/@href').get()
            if not link or not re.search(self.get_selector_map('external_id'), link):
                continue
            meta = {}
            title = card.xpath('.//h3/a/text()').get()
            if title:
                meta['title'] = self.cleanup_title(title)
            scenedate = card.xpath('.//time/text()').get()
            if scenedate:
                scenedate = re.search(r'(\d{2}/\d{2}/\d{4})', scenedate)
                if scenedate:
                    scenedate = self.parse_date(scenedate.group(1), date_formats=['%m/%d/%Y'])
                    if scenedate:
                        meta['date'] = scenedate.strftime('%Y-%m-%d')
            performers = [x.strip() for x in card.xpath('.//a[contains(@href, "/model/")]/text()').getall() if x and x.strip()]
            if performers:
                meta['performers'] = performers
            image = card.xpath('.//img/@src').get()
            if image and image.strip():
                meta['image'] = self.format_link(response, image.strip())
                meta['image_blob'] = self.get_image_blob_from_link(meta['image'])
            yield scrapy.Request(url=self.format_link(response, link), callback=self.parse_scene, meta=meta)
