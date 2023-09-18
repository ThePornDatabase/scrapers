import re
import string
import scrapy
from deep_translator import GoogleTranslator
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class JavKOVideoSpider(BaseSceneScraper):
    name = 'KOVideo'
    network = 'KO Video'

    start_urls = [
        'https://ko-video.com',
    ]

    selector_map = {
        'title': '//h2[@class="p-workPage__title"]/text()',
        'description': '//p[@class="p-workPage__text"]/text()',
        'date': '//div[@class="item"]/a[contains(@href, "/works/list/date")]/@href',
        're_date': r'(\d{4}-\d{2}-\d{2})',
        'image': '',
        'back': '//div[@class="swiper-wrapper"]/div[@class="swiper-slide"][1]/img/@data-src',
        'performers': '//div[@class="item"]/a[contains(@href, "actress/detail")]/text()',
        'tags': '//div[@class="item"]/a[contains(@href, "/works/list/genre")]/text()',
        'duration': '',
        'trailer': '',
        'external_id': r'.*/(.*?)$',
        'pagination': '/products/list.php?mode=&type=&label=&maker=&series=&genre=&mgenre=&model=&name=&orderby=&disp_number=20&pageno=%s',
        'type': 'Jav',
    }

    custom_scraper_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.57',
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 10,
        'CONCURRENT_REQUESTS': 1,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'CONCURRENT_REQUESTS_PER_IP': 1,
        'DOWNLOADER_MIDDLEWARES': {},
        'DOWNLOAD_MAXSIZE': 0,
        'DOWNLOAD_TIMEOUT': 100000,
        'DOWNLOAD_WARNSIZE': 0,
        'RETRY_ENABLED': True,
        "LOG_LEVEL": 'INFO',
        "EXTENSIONS": {'scrapy.extensions.logstats.LogStats': None},
        "MEDIA_ALLOW_REDIRECTS": True,
        "HTTPERROR_ALLOWED_CODES": [404],
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class,"swiper-slide")]/div[@class="item"]')
        for scene in scenes:
            image = scene.xpath('.//img/@data-src')
            if image:
                meta['image'] = image.get()
                meta['image_blob'] = self.get_image_blob_from_link(meta['image'])
            scene = scene.xpath('./div/a[1]/@href').get()
            meta['id'] = re.search(r'.*/(.*?)$', scene).group(1)

            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_title(self, response):
        meta = response.meta
        title = super().get_title(response)
        title = GoogleTranslator(source='ja', target='en').translate(title.lower())
        title = string.capwords(title)
        title = title + " - " + meta['id']
        return title

    def get_description(self, response):
        description = super().get_description(response)
        description = GoogleTranslator(source='ja', target='en').translate(description)
        return description

    def get_tags(self, response):
        tags = super().get_tags(response)
        tags2 = []
        for tag in tags:
            tag = GoogleTranslator(source='ja', target='en').translate(tag.lower())
            tags2.append(string.capwords(tag))
        if "Asian" not in tags2:
            tags2.append("Asian")
        if "JAV" not in tags2:
            tags2.append("JAV")

        return tags2

    def get_performers(self, response):
        performers = super().get_performers(response)
        performers2 = []
        for performer in performers:
            performer = GoogleTranslator(source='ja', target='en').translate(performer.lower())
            performers2.append(string.capwords(performer))
        return performers2

    def get_duration(self, response):
        duration = response.xpath('//div[contains(text(), "収録時間")]/following-sibling::div[1]/div[1]/p/span/following-sibling::text()')
        if duration:
            duration = re.search(r'(\d+)', duration.get())
            if duration:
                return str(int(duration.group(1)) * 60)
        return None

    def parse_scene(self, response):
        item = SceneItem()
        item['title'] = self.get_title(response)
        item['description'] = self.get_description(response)
        item['site'] = self.get_site(response)
        item['date'] = self.get_date(response)

        item['image'] = response.meta['image']
        item['image_blob'] = response.meta['image_blob']
        item['back'] = self.get_back_image(response)
        if item['back']:
            item['back_blob'] = self.get_image_blob_from_link(item['back'])
        else:
            item['back_blob'] = ''

        item['performers'] = self.get_performers(response)
        item['tags'] = self.get_tags(response)
        item['id'] = response.meta['id']
        item['trailer'] = self.get_trailer(response)
        item['duration'] = self.get_duration(response)
        item['url'] = self.get_url(response)
        item['network'] = self.network
        item['parent'] = self.parent
        item['type'] = 'JAV'

        yield self.check_item(item, self.days)
