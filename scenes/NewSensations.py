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
    ]

    selector_map = {
        'title': '//div[@class="indScene"]/h2/text()',
        'description': '//div[@class="description"]/p/text()',
        'date': "//div[contains(@class, 'stat')]//span[contains(text(),'Date:')]/following-sibling::span/text()",
        'image': '//span[@id="trailer_thumb"]//img/@src',
        'performers': '//div[@class="sceneTextLink"]//span[@class="tour_update_models"]/a/text()',
        'tags': "",
        'external_id': 'tour_ns\\/updates\\/(.+)\\.html',
        'trailer': '',
        'pagination': '/tour_ns/categories/movies_%s_d.html'
    }

    def get_scenes(self, response):
        scenes = response.css(
            ".updatesBlock .videoBlock h4 a::attr(href)").getall()
        for scene in scenes:
            yield scrapy.Request(url=scene, callback=self.parse_scene)

    def get_date(self, response):
        date = response.xpath(
            '//div[@class="sceneDateP"]/span/text()').get().strip(',').strip()
        return dateparser.parse(date).isoformat()
