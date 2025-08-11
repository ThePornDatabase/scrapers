import html
import json
from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteJavHubPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/models?page=%s&order_by=publish_date&sort_by=desc',
        'external_id': 'girls/(.+)/?$'
    }

    name = 'JavHubPerformer'

    start_urls = [
        'https://tour.javhub.com',
    ]

    def get_performers(self, response):
        jsondata = response.xpath('//script[@id="__NEXT_DATA__"]/text()')
        if jsondata:
            jsondata = json.loads(jsondata.get())
            jsondata = jsondata['props']['pageProps']
            for jsonrow in jsondata['models']['data']:
                item = PerformerItem()
                item['name'] = self.cleanup_title(jsonrow['name'])
                item['image'] = jsonrow['thumb']
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
                item['url'] = f"https://javhub.com/models/{jsonrow['slug']}"
                item['network'] = 'JavHub'
                item['astrology'] = None

                if "Bio" in jsonrow:
                    item['bio'] = self.cleanup_text(jsonrow['Bio'])
                else:
                    item['bio'] = None

                if "Birthdate" in jsonrow:
                    item['birthday'] = self.parse_date(jsonrow['Birthdate']).isoformat()
                else:
                    item['birthday'] = None

                if "Born" in jsonrow:
                    item['birthplace'] = self.cleanup_text(jsonrow['Born'])
                else:
                    item['birthplace'] = None

                if "Eyes" in jsonrow:
                    item['eyecolor'] = self.cleanup_text(jsonrow['Eyes'])
                else:
                    item['eyecolor'] = None

                if "Hair" in jsonrow:
                    item['haircolor'] = self.cleanup_text(jsonrow['Hair'])
                else:
                    item['haircolor'] = None

                if "Height" in jsonrow:
                    item['height'] = self.cleanup_text(jsonrow['Height'])
                else:
                    item['height'] = None

                if "Weight" in jsonrow:
                    item['weight'] = self.cleanup_text(jsonrow['Weight'])
                else:
                    item['weight'] = None

                item['ethnicity'] = None
                item['fakeboobs'] = None
                item['gender'] = 'Female'

                if "Measurements" in jsonrow and re.search(r'(\d{1,3}\w+?)-\d{2,3}-\d{2,3}', jsonrow['Measurements']):
                    item['measurements'] = jsonrow['Measurements']
                    item['cupsize'] = re.search(r'(\d{1,3}\w+?)-\d{2,3}-\d{2,3}', jsonrow['Measurements']).group(1)
                else:
                    item['measurements'] = None
                    item['cupsize'] = None

                item['nationality'] = None
                item['piercings'] = None
                item['tattoos'] = None

                yield item
