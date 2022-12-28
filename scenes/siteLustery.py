import re
import string
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
        'title': '//h1[contains(@class,"VideoTitle_title__")]/text()',
        'description': '//div[contains(@class,"VideoInfo_description__")]/text()',
        'tags': '//script[contains(text(), "permalink")]/text()',
        'date': '',
        'external_id': 'video-preview/(.+)',
        'pagination': 'videos?start=%s',
    }

    def get_image(self, response):
        image_url = response.xpath('//meta[@property="og:image"]/@content').get()
        if image_url is None:
            image_url = response.xpath('//video-js/@data-poster').get()
        if image_url is None:
            image_url = response.xpath('//div[@class="poster-with-video lazy-image"]/@data-src').get()
        image_url = image_url.replace(" ", "%20")
        image_url = image_url.replace("_20_blurred", "")
        return image_url

    def get_trailer(self, response):
        video_id = response.url.split("/")[-1]
        return self.format_link(response, "play_preview_video_mp4/" + video_id)

    def get_performers(self, response):
        couple = response.xpath('//a[contains(@class,"VideoCoupleCard_name")]/text()').get()
        if couple is None:
            couple = response.xpath('//div[contains(@class,"couple")]/a//text()').get()
        
        if couple is None:
            # Some of the early videos don't include the couple features
            # Instead use a heuristic on the description
            #  - Find capitalized words in the format 'Name and Name'
            desc = self.get_description(response)
            couple = re.search(r'[A-Z][a-z]+ (and|&) [A-Z][a-z]+', desc)
            if couple:
                couple = couple.group()
                return [couple.split()[0], couple.split()[1]]
            else:
                return []
        return [p.strip() for p in couple.split("&")]

    def get_next_page_url(self, base, page):
        return self.format_url(base, self.get_selector_map('pagination') % ((page - 1) * 12))

    # ~ def get_date(self, response):
        # ~ '''Date is not shown anywhere without logging in.
            # ~ Using the Unix timestamp of the poster image as the date'''
        # ~ img_url = self.get_image(response)
        # ~ if img_url is None:
            # ~ img_url = response.xpath('//div[@class="poster-with-video lazy-image"]/@data-src').get()
        # ~ timestamp = int(img_url.split("=")[1])
        # ~ return datetime.fromtimestamp(timestamp).isoformat()

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
                    
    def get_tags(self, response):
        slug = re.search(r'.*/(.*?)$', response.url).group(1)
        tags = response.xpath('//script[contains(text(), "permalink")]/text()').get()
        tagquery = f"\"video\".*?{slug}.*?\"tags\".*?\[(.*?)\]"
        tags = re.search(tagquery, tags).group(1)
        tags = tags.replace("\"", "")
        tags = tags.split(",")
        return list(map(lambda x: string.capwords(x.strip()), tags))
                    
    def get_duration(self, response):
        slug = re.search(r'.*/(.*?)$', response.url).group(1)
        duration = response.xpath('//script[contains(text(), "permalink")]/text()').get()
        durquery = f"\"video\".*?{slug}.*?\"duration\":\s?(\d+)"
        duration = re.search(durquery, duration).group(1)
        duration = str(duration)
        return duration
                    
    # ~ def get_date(self, response):
        # ~ slug = re.search(r'.*/(.*?)$', response.url).group(1)
        # ~ scenedate = response.xpath('//script[contains(text(), "permalink")]/text()').get()
        # ~ datequery = f"\"video\".*?{slug}.*?\"lastEditedAt\":\s?(\d+)"
        # ~ scenedate = re.search(datequery, scenedate).group(1)
        # ~ print(f"Scenedate: {scenedate}")
        # ~ scenedate = datetime.fromtimestamp(int(scenedate)).isoformat()
        # ~ print(f"Scenedate: {scenedate}")
        # ~ return scenedate
