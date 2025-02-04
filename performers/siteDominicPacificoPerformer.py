import re
from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteDominicPacificoPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/models.html?start=%s&count=24',
        'external_id': r'model/(.*)/'
    }

    name = 'DominicPacificoPerformer'
    network = 'Dominic Pacifico'

    start_urls = [
        'https://dominicpacifico.com',
    ]

    def get_next_page_url(self, base, page):
        page = str((int(page) - 1) * 24)
        return self.format_url(base, self.get_selector_map('pagination') % page)

    def get_performers(self, response):
        performers = response.xpath('//div[contains(@class, "img-wrapper")]')
        for performer in performers:
            item = PerformerItem()

            item['name'] = self.cleanup_title(performer.xpath('//h3/a/text()').get())
            image = performer.xpath('.//img/@src')
            if image:
                item['image'] = self.format_link(response, image.get())
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
            else:
                item['image'] = ""
                item['image_blob'] = ""
            item['bio'] = ''
            item['gender'] = 'Male'
            item['astrology'] = ''
            item['birthday'] = ''
            item['birthplace'] = ''
            item['cupsize'] = ''
            item['ethnicity'] = ''
            item['eyecolor'] = ''
            item['fakeboobs'] = ''
            item['haircolor'] = ''
            item['height'] = ''
            item['measurements'] = ''
            item['nationality'] = ''
            item['piercings'] = ''
            item['tattoos'] = ''
            item['weight'] = ''
            item['network'] = 'Dominic Pacifico'
            url = performer.xpath('./a/@href').get()
            if "?nats" in url:
                url = re.search(r'(.*?)\?nat', url).group(1)
            item['url'] = self.format_link(response,url)

            yield item
