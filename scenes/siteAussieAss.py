import re
from datetime import date, timedelta
import string
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class AussieAssSpider(BaseSceneScraper):
    name = 'AussieAss'
    network = "AussieAss"

    start_urls = [
        'https://aussieass.com/',
        'https://aussiepov.com/'
    ]

    selector_map = {
        'title': '//div[@class="videoblock"]/h2/text()',
        'description': '//div[@class="epDescription"]/strong/following-sibling::text()',
        'date': "//div[@class='views']/span/text()",
        'image': '//div[@class="video_here"]/img/@src',
        'performers': '//div[@class="featuringWrapper"]/a/text()',
        'tags': "",
        'external_id': '\\/videos\\/(.*).htm',
        'trailer': '',
        'pagination': '/updates/page_%s.html'
    }

    def get_next_page_url(self, base, page):
        if "aussieass" in base:
            pagination = '/updates/page_%s.html'
        if "aussiepov" in base:
            pagination = '/index.php?page=%s'
        return self.format_url(base, pagination % page)

    def get_scenes(self, response):
        parentxpath = response.xpath('//div[@class="box"]')
        for child in parentxpath:
            item = SceneItem()

            title = child.xpath('.//span[@class="video-title"]/a/text()').get()
            if title:
                if re.search(r'^\d+\s+?.*', title):
                    title = re.sub(r'^(\d+\s+?)', '', title)
                item['title'] = self.cleanup_title(title)
            else:
                item['title'] = ''

            description = child.xpath('.//span[@class="video-title"]/a/@title').get()
            if description:
                item['description'] = self.cleanup_description(description)
            else:
                item['description'] = ''

            scenedate = child.xpath('.//span[@class="video-date"]/text()[2]').get()
            if scenedate:
                item['date'] = self.parse_date(scenedate.strip()).isoformat()
            else:
                item['date'] = self.parse_date('today').isoformat()

            image = child.xpath('./div/a/img/@src').get()
            if image:
                if "aussieass" in response.url:
                    item['image'] = "https://aussieass.com/" + image.strip()
                if "aussiepov" in response.url:
                    item['image'] = "https://aussiepov.com/" + image.strip()
            else:
                item['image'] = None
            item['image_blob'] = None

            performers = child.xpath('.//span[@class="update_models"]/a/text()').getall()
            if performers:
                item['performers'] = list(map(lambda x: string.capwords(x.strip()), performers))
            else:
                item['performers'] = []

            item['tags'] = []
            item['trailer'] = ''

            if "aussieass" in response.url:
                item['site'] = "Aussie Ass"
            if "aussiepov" in response.url:
                item['site'] = "Aussie POV"

            item['parent'] = "Aussie Ass"
            item['network'] = "Aussie Ass"

            url = child.xpath('.//span[@class="video-title"]/a/@href').get()
            if url:
                item['url'] = url.strip()
                if "id=" in url:
                    external_id = re.search(r'id=(\d+)', url).group(1)
                else:
                    external_id = re.search(r'(\d{2,4})', url)
                    if external_id:
                        external_id = external_id.group(1)
                    else:
                        external_id = re.search(r'.*\/(.*).html', url).group(1)
                if external_id:
                    item['id'] = external_id.strip()

            if item['id'] and item['url'] and "vids" in item['image']:
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
