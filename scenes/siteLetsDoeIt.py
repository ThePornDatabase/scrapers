import re
import scrapy
import tldextract

from tpdb.BaseSceneScraper import BaseSceneScraper


class LetsDoeItSpider(BaseSceneScraper):
    name = 'LetsDoeIt'
    network = "LetsDoeIt"

    start_urls = [
        'https://www.letsdoeit.com',
        'https://amateureuro.com',
        'https://mamacitaz.com/',
        'https://dirtycosplay.com/',
        'https://transbella.com/',
        'https://vipsexvault.com',
    ]

    selector_map = {
        'title': '//div[contains(@class,"module-video-details")]//h1/text()',
        'description': '//meta[@name="description"]/@content',
        'date': '//meta[@itemprop="uploadDate"]/@content',
        'image': '//meta[@itemprop="thumbnailUrl"]/@content',
        'performers': '//div[@class="actors"]/h2/span/a/strong/text()',
        'tags': "//a[contains(@href,'/tags/') or contains(@href,'/categories/')]/text()",
        'external_id': r'/watch/(.*)/',
        'trailer': '//meta[@itemprop="contentURL"]/@content',
        'pagination': '/videos.en.html?order=-recent&page=%s'
    }

    def get_scenes(self, response):
        responsetext = response.xpath('//*').getall()
        responsetext = "".join(responsetext)
        scenes = re.findall(r'a\ target=\"_self\" class=\"-g-vc-fake\"\ href=\"(.*?.html)\"', responsetext)
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        site = response.xpath('//div[@class="actors"]/h2/a/strong/text()').get().strip()
        return site

    def get_parent(self, response):
        if "amateureuro" in response.url:
            return "Amateur Euro"
        if "letsdoeit" in response.url:
            return "LetsDoeIt"
        if "vipsexvault" in response.url:
            return "VIP Sex Vault"
        if "mamacitaz" in response.url:
            return "MamacitaZ"
        if "transbella" in response.url:
            return "Trans Bella"
        if "dirtycosplay" in response.url:
            return "Dirty Cosplay"

        return tldextract.extract(response.url).domain
