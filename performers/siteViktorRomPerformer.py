import html
from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class PerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/en/modeles?page=%s',
        'external_id': r'model/(.*)/'
    }

    name = 'ViktorRomPerformer'
    network = 'Viktor Rom'

    start_urls = [
        'https://www.viktor-rom.com',
    ]

    def get_next_page_url(self, base, page):
        page = str(int(page) - 1)
        return self.format_url(base, self.get_selector_map('pagination') % page)

    def get_performers(self, response):
        performers = response.xpath('//a[contains(@href, "en/modeles/detail")]')
        for performer in performers:
            item = PerformerItem()

            name = performer.xpath('.//div[contains(@class, "text-dark")]/text()')
            if name:
                item['name'] = html.unescape(name.get().strip().title())

            image = performer.xpath('.//img/@src')
            if image:
                image = image.get()
                item['image'] = self.format_link(response, image)
            else:
                item['image'] = None

            item['image_blob'] = self.get_image_blob_from_link(item['image'])

            url = performer.xpath('./@href')
            if url:
                item['url'] = self.format_link(response, url.get().strip()).replace(" ", "%20")
            else:
                item['url'] = response.url

            item['network'] = 'Viktor Rom'

            item['astrology'] = ''
            item['bio'] = ''
            item['birthday'] = ''
            item['birthplace'] = ''
            item['cupsize'] = ''
            item['ethnicity'] = ''
            item['eyecolor'] = ''
            item['fakeboobs'] = ''
            item['gender'] = 'Male'
            item['haircolor'] = ''
            item['height'] = ''
            item['measurements'] = ''
            item['nationality'] = ''
            item['piercings'] = ''
            item['tattoos'] = ''
            item['weight'] = ''

            yield item
