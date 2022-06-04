import string
import time
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteLifeSelectorSpider(BaseSceneScraper):
    name = 'LifeSelector'
    network = 'Life Selector'
    parent = 'Life Selector'
    site = 'Life Selector'

    start_urls = [
        'https://lifeselector.com',
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
        'pagination': '/game/listGames?format=partial&offset=%s&gameType=all&order=releaseDate&_=%s'
    }

    def get_next_page_url(self, base, page):
        page = str((int(page) - 1) * 20)
        timestamp = str(int(time.time()))
        return self.format_url(base, self.get_selector_map('pagination') % (page, timestamp))

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class, "episodeBlock") and contains(@class, "normal")]')
        for scene in scenes:
            item = SceneItem()
            item['title'] = self.cleanup_title(scene.xpath('.//h1/a/text()').get())
            item['description'] = ""
            description = scene.xpath('.//div[@class="td story"]//text()[not(ancestor::a) and not(ancestor::em)]')
            if description:
                item['description'] = " ".join(list(map(lambda x: x.strip(), description.getall()))).strip().replace("\n", "").replace("\t", "").replace("\r", "")
            item['date'] = self.parse_date('today').isoformat()
            item['image'] = ""
            item['image_blob'] = ""
            image = scene.xpath('./div/a/img/@src')
            if image:
                item['image'] = self.format_link(response, image.get())
                if "list/1.jpg" in item['image']:
                    item['image'] = item['image'].replace("list/1", "poster/1_size2000")
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
            performers = scene.xpath('.//div[@class="details"]/div[@class="tr"]/div[@class="th" and contains(./text(), "Starring")]/following-sibling::div[@class="td"]/a/text()')
            item['performers'] = []
            if performers:
                item['performers'] = performers.getall()
            tags = scene.xpath('.//div[@class="details"]/div[@class="tr"]/div[@class="th" and contains(./text(), "Labels")]/following-sibling::div[@class="td"]/a/text()')
            item['tags'] = []
            if tags:
                item['tags'] = list(map(lambda x: string.capwords(x.strip()), tags.getall()))
            item['trailer'] = ''
            trailer = scene.xpath('.//span[@class="view-trailer"]/a/@data-video-src')
            if trailer:
                item['trailer'] = self.format_link(response, trailer.get())
            item['id'] = scene.xpath('./@id').get()
            item['network'] = "Life Selector"
            item['parent'] = "Life Selector"
            item['site'] = "Life Selector"
            item['url'] = self.format_link(response, scene.xpath('./div[@class="thumb"]/a/@href').get())
            yield self.check_item(item, self.days)
