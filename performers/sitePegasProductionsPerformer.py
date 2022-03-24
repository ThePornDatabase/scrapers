import re
import unicodedata
import html
import string
from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SitePegasProductionsPerformerSpider(BasePerformerScraper):
    selector_map = {
        # The performers are listed on the pages randomly.  There are about 80 or so on the site
        # I just scraped 50 pages to make sure to get them all
        'pagination': '/pornstars-quebecoises-tour/page/%s',
        'external_id': 'girls/(.+)/?$'
    }

    name = 'PegasProductionsPerformer'

    start_urls = [
        'https://www.pegasproductions.com',
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[contains(@class, "span2") and contains(@itemtype, "Person")]')
        for performer in performers:
            item = PerformerItem()

            name = performer.xpath('./a/h3/text()').get()
            if name:
                item['name'] = self.strip_accents(html.unescape(name.strip()))

            image = performer.xpath('./a/img/@src').get()
            if image:
                item['image'] = self.format_link(response, image).replace(" ", "%20")
            else:
                item['image'] = None
            item['image_blob'] = None

            url = performer.xpath('./a/@href').get()
            if url:
                if "?nom" in url:
                    url = re.search(r'(.*)\?nom', url).group(1)
                if "&nats" in url:
                    url = re.search(r'(.*)&nats', url).group(1)
                item['url'] = self.format_link(response, url.strip()).replace(" ", "%20")

            item['network'] = 'Pegas Productions'

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

    def strip_accents(self, text):
        try:
            text = unicode(text, 'utf-8')
        except (TypeError, NameError):  # unicode is a default on python 3
            pass
        text = unicodedata.normalize('NFD', text)
        text = text.encode('ascii', 'ignore')
        text = text.decode("utf-8")
        text = re.sub('[^0-9a-zA-Z ]', '', text)
        return string.capwords(str(text))
