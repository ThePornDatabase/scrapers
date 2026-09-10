import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteTNVGirlsSpider(BaseSceneScraper):
    name = 'TNVGirls'
    network = 'TNVGirls'
    parent = 'TNVGirls'
    site = 'TNVGirls'

    start_urls = [
        'https://www.tnvgirls.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/tour/models/models_%s_d.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        models = response.xpath('//div[@class="model"]//img/@id').getall()
        for model in models:
            modelid = re.search(r'target-(\d+)', model).group(1)
            for i in range(1, 10):
                url = f"https://www.tnvgirls.com/tour/sets.php?id={modelid}&page={str(i)}"
                yield scrapy.Request(url, callback=self.parse_model, meta=meta)        

    def parse_model(self, response):
        scenes = response.xpath('//div[@class="update_block"]')

        perf_name = response.xpath('//div[@class="updatesBlock"]/h2/text()').get()
        perf_name = re.sub(r'[^a-z0-9 ]+', '', perf_name, flags=re.IGNORECASE).strip()

        perf_id = response.xpath('//div[@class="updatesBlock"]//img[contains(@class, "model_bio_thumb")]/@id')
        if perf_id:
            perf_id = re.search(r'-(\d+)', perf_id.get()).group(1)
            perf_name = perf_name + '_' + perf_id
        else:
            perf_id = response.xpath('//div[@class="rating_box"]/@data-id')
            if perf_id:
                perf_id = perf_id.get()
                perf_name = perf_name + '_' + perf_id

        perf_image = response.xpath('//div[@class="updatesBlock"]//img[contains(@class, "model_bio_thumb")]/@src0_2x')
        if perf_image:
            perf_image = self.format_link(response, perf_image.get())
            perf_blob = self.get_image_blob_from_link(perf_image)
        else:
            perf_image = None
            perf_blob = None


        for scene in scenes:
            item = self.init_scene()

            title = scene.xpath('.//span[@class="update_title"]/text()').get()
            item['title'] = self.cleanup_title(title)

            scenedate = scene.xpath('.//span[@class="availdate"]/text()')
            if scenedate:
                scenedate = scenedate.get().strip()
                item['date'] = self.parse_date(scenedate, date_formats=['%m/%d/%Y']).strftime('%Y-%m-%d')
            
            if self.check_item(item, self.days):
                # Instead of pulling all of them, only going to pull the performer that is the model page being parsed
                # performers = response.xpath('.//span[@class="tour_update_models"]/text()')
                # if performers:
                #     performers = performers.get()
                #     performers = performers.strip()
                #     performers = performers.split(',')
                #     item['performers'] = []
                #     item['performers_data'] = []
                #     for performer in performers:
                #         performer = self.cleanup_title(performer)
                #         item['performers'].append(performer)
                #         perf = {}
                #         perf['name'] = performer
                #         perf['gender'] = 'Female'
                #         perf['site'] = 'TNVGirls'
                #         item['performers_data'].append(perf)

                item['performers'] = [perf_name]
                perf = {}
                perf['name'] = perf_name
                perf['gender'] = 'Female'
                perf['site'] = 'TNVGirls'
                perf['image'] = perf_image
                perf['image_blob'] = perf_blob
                item['performers_data'] = [perf]

                description = scene.xpath('.//span[@class="latest_update_description"]/text()')
                if description:
                    description = description.get().strip()
                    item['description'] = self.cleanup_description(description)

                tags = scene.xpath('.//span[@class="update_tags"]/a/text()')
                if tags:
                    tags = tags.getall()
                    item['tags'] = []
                    for tag in tags:
                        tag = self.cleanup_title(tag)
                        item['tags'].append(tag)
                
                image = scene.xpath('.//comment()[contains(., "First Thumb")]/following-sibling::a[1]/img/@src0_4x')
                if image:
                    item['image'] = self.format_link(response, image.get())
                    item['image_blob'] = self.get_image_blob_from_link(item['image'])
                else:
                    item['image'] = None
                    item['image_blob'] = None

                item['url'] = self.format_link(response, scene.xpath('.//comment()[contains(., "First Thumb")]/following-sibling::a[1]/@href').get())
                item['id'] = re.search(r'updates/(.*?)\.htm', item['url']).group(1).lower()

                item['site'] = 'TNVGirls'
                item['parent'] = 'TNVGirls'
                item['network'] = 'TNVGirls'

                yield item
