import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteJavDatabaseSpider(BaseSceneScraper):
    name = 'JavDatabase'
    network = 'JavDatabase'

    start_urls = [
        'https://www.javdatabase.com',
    ]

    selector_map = {
        'title': '//header[@class="entry-header"]/h1/text()',
        'description': '',
        'date': '//b[contains(text(), "Release Date:")]/../following-sibling::td[1]/text()|//b[contains(text(), "Release Date:")]/following-sibling::text()',
        'image': '//meta[@property="og:image"]/@content|//meta[@name="twitter:image"]/@content',
        'performers': '//b[contains(text(), "Actress")]/following-sibling::span[1]/a/text()',
        'tags': '//td[@class="tablevalue"]/span/a[contains(@href, "genres")]/text()|//b[contains(text(), "Genre")]/following-sibling::span/a[contains(@href, "genres")]/text()',
        'director': '//b[contains(text(), "Director:")]/following-sibling::span[1]/a/text()',
        'trailer': '',
        'external_id': r'.*/(.*?)/',
        'pagination': '/movies/page/%s/',
        'type': 'JAV',
    }

    def start_requests(self):
        meta = {}
        meta['page'] = self.page
        if self.limit_pages == 1:
            self.limit_pages = 10

        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, self.page), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="movie-cover-thumb"]/a[contains(@href, "javdatabase")]/@href').getall()
        for scene in scenes:
            meta['id'] = re.search(r'.*/(.*?)/', scene).group(1).upper()
            if meta['id']:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_duration(self, response):
        duration = response.xpath('//b[contains(text(), "Runtime:")]/../following-sibling::td[1]/text()|//b[contains(text(), "Runtime:")]/following-sibling::text()')
        if duration:
            duration = duration.get()
            duration = re.sub(r'[^a-z0-9]', '', duration.lower())
            duration = re.search(r'(\d+)min', duration)
            if duration:
                return str(int(duration.group(1)) * 60)
        return None

    def get_site(self, response):
        site = response.xpath('//b[contains(text(), "Studio:")]/../following-sibling::td[1]/span/a/text()|//b[contains(text(), "Studio:")]/following-sibling::span//text()')
        if site:
            return site.get()
        return "Studio Unknown"

    def get_parent(self, response):
        return super().get_site(response)

    def get_tags(self, response):
        tags = super().get_tags(response)
        tags2 = []
        matches = ['hours', 'hi-def', 'exclusive', 'featured']
        for tag in tags:
            tag = tag.lower()
            if not any(x in tag for x in matches):
                tags2.append(string.capwords(tag))
        return tags2

    def get_id(self, response):
        javid = super().get_id(response)
        return javid.upper()

    def get_title(self, response):
        title = super().get_title(response)
        if len(title) > 240:
            title = title[:240] + "..."
            print(f"*** Title truncated to: {title}")
        return self.uncensor_title(title)

    def uncensor_title(self, title):
        title = title.replace("A*****t", "Assault")
        title = title.replace("A****p", "Asleep")
        title = title.replace("A***e", "Abuse")
        title = title.replace("B***d", "Blood")
        title = title.replace("B**d", "Bled")
        title = title.replace("C***d", "Child")
        title = title.replace("C*ck", "Cock")
        title = title.replace("D******e", "Disgrace")
        title = title.replace("D***king", "Drinking")
        title = title.replace("D***k", "Drunk")
        title = title.replace("D**g", "Drug")
        title = title.replace("F*****g", "Forcing")
        title = title.replace("F***e", "Force")
        title = title.replace("G*******g", "Gangbang")
        title = title.replace("G******g", "Gang Bang")
        title = title.replace("H*********n", "Humiliation")
        title = title.replace("H*******e", "Hypnotize")
        title = title.replace("H*******m", "Hypnotism")
        title = title.replace("H**t", "Hurt")
        title = title.replace("I****t", "Incest")
        title = title.replace("K****p", "Kidnap")
        title = title.replace("K****r", "Killer")
        title = title.replace("K**l", "Kill")
        title = title.replace("K*d", "Kid")
        title = title.replace("L****a", "Lolita")
        title = title.replace("M************n", "Mother And Son")
        title = title.replace("M****t", "Molest")
        title = title.replace("P********t", "Passed Out")
        title = title.replace("P****h", "Punish")
        title = title.replace("R****g", "Raping")
        title = title.replace("R**e", "Rape")
        title = title.replace("RStepB****************r", "Stepbrother and Sister")
        title = title.replace("S*********l", "School Girl")
        title = title.replace("S**********s", "School Girls")
        title = title.replace("S********l", "Schoolgirl")
        title = title.replace("S*********s", "Schoolgirls")
        title = title.replace("S******g", "Sleeping")
        title = title.replace("S*****t", "Student")
        title = title.replace("S***e", "Slave")
        title = title.replace("S**t", "Scat")
        title = title.replace("Sch**l", "School")
        title = title.replace("StepM************n", "Stepmother and Son")
        title = title.replace("T******e", "Tentacle")
        title = title.replace("T*****e", "Torture")
        title = title.replace("U*********s", "Unconscious")
        title = title.replace("V*****e", "Violate")
        title = title.replace("V*****t", "Violent")
        title = title.replace("Y********l", "Young Girl")
        title = title.replace("A*****t", "Assault")
        title = title.replace("a*****t", "assault")
        title = title.replace("a****p", "asleep")
        title = title.replace("a***e", "abuse")
        title = title.replace("b***d", "blood")
        title = title.replace("b**d", "bled")
        title = title.replace("c***d", "child")
        title = title.replace("c*ck", "cock")
        title = title.replace("d******e", "disgrace")
        title = title.replace("d***king", "drinking")
        title = title.replace("d***k", "drunk")
        title = title.replace("d**g", "drug")
        title = title.replace("f*****g", "forcing")
        title = title.replace("f***e", "force")
        title = title.replace("g*******g", "gangbang")
        title = title.replace("g******g", "gang bang")
        title = title.replace("h*********n", "humiliation")
        title = title.replace("h*******e", "hypnotize")
        title = title.replace("h*******m", "hypnotism")
        title = title.replace("h**t", "hurt")
        title = title.replace("i****t", "incest")
        title = title.replace("k****p", "kidnap")
        title = title.replace("k****r", "killer")
        title = title.replace("k**l", "kill")
        title = title.replace("k*d", "kid")
        title = title.replace("l****a", "lolita")
        title = title.replace("m************n", "mother and son")
        title = title.replace("m****t", "molest")
        title = title.replace("p********t", "passed out")
        title = title.replace("p****h", "punish")
        title = title.replace("r****g", "raping")
        title = title.replace("r**e", "rape")
        title = title.replace("rstepb****************r", "stepbrother and sister")
        title = title.replace("s*********l", "school girl")
        title = title.replace("s********l", "schoolgirl")
        title = title.replace("s**********s", "school girls")
        title = title.replace("s*********s", "schoolgirls")
        title = title.replace("s******g", "sleeping")
        title = title.replace("s*****t", "student")
        title = title.replace("s***e", "slave")
        title = title.replace("s**t", "scat")
        title = title.replace("sch**l", "school")
        title = title.replace("stepm************n", "stepmother and son")
        title = title.replace("t******e", "tentacle")
        title = title.replace("t*****e", "torture")
        title = title.replace("u*********s", "unconscious")
        title = title.replace("v*****e", "violate")
        title = title.replace("v*****t", "violent")
        title = title.replace("y********l", "young girl")

        return title

    def get_performers_data(self, response):
        performers = self.get_performers(response)
        performers_data = []
        if len(performers):
            for performer in performers:
                perf = {}
                perf['name'] = performer
                perf['extra'] = {}
                perf['extra']['gender'] = "Female"
                perf['network'] = "JavDatabase"
                perf['site'] = self.get_site(response)
                performers_data.append(perf)
        return performers_data

    def get_image(self, response):
        image = super().get_image(response)
        # ~ print(image)
        return image

    def parse_scene(self, response):
        item = self.init_scene()

        if 'title' in response.meta and response.meta['title']:
            item['title'] = response.meta['title']
        else:
            item['title'] = self.get_title(response)

        if 'description' in response.meta:
            item['description'] = response.meta['description']
        else:
            item['description'] = self.get_description(response)

        if hasattr(self, 'site'):
            item['site'] = self.site
        elif 'site' in response.meta:
            item['site'] = response.meta['site']
        else:
            item['site'] = self.get_site(response)

        if 'date' in response.meta:
            item['date'] = response.meta['date']
        else:
            item['date'] = self.get_date(response)

        if 'image' in response.meta:
            item['image'] = response.meta['image']
        else:
            item['image'] = self.get_image(response)

        if 'image' not in item or not item['image']:
            item['image'] = None

        if 'image_blob' in response.meta:
            item['image_blob'] = response.meta['image_blob']
        else:
            item['image_blob'] = self.get_image_blob(response)

        if ('image_blob' not in item or not item['image_blob']) and item['image']:
            item['image_blob'] = self.get_image_blob_from_link(item['image'])

        if 'image_blob' not in item:
            item['image_blob'] = None

        if item['image']:
            if "?" in item['image'] and ("token" in item['image'].lower() or "expire" in item['image'].lower()):
                item['image'] = re.search(r'(.*?)\?', item['image']).group(1)

        if 'performers' in response.meta:
            item['performers'] = response.meta['performers']
        else:
            item['performers'] = self.get_performers(response)

        if 'performers_data' in response.meta:
            item['performers_data'] = response.meta['performers_data']
        else:
            item['performers_data'] = self.get_performers_data(response)

        if 'tags' in response.meta:
            item['tags'] = response.meta['tags']
        else:
            item['tags'] = self.get_tags(response)

        if 'markers' in response.meta:
            item['markers'] = response.meta['markers']
        else:
            item['markers'] = self.get_markers(response)

        if 'id' in response.meta:
            item['id'] = response.meta['id']
        else:
            item['id'] = self.get_id(response)

        if 'merge_id' in response.meta:
            item['merge_id'] = response.meta['merge_id']
        else:
            item['merge_id'] = self.get_merge_id(response)

        if 'trailer' in response.meta:
            item['trailer'] = response.meta['trailer']
        else:
            item['trailer'] = self.get_trailer(response)

        if 'duration' in response.meta:
            item['duration'] = response.meta['duration']
        else:
            item['duration'] = self.get_duration(response)

        if 'url' in response.meta:
            item['url'] = response.meta['url']
        else:
            item['url'] = self.get_url(response)

        if hasattr(self, 'network'):
            item['network'] = self.network
        elif 'network' in response.meta:
            item['network'] = response.meta['network']
        else:
            item['network'] = self.get_network(response)

        if hasattr(self, 'parent'):
            item['parent'] = self.parent
        elif 'parent' in response.meta:
            item['parent'] = response.meta['parent']
        else:
            item['parent'] = self.get_parent(response)

        # Movie Items

        if 'store' in response.meta:
            item['store'] = response.meta['store']
        else:
            item['store'] = self.get_store(response)

        if 'director' in response.meta:
            item['director'] = response.meta['director']
        else:
            item['director'] = self.get_director(response)

        if 'format' in response.meta:
            item['format'] = response.meta['format']
        else:
            item['format'] = self.get_format(response)

        if 'back' in response.meta:
            item['back'] = response.meta['back']
        else:
            item['back'] = self.get_back_image(response)

        if 'back' not in item or not item['back']:
            item['back'] = None
            item['back_blob'] = None
        else:
            if 'back_blob' in response.meta:
                item['back_blob'] = response.meta['back_blob']
            else:
                item['back_blob'] = self.get_image_back_blob(response)

            if ('back_blob' not in item or not item['back_blob']) and item['back']:
                item['back_blob'] = self.get_image_from_link(item['back'])

        if 'back_blob' not in item:
            item['back_blob'] = None

        if 'sku' in response.meta:
            item['sku'] = response.meta['sku']
        else:
            item['sku'] = self.get_sku(response)

        if hasattr(self, 'type'):
            item['type'] = self.type
        elif 'type' in response.meta:
            item['type'] = response.meta['type']
        elif 'type' in self.get_selector_map():
            item['type'] = self.get_selector_map('type')
        else:
            item['type'] = 'Scene'

        yield item
