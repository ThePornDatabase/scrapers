import scrapy
import re
import dateparser
from urllib.parse import urlparse
import html
from tpdb.BaseSceneScraper import BaseSceneScraper


class siteFit18Spider(BaseSceneScraper):
    name = 'Fit18'
    network = 'Fit18'
    parent = 'Fit18'

    start_urls = [
        'https://www.fit18.com',
    ]

    selector_map = {
        'title': '//div[@class="row scene"]/div/h1/text()',
        'description': '//div[@class="row scene"]/div/p/text()',
        'date': '',
        'image': '//div[@class="video-box"]/div/a/img[contains(@src,".jpg")]/@src',
        'performers': '//div[@class="row scene"]/div/h2/span/following-sibling::a/text()',
        'tags': '',
        'external_id': '.*models\/(.*)',
        'trailer': '',
        'pagination': ''
    }
    

    def start_requests(self):
        if self.input:
            input = self.input
            fileurl = "file:///" + input
            print(fileurl)
            yield scrapy.Request(fileurl,
                         callback=self.get_scenes,
                         headers=self.headers,
                         cookies=self.cookies)    

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class,"model-videos")]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        return "Fit18"

    def get_parent(self, response):
        return "Fit18"


    def get_id(self, response):
        search = self.regex['external_id'].search(response.url).group(1)
        if search:
            search = search.replace("/","-")
            return search
        return None

    def get_date(self, response):
        return dateparser.parse('today').isoformat()


    def get_description(self, response):
        description = self.process_xpath(response, self.get_selector_map('description')).get()
        if description:
            description = description.replace('In 60FPS.', '')

            return html.unescape(description.strip())

        return ''


    def format_url(self, base, path):
        base = 'https://www.fit18.com'
        if path.startswith('http'):
            return path

        if path.startswith('//'):
            return 'https:' + path

        new_url = urlparse(path)
        url = urlparse(base)
        url = url._replace(path=new_url.path, query=new_url.query)

        return url.geturl()
