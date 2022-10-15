from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteJukujoClubPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/actress/?&page=%s',
        'external_id': r'model/(.*)/'
    }

    name = 'JukujoClubPerformer'
    network = 'Jukujo Club'

    start_urls = [
        'https://en.jukujo-club.com',
    ]

    def get_next_page_url(self, base, page):
        page = str((page - 1) * 20)
        return self.format_url(base, self.get_selector_map('pagination') % page)

    def get_performers(self, response):
        performers = response.xpath('//li[@class="act_list"]')
        for performer in performers:
            item = PerformerItem()

            item['name'] = performer.xpath('./div/a/span/text()').get()
            image = performer.xpath('./div/a/img/@src')
            if image and "noimage" not in image.get():
                image = image.get()
                item['image'] = self.format_link(response, image)
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
            else:
                item['image'] = ''
                item['image_blob'] = ''
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
            item['network'] = 'Jukujo Club'
            item['url'] = performer.xpath('./div/a/@href').get()

            yield item
