from tpdb.BasePerformerScraper import BasePerformerScraper


class GirlsOutWestPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/models//models_%s_d.html',
        'external_id': r'model/(.*)/'
    }

    name = 'GirlsOutWestPerformer'
    network = 'Girls Out West'

    start_urls = [
        'https://tour.girlsoutwest.com',
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[@class="modelPic"]')
        for performer in performers:
            item = self.init_performer()

            perf_name = performer.xpath('.//h5/a/text()').get()
            item['name'] = self.cleanup_title(perf_name.strip())
            image = performer.xpath('.//img/@src0_1x')
            if image:
                item['image'] = self.format_link(response, image.get())
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
            else:
                item['image'] = ""
                item['image_blob'] = ""
            item['gender'] = 'Female'
            item['network'] = 'Girls Out West'
            item['url'] = self.format_link(response, performer.xpath('.//h5/a/@href').get())

            yield item
