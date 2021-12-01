import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteLANewGirlSpider(BaseSceneScraper):
    name = 'LANewGirl'
    network = 'LA New Girl'
    parent = 'LA New Girl'
    site = 'LA New Girl'

    start_urls = [
        'https://www.lanewgirl.com',
    ]

    selector_map = {
        'title': '',
        'description': '//article/p[1]/text()',
        'date': '',
        'image': '//ul[@class="slides"]/li[1]/a/img/@src',
        'performers': '//span[@class="tour_update_models"]/a/text()',
        'tags': '//div[@class="checklist"]/ul/li/i/following-sibling::text()',
        'external_id': r'.*/(.*?)/',
        'trailer': '',
        'pagination': '/aspiring-models-doing-porn/page/%s/'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//span[@class="gridblock-link-hover"]/a/@href').getall()
        for scene in scenes:
            if "amember_redirect_url" not in scene:
                if re.search(self.get_selector_map('external_id'), scene):
                    yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_title(self, response):
        title = response.url
        title = re.search(r'.*/(.*?)/', title)
        if title:
            title = title.group(1)
            title = title.replace("-", " ").title()
            return title.strip()
        return ''

    #  The date code was used for the initial fill scrape.  It's pretty inaccurate,
    #  so going forward commenting it out so that current date is used.  Leaving
    #  the function in as a comment in case it's needed later though.
    # ~ def get_date(self, response):
    # ~ image = response.xpath('//ul[@class="slides"]/li[1]/a/img/@src')
    # ~ if image:
    # ~ image = image.get()
    # ~ year = re.search(r'uploads/(\d{4})/', image)
    # ~ month = re.search(r'uploads/\d+/(\d{1,2})/', image)
    # ~ if month and year:
    # ~ date = year.group(1) + "-" + month.group(1) + "-01"
    # ~ return self.parse_date(date).isoformat()
    # ~ return self.parse_date('today').isoformat()

    def get_tags(self, response):
        tags = []
        tags2 = super().get_tags(response)
        if tags2:
            for tag in tags2:
                if "/" not in tag:
                    tags.append(tag.title())
                else:
                    temptags = tag.split("/")
                    for temptag in temptags:
                        tags.append(temptag.strip().title())
        return tags

    def get_performers(self, response):
        url = re.search(r'.*/(.*?)/', response.url).group(1)
        if "modeling-audition" in url:
            url = re.search(r'(.*)-modeling-audition', url)
        elif "-audition" in url:
            url = re.search(r'(.*)-audition', url)
        elif "returns" in url:
            url = re.search(r'(.*)-returns', url)
        elif "shoot" in url:
            url = re.search(r'(.*)-shoot', url)
        else:
            url = None

        if url:
            performer = url.group(1)
            performer = re.sub('[^a-zA-Z ]', '', performer.replace("-", " ")).title().strip()
            if " vs " in performer.lower():
                performers = performer.lower().split(" vs ")
                return list(map(lambda x: x.strip().title(), performers))
            return [performer.strip().title()]
        return []

    def get_id(self, response):
        sceneid = super().get_id(response)
        if sceneid == "access":
            return ''
        return sceneid
