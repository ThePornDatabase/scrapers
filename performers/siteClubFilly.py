import html
import string
from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteClubFillyPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/pornstars.php?page=%s',
        'external_id': 'girls/(.+)/?$'
    }

    name = 'ClubFillyPerformer'

    start_urls = [
        'http://www.clubfilly.com',
    ]

    def get_performers(self, response):
        performers = response.xpath('//ul[@id="lstPornstars"]/li')
        for performer in performers:
            item = PerformerItem()

            name = performer.xpath('./p[1]/a/text()').get()
            if name:
                item['name'] = string.capwords(html.unescape(name.strip()))

            image = performer.xpath('./div/a/img/@src').get()
            if image:
                item['image'] = self.format_link(response, image).replace(" ", "%20")
            else:
                item['image'] = None
            item['image_blob'] = None

            url = performer.xpath('./p[1]/a/@href').get()
            if url:
                item['url'] = self.format_link(response, url.strip()).replace(" ", "%20")

            item['network'] = 'Club Filly'

            item['astrology'] = ''
            item['bio'] = ''
            item['birthday'] = ''
            item['birthplace'] = ''
            item['cupsize'] = ''
            item['ethnicity'] = ''
            item['eyecolor'] = ''
            item['fakeboobs'] = ''
            item['gender'] = 'Female'
            item['haircolor'] = ''
            item['height'] = ''
            item['measurements'] = ''
            item['nationality'] = ''
            item['piercings'] = ''
            item['tattoos'] = ''
            item['weight'] = ''

            yield item
