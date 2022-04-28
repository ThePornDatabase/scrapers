import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteCumfortuneSpider(BaseSceneScraper):
    name = 'Cumfortune'

    start_url = 'https://www.cumfortune.com'

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'external_id': r'.*/(.*?).htm',
        'trailer': '',
        'pagination': '/categories/movies_%s_d.html#'
    }

    def start_requests(self):
        link = 'https://www.cumfortune.com/Scenes_Start.htm'
        yield scrapy.Request(link, callback=self.start_requests2)

    def start_requests2(self, response):
        meta = {}
        pagelinks = response.xpath('//table[@class="Table_3"]//a[contains(@href, "Promos/ZZZZ")]/@href').getall()
        pagelinks.reverse()
        meta['pagelinks'] = pagelinks
        meta['page'] = self.page
        yield scrapy.Request(url=self.get_next_page_url(self.start_url, self.page, meta['pagelinks']),
                             callback=self.parse,
                             headers=self.headers,
                             cookies=self.cookies, meta=meta)

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
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page'], meta['pagelinks']),
                                     callback=self.parse,
                                     meta=meta,
                                     headers=self.headers,
                                     cookies=self.cookies)

    def get_next_page_url(self, base, page, pagelinks):
        if page <= len(pagelinks):
            return self.format_url(base, pagelinks[page - 1])

    def get_scenes(self, response):
        scenes = response.xpath('//td[@colspan="3" and @class="Actor"]/../..')
        for scene in scenes:
            item = SceneItem()

            external_id = scene.xpath('.//a[contains(@href, "GIRLS")]/../following-sibling::td[@align="right"]/text()|.//a[contains(@href, "GIRLS")]/../following-sibling::td[@align="right"]/p/text()|.//a[contains(@href, "GIRLS")]/../following-sibling::td[contains(text(), "Scene ")]/text()')
            if external_id:
                item['id'] = re.search(r'(\d{1,4})', external_id.get()).group(1)
                idxpath = '//td[@align="right" and contains(.//text(), "{}")]/../../following-sibling::table[@class="table"][1]'.format(item['id'])
                scene2 = response.xpath(idxpath)

                title = scene.xpath('.//td[@class="Actor"]/text()')
                if title:
                    item['title'] = title.get()
                else:
                    item['title'] = ''

                performers = scene.xpath('.//tr/td[@class="TXT"]/a/text()')
                if performers:
                    item['performers'] = performers.getall()
                else:
                    item['performers'] = []

                item['tags'] = self.get_tags(scene2)
                item['description'] = " ".join(scene2.xpath('.//p[@class="TXT"]//text()').getall())

                item['trailer'] = None
                item['site'] = 'Cumfortune'
                item['parent'] = 'Cumfortune'
                item['network'] = 'Cumfortune'

                item['image'] = ''
                item['image_blob'] = ''
                images = scene2.xpath('.//img/@xthumbnail-orig-image').getall()
                if len(images) > 1:
                    item['image'] = "https://www.cumfortune.com/Promos" + images[2].replace("..", "")
                    item['image_blob'] = self.get_image_blob_from_link(item['image'])
                else:
                    images = scene2.xpath('.//img[contains(@src, ".jpg")]/@src').getall()
                    if len(images) > 1:
                        item['image'] = "https://www.cumfortune.com/Promos" + images[2].replace("..", "")
                        item['image_blob'] = self.get_image_blob_from_link(item['image'])

                item['url'] = response.url

                item['date'] = self.parse_date('today').isoformat()

                yield item

    def get_tags(self, response):
        taglist = []
        tags = response.xpath('.//span[@class="TXT"]/img[contains(@src, "/Buttons/")]/@src').getall()
        for tag in tags:
            tag = re.search(r'Buttons/(.*).png', tag)
            if tag:
                tag = tag.group(1)
                if tag.lower() == 'femorg':
                    tag = 'Orgasm'
                if tag.lower() == 'bj':
                    tag = 'Blowjob'
                if tag.lower() == 'cuminmouth':
                    tag = 'Cum in Mouth'
                taglist.append(tag)
        return taglist
