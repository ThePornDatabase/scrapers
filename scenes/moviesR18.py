import re
import html
import textwrap
import unidecode
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class MoviesR18Spider(BaseSceneScraper):
    name = 'R18Movies'
    network = 'R18'
    parent = 'R18'
    site = 'R18'

    start_urls = [
        'https://www.r18.com',
    ]

    custom_settings = {'AUTOTHROTTLE_ENABLED': 'True', 'AUTOTHROTTLE_DEBUG': 'False'}

    selector_map = {
        'external_id': '(\\d+)$',
        'pagination': '/videos/vod/movies/list/?page=%s'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//li[@class="item-list"]/@data-content_id').getall()
        for scene in scenes:
            scene = f"https://www.r18.com/api/v4f/contents/{scene.strip()}?lang=en&unit=USD"
            yield scrapy.Request(scene, callback=self.parse_scene, meta=meta)

    def parse_scene(self, response):
        jsondata = response.json()
        scene = jsondata['data']
        item = SceneItem()

        title = ''
        if scene['dvd_id']:
            item['id'] = scene['dvd_id'].upper().strip()
        else:
            item['id'] = scene['content_id'].upper().strip()

        if not title:
            title = self.cleanup_title(scene['title'])

        item['title'] = unidecode.unidecode(html.unescape(re.sub('<[^<]+?>', '', title)).strip())
        item['title'] = self.uncensor_title(item['title'])

        if len(item['title']) > 100:
            item['title'] = textwrap.wrap(item['title'], 100)[0] + "..."
        item['title'] = f"{self.cleanup_title(item['title'])} - {item['id']}"
        item['description'] = self.uncensor_title(scene['title'])
        if scene['release_date']:
            item['date'] = re.search(r'(\d{4}-\d{2}-\d{2})', scene['release_date']).group(1)
        else:
            item['date'] = self.parse_date('today').isoformat()

        images = scene['images']
        if "jacket_image" in images:
            images = images['jacket_image']

            item['back'] = None
            item['back_blob'] = None
            if 'medium' in images:
                item['back'] = images['medium']
            elif 'small' in images:
                item['back'] = images['small']
            else:
                item['back'] = None
            if item['back']:
                item['back_blob'] = self.get_image_blob_from_link(item['back'])
            else:
                item['back_blob'] = None

            item['image'] = None
            item['image_blob'] = None
            if 'large' in images:
                item['image'] = images['large']
            elif 'medium' in images:
                item['image'] = images['medium']
            if item['image']:
                item['image_blob'] = self.get_image_blob_from_link(item['image'])

        item['performers'] = []
        if scene['actresses']:
            for performer in scene['actresses']:
                item['performers'].append(self.cleanup_title(unidecode.unidecode(html.unescape(re.sub('<[^<]+?>', '', performer['name'])).strip())))

        item['tags'] = []
        if scene['categories']:
            for category in scene['categories']:
                item['tags'].append(self.cleanup_title(unidecode.unidecode(html.unescape(re.sub('<[^<]+?>', '', category['name'])).strip())))
        if "Asian" not in item['tags']:
            item['tags'].append("Asian")
        if "JAV" not in item['tags']:
            item['tags'].append("JAV")

        item['parent'] = "R18"
        item['site'] = "R18"
        if scene['maker']:
            if scene['maker']['name']:
                item['parent'] = scene['maker']['name']
                item['site'] = scene['maker']['name']

        item['network'] = 'R18'
        item['director'] = scene['director']
        item['format'] = "DVD/VOD"
        item['duration'] = str(int(scene['runtime_minutes']) * 60)
        item['sku'] = scene['content_id']
        if 'id' not in item:
            item['id'] = item['sku']
        item['url'] = f"https://www.r18.com/videos/vod/movies/detail/-/id={item['sku']}/"
        item['type'] = "JAV"

        item['trailer'] = None
        if scene['sample']:
            if "high" in scene['sample']:
                item['trailer'] = scene['sample']['high']
            elif "medium" in scene['sample']:
                item['trailer'] = scene['sample']['medium']
            elif "small" in scene['sample']:
                item['trailer'] = scene['sample']['small']

        yield self.check_item(item, self.days)

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
