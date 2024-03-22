import re
import string
import json
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class MoviesHotMoviesSpider(BaseSceneScraper):
    name = 'HotMovies'
    network = 'Hot Movies'

    start_urls = [
        'https://www.hotmovies.com/studio/2126/Den-Of-Iniquity/',
        'https://www.hotmovies.com/studio/1959/18teen/',
        'https://www.hotmovies.com/studio/3183/18-Wheeler/',
        'https://www.hotmovies.com/studio/4321/1726-Media/',
        'https://www.hotmovies.com/studio/3893/1257-MARGARET-MARY/',
        'https://www.hotmovies.com/studio/473/100-Brazil-Productions/',
        'https://www.hotmovies.com/studio/5559/100-Amateur/',
        'https://www.hotmovies.com/studio/5692/100-Africa/',
        'https://www.hotmovies.com/studio/5533/18VR/',
        'https://www.hotmovies.com/studio/523/2-Pop-Productions/',
        'https://www.hotmovies.com/studio/1893/3X-Film-Productions/',
        'https://www.hotmovies.com/studio/2631/3XL-Productions/',
        'https://www.hotmovies.com/studio/1610/4-You-Only-Entertainment/',
        'https://www.hotmovies.com/studio/1689/414extreme-com/',
        'https://www.hotmovies.com/studio/1307/42nd-Street-Pete-VOD/',
        'https://hotmovies.com/studio/2/4Reel-Productions/',
        'https://www.hotmovies.com/studio/3105/5-Points-Entertainment/',
        'https://www.hotmovies.com/studio/249/6666-Productions/',
        'https://www.hotmovies.com/studio/4333/7th-Street-Media/',
        'https://www.hotmovies.com/studio/3527/97-Amateurs/',
        'https://www.hotmovies.com/studio/2837/9th-Avenue-Exploitation/',
        'https://www.hotmovies.com/studio/59/A-Wizard-of-Ass/',
        'https://www.hotmovies.com/studio/3576/Aardvark-Video/',
        'https://www.hotmovies.com/studio/2032/abART/',
        'https://www.hotmovies.com/studio/352/Abbraxa-Productions/',
        'https://www.hotmovies.com/studio/3747/Abbsx/',
        'https://www.hotmovies.com/studio/662/AbleMale-Video/',
        'https://www.hotmovies.com/studio/1928/Absurdum-Productions/',
        'https://www.hotmovies.com/studio/3828/Academy-Wrestling/',
        'https://www.hotmovies.com/studio/1117/Access-Instructional-Media/',
        'https://www.hotmovies.com/studio/3261/Action-X-Shots/',
        'https://www.hotmovies.com/studio/4504/Addicted/',
        'https://www.hotmovies.com/studio/3176/Ado-Style/',
        'https://www.hotmovies.com/studio/1511/Adorable-Productions/',
        'https://hotmovies.com/studio/5836/Adreena-Winters/',
        'https://www.hotmovies.com/studio/1665/Adult-Players-Club/',
        'https://www.hotmovies.com/studio/2493/Adult-Power/',
        'https://www.hotmovies.com/studio/1441/AdultInternet-TV/',
        'https://www.hotmovies.com/studio/857/Adultz-Only/',
        'https://www.hotmovies.com/studio/1659/Advantage-Video-Norway/',
        'https://www.hotmovies.com/studio/4975/African-American/',
        'https://www.hotmovies.com/studio/5830/African-Porn-Movies/',
        'https://www.hotmovies.com/studio/5227/After-Dark-with-Nadia-White/',
        'https://www.hotmovies.com/studio/2667/AfterDark-Pictures/',
        'https://www.hotmovies.com/studio/557/Aftershock/',
        'https://www.hotmovies.com/studio/5856/Aglaea-Group/',
        'https://www.hotmovies.com/studio/138/AGV/',
        'https://www.hotmovies.com/studio/1906/Bijou-Classics/',
        'https://www.hotmovies.com/studio/1728/AlboGirls/',
        'https://www.hotmovies.com/studio/2382/Allusion-Studio/',
        'https://www.hotmovies.com/studio/4162/Alpha-Beta-Media/',
        'https://www.hotmovies.com/studio/3833/Alpine-Sierra-Studios/',
        'https://www.hotmovies.com/studio/3799/Alt-Porn-Network/',
        'https://www.hotmovies.com/studio/4196/Alesia-Pleasure-Entertainment/',
        'https://www.hotmovies.com/studio/702/Alibi-Entertainment/',
        'https://www.hotmovies.com/studio/3551/All-Asian-Access/',
        'https://www.hotmovies.com/studio/2424/All-Wet-Productions/',
        'https://www.hotmovies.com/studio/808/All-Amateursdvd-com/',
        'https://www.hotmovies.com/studio/3181/Amateur-Associates/',
        'https://www.hotmovies.com/studio/722/Amateur-Flix/',
        'https://www.hotmovies.com/studio/5956/Amateur-Spankings/',
        'https://www.hotmovies.com/studio/1064/Amateur-Straight-Guys/',
        'https://www.hotmovies.com/studio/2553/AmateurBound-com/',
        'https://www.hotmovies.com/studio/201/AmateurNewGirls/',
        'https://www.hotmovies.com/studio/3611/AmateurUpskirts-com/',
        'https://www.hotmovies.com/studio/1007/Amazing-Scandinavian-Studios/',
        'https://www.hotmovies.com/studio/2474/Amazon-Digital/',
        'https://www.hotmovies.com/studio/3035/Amber-Love-Productions/',
        'https://www.hotmovies.com/studio/5517/Amber-Michaels-Productions/',
        'https://www.hotmovies.com/studio/2471/American-Stripper/',
        'https://www.hotmovies.com/studio/1224/Ammo-Dump-Pictures/',
        'https://www.hotmovies.com/studio/1957/Amor-Ardiente/',
        'https://www.hotmovies.com/studio/1086/AMX-Video/',
        'https://www.hotmovies.com/studio/3179/Ana-Nova-Productions/',
        'https://www.hotmovies.com/studio/3859/Anal-File-Repository/',
        'https://www.hotmovies.com/studio/1181/Anal-Titans/',
        'https://www.hotmovies.com/studio/5177/Anatomik-Media/',
        'https://www.hotmovies.com/studio/3381/AndreaContent/',
        'https://www.hotmovies.com/studio/2608/Andrej-Bass/',
        'https://www.hotmovies.com/studio/1545/Andrew-Ward-TV-Productions/',
        'https://www.hotmovies.com/studio/2103/Androgeny-Productions/',
        'https://www.hotmovies.com/studio/2099/Ange-Venus-Productions/',
        'https://www.hotmovies.com/studio/4578/Angela-White/',
        'https://www.hotmovies.com/studio/790/Angelini-Media-Ltd-/',
        'https://www.hotmovies.com/studio/2528/Angelmania/',
        'https://www.hotmovies.com/studio/3631/Anna-Devia-Productions/',
        'https://www.hotmovies.com/studio/951/Anna-Span-s-Diary/',
        'https://www.hotmovies.com/studio/800/C-S-G-Entertainment/',
        'https://www.hotmovies.com/studio/3075/Antigua-Classics/',
        'https://hotmovies.com/studio/690/Anton-Productions/',
        'https://www.hotmovies.com/studio/6249/Anton-Video/',
        'https://www.hotmovies.com/studio/3297/Aphrotis/',
        'https://www.hotmovies.com/studio/580/Azure-Entertainment/',
        'https://www.hotmovies.com/studio/3234/Aziani-Studios/',
        'https://www.hotmovies.com/studio/3935/Awesome-Snookie/',
        'https://www.hotmovies.com/studio/2571/AVN-Media-Network/',
        'https://www.hotmovies.com/studio/795/AVBox-Inc-/',
        'https://www.hotmovies.com/studio/1512/Avalon-Productions/',
        'https://www.hotmovies.com/studio/801/Authentic-Extreme-Reality/',
        'https://www.hotmovies.com/studio/1890/ATV-Entertainment/',
        'https://www.hotmovies.com/studio/1031/Atom-Xstacy-Productions/',
        'https://www.hotmovies.com/studio/1611/Atlantis-Video/',
        'https://www.hotmovies.com/studio/1544/AtlantaEroticVideos/',
        'https://www.hotmovies.com/studio/3727/Atl-Bad-Boy-com/',
        'https://www.hotmovies.com/studio/1764/ATF-Entertainment/',
        'https://www.hotmovies.com/studio/3959/At-Home-Horny-Productions/',
        'https://www.hotmovies.com/studio/358/Astrux-Entertainment/',
        'https://www.hotmovies.com/studio/4732/Astral-Blue/',
        'https://www.hotmovies.com/studio/4496/Assylum-com/',
        'https://www.hotmovies.com/studio/3208/AssWorshipMovies-com/',
        'https://www.hotmovies.com/studio/837/Asphyxiation-Films/',
        'https://www.hotmovies.com/studio/2647/Asian-Torture/',
        'https://www.hotmovies.com/studio/2828/Asian-SM/',
        'https://www.hotmovies.com/studio/1361/Asian-Shemales-XXX/',
        'https://www.hotmovies.com/studio/3897/Asian-Sex-Addicts/',
        'https://www.hotmovies.com/studio/3647/Asian-Sex/',
        'https://www.hotmovies.com/studio/3772/Asian-Queen/',
        'https://www.hotmovies.com/studio/1424/Asian-Productions/',
        'https://www.hotmovies.com/studio/3648/Asian-Lesbian/',
        'https://www.hotmovies.com/studio/3692/Asian-Foot/',
        'https://www.hotmovies.com/studio/3870/Asian-Fetish/',
        'https://www.hotmovies.com/studio/2719/Asian-Candy-Shop/',
        'https://www.hotmovies.com/studio/3649/Asian-Bondage/',
        'https://www.hotmovies.com/studio/1745/Asian-Beauty/',
        'https://www.hotmovies.com/studio/1035/Asia-Diva/',
        'https://www.hotmovies.com/studio/2930/ArteCom/',
        'https://www.hotmovies.com/studio/2229/Arrogant-Entertainment/',
        'https://www.hotmovies.com/studio/4650/Armand-Studio/',
        'https://www.hotmovies.com/studio/1242/Armageddon-Entertainment/',
        'https://www.hotmovies.com/studio/742/ArielsFantasies-com/',
        'https://www.hotmovies.com/studio/1156/Ari-Productions/',
        'https://www.hotmovies.com/studio/3406/Argentina-Triple-X/',
        '',
        '',
        '',
        '',
        '',
        '',
        '',
        '',
        '',
        '',
        '',
        '',
        '',
        '',
        '',
        '',
        '',
        '',
        '',
        '',
        '',
        '',
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'duration': '',
        'trailer': '',
        'external_id': r'',
        'pagination': '/new_release.php?page=%s'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="cell movie_box"]/div[1]/div/h3[contains(@class, "title")]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                scene = scene + "?my_scene_info=more"
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def parse_scene(self, response):
        jsondata = json.loads(response.xpath('//script[contains(@type,"ld+json")]/text()').get())
        movie = SceneItem()

        movie['title'] = self.cleanup_title(jsondata['name'])
        movie['description'] = jsondata['description']
        movie['image'] = jsondata['image']
        movie['image_blob'] = self.get_image_blob_from_link(movie['image'])
        movie['back'] = response.xpath('//div[@class="lg_inside_wrap"]/@data-back').get()
        movie['back_blob'] = self.get_image_blob_from_link(movie['back'])
        movie['trailer'] = jsondata['trailer']['embedUrl']
        movie['type'] = 'Movie'
        movie['duration'] = self.convert_duration(jsondata['duration'])
        if jsondata['copyrightYear']:
            movie['date'] = self.parse_date(self.convert_date(jsondata['dateCreated'], jsondata['copyrightYear'])).isoformat()
        else:
            movie['date'] = self.parse_date(jsondata['dateCreated']).isoformat()
        movie['director'] = ''
        if "keywords" in jsondata:
            if "," in jsondata['keywords']:
                movie['tags'] = jsondata['keywords'].split(",")
            else:
                movie['tags'] = jsondata['keywords']
        else:
            movie['tags'] = []
        movie['tags'] = self.cleantags(movie['tags'])
        movie['performers'] = []
        for performer in jsondata['actor']:
            movie['performers'].append(performer['name'])
        movie['id'] = re.search(r'video/(\d+)/', response.url).group(1)
        site = jsondata['productionCompany']['name']
        if ".com" in site.lower():
            site = site.lower()
            site = re.search(r'^(.*?)\.com', site).group(1)
            site = self.cleanup_title(site)
        movie['site'] = site
        movie['parent'] = site
        movie['network'] = "Hot Movies"
        movie['url'] = response.url
        movie['scenes'] = []

        scenes = response.xpath('//div[@class="scenes section"]//div[@id="results"]/div[contains(@class, "scene_cell")]')
        scenecount = 1
        if len(scenes) > 1:
            for scene in scenes:
                item = SceneItem()

                item['title'] = movie['title'] + f" - Scene {scenecount}"
                item['url'] = response.url
                item['description'] = movie['description']
                item['id'] = scene.xpath('./@id').get()
                movie['scenes'].append({'site': movie['site'], 'external_id': item['id']})
                item['site'] = movie['site']
                item['parent'] = movie['parent']
                item['network'] = movie['network']
                item['date'] = movie['date']
                item['image'] = scene.xpath('.//div[@class="swiper-wrapper"]/div[1]/a/img/@src').get()
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
                item['trailer'] = movie['trailer']
                item['director'] = ''
                scenestart = int(self.duration_to_seconds(scene.xpath('.//button[@class="buy_this_scene_responsive"]/@data-start').get()))
                sceneend = int(self.duration_to_seconds(scene.xpath('.//button[@class="buy_this_scene_responsive"]/@data-stop').get()))
                item['duration'] = str(sceneend - scenestart)
                performers = scene.xpath('.//strong[contains(text(), "Stars")]/following-sibling::a/text()')
                if performers:
                    item['performers'] = list(map(lambda x: string.capwords(x.strip()).replace(" (Trans)", ""), performers.getall()))
                else:
                    item['performers'] = []
                item['tags'] = self.cleantags(scene.xpath('.//span[@class="list_attributes"]/a/text()').getall())
                item['type'] = "Scene"
                scenecount = scenecount + 1
                yield self.check_item(item, self.days)

            yield self.check_item(movie, self.days)

    def convert_duration(self, duration):
        if "PT" in duration:
            if "H" in duration:
                duration = re.search(r'(\d{1,2})H(\d{1,2})M(\d{1,2})S', duration)
                hours = int(duration.group(1)) * 3600
                minutes = int(duration.group(2)) * 60
                seconds = int(duration.group(3))
                duration = str(hours + minutes + seconds)
            else:
                duration = re.search(r'(\d{1,2})M(\d{1,2})S', duration)
                minutes = int(duration.group(1)) * 60
                seconds = int(duration.group(2))
                duration = str(hours + minutes + seconds)
            return duration
        return ''

    def convert_date(self, created, year):
        created_year = re.search(r'(\d{4})-', created).group(1)
        if int(year) < int(created_year):
            return year + "-01-01"
        return created

    def cleantags(self, taglist):
        tags = []
        for tag in taglist:
            tag = tag.lower()
            if "/" in tag:
                tag = re.search(r'(.*)/', tag).group(1)
            if "masturbation" in tag:
                tag = "masturbation"
            if "undressing" in tag:
                tag = "undressing"
            if "spooning" in tag:
                tag = "spooning"
            if "standing" in tag:
                tag = "standing sex"
            if "cowgirl" in tag:
                tag = "cowgirl"
            if "doggy" in tag:
                tag = "doggystyle"
            if "tribbing" in tag:
                tag = "tribbing"
            if "rimming" in tag:
                tag = "rimming"
            if "cunnilingus" in tag:
                tag = "cunnilingus"
            if "anal creampie" in tag:
                tag = "Anal Creampie"
            if "creampie" in tag:
                tag = "creampie"
            if "deep throating" in tag:
                tag = "deepthroat"
            if "anal" in tag:
                tag = "anal"
            tags.append(self.cleanup_title(tag).strip())
        return tags
