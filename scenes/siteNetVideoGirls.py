import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteNetVideoGirlsSpider(BaseSceneScraper):
    name = 'NetVideoGirls'
    network = 'NetVideoGirls'
    parent = 'NetVideoGirls'
    site = 'NetVideoGirls'

    start_urls = [
        'https://netvideogirls.com',
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
        'pagination': ''
    }

    def start_requests(self):

        url = "https://netvideogirls.com/page-data/home/page-data.json"
        yield scrapy.Request(url, callback=self.get_scenes)

    def get_scenes(self, response):
        jsondata = response.json()
        jsondata = jsondata['result']['data']['allupdates']['nodes']
        for scene in jsondata:
            item = SceneItem()

            item['network'] = 'NetVideoGirls'
            item['parent'] = 'NetVideoGirls'
            item['site'] = 'NetVideoGirls'

            item['date'] = scene['release_date']
            if not item['date']:
                item['date'] = None
            item['title'] = scene['short_title']
            item['id'] = scene['mysqlId']
            item['url'] = 'https://netvideogirls.com/home'

            item['image'] = "https://netvideogirls.com/" + scene['tour_stats'][0]['tour_thumb']['localImage']['childImageSharp']['gatsbyImageData']['images']['fallback']['src']
            item['image_blob'] = self.get_image_blob_from_link(item['image'])

            item['description'] = ''
            item['performers'] = []
            item['tags'] = ['Amateur', 'Audition']
            item['trailer'] = ''
            if item['date'] > "2021-01-01" or not item['date']:
                yield self.check_item(item, self.days)
