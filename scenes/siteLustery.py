import re
from datetime import datetime
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper

# Call with -a max_id=1000
# This needs to be increased over time


class LusterySpider(BaseSceneScraper):
    name = 'Lustery'
    network = 'Lustery'
    parent = 'Lustery'
    max_id = '2000'

    start_urls = ["https://lustery.com"]

    selector_map = {
        'title': '//div[@class="title"]/h3/text()',
        'description': '//div[@class="video-popup-info"]/div[@class="description"]//text()',
        'tags': '//div[@class="video-popup-info"]//div[@class="tags"]/a//text()',
        'date': '',
        'external_id': 'video-preview/(.+)',
        'pagination': 'videos?start=%s',
    }

    def get_image(self, response):
        image_url = response.xpath('//video-js/@data-poster').get()
        if image_url is None:
            image_url = response.xpath('//div[@class="poster-with-video lazy-image"]/@data-src').get()
        image_url = image_url.replace("_20_blurred", "")
        return image_url

    def get_trailer(self, response):
        video_id = response.url.split("/")[-1]
        return self.format_link(response, "play_preview_video_mp4/" + video_id)

    def get_performers(self, response):
        couple = response.xpath('//div[contains(@class,"couple")]/a//text()').get()
        if couple is None:
            # Some of the early videos don't include the couple features
            # Instead use a heuristic on the description
            #  - Find capitalized words in the format 'Name and Name'
            desc = self.get_description(response)
            couple = re.search(r'[A-Z][a-z]+ (and|&) [A-Z][a-z]+', desc).group()
            return [couple.split()[0], couple.split()[1]]
        return [p.strip() for p in couple.split("&")]

    def get_next_page_url(self, base, page):
        return self.format_url(base, self.get_selector_map('pagination') % ((page - 1) * 12))

    def get_date(self, response):
        '''Date is not shown anywhere without logging in.
            Using the Unix timestamp of the poster image as the date'''
        img_url = self.get_image(response)
        if img_url is None:
            img_url = response.xpath('//div[@class="poster-with-video lazy-image"]/@data-src').get()
        timestamp = int(img_url.split("=")[1])
        return datetime.fromtimestamp(timestamp).isoformat()

    def start_requests(self):
        # Lustery doesn't allow you to see all pages without logging in.
        # Instead we guess at video ids up to maximum
        self.download_delay = 0.25  # Important as they will block you
        for url in self.start_urls:
            for video_id in range(30, int(self.max_id)):
                yield scrapy.Request(
                    cookies={},
                    url=url + "/video-preview/" + str(video_id),
                    callback=self.parse_scene)
