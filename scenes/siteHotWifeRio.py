from datetime import date, timedelta
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteHotWifeRioSpider(BaseSceneScraper):
    name = 'HotWifeRio'
    network = 'Hot Wife Rio'

    start_urls = [
        'https://hotwiferio.com',
    ]

    selector_map = {
        'external_id': r'updates\/(.*).html',
        'pagination': '/newtour/categories/updates_%s.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="update_details"]')
        for scene in scenes:
            item = SceneItem()
            title = scene.xpath('./a[@class="upmg"]/text()')
            item['title'] = ''
            if title:
                item['title'] = self.cleanup_title(title.get())

            item['description'] = ''

            scenedate = scene.xpath('.//comment()[contains(., "Date")]/following-sibling::text()')
            item['date'] = ""
            if scenedate:
                item['date'] = self.parse_date(scenedate.get().strip(), date_formats=['%m/%d/%Y']).strftime('%Y-%m-%d')

            image = scene.xpath('./a/img/@src0_3x')
            item['image'] = None
            if image:
                item['image'] = "https://hotwiferio.com" + image.get().strip()

            item['image_blob'] = self.get_image_blob_from_link(item['image'])

            item['performers'] = ['Rio Blaze']

            item['tags'] = []

            item['url'] = scene.xpath('./a[@class="upmg"]/@href').get()
            item['site'] = "Hot Wife Rio"
            item['parent'] = "Hot Wife Rio"
            item['network'] = "Hot Wife Rio"

            item['trailer'] = ''

            item['id'] = scene.xpath('./@data-setid').get()

            if item['id'] and item['title'] and item['date'] > '2023-09-10':
                days = int(self.days)
                if days > 27375:
                    filterdate = "0000-00-00"
                else:
                    filterdate = date.today() - timedelta(days)
                    filterdate = filterdate.strftime('%Y-%m-%d')

                if self.debug:
                    if not item['date'] > filterdate:
                        item['filtered'] = "Scene filtered due to date restraint"
                    print(item)
                else:
                    if filterdate:
                        if item['date'] > filterdate:
                            yield item
                    else:
                        yield item
