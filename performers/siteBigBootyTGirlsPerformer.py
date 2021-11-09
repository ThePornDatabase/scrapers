import html
from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteBigBootyTGirlsPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h1/text()',
        'image': '//span[contains(@class,"fusion-imageframe")]/img/@src',
        'haircolor': '//strong[contains(text(),"Hair")]/following-sibling::text()',
        'ethnicity': '//strong[contains(text(),"Ethnicity")]/following-sibling::text()',
        'fakeboobs': '//strong[contains(text(),"Tits Type")]/following-sibling::text()',
        'pagination': '/models/models_%s.html',
        'external_id': r'models\/(.*).html'
    }

    name = 'BigBootyTGirlsPerformer'

    start_urls = [
        'https://www.bigbootytgirls.com',
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[@class="modelPic"]')
        for performer in performers:
            item = PerformerItem()

            name = performer.xpath('./div[@class="modelName"]/p/a/text()').get()
            if name:
                item['name'] = html.unescape(name.strip().title())

            image = performer.xpath('.//img/@src0_3x|.//img/@src0_2x|.//img/@src0_1x').get()
            if image:
                item['image'] = "https://www.bigbootytgirls.com/" + image.strip()
            else:
                item['image'] = None
            item['image_blob'] = None

            url = performer.xpath('./a/@href').get()
            if url:
                item['url'] = url.strip()

            item['network'] = 'Big Booty Tgirls'

            item['astrology'] = ''
            item['bio'] = ''
            item['birthday'] = ''
            item['birthplace'] = ''
            item['cupsize'] = ''
            item['ethnicity'] = ''
            item['eyecolor'] = ''
            item['fakeboobs'] = ''
            item['gender'] = 'Trans'
            item['haircolor'] = ''
            item['height'] = ''
            item['measurements'] = ''
            item['nationality'] = ''
            item['piercings'] = ''
            item['tattoos'] = ''
            item['weight'] = ''

            yield item
