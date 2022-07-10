import re
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteJoannaJetSpider(BaseSceneScraper):
    name = 'JoannaJet'
    network = 'Joanna Jet'
    parent = 'Joanna Jet'
    site = 'Joanna Jet'

    start_urls = [
        'http://www.joannajet.com',
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'trailer': '',
        'external_id': r'',
        'pagination': '/home.php?this_page={}&offset={}&vcat=100'
    }

    def get_next_page_url(self, base, page):
        pageurl = f"http://www.joannajet.com/home.php?this_page={page}&offset={(page - 1) * 16}&vcat=100"
        return pageurl

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="JJVidArea"]')
        for scene in scenes:
            item = SceneItem()
            title = scene.xpath('.//h2//text()').getall()
            title = self.cleanup_title(" ".join(title).replace("  ", " ").strip())
            item['title'] = title
            item['description'] = scene.xpath('.//div[@class="JJVidDesc"]//text()').get().replace('\n', '').replace('\t', '').replace('\r', '')
            scenedate = scene.xpath('.//span[contains(text(), "Released")]/strong/text()')
            if scenedate:
                item['date'] = self.parse_date(scenedate.get(), date_formats=['%d %B %Y']).isoformat()
            else:
                item['date'] = self.parse_date('today').isoformat()
            item['image'] = self.format_link(response, scene.xpath('.//img[contains(@src, "thumbnail")]/@src').get())
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['performers'] = ['Joanna Jet']
            item['tags'] = ['Trans', 'Shemale']
            item['trailer'] = ''
            item['id'] = re.search(r'thumbnails/(.*?)/', item['image']).group(1)
            item['url'] = self.format_link(response, scene.xpath('./a/@href').get())
            item['network'] = "Joanna Jet"
            item['parent'] = "Joanna Jet"
            item['site'] = "Joanna Jet"

            yield self.check_item(item, self.days)
