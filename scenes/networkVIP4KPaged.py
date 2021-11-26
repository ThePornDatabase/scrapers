import re
import scrapy
import tldextract
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class VIP4KPagedSpider(BaseSceneScraper):
    name = 'VIP4KPaged'
    network = 'VIP 4K'
    parent = 'VIP 4K'

    start_urls = [
        'https://debt4k.com',
        'https://hunt4k.com',
        'https://law4k.com',
        'https://loan4k.com',
        'https://shame4k.com',
        'https://stuck4k.com',
        'https://tutor4k.com',
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': "",
        'external_id': 'updates\\/(.*)\\.html$',
        'trailer': '//video/source/@src',
        'pagination': '/en/%s'
    }

    def parse(self, response, **kwargs):
        count = 0
        if "debt4k" in response.url:
            scenes = response.xpath('//div[@class="episode__body"]')
        if "hunt4k" in response.url:
            scenes = response.xpath('//div[@class="box-index"]')
        if "law4k" in response.url:
            scenes = response.xpath('//div[@class="content__block episode-block"]')
        if "loan4k" in response.url:
            scenes = response.xpath('//div[@class="holder"]')
        if "stuck4k" in response.url:
            scenes = response.xpath('//div[@class="content__block episode"]')
        if "shame4k" in response.url:
            scenes = response.xpath('//div[@class="content__block episode"]')
        if "tutor4k" in response.url:
            scenes = response.xpath('//div[@class="content__block episode"]')
        for scene in scenes:
            count = count + 1
            item = SceneItem()
            item['performers'] = []
            item['trailer'] = ''
            item['description'] = ''
            item['parent'] = "VIP 4K"
            item['network'] = "VIP 4K"
            item['url'] = response.url
            item['tags'] = []
            description = ''

            item['date'] = self.parse_date('today').isoformat()

            if "debt4k" in response.url:
                performer = scene.xpath('.//strong[contains(text(),"Name")]/../following-sibling::div/text()').get()
            if "hunt4k" in response.url:
                performer = ''
            if "law4k" in response.url:
                performer = scene.xpath('./following-sibling::div[contains(@class,"episode")][1]//div[contains(text(),"Alias")]/following-sibling::div/text()').get()
            if "loan4k" in response.url:
                performer = scene.xpath('.//li/span[contains(text(), "Name")]/following-sibling::strong/text()').get()
            if "shame4k" in response.url:
                performer = scene.xpath('.//div[@class="record__about"]/div/span[contains(text(),"Name:")]/following-sibling::text()').get()
            if "stuck4k" in response.url:
                performer = ''
            if "tutor4k" in response.url:
                performer = ''
            performer = performer.strip()
            item['performers'].append(performer)

            if "debt4k" in response.url:
                title = scene.xpath('.//h2[contains(@class,"episode__title")]/text()').get()
            if "hunt4k" in response.url:
                title = scene.xpath('.//div[@class="title-embed"]/span/text()').get()
            if "law4k" in response.url:
                title = scene.xpath('.//h2[contains(@class,"title")]/text()').get()
            if "loan4k" in response.url:
                title = scene.xpath('.//div[@class="top_panel"]/span/text()').get()
            if "shame4k" in response.url:
                title = scene.xpath('./h2/text()').get()
            if "stuck4k" in response.url:
                title = scene.xpath('.//div[@class="record__title"]/text()').get()
            if "tutor4k" in response.url:
                title = scene.xpath('.//h2[contains(@class,"episode__title")]/text()').get()

            title = title.strip().title()
            item['id'] = re.sub(r'[^a-zA-Z0-9\-]', '', title.replace(" ", "-").lower())
            if performer and "law4k" not in response.url and "stuck4k" not in response.url and "shame4k" not in response.url and "tutor4k" not in response.url:
                title = title + ": " + performer

            item['title'] = title

            if "debt4k" in response.url:
                description = scene.xpath('.//div[@class="player-item__text"]/text()').get()
            if "hunt4k" in response.url:
                description = scene.xpath('.//div[@class="descr-embed"]/text()').get()
            if "law4k" in response.url:
                description = scene.xpath('./following-sibling::div[@class="content__block episode"][1]//div[contains(@class,"debt-note__text")]/text()').get()
            if "loan4k" in response.url:
                managernotes = scene.xpath('.//div[@class="hold_notes"]/p/text()').get()
                description = scene.xpath('//div[@class="post hide_block"]/p/text()').get()
                if managernotes:
                    description = "Managers Notes: " + managernotes + '\r\nDescription: ' + description
            if "shame4k" in response.url:
                description = scene.xpath('.//div[@class="episode__text"]/text()').get()
            if "stuck4k" in response.url:
                description = scene.xpath('.//div[@class="episode__text"]/span[@class="episode__text-area"]/text()').get()
            if "tutor4k" in response.url:
                description = scene.xpath('.//span[@class="episode-about__text text"]/text()').get()

            if description:
                item['description'] = description.strip()

            if "debt4k" in response.url:
                image = scene.xpath('.//div[@class="episode__player"]//img/@data-src').get()
            if "hunt4k" in response.url:
                image = scene.xpath('.//div[@class="embed"]/a//img/@data-src').get()
            if "law4k" in response.url:
                image = scene.xpath('.//div/span[contains(text(),"Punishment")]/../../../a/@style').get()
                if image:
                    image = re.search(r'url\((.*\.jpg)\)', image).group(1)
            if "loan4k" in response.url:
                image = scene.xpath('.//div[@class="wrapper_player"]/img/@data-src').get()
            if "shame4k" in response.url:
                image = scene.xpath('./div/a/picture//source[@type="image/jpeg"]/@data-srcset').get()
            if "stuck4k" in response.url:
                image = scene.xpath('./div[@class="episode__img"]/a/img/@data-src').get()
            if "tutor4k" in response.url:
                image = scene.xpath('./div[@class="episode__img"]/a/img/@data-src').get()
            if image:
                if image[:2] == "//":
                    image = "https:" + image.strip()

            item['image'] = image
            item['image_blob'] = None
            item['site'] = tldextract.extract(response.url).domain

            yield item

        if count and ("hunt4k" in response.url and count > 1):
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                meta = response.meta
                meta['page'] = meta['page'] + 1
                print('NEXT PAGE: ' + str(meta['page']))
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page']),
                                     callback=self.parse,
                                     meta=meta,
                                     headers=self.headers,
                                     cookies=self.cookies)
