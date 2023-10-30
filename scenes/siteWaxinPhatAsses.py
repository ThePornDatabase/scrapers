import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


def match_site(argument):
    match = {
        '40ddd': '40DDD',
        'doggystylebjs': 'Doggystyle BJs',
        'farrahfeet': 'Farrah Feet',
        'gearsofwhores': 'Gears of Whores',
        'jervonilee': 'Jervoni Lee',
        'phuckfumasters': 'Phuck-Fu Masters',
        'sex-xxxtv': 'Sex-XXXTv',
        'waxinphatasses': 'Waxin Phat Asses',
        'womenwithnuttinbuttass': 'Women With Nuttin Butt Ass',
    }
    return match.get(argument, argument)


class SiteWaxinPhatAssesSpider(BaseSceneScraper):
    name = 'WaxinPhatAsses'
    network = 'SLP Adult Media'

    start_urls = [
        'http://40ddd.com',
        'http://doggystylebjs.com',
        'http://farrahfeet.com',
        'http://gearsofwhores.com',
        'http://jervonilee.com',
        'http://phuckfumasters.com',
        'http://sex-xxxtv.com',
        'http://waxinphatasses.com',
        'http://womenwithnuttinbuttass.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//div[@class="col-md-12"]/p/text()',
        'date': '//i[contains(@class,"fa-calendar")]/following-sibling::text()[1]',
        'date_formats': ['%m/%d/%y'],
        'image': '//video/@poster',
        'performers': '',
        'tags': '',
        'duration': '',
        'trailer': '',
        'external_id': r'.*/(.*?)\.\w{3,4}$',
        'pagination': '/videos/?p=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "video-box")]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_title(self, response):
        title = super().get_title(response)
        if re.search(r'(.*)\.\w{3,4}$', title):
            title = re.search(r'(.*)\.\w{3,4}$', title).group(1)
        title = title.replace("-fscene", "")
        title = title.replace("_", " ")
        if re.search(r'^(\w{3,4}-\d+)-(.*)', title):
            title = re.search(r'^(\w{3,4}-\d+)-(.*)', title).group(1) + " " + re.search(r'^(\w{3,4}-\d+)-(.*)', title).group(2)

        title = string.capwords(title)
        return title

    def get_site(self, response):
        site = super().get_site(response)
        return match_site(site)

    def get_parent(self, response):
        parent = super().get_site(response)
        return match_site(parent)
