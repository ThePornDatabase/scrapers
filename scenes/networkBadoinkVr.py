from datetime import datetime
import dateparser
import scrapy
import re
from tpdb.helpers.http import Http
from tpdb.items import SceneItem
from tpdb.BaseSceneScraper import BaseSceneScraper
true = True
false = False

class BadoinkVrSpider(BaseSceneScraper):
    name = 'BadoinkVr'
    network = 'Badoink VR'
    parent = 'Badoink VR'
    max_pages = 100
    start_urls = [
        'https://badoinkvr.com',
        'https://babevr.com',
        'https://18vr.com',
        'http://kinkvr.com',
        'https://vrcosplayx.com',
        'https://realvr.com',
    ]

    cookies = [{"domain":"kinkvr.com","hostOnly":true,"httpOnly":false,"name":"agreedToDisclaimer","path":"/","sameSite":"unspecified","secure":false,"session":false,"storeId":"0","value":"true"}]

    selector_map = {
        'title': '//h1[@itemprop="name"]/@content | //h1[contains(@class, "video-title")]/text()|//h1[contains(@class, "page-title")]/text()',
        'description': '//p[@itemprop="description"]/@content | //p[@class="video-description"]/text()|//div[contains(@class, "accordion-body")]',
        'date': '//p[@itemprop="uploadDate"]/@content | //p[@class="video-upload-date"]/text()',
        'image': '//meta[@itemprop="thumbnailUrl"]/@content|//img[@class="video-image"]/@src|//video/@poster|//dl8-video/@poster',
        'performers': '//a[contains(@class, "video-actor-link")]/text()|//td[contains(text(), "Starring:")]/following-sibling::td/a[contains(@href, "girl")]/text()',
        'tags': '//p[@class="video-tags"]//a/text()|//td[contains(text(), "Categories:")]/following-sibling::td/a[contains(@href, "category")]/text()',
        'external_id': '-(\\d+)\\/?$',
        'trailer': '//meta[@property="og:video"]/@content'
    }

    def get_scenes(self, response):
        if "kinkvr" in response.url:
            scenes = response.xpath("//div[@class='video-grid-view']//a[1]/@href").getall()
        else:
            scenes = response.xpath("//div[@class='tile-grid-item']//a[contains(@class, 'video-card-title')]/@href").getall()
        for scene in scenes:
            scene = self.format_link(response, scene)
            yield scrapy.Request(scene, callback=self.parse_scene)

    def get_next_page_url(self, base, page):
        selector = '/vrpornvideos/%s?order=newest'

        if 'vrbtrans' in base:
            selector = '/videos/?category=all&sort=latest&page=%s'
        elif 'vrcosplay' in base:
            selector = '/cosplaypornvideos/%s?order=newest'
        elif 'kinkvr' in base:
            selector = '/videos/page%s/?sortby=NEWEST'

        return self.format_url(base, selector % page)

    def get_date(self, response):
        if "kinkvr" in response.url:
            date = response.xpath('//td[contains(text(), "Released:")]/following-sibling::td/text()')
            if date:
                date = self.parse_date(date.get().strip(), date_formats=['%B %d, %Y']).strftime('%Y-%m-%d')
                return date
        else:
            date = self.process_xpath(response, self.get_selector_map('date'))
            if date:
                return dateparser.parse(date.get().strip()).strftime('%Y-%m-%d')
        return ""

    def parse_scene(self, response):
        item = self.init_scene()
        item['title'] = self.get_title(response)
        item['description'] = self.get_description(response)
        item['site'] = self.get_site(response)
        item['date'] = self.get_date(response)
        image = self.get_image(response)
        if "-small" in image:
            image = image.replace("-small", "-medium")
        if image:
            item['image'] = image
            item['image_blob'] = self.get_image_blob_from_link(image)
            if "?" in item['image'] and ("token" in item['image'].lower() or "expire" in item['image'].lower()):
                item['image'] = re.search(r'(.*?)\?', item['image']).group(1)

        item['performers'] = self.get_performers(response)
        item['tags'] = self.get_tags(response)
        item['id'] = self.get_id(response)
        item['trailer'] = self.get_trailer(response)
        item['duration'] = self.get_duration(response)
        item['url'] = self.get_url(response)
        item['network'] = self.network
        item['parent'] = item['site']

        item['type'] = 'Scene'
        yield self.check_item(item, self.days)

    def get_image_from_link(self, image):
        if image:
            req = Http.get(image)
            if req and req.is_success:
                return req.content
        return None
