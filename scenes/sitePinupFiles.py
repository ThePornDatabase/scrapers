import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SitePinupFilesSpider(BaseSceneScraper):
    name = 'PinupFiles'
    network = 'Pinup Files'
    parent = 'Pinup Files'
    site = 'Pinup Files'

    start_urls = [
        'https://www.pinupfiles.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//div[@class="update-info-block"]/h3/following-sibling::text()',
        'date': '//strong[contains(text(),"Added")]/following-sibling::text()',
        'image': '//script[contains(text(),"video_content")]/text()',
        're_image': r'(http.*\.jpg)',
        'performers': '//div[contains(@class,"models-list-thumbs")]/ul/li/a/span/text()',
        'tags': '//h3[contains(text(),"Tags")]/following-sibling::ul/li/a/text()',
        'external_id': r'.*/(.*?).html',
        'trailer': '//script[contains(text(),"video_content")]/text()',
        're_trailer': r'(/trailers.*?\.mp4)',
        'pagination': '/categories/movies/%s/latest/'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="item-title"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_description(self, response):
        description = self.process_xpath(response, self.get_selector_map('description')).getall()
        if description:
            description = " ".join(description)
            description = description.replace("\r", "").replace("\n", "").replace("&nbsp;", "").strip()
            description = re.sub(r'\s{3,100}', ' ', description)
            return self.cleanup_description(description)

        return ''

    def get_image(self, response):
        image = self.process_xpath(response, self.get_selector_map('image'))
        if image:
            image = self.get_from_regex(image.get(), 're_image')
            if image:
                image = self.format_link(response, image)
                return image.replace(" ", "%20")
        else:
            image = response.xpath('//meta[@property="og:image"]/@content').get()
            if image:
                return image.strip().replace(" ", "%20").replace("https://www.pinupfiles.com/https://", "https://")

        return None
