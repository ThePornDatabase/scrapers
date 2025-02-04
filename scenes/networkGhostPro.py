import re
import json
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteGhostProSpider(BaseSceneScraper):
    name = 'GhostPro'
    network = 'Ghost Pro'

    start_urls = [
        'https://www.creampiethais.com',
        'https://www.thaigirlswild.com',
        'https://www.creampieinasia.com',
        'https://www.asiansuckdolls.com',
        'https://www.creampiecuties.com',
        'https://www.trixieswallows.com',
        'https://www.gogobarauditions.com',
        'https://www.creamedcuties.com',
        'https://www.asiansybian.com',
        'https://www.thaipussymassage.com',
        'https://www.thainee.com',
        'https://www.analjesse.com',
        'https://www.analjesse_ss.com',
        'https://www.lulusexbomb.com',
        'https://www.submityourthai.com',
        'https://www.tailynn.com',
        'https://www.thaigirlswild.com',
        'https://www.tussinee.com',
        'https://www.tittiporn.com',
    ]

    selector_map = {
        'pagination': '/videos?page=%s&order_by=publish_date&sort_by=desc',
        'external_id': r''
    }

    def get_next_page_url(self, base, page):
        if "lulusex" in base:
            pagination = '/categories/updates_%s_d.html'
        if "analjesse_ss" in base:
            pagination = '/tags/shorts?page=%s&order_by=publish_date&sort_by=desc'
            base = 'https://www.analjesse.com'
        else:
            pagination = self.get_selector_map('pagination')
        return self.format_url(base, pagination % page)

    def get_scenes(self, response):
        print(response.url)
        jsoncode = response.xpath('//script[contains(@id, "NEXT_DATA")]/text()')
        if jsoncode:
            jsondata = json.loads(jsoncode.get())
            jsondata = jsondata['props']['pageProps']['contents']['data']
            for scene in jsondata:
                item = SceneItem()
                site = re.search(r'https://www\.(.*?)\.', response.url).group(1)
                item['title'] = scene['title']
                item['description'] = re.sub('<[^<]+?>', '', scene['description'])
                if 'trailer_screencap' in scene and scene['trailer_screencap'] and 'tussinee' not in response.url:
                    item['image'] = scene['trailer_screencap']
                else:
                    item['image'] = scene['thumb']
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
                item['id'] = re.search(r'.*/(\d*)', item['image']).group(1)
                item['trailer'] = scene['trailer_url']
                scene_date = self.parse_date(scene['publish_date'], date_formats=['%Y/%m/%d %h:%m:%s']).strftime('%Y-%m-%d')
                if scene_date:
                    item['date'] = scene_date
                else:
                    item['date'] = self.parse_date('today').isoformat()
                item['url'] = f"https://www.{site}.com/videos/{scene['slug']}"
                item['duration'] = self.duration_to_seconds(scene['videos_duration'])
                item['site'] = site
                item['parent'] = site
                item['network'] = 'Ghost Pro'

                item['performers'] = []
                item['performers_data'] = []
                for model in scene['models_slugs']:
                    if model['name']:
                        item['performers'].append(model['name'])
                        performer_extra = {}
                        performer_extra['name'] = model['name']
                        performer_extra['network'] = item['network']
                        performer_extra['site'] = item['network']
                        performer_extra['extras'] = {}
                        performer_extra['extras']['gender'] = "Female"
                        item['performers_data'].append(performer_extra)

                if not item['performers'] and "trixieswallows" in response.url:
                    item['performers'] = ['Trixie Swallows']

                if not item['performers'] and "thainee" in response.url:
                    item['performers'] = ['Thainee']

                if not item['performers'] and "tussinee" in response.url:
                    item['performers'] = ['Tussinee']

                if not item['performers'] and "tailynn" in response.url:
                    item['performers'] = ['Tailynn']

                item['tags'] = []

                if "creampiethais" in site or "creampieinasia" in site:
                    item['tags'] = ['Asian', 'Amateur', 'Creampie']

                if "asiansybian" in site:
                    item['tags'] = ['Asian', 'Amateur', 'Fucking Machine', 'Vibrator', 'Sybian']

                if "thaipussymassage" in site:
                    item['tags'] = ['Asian', 'Amateur', 'Massage']

                if "analjesse" in site:
                    item['tags'] = ['Asian', 'Amateur', 'Anal']

                if "thainee" in site or "tailynn" in site or "tussinee" in site or "tittiporn" in site or "thaigirlswild" in site or "submityourthai" in site:
                    item['tags'] = ['Asian', 'Amateur']

                if "asiansuckdolls" in site:
                    item['tags'] = ['Asian', 'Amateur', 'Blowjob']

                if "asiansuckdolls" in site:
                    item['tags'] = ['Asian', 'Amateur', 'Blowjob']

                if "creampiecuties" in site or "creamedcuties" in site:
                    item['tags'] = ['Creampie', 'Amateur']

                if "trixieswallows" in site:
                    item['tags'] = ['Blowjob', 'Swallowing']

                if "thaigirlswild" in site or "asiansybian" in site or "gogobarauditions" in site:
                    item['tags'] = ['Asian', 'Amateur']

                yield self.check_item(item, self.days)
