import re
import json
import scrapy


from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class NetworkPubaNetworkSpider(BaseSceneScraper):
    name = 'PubaNetwork'
    network = 'Puba Network'

    url = 'https://www.puba.com/'

    sites = [
        ['1 Girl 1 Camera', '3'],
        ['Abigail Mac', '79'],
        ['Adventures XXX', '66'],
        ['Alison Tyler', '57'],
        ['Alix Lynx', '104'],
        ['Asa Akira', '14'],
        ['Ashlee Graham', '127'],
        ['Avy Scott', '10'],
        ['Banging Pornstars', '77'],
        ['Bonus Content', '16'],
        ['Bouncy Pictures', '2'],
        ['Bree Olson', '131'],
        ['Brett Rossi', '72'],
        ['Britney Amber', '55'],
        ['Brooke Brand', '18'],
        ['Brooklyn Chase', '114'],
        ['Capri Cavanni', '51'],
        ['Charley Chase', '11'],
        ['Christiana Cinn', '130'],
        ['Christy Mack', '59'],
        ['Czech Hotties', '8'],
        ['Dahlia Sky', '60'],
        ['Daisy Monroe', '105'],
        ['Dana DeArmond', '73'],
        ['Dani Daniels', '56'],
        ['Dava Foxx', '90'],
        ['Diamond Kitty', '52'],
        ['Elsa Jean', '106'],
        ['Face Pounders', '7'],
        ['Forbidden Hookups', '137'],
        ['Gianna Michaels', '132'],
        ['Hard Gonzo', '23'],
        ['Jayden Cole', '123'],
        ['Jayden Jaymes', '4'],
        ['Jen Hexxx', '126'],
        ['Jezebelle Bond', '118'],
        ['Kendall Karson', '58'],
        ['Kendra Cole', '124'],
        ['Kiki D&#039;Aire', '129'],
        ['Kirsten Price', '65'],
        ['Leya Falcon', '67'],
        ['Lily Carter', '47'],
        ['Lola Foxx', '76'],
        ['Lolly Ink', '122'],
        ['London Keyes', '5'],
        ['Marica Hase', '108'],
        ['Mason Moore', '6'],
        ['Mia Lelani', '80'],
        ['Mr. Facial', '17'],
        ['My Doll Parts', '125'],
        ['Nadia White', '121'],
        ['Natasha Nice', '12'],
        ['Nick Manning', '19'],
        ['Nicole Aniston', '87'],
        ['Nikita Von James', '78'],
        ['Olivia Austin', '117'],
        ['Priya Rai', '128'],
        ['Rachel Roxxx', '53'],
        ['Romi Rain', '75'],
        ['Samantha Saint', '46'],
        ['Sarah Jessie', '102'],
        ['Sarah Vandella', '119'],
        ['Sasha Grey', '133'],
        ['Shyla Stylez', '13'],
        ['Skin Diamond', '61'],
        ['Summer Brielle', '107'],
        ['Taylor Vixen', '45'],
        ['Ty Endicott', '1'],
        ['Vanessa Cage', '49'],
        ['Victoria White', '48'],
        ['Vyxen Steel', '98'],
    ]

    def start_requests(self):
        for site in self.sites:

            yield scrapy.Request(url=self.get_next_page_url(self.url, self.page, site[1]),
                                 callback=self.parse,
                                 meta={'page': self.page, 'site': site[0], 'group': site[1]},
                                 headers=self.headers,
                                 cookies=self.cookies)

    def parse(self, response, **kwargs):
        scenes = self.get_scenes(response)
        count = 0
        for scene in scenes:
            count += 1
            yield scene

        if count:
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                meta = response.meta
                meta['page'] = meta['page'] + 1
                print('NEXT PAGE: ' + str(meta['page']))
                yield scrapy.Request(url=self.get_next_page_url(self.url, meta['page'], meta['group']),
                                     callback=self.parse,
                                     meta=meta,
                                     headers=self.headers,
                                     cookies=self.cookies)

    def get_next_page_url(self, base, page, group):
        page = str((int(page) - 1) * 12)
        url = "https://www.puba.com/pornstarnetwork/index.php?section=538&group={}&searching=Search&start={}&count=12&format=json&resource=video".format(group, page)
        return url

    selector_map = {
        'image': '//div[@class="tour-video-title"]/following-sibling::a/img/@style',
        're_image': r'\((.*\.jpg)\)',
        'tags': '//a[contains(@class,"btn-outline-secondary")]/text()',
        'performers': '//a[contains(@class,"btn-secondary")]/text()',
        'external_id': '',
        'pagination': ''
    }

    def get_scenes(self, response):
        meta = response.meta
        jsondata = json.loads(response.text)
        data = jsondata['items']
        for jsonentry in data:
            meta['id'] = str(jsonentry['galid'])
            meta['url'] = "https://www.puba.com/pornstarnetwork/" + jsonentry['video_url']
            meta['title'] = self.cleanup_title(jsonentry['description'])
            meta['description'] = self.cleanup_description(jsonentry['description'])
            meta['parent'] = meta['site']
            meta['network'] = "Puba Network"
            meta['trailer'] = ''
            if meta['url'] and meta['id']:
                yield scrapy.Request(meta['url'], callback=self.parse_scene, meta=meta)

    def get_image(self, response):
        image = self.process_xpath(response, self.get_selector_map('image'))
        if image:
            image = self.get_from_regex(image.get(), 're_image')
            if image:
                image = "https://www.puba.com/pornstarnetwork/" + image.strip()
                return image.replace(" ", "%20")
        return None

    def parse_scene(self, response):
        meta = response.meta
        item = SceneItem()

        item['title'] = self.cleanup_title(meta['title'])
        item['title'] = item['title'].replace("&amp;", "&")
        item['description'] = self.cleanup_description(meta['title'])
        item['description'] = item['description'].replace("&amp;", "&")
        item['performers'] = self.get_performers(response)
        item['id'] = meta['id']
        item['site'] = meta['site']
        item['parent'] = meta['parent']
        item['network'] = meta['network']
        item['date'] = self.parse_date('today').isoformat()
        item['trailer'] = ''
        item['url'] = re.search(r'(.*)\&nats', meta['url']).group(1)

        item['image'] = self.get_image(response)
        item['image_blob'] = None
        item['tags'] = self.get_tags(response)

        if self.debug:
            print(item)
        else:
            yield item
