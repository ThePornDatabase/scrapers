import re
from datetime import date, timedelta
import string
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class NetworkSirenXXXStudiosSpider(BaseSceneScraper):
    name = 'SirenXXXStudios'
    network = 'Siren XXX Studios'
    parent = 'Siren XXX Studios'

    start_urls = [
        'https://myfirsttimesluts.com/',
        'https://realnaughtynymphos.com/',
    ]

    selector_map = {
        'title': '//h2/text()',
        'description': '//span[contains(text(),"Description")]/following-sibling::text()',
        'date': '//meta[@property="og:image"]/@content',
        're_date': r'content/(\d{8})',
        'date_formats': ['%Y%m%d', '%m/%d/%Y'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//li[contains(text(),"Starring")]/a/text()',
        'tags': '//li[contains(text(),"Tags")]/a/text()',
        'external_id': r'.*/(.*).html',
        'trailer': '//script[contains(text(),"preview")]',
        're_trailer': 'src=\"(.*.mp4)',
        'pagination': '/tour/categories/movies_%s_d.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath(
            '//div[@class="videoBlock"]')
        for scene in scenes:
            scenedate = scene.xpath('.//comment()[contains(.,"Release")]').get()
            if scenedate:
                scenedate = re.search(r'(\d{2}/\d{2}/\d{4})', scenedate).group(1)
                scenedate = self.parse_date(scenedate, date_formats=['%m/%d/%Y']).isoformat()
            scenelink = scene.xpath('./div/a/@href').get()
            if re.search(self.get_selector_map('external_id'), scenelink) and "signup.php" not in scenelink:
                yield scrapy.Request(url=self.format_link(response, scenelink), callback=self.parse_scene, meta={'date': scenedate})
            else:
                item = SceneItem()
                item['date'] = scenedate
                title = scene.xpath('.//span/text()').get()
                if title:
                    item['title'] = string.capwords(title.strip())
                else:
                    item['title'] = ''

                extern_id = item['title'].replace(" ", "-").replace("_", "-").strip().lower()
                extern_id = re.sub('[^a-zA-Z0-9-]', '', extern_id)
                if extern_id:
                    item['id'] = extern_id.strip()

                image = scene.xpath('.//img/@src0_4x').get()
                if not image:
                    image = scene.xpath('.//img/@src0_3x').get()
                if not image:
                    image = scene.xpath('.//img/@src0_2x').get()
                if not image:
                    image = scene.xpath('.//img/@src0_1x').get()

                if image:
                    item['image'] = image.strip()
                else:
                    item['image'] = None
                item['image_blob'] = None

                performers = scene.xpath('./p/a/text()').getall()
                if performers:
                    item['performers'] = list(map(lambda x: x.strip(), performers))
                else:
                    item['performers'] = []

                item['tags'] = []
                item['trailer'] = ''
                item['url'] = scenelink

                item['network'] = "Siren XXX Studios"
                item['parent'] = "Siren XXX Studios"
                item['site'] = self.get_site(response)
                item['description'] = ''

                days = int(self.days)
                if days > 27375:
                    filterdate = "0000-00-00"
                else:
                    filterdate = date.today() - timedelta(days)
                    filterdate = filterdate.strftime('%Y-%m-%d')

                if self.debug:
                    if not item['date'] > filterdate:
                        item['filtered'] = "Scene filtered due to date restraint"
                    print(item)
                else:
                    if filterdate:
                        if item['date'] > filterdate:
                            yield item
                    else:
                        yield item

    def get_site(self, response):
        if "realnaughtynymphos" in response.url:
            return "Real Naughty Nymphos"
        if "myfirsttimesluts" in response.url:
            return "My First Time Sluts"
        return ''

    def get_id(self, response):
        externid = super().get_id(response)
        return externid.lower()

    def get_trailer(self, response):
        if 'trailer' in self.get_selector_map() and self.get_selector_map('trailer'):
            trailer = self.process_xpath(response, self.get_selector_map('trailer')).get()
            if trailer:
                trailer = re.search('src=\"(.*.mp4)', trailer)
                if trailer:
                    trailer = trailer.group(1)
                    trailer = trailer.replace(" ", "%20")
                    if trailer[0] == "/":
                        if "realnaughtynymphos" in response.url:
                            return "https://realnaughtynymphos.com" + trailer.strip()
                        if "myfirsttimesluts" in response.url:
                            return "https://myfirsttimesluts.com" + trailer.strip()
                    else:
                        return trailer.strip()
        return ''
