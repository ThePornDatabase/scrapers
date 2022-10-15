import re
from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteKillergramPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/ourgirls.asp?page=our%20girls&p=16',
        'external_id': r'model/(.*)/'
    }

    name = 'KillergramPerformer'
    network = 'Killergram'

    start_urls = [
        'https://killergram.com',
    ]

    def get_next_page_url(self, url, page):
        page = str(((page - 1) * 21) + 1)
        return f"https://killergram.com/ourgirls.asp?page=our%20girls&p={page}"

    def get_performers(self, response):
        performers = response.xpath('//img[contains(@src, "modelprofilethumb.jpg")]/@src').getall()
        for performer in performers:
            item = PerformerItem()

            name = re.search(r'models/(.*?)/', performer).group(1)
            name = name.replace("_", " ").replace("-", " ").replace("%20", " ")
            item['name'] = self.cleanup_title(name).strip()
            item['image'] = self.format_link(response, performer).replace(" ", "%20")
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['bio'] = ''
            item['gender'] = 'Female'
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
            item['network'] = 'Killergram'
            item['url'] = f'https://killergram.com/episodes.asp?page=episodes&model={name.replace(" ", "%20")}&ct=model'

            yield item
