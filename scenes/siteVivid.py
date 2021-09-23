import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper

# This is historical scraping from before they joined AdultTime
# Included sites:
# "65InchHugeAsses",
# "BlackWhiteFuckFest",
# "BrandNewFaces",
# "GirlsWhoFuckGirls",
# "MomIsAMilf",
# "NastyStepFamily",
# "Nineteen",
# "OrgyTrain",
# "Petited",
# "VividCeleb",
# "VividClassic",
# "Vivid",


class SiteVividSpider(BaseSceneScraper):
    name = 'Vivid'
    network = 'Vivid'

    start_urls = [
        'https://www.vivid.com',
    ]

    selector_map = {
        'title': '',
        'description': '//p[contains(@class,"indie-model")]/text()',
        'date': '',
        'image': '',
        'performers': '//h4[contains(text(), "Starring")]/a/text()',
        'tags': '//h5[contains(text(), "Categories")]/a/text()',
        'external_id': r'updates\/(.*).html',
        'trailer': '',
        'pagination': '/videos/api/?limit=24&offset=%s&sort=datedesc&flagType=video'
    }

    def get_scenes(self, response):
        jsondata = response.json()
        jsondata = jsondata['responseData']
        for scene in jsondata:
            meta = {}
            meta['id'] = scene['id']
            meta['title'] = scene['name']
            meta['site'] = scene['site']['name']
            meta['parent'] = "Vivid"
            meta['network'] = "Vivid"
            meta['date'] = scene['release_date']
            meta['image'] = scene['placard_800']
            if not meta['image']:
                meta['image'] = scene['placard']
            if "cast" in scene:
                meta['performers'] = []
                for model in scene['cast']:
                    meta['performers'].append(model['stagename'])
            sceneurl = self.format_link(response, scene['url'])
            if sceneurl and meta['id']:
                yield scrapy.Request(sceneurl, callback=self.parse_scene, meta=meta)

    def get_site(self, response):
        return "Vivid"

    def get_parent(self, response):
        return "Vivid"

    def get_next_page_url(self, base, page):
        page = str((int(page) - 1) * 24)
        url = self.format_url(base, self.get_selector_map('pagination') % page)
        return url
