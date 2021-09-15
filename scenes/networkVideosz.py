import re
import html
import string
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkVideoszSpider(BaseSceneScraper):
    name = 'Videosz'
    network = 'Videosz'

    start_urls = [
        # ~ 'https://www.videosz.com',  Scraper is unused.  Data is already pulled from Bang! with different scene names
    ]

    selector_map = {
        'title': '//h1//span[@itemprop="name"]//text()',
        'description': '//div[@id="main_content"]/comment()',
        're_description': r'description\">(.*?)</div',
        'date': '//span[@itemprop="datePublished"]/@content',
        'date_formats': ['%m/%d/%Y'],
        'image': '//ul[@id="preview_thumbs"]/li[2]/div/a/img/@src',
        'performers': '//h2[contains(@class,"font11")]/a[contains(@href,"porn-star")]//text()',
        'tags': '//div[@itemprop="genre"]/h2/a/text()',
        'external_id': r'scene/(\d+)_',
        'site': '//span[@itemprop="productionCompany"]/span/text()',
        'trailer': '',
        'pagination': '/us/scenes/new-releases/%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class,"scene_meta_data")]/div/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        site = self.process_xpath(response, self.get_selector_map('site'))
        if site:
            return string.capwords(site.get().strip())
        return 'Videosz'

    def get_parent(self, response):
        return ''

    def get_title(self, response):
        title = self.process_xpath(response, self.get_selector_map('title'))
        if title:
            title = title.getall()
            title = list(map(lambda x: x.strip(), title))
            title = " ".join(title).replace("  ", " ")
            title = title.lower().replace(" scene", " - scene")
            return string.capwords(html.unescape(title.strip()))
        return None

    def get_image(self, response):
        image = super().get_image(response)
        image = re.sub(r'/thumbs\d{1,3}/', '/', image)
        return image
