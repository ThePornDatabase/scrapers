import re
import unidecode
import html
import string
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class PerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h2[@class="title"]/a[1]/following-sibling::text()',
        'image': '//div[@class="cell_top model_picture"]/img/@src0_3x|//div[@class="cell_top model_picture"]/img/@src0_2x',
        'image_blob': True,
        'bio': '//comment()[contains(., "Bio Extra Field") and not(contains(., "Accompanying"))]/following-sibling::text()',
        'astrology': '//text()[contains(., "Astrological Sign")]',
        'height': '//span[@class="model_bio_heading"]/following-sibling::text()[contains(., "Height")]',
        'nationality': '//span[@class="model_bio_heading"]/following-sibling::text()[contains(., "Country")]',

        'pagination': '/models/models_%s_d.html',
        'external_id': r'model/(.*)/'
    }

    name = 'HiginioDomingoPerformer'
    network = 'Higinio Domingo'

    start_urls = [
        'https://charmmodels.net',
        'https://domingoview.com',
        'https://letstryhard.com',
        'https://test-shoots.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="modelPic"]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, cookies=self.cookies, headers=self.headers)

    def get_name(self, response):
        perf_name = super().get_name(response)
        perf_name = perf_name.replace("/", "").strip()
        return perf_name

    def get_astrology(self, response):
        astrology = super().get_astrology(response)
        astrology = unidecode.unidecode(html.unescape(astrology.lower().replace("&nbsp;", " ").replace("\xa0", " ")))
        astrology = re.search(r'.*:(.*)', astrology)
        if astrology:
            return string.capwords(astrology.group(1).strip())
        return None

    def get_nationality(self, response):
        nationality = super().get_nationality(response)
        nationality = unidecode.unidecode(html.unescape(nationality.lower().replace("&nbsp;", " ").replace("\xa0", " ")))
        nationality = re.search(r'.*:(.*)', nationality)
        if nationality:
            return string.capwords(nationality.group(1).strip())
        return None

    def get_height(self, response):
        height = super().get_height(response)
        height = unidecode.unidecode(html.unescape(height.lower().replace("&nbsp;", " ").replace("\xa0", " ")))
        height = re.search(r'(\d+)', height)
        if height:
            return height.group(1) + "cm"
        return None
