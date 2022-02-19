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
        jsondata = jsondata['result']['data']['allMysqlTourStats']['edges']
        for scene in jsondata:
            item = SceneItem()

            item['network'] = 'NetVideoGirls'
            item['parent'] = 'NetVideoGirls'
            item['site'] = 'NetVideoGirls'

            item['date'] = scene['node']['tour_thumbs']['updates']['release_date']
            item['title'] = scene['node']['tour_thumbs']['updates']['short_title']
            item['id'] = scene['node']['tour_thumbs']['updates']['mysqlId']
            item['url'] = 'https://netvideogirls.com/home'

            item['image'] = "https://netvideogirls.com/" + scene['node']['tour_thumbs']['localFile']['childImageSharp']['fluid']['src']
            item['image_blob'] = False

            item['description'] = ''
            item['performers'] = []
            item['tags'] = ['Amateur', 'Audition']
            item['trailer'] = ''
            if item['date'] > "2021-01-01":
                yield item
