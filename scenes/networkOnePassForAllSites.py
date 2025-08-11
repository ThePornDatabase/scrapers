import re
import string
import scrapy
from PIL import Image
import base64
from io import BytesIO
from tpdb.BaseSceneScraper import BaseSceneScraper

# ~ Sites included in this network:
# ~ "18 Virgin Sex"
# ~ "Creampied Sweeties"
# ~ "Daddies And Darlings"
# ~ "Dirty Ass 2 Mouth"
# ~ "Dirty Daddys Girls"
# ~ "Dirty Home Vids"
# ~ "Do My Wife Slut"
# ~ "Drilled Mouths"
# ~ "Frisky Baby Sitters"
# ~ "Horny In Hospital"
# ~ "I Fucked Her Finally"
# ~ "Lovely Teen Land"
# ~ "Milfs On Sticks"
# ~ "Mommies Do Bunnies"
# ~ "Old Goes Young"
# ~ "Old Young Anal"
# ~ "Shabby Virgins"
# ~ "She Made Us Lesbians"
# ~ "Spoiled Virgins"
# ~ "Strapon Service"
# ~ "Tricky Old Teacher"
# ~ "Wild Young Honeys"
# ~ "Young Anal Tryouts"
# ~ "Young And Banged"
# ~ "Young Cum Gulpers"
# ~ "Young Lesbians Portal"
# ~ "Young Models Casting"
# ~ "Young Porn Home Video"


class OnePassForAllSitesSpider(BaseSceneScraper):
    name = 'OnePassForAllSites'
    network = "1 Pass for All Sites"

    start_urls = [
        'https://www.1passforallsites.com'
    ]

    selector_map = {
        'title': '//div[@class="block-title"]/p[@class="path"]/span[@class="path-arrow"]/following-sibling::text()',
        'description': '//div[@class="sp-info-txt"]/h3/following-sibling::p/text()',
        'date': '//div[@class="movie-info"]/ul/li[contains(text(),"Added:")]/span/text()',
        'image': '//video/@poster',
        'performers': '//p[@class="sp-info-name"]/a/text()',
        'tags': '//p[@class="niches-list"]/a/text()',
        'external_id': '\\/episode\\/(\\d+)\\/',
        'trailer': '//video/source[@data-quality="SD"]/@src',
        'pagination': '/scenes/date?page=%s&site=0&order=date'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath(
            "//ul[@class='thumbs tn-updates tn-allmovs']/li")
        for scene in scenes:
            image = scene.xpath('.//img/@src')
            if image:
                image = image.get()
                image = image.replace("mainthumb", "big")
                meta['orig_image'] = image

            performers = scene.xpath('.//a[contains(@href, "model?")]')
            meta['orig_perf'] = []
            if performers:
                for performer in performers:
                    perf_name = string.capwords(performer.xpath('./text()').get())
                    perf_id = performer.xpath('./@href').get()
                    perf_id = re.search(r'=(\d+)', perf_id)
                    if perf_id and " " not in perf_name:
                        perf_name = perf_name + perf_id.group(1)
                    meta['orig_perf'].append(perf_name)

            scene = scene.xpath('./a[@class="tn"]/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_site(self, response):
        site = response.xpath('//p[@class="path"]/a/text()').get().strip()
        return site

    def get_image(self, response):
        meta = response.meta
        image = self.process_xpath(
            response, self.get_selector_map('image')).get()
        if not image:
            image = response.xpath('//div[@class="movie-wrapper"]/div[@id="join"]/@data-poster').get()
        if not image:
            image = ""

        if ("movie_tn" in image or not image) and "orig_image" in meta:
            image = meta['orig_image']

        return self.format_link(response, image)

    def get_title(self, response):

        title = self.process_xpath(response, self.get_selector_map('title'))
        if title:
            title = title.get()
        else:
            title = ""

        title2 = response.xpath('//meta[@name="description"]/@content')
        if title2:
            title2 = string.capwords(title2.get())
        else:
            title2 = ""

        title3 = response.xpath('//head/title/text()')
        if title3:
            title3 = string.capwords(title3.get()).strip()
            title3 = re.search(r'(.*?) - ', title3)
            if title3:
                title3 = title3.group(1)
            else:
                title3 = ""

        if title3:
            if len(title3) > len(title):
                title = title3
        elif title2:
            if len(title2) > len(title):
                title = title2

        if not title:
            title = "No Title Available"
        else:
            title = title.strip().replace(u'\xa0', u' ')
        return title

    def get_performers(self, response):
        meta = response.meta
        performers = []
        perf_list = response.xpath('//p[@class="sp-info-name"]/a')
        if perf_list:
            for performer in perf_list:
                perf_name = string.capwords(performer.xpath('./text()').get())
                perf_id = performer.xpath('./@href').get()
                perf_id = re.search(r'=(\d+)', perf_id)
                if perf_id and " " not in perf_name:
                    perf_name = perf_name + perf_id.group(1)
                performers.append(perf_name)
        elif meta['orig_perf']:
            performers = meta['orig_perf']
        return performers

    def get_performers_data(self, response):
        performers = self.get_performers(response)
        performers_data = []
        if len(performers):
            for performer in performers:
                perf = {}

                model_id = re.search(r'(\d+)', performer)
                if model_id:
                    image = f"https://img5.thepluginz.com/model_img/{model_id.group(1)}/big.jpg"
                    perf['image'] = image
                    perf['image_blob'] = self.get_image_blob_from_link(image)

                perf['name'] = performer
                perf['extra'] = {}
                perf['extra']['gender'] = "Female"
                perf['network'] = "1 Pass for All Sites"
                perf['site'] = "1 Pass for All Sites"
                performers_data.append(perf)
        return performers_data

    def get_image_blob_from_link(self, image):
        force_update = self.settings.get('force_update')
        if force_update:
            force_update = True
        force_fields = self.settings.get('force_fields')
        if force_fields:
            force_fields = force_fields.split(",")

        if image and "model_img" in image:
            force_update = False

        if (not force_update or (force_update and "image" in force_fields)) and image:
            data = self.get_image_from_link(image)
            if data:
                try:
                    img = BytesIO(data)
                    img = Image.open(img)
                    img = img.convert('RGB')
                    width, height = img.size
                    if height > 1080 or width > 1920:
                        img.thumbnail((1920, 1080))
                    buffer = BytesIO()
                    img.save(buffer, format="JPEG")
                    data = buffer.getvalue()
                except Exception as ex:
                    print(f"Could not decode image for evaluation: '{image}'.  Error: ", ex)
                return base64.b64encode(data).decode('utf-8')
        return None
