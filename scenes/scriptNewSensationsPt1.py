import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.helpers.dbhelper import db_conn


class NewSensationsPt1Spider(BaseSceneScraper):
    name = 'NewSensationsPt1'
    network = 'New Sensations'

    start_urls = [
        'https://www.newsensations.com'

        # Sites that are included in scrape, though site names aren't given for scraping
        # Here for reference so we don't double scrape:
        # -------------------------------
        # https://familyxxx.com
        # https://hotwifexxx.com
        # https://parodypass.com
        # https://stretchedoutsnatch.com
        # https://tabutales.com
        # https://talesfromtheedge.com
        # https://thelesbianexperience.com
        # https://girlgirlxxx.com/tour_girlgirlxxx/categories/movies_%s_d.html
        # https://www.hotwifexxx.com/tour_hwxxx/categories/movies_%s_d.html
        # https://familyxxx.com/tour_famxxx/categories/movies_%s_d.html
        # https://shanedieselxxx.com/tour_sdxxx/categories/movies_%s_d.html
        # https://freshoutofhighschool.com/tour_fohs/categories/movies_%s_d.html
        # https://www.newsensations.com/tour_ns/categories/movies_%s_d.html
        # https://unlimitedmilfs.com/tour_um/categories/movies_%s_d.html
    ]

    selector_map = {
        'title': '//div[@class="indScene" or @class="trailerMInfo"]/*[self::h1 or self::h2 or self::h3]/text()',
        'description': '//div[@class="description"]/span/following-sibling::h2/text()|//div[@class="videoDetails" or contains(@class,"indLeft")]//span[contains(text(), "escription:")]/following-sibling::text()[1]',
        'date': '//div[@class="sceneDateP"]/span/text()',
        'image': '//span[@id="trailer_thumb"]//img/@src',
        'image_blob': '//span[@id="trailer_thumb"]//img/@src',
        'performers': '//div[@class="sceneTextLink" or @class="trailerMInfo"]//span[@class="tour_update_models"]/a/text()',
        'tags': '//meta[@name="keywords"]/@content',
        'external_id': 'tour_ns\\/updates\\/(.+)\\.html',
        'trailer': '',
        'pagination': '/tour_ns/categories/movies_%s_d.html'
    }

    def start_requests(self):
        meta = {}
        meta['page'] = self.page
        meta['local'] = self.settings.get('local')
        url = self.settings.get('siteurl')
        if url:
            url = re.search(r'(.*?\.com)(/.*)', url)
            meta['sitelink'] = url.group(1)
            meta['pagination'] = url.group(2)

            yield scrapy.Request(url=self.get_next_page_url(meta['sitelink'], self.page, meta['pagination']), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)
        else:
            print("No Site URL/Pagination given, aborting")

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
                yield scrapy.Request(url=self.get_next_page_url(meta['sitelink'], meta['page'], meta['pagination']), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_next_page_url(self, base, page, pagination):
        return self.format_url(base, pagination % page)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="captions"]/h4/a/@href|//div[contains(@class,"movieBlock")]//h4/a/@href|//div[@class="update_details"]/a[1]/@href').getall()
        for scene in scenes:
            yield scrapy.Request(url=scene, callback=self.parse_scene, meta=meta)

    def get_date(self, response):
        # Check for standard
        scenedate = super().get_date(response)

        # Hotwife XXX
        if not scenedate:
            scenedate = response.xpath('//div[@class="trailerMInfo"]//div[contains(@class, "released")]/text()')
            if scenedate:
                scenedate = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', scenedate.get())
                if scenedate:
                    scenedate = self.parse_date(scenedate.group(1), date_formats=['%m/%d/%Y']).strftime('%Y-%m-%d')

        if scenedate:
            return scenedate
        else:
            return ''

    def get_duration(self, response):
        duration = None
        # Hotwife XXX
        duration = response.xpath('//div[@class="trailerMInfo"]//div[contains(@class, "released")]/text()')
        if not duration:
            # Girl Girl XXX
            duration = response.xpath('//div[@class="sceneDateP"]//text()[contains(., "min") or contains(., "Min")]')

        if duration:
            duration = re.sub(r'[^a-z0-9]+', '', duration.get().lower())
            duration = re.search(r'(\d+)min', duration)
            if duration:
                duration = str(int(duration.group(1)) * 60)

        if duration:
            return duration

        return None

    def get_site(self, response):
        if not isinstance(response, str):
            if self.get_selector_map('tags'):
                taglist = self.process_xpath(response, self.get_selector_map('tags')).get()
                taglist = taglist.replace(" ", "")
        else:
            taglist = response

        if "familyxxx" in taglist.lower():
            return "Family XXX"
        if "girlgirlxxx" in taglist.lower():
            return "Girl Girl XXX"
        if "freshouttahighschool" in taglist.lower():
            return "Fresh Outta High School"
        if "freshoutofhighschool" in taglist.lower():
            return "Fresh Outta High School"
        if "hotwifexxx" in taglist.lower():
            return "HotWifeXXX"
        if "shanedieselxxx" in taglist.lower():
            return "Shane Diesel XXX"

        return "New Sensations"

    def get_image(self, response):
        image = super().get_image(response)
        if image[-3:] == "%20":
            image = image[:-3]
        return image

    def get_tags(self, response):
        performers = super().get_performers(response)
        site = self.get_site(response).strip().title()

        tags = super().get_tags(response)
        if len(tags) == 1 and "," in tags[0]:
            tags = tags[0].split(',')
            tags = list(map(lambda x: x.strip().title(), tags))
            for performer in performers:
                if performer in tags:
                    tags.remove(performer)
            if "Movies" in tags:
                tags.remove("Movies")
            if "4K" in tags:
                tags.remove("4K")
            if "New Sensations" in tags:
                tags.remove("New Sensations")
            if site in tags:
                tags.remove(site)

        tags2 = tags.copy()
        tagremove = False
        for tag in tags2:
            for match in ['#', 'lovense', 'movie', 'new', 'vibemate', 'kiiro', 'feel', 'new sensation', 'shane diesel']:
                if match in tag.lower():
                    tagremove = True
            if tagremove:
                tags.remove(tag)

        return tags

    def get_id(self, response):
        sceneid = response.xpath('//comment()[contains(.,"data-id")]')
        if sceneid:
            return re.search(r'data-id=\"(\d+)\"', sceneid.get()).group(1)
        return None

    def parse_scene(self, response):
        meta = response.meta
        item = self.init_scene()

        item['title'] = self.get_title(response)
        item['description'] = self.get_description(response)
        item['description'] = item['description'].replace("\r", " ").replace("\n", " ").replace("\t", " ").replace("  ", " ")
        item['site'] = self.get_site(meta['sitelink'])
        item['date'] = self.get_date(response)

        if self.check_item(item, self.days):
            item['image'] = self.get_image(response)

            if 'image' not in item or not item['image']:
                item['image'] = None
                item['image_blob'] = None
            else:
                item['image_blob'] = self.get_image_blob_from_link(item['image'])

            if item['image']:
                if "?" in item['image'] and ("token" in item['image'].lower() or "expire" in item['image'].lower()):
                    item['image'] = re.search(r'(.*?)\?', item['image']).group(1)
        else:
            item['image'] = ''
            item['image_blob'] = ''

        item['performers'] = self.get_performers(response)
        item['tags'] = self.get_tags(response)
        item['id'] = self.get_id(response)
        item['trailer'] = self.get_trailer(response)
        item['duration'] = self.get_duration(response)
        item['url'] = self.get_url(response)
        item['network'] = "New Sensations"
        item['parent'] = "New Sensations"
        item['type'] = 'Scene'

        # ~ if not meta['local']:
        if self.check_newsens_cache(item):
            yield self.check_item(item, self.days)
        # ~ else:
            # ~ yield self.check_item(item, self.days)

    def check_newsens_cache(self, item):

        #######################################################
        # Check to see if the movie has already been submitted.  If so, no reason to pull the images or scenes
        conn, cursor = db_conn()
        submitscene = True
        hide_cache = self.settings.get('hide_cache')

        # First we check a Site/ID Combo
        cursor.execute("SELECT scene_id FROM nscache WHERE scene_id = %s AND scene_date = %s", (item['id'], item['date']))
        if cursor.rowcount:
            submitscene = False
            if not hide_cache:
                print(f"Not submitting due to Date/ID Combo in cache:  ID# {item['id']}  \"{item['title']}\"   \"{item['date']}\" for \"{item['site']}\"")

        else:
            cursor.execute("INSERT into nscache (scene_id, scene_title, scene_url, scene_date, scene_site) VALUES (%s, %s, %s, %s, %s) RETURNING scene_id", (item['id'], item['title'], item['url'], item['date'], item['site']))
            rows = cursor.fetchone()[0]
            if not rows:
                submitscene = False
                print(f"Not submitting due to INSERT failure into cache:  ID# {item['id']}  \"{item['title']}\" for \"{item['site']}\"")
            else:
                conn.commit()

        cursor.close()
        conn.close()
        return submitscene
