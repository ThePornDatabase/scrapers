import re
import html
import warnings
import dateparser
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper

# Ignore dateparser warnings regarding pytz
warnings.filterwarnings(
    "ignore",
    message="The localize method is no longer necessary, as this time zone supports the fold attribute",
)


class SiteBoundHoneysSpider(BaseSceneScraper):
    name = 'BoundHoneys'
    network = 'Bound Honeys'

    start_urls = [
        'http://boundhoneys.com',
    ]

    selector_map = {
        'title': '//div[@class="updateVideoTitle"]/text()',
        'description': '//div[@class="updateDescription"]//text()',
        'date': '',
        'image': '//meta[@name="twitter:image"]/@content',
        'performers': '//div[@class="updateModelsList"]/a/text()',
        'tags': '//div[contains(@class, "updateCategoriesList")]/a/text()',
        'external_id': r'updates\/(.*).html',
        'trailer': '',
        'pagination': '/bondage-videos.php?perpage=24&id=999&p=%s#videos'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="update"]')
        for scene in scenes:
            date = scene.xpath('./div[@class="updateDate"]/text()')
            if date:
                date = date.get()
                date = dateparser.parse(date).isoformat()
            else:
                date = dateparser.parse('today').isoformat()
            scene = scene.xpath('./a/@href').get()
            if scene:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta={'date': date})

    def get_description(self, response):
        description = response.xpath(self.get_selector_map('description'))
        if description:
            description = description.getall()
            description = " ".join(description).replace("\n", "").replace("\r", "")
            description = description.replace("\t", "").replace("  ", " ").replace("&nbsp;", "")
            description = re.sub(r'^Action ', ' ', description.strip())
            return html.unescape(description.strip())
        return ''

    def get_id(self, response):
        externid = response.xpath('//script[contains(text(), "updateIDForPlayer")]/text()')
        if externid:
            externid = externid.get()
            externid = re.search(r'updateIDForPlayer.*?(\d{1,4})', externid)
            if externid:
                return externid.group(1).strip()
        externid = response.xpath('//script[contains(text(), "gtag")]/text()')
        if externid:
            externid = externid.get()
            externid = re.search(r'name.*?(\d{1,4})', externid)
            if externid:
                return externid.group(1).strip()

        return None

    def get_site(self, response):
        return "Bound Honeys"

    def get_parent(self, response):
        return "Bound Honeys"
