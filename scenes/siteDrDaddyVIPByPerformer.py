import re
import string
import scrapy
from slugify import slugify
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteDrDaddyVIPByPerformerSpider(BaseSceneScraper):
    name = 'DrDaddyVIPByPerformer'
    network = 'Dr Daddy VIP'
    parent = 'Dr Daddy VIP'
    site = 'Dr Daddy VIP'

    selector_map = {
        'external_id': r'',
        'pagination': '',
    }
    async def start(self):
        meta = {}
        yield scrapy.Request('https://www.drdaddyvip.com/models/models_d.html', callback=self.get_models, meta=meta)

    def get_models(self, response):
        meta = self.copy_meta(response)
        models = response.xpath('//div[contains(@class,"pornstar-item")]')
        for model in models:
            name = string.capwords(model.xpath('.//div[contains(@class, "pornstar-name")]/a/text()').get().strip())
            url = self.format_link(response, model.xpath('.//div[contains(@class, "pornstar-name")]/a/@href').get().strip())
            image = self.format_link(response, model.xpath('.//img/@src').get().strip())
            meta['performers'] = [name]
            perf = {}
            perf['name'] = name
            perf['image'] = image
            # perf['image_blob'] = self.get_image_blob_from_link(perf['image'])
            perf['url'] = url
            perf['site'] = self.site
            perf['extra'] = {'gender': 'Female'}
            meta['performers_data'] = [perf]

            yield scrapy.Request(url=url, callback=self.parse_model, meta=meta)

    def parse_model(self, response):
        meta = self.copy_meta(response)
        birthday = response.xpath('//section[contains(@id, "model-bio-cel")]//div[contains(@class, "model-bio-item")]/b[contains(text(), "BIRTH")]/following-sibling::text()')
        if birthday:
            birthday = birthday.get().strip()
            birthday = re.search(r'(\w+ \d{1,2}, \d{4})', birthday)
            if birthday:
                birthday = birthday.group(1)
                birthday = self.parse_date(birthday).strftime('%Y-%m-%d')
                meta['performers_data'][0]['extra']['birthday'] = birthday

        height = response.xpath('//section[contains(@id, "model-bio-cel")]//div[contains(@class, "model-bio-item")]/b[contains(text(), "HEIGHT")]/following-sibling::text()')
        if height:
            height = height.get().strip()
            height = re.sub(r'[^0-9cm]', '', height.lower())
            height = re.search(r'([0-9]+)cm', height)
            if height:
                height = height.group(1)
                meta['performers_data'][0]['extra']['height'] = height

        scenes = response.xpath('//div[@class="title-label"]/a/@href').getall()
        main_entry = response.xpath('//div[@id="block-content"]/img/@alt')
        if main_entry:
            main_entry = main_entry.get().strip().replace("'", "")
            main_entry = slugify(main_entry)
            main_entry = f"https://www.drdaddyvip.com/updates/{main_entry}.html"

        scenes.append(main_entry)
        scenes = list(dict.fromkeys(s.lower() for s in scenes))

        for scene in scenes:
            sceneid = re.search(r'/updates/(.*?)\.', scene)
            if sceneid:
                meta['id'] = sceneid.group(1)
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.get_scenes, meta=meta)

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        item = self.init_scene()

        item['performers_data'] = meta['performers_data']
        item['site'] = self.site
        item['parent'] = self.parent
        item['network'] = self.network
        item['id'] = meta['id']
        item['url'] = response.url

        title = response.xpath('//div[@class="title-trailer"]/h2/text()').get()
        item['title'] = self.cleanup_title(title)
        
        description  = response.xpath('//div[@class="description-trailer"]//text()').getall()
        description = " ".join(description).strip()
        description = self.cleanup_description(description)
        item['description'] = description.replace("...", "").replace("Read More", "").strip()

        scenedate = response.xpath('//b[contains(text(), "RELEASE DATE")]/following-sibling::text()')
        if scenedate:
            scenedate = scenedate.get().strip()
            item['date'] = self.parse_date(scenedate).strftime('%Y-%m-%d')

        image = response.xpath('//meta[@property="og:image"]/@content')
        if image:
            item['image'] = self.format_link(response, image.get().strip())
            # item['image_blob'] = self.get_image_blob_from_link(item['image'])

        duration = response.xpath('//b[contains(text(), "LENGTH")]/following-sibling::text()')
        if duration:
            duration = duration.get().strip()
            item['duration'] = self.duration_to_seconds(duration)

        performers = response.xpath('//b[contains(text(), "GIRLS")]/following-sibling::span[@class="update_models"]/a/text()')
        if performers:
            item['performers'] = performers.getall()
            item['performers'] = [string.capwords(p.strip()) for p in item['performers'] if p.strip()]
        else:
            item['performers'] = meta['performers']

        yield self.check_item(item, self.days)