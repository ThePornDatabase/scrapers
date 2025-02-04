import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkCzechVRSpider(BaseSceneScraper):
    name = 'CzechVR'
    network = 'Mental Pass'

    cookies = {'name': 'iagree', 'value': 'ano'}

    start_urls = [
        # ~ 'https://www.czechvr.com',
        'https://www.czechvrcasting.com',
        'https://www.czechvrfetish.com',
        'https://www.vrintimacy.com',
        'https://www.czechar.com',
    ]

    selector_map = {
        'title': '//div[contains(@class,"nazev")]/h1/span/following-sibling::text()|//div[contains(@class,"nazev")]/h2/span/following-sibling::text()',
        'description': '//div[@class="textDetail"]/text()|//div[@class="cistic"]/following-sibling::div[@class="text"]/text()',
        'date': '//article[@class="detail"]//div[contains(@class,"nazev")]/div[@class="datum"]/text()|//div[@class="datum"]/text()',
        'date_formats': ['%b %d %Y', '%b %d, %Y'],
        'image': '//article[@class="detail"]//div[@class="foto"]/dl8-video/@poster|//dl8-video/@poster',
        'performers': '//article[@class="detail"]//div[contains(@class,"nazev")]/div[@class="featuring"]/a[contains(@href, "model")]/text()|//div[@class="modelky"]/a//span/text()',
        'tags': '//div[@id="MoreTags"]//a/text()|//div[@id="VideoTagy"]//a/text()',
        'duration': '//div[@class="casDetail"]/span[1]/text()|//div[@class="datum"]/following-sibling::div[@class="cas"][1]/text()',
        'trailer': '//article[@class="detail"]//div[@class="foto"]/dl8-video/source/@src|//dl8-video/source/@src',
        'external_id': r'detail-(\d+)-',
        'pagination': '/vr-porn-videos?&next=%s',
        'type': 'Scene',
    }

    def get_next_page_url(self, base, page):
        if "fetish" in base or "casting" in base:
            pagination = "/vr-porn-videos"
        if "intimacy" in base:
            pagination = "intimate-vr-porn-videos"
        elif "czechar" in base:
            pagination = "/passthrough-ar-porn-videos"
        else:
            pagination = "/vr-porn-videos"

        if page == 1:
            return self.format_url(base, pagination)
        else:
            page = str(((int(page) - 1) * 15) + 1)
        return self.format_url(base, f"{pagination}?&next={page}")

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="nazev"]/h2/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                if scene[0] == '.':
                    scene = scene[1:]
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_tags(self, response):
        tags = super().get_tags(response)
        if "Vr" not in tags and "VR" not in tags and "Virtual Reality" not in tags:
            tags.append("Virtual Reality")
        return tags

    def get_trailer(self, response):
        trailer = self.get_element(response, 'trailer', 're_trailer')
        if len(trailer) > 1:
            trailer.sort(reverse=True)
            trailer = trailer[0]
        return trailer

    def get_image(self, response):
        image = super().get_image(response)
        if "/./" in image:
            image = image.replace("/./", "/")
        return image

    def get_title(self, response):
        title = response.xpath('//div[contains(@class,"nazev")]/h1/span/following-sibling::text()|//div[contains(@class,"nazev")]/h2/span/following-sibling::text()')
        if len(title) > 1:
            title = " ".join(title.getall())
            title = title.replace("  ", " ")
        else:
            title = title.get()
        return self.cleanup_title(title)
