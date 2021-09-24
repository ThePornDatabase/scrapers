import re
import html
import scrapy
from tpdb.BasePerformerScraper import BasePerformerScraper


class DorcelClubPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//title/text()',
        'image': '//picture[@class="banner"]//source[contains(@media, "1024px")]/@data-srcset',
        'nationality': '//span[@class="nationality"]/text()',
        'bio': '//div[contains(@class,"content-description")]//span[@class="full"]//text()',
        'pagination': '/actor/list/more?lang=en&page={}&sorting=views&filters%5B0%5D=breast_average-tits&filters%5B1%5D=breast_big-boobs&filters%5B2%5D=breast_natural-breasts&filters%5B3%5D=breast_small-tits',
        'external_id': r'models\/(.*).html'
    }

    max_pages = 50

    name = 'DorcelClubPerformer'
    network = "Dorcel Club"

    start_urls = [
        'https://www.dorcelclub.com'
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[contains(@class,"actor thumbnail")]')
        for performer in performers:
            image = performer.xpath('.//source[contains(@media, "480px")]/@data-srcset')
            imagepath = ''
            if image:
                image = image.get()
                image = re.search(r'1x, (http.*?\.jpg) ', image)
                if image:
                    imagepath = image.group(1)

            performer = performer.xpath('.//a/@href').get()
            performer = performer.replace("actrice-x", "en/pornstar")
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer, meta={'image': imagepath})

    def get_gender(self, response):
        return "Female"

    def get_next_page_url(self, base, page):
        url = self.format_url(base, self.get_selector_map('pagination').format(page))
        return url

    def get_bio(self, response):
        bio = response.xpath(self.get_selector_map('bio'))
        if bio:
            bio = bio.getall()
            bio = " ".join(bio)
            return html.unescape(bio.strip())
        return ''
