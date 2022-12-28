import re
import tldextract
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


def match_site(argument):
    match = {
        'ambushmassage': "Ambush Massage",
        'cfnmeu': "CFNMEU",
        'malefeet4u': "Male Feet 4U",
        'str8hell': "STR8HELL",
        'swnude': "SWNude: Submission Wrestling Nude",
        'williamhiggins': "William Higgins",
    }
    return match.get(argument, argument)


class NetworkWilliamHigginsSpider(BaseSceneScraper):
    name = 'WilliamHiggins'
    network = 'William Higgins'

    start_urls = [
        'https://www.ambushmassage.com',
        'https://www.cfnmeu.com',
        'https://www.malefeet4u.com',
        'https://www.str8hell.com',
        'https://www.swnude.com',
        'https://www.williamhiggins.com',
    ]

    cookies = {'adult': '1'}

    selector_map = {
        'title': '//p[@class="video-detailinfo"]/span/text()',
        'description': '//div[contains(@class,"set_text")]//text()',
        'date': '//span[contains(@class,"date_field")]/text()',
        'date_formats': ['%d/%m/%Y'],
        'image': '//script[contains(text(), "NUXT")]/text()',
        'performers': '',
        'tags': '',
        'duration': '//script[contains(text(), "NUXT")]/text()',
        're_duration': r'videoduration:\s?[\'\"](\d+?\:?\d+\:\d+)',
        'trailer': '',
        'external_id': r'.*/(\d+)',
        'pagination': '/scenes/latest/%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "set-overview")]')
        for scene in scenes:
            image = scene.xpath('./a/div/img[1]/@src')
            if image:
                meta['image'] = self.format_link(response, image.get())
                meta['image_blob'] = self.get_image_blob_from_link(meta['image'])
            else:
                meta['image'] = None
                meta['image_blob'] = None
            scene = scene.xpath('./a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta, cookies=self.cookies, headers=self.headers)

    def parse_scene(self, response):
        item = SceneItem()
        meta = response.meta

        item['title'] = self.get_title(response)
        item['description'] = self.get_description(response)
        item['site'] = match_site(tldextract.extract(response.url).domain)
        item['date'] = self.get_date(response)
        item['image'] = response.meta['image']
        item['image_blob'] = response.meta['image_blob']
        item['tags'] = []
        item['id'] = self.get_id(response)
        item['trailer'] = ""
        item['duration'] = self.get_duration(response)
        item['url'] = self.get_url(response)
        item['network'] = "William Higgins Productions"
        item['parent'] = "William Higgins Productions"
        item['type'] = 'Scene'
        setid = re.search(r'setdata:{id:(\d+)', response.text)
        if setid:
            meta['item'] = item
            modellink = f"/api/set/set-model-info?id={setid.group(1)}"
            yield scrapy.Request(url=self.format_link(response, modellink), callback=self.get_models, meta=meta, cookies=self.cookies, headers=self.headers)
        else:
            yield self.check_item(item, self.days)

    def get_models(self, response):
        item = response.meta['item']
        # ~ print(item)
        item['performers'] = response.xpath('//td/span[contains(text(), "Model Name")]/following-sibling::a/text()').getall()
        yield self.check_item(item, self.days)
