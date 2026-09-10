import re
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteMPLStudiosSpider(BaseSceneScraper):
    name = 'MPLStudios'
    network = 'MPL Studios'

    start_urls = [
        'https://www.mplstudios.com',
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'external_id': r'',
        'trailer': '',
        'pagination': '/videos/%s/'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class, "box1") and contains(@class, "mb-3")]')
        for scene in scenes:
            item = self.init_scene()
            item['title'] = scene.xpath('.//span[@class="ellipsis"]/@title').get()
            item['performers'] = scene.xpath('.//span[@class="ellipsis"]/a[contains(@href, "portfolio")]/text()').getall()
            # the cover is a plain src now; the lazy-load data-src attribute is gone
            image = scene.xpath('./div/a/img/@src').get()
            if not image:
                continue
            item['image'] = self.format_link(response, image)
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['id'] = scene.xpath('./@data-id').get()
            pathsegment = re.search(r'videoPreview/(\d+)/', item['image'])
            if pathsegment:
                pathsegment = pathsegment.group(1)
            else:
                pathsegment = re.search(r'videoCovers/(\d+)/', item['image'])
                if pathsegment:
                    pathsegment = pathsegment.group(1)
            if not pathsegment:
                pathsegment = "290"
            item['trailer'] = f"https://cdn.mplstudios.com/v3Assets/videoPreview/{pathsegment}/{item['id']}/{item['id']}_1280x720.mp4"
            item['description'] = ''
            # was response.url, which gave every scene the listing URL
            link = scene.xpath('.//a[contains(@href, "/update/")]/@href').get()
            item['url'] = self.format_link(response, link) if link else response.url
            dates = scene.xpath('.//span[@class="ellipsis"]/text()').getall()
            item['date'] = self.parse_date('today').isoformat()
            for date in dates:
                if re.search(r'(\w{3} \d{1,2}, \d{4})', date):
                    item['date'] = self.parse_date(re.search(r'(\w{3} \d{1,2}, \d{4})', date).group(1), date_formats=['%b %d, %Y']).isoformat()
            item['tags'] = ['Erotica']
            item['site'] = 'MPL Studios'
            item['parent'] = 'MPL Studios'
            item['network'] = 'MPL Studios'
            yield item
