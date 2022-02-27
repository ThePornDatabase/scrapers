import re
from datetime import date, timedelta
import string
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class NetworkXSiteAbilitySpider(BaseSceneScraper):
    name = 'XSiteAbility'
    network = 'XSiteAbility'

    start_urls = [
        ['https://rachel-steele.com', '/x-new/new-preview-list.php?page=%s&user=rachel-steele', 'Rachel Steele'],
        ['https://4tomiko.com', '/x-new/new-preview-list.php?page=%s&user=4tomiko.com', '4Tomiko'],
        ['https://sandrasilvers.com', '/x-new/new-preview-list.php?page=%s&user=', 'Sandra Silvers'],
        ['https://officeperils.com', '/x-new/new-preview-list.php?page=%s&user=officeperils.com', 'Office Perils'],
        ['https://gndbondage.com', '/x-new/new-preview-list.php?page=%s&user=gndbondage.com', 'Girls Next Door Bondage'],
        ['https://sereneisley.com', '/x-new/new-preview-list.php?page=%s&user=sereneisley.com', 'Serene Isley'],
        ['https://www.nyxonsbondagefiles.com', '/x-new/new-preview-list.php?page=%s&user=nyxonsbondagefiles', 'Nyxons Bondage Files'],
        ['https://xsiteability.com', '/x-new/new-preview-list.php?page=%s&user=bedroombondage', 'Loreleis Bedroom Bondage'],
        ['https://milfgigi.com', '/x-new/new-preview-list.php?page=%s&user=milfgigi.com', 'MILF Gigi'],
        ['https://brendasbound.com', '/x-new/new-preview-list.php?page=%s&user=brendasbound.com', 'Brendas Bound'],
        ['https://misswhitneymorgan.com', '/x-new/new-preview-list.php?page=%s&user=misswhitneymorgan.com', 'Miss Whitney Morgan'],
        ['https://leagueofamazingwomen.com', '/x-new/new-preview-list.php?page=%s&user=leagueofamazingwomen.com', 'League of Amazing Women'],
        ['https://maidensinmayhem.com', '/x-new/new-preview-list.php?page=%s&user=maidensinmayhem.com', 'Maidens in Mayhem'],
        ['https://lewrubens.com', '/x-new/new-preview-list.php?page=%s&user=lewrubens.com', 'Lew Rubens'],
        ['https://jimhunterslair.com', '/x-new/new-preview-list.php?page=%s&user=jimhunterslair.com', 'Jim Hunters Lair'],
        ['https://laurenkiley.com', '/x-new/new-preview-list.php?page=%s&user=laurenkiley.com', 'Lauren Kiley'],
        ['https://ivanboulder.com', '/x-new/new-preview-list.php?page=%s&user=ivanboulder.com', 'Ivan Boulder'],
        ['https://cinchedandsecured.com', '/x-new/new-preview-list.php?page=%s&user=cinchedandsecured.com', 'Cinched and Secured'],
        ['https://tiedinheels.com', '/x-new/new-preview-list.php?page=%s&user=tiedinheels.com', 'Tied in Heels'],
        ['https://faythonfire.com', '/x-new/new-preview-list.php?page=%s&user=faythonfire.com', 'Fayth on Fire'],
        ['https://sydneyscreams4u.com', '/x-new/new-preview-list.php?page=%s&user=sydneyscreams4u.com', 'Sydney Screams 4U'],
        ['https://ogres-world.com', '/x-new/new-preview-list.php?page=%s&user=ogres-world.com', 'Vivienne Velvet'],
        ['https://jackiebound.com', '/x-new/new-preview-list.php?page=%s&user=jackiebound.com', 'Jackie Bound'],
        ['https://christinasapphire.com', '/x-new/new-preview-list.php?page=%s&user=christinasapphire.com', 'Christina Sapphire'],
        ['https://captivechrissymarie.com', '/x-new/new-preview-list.php?page=%s&user=captivechrissymarie.com', 'Captive Chrissy Marie'],
        ['https://xsiteability.com', '/x-new/new-preview-list.php?page=%s&user=kaeciejames', 'Kaecie James'],
        ['https://desperatepleasures.com', '/x-new/new-preview-list.php?page=%s&user=desperatepleasures.com', 'Desperate Pleasures'],
        ['https://ajmarion.com', '/x-new/new-preview-list.php?page=%s&user=ajmarion.com', 'AJ Marion'],
        ['https://leggybondage.com', '/x-new/new-preview-list.php?page=%s&user=leggybondage.com', 'Leggy Bondage'],
        ['https://bbwbound.com', '/x-new/new-preview-list.php?page=%s&user=bbwbound.com', 'BBW Bound'],
        ['https://www.oldschoolbondage.com', '/x-new/new-preview-list.php?page=%s&user=www.oldschoolbondage.com', 'Old School Bondage'],
        ['https://hosednhelpless.com', '/x-new/new-preview-list.php?page=%s&user=hosednhelpless.com', 'Hosed and Helpless'],
        ['https://dpstonefetish.com', '/x-new/new-preview-list.php?page=%s&user=dpstonefetish.com', 'DP Stone Fetish'],
        ['https://www.caroline-pierce.com', '/x-new/new-preview-list.php?page=%s&user=www.caroline-pierce.com', 'Caroline Pierce'],
        ['https://collegecaptures.com', '/x-new/new-preview-list.php?page=%s&user=collegecaptures.com', 'College Captures'],
        ['https://lynnwinters.com', '/x-new/new-preview-list.php?page=%s&user=lynnwinters.com', 'Lynn Winters'],
        ['https://thelunadawn.com', '/x-new/new-preview-list.php?page=%s&user=thelunadawn.com', 'Luna Dawn'],
        ['https://bondagedownsouth.com', '/x-new/new-preview-list.php?page=%s&user=bondagedownsouth.com', 'Bondage Down South'],
        ['https://lisaharlotte.com', '/x-new/new-preview-list.php?page=%s&user=lisaharlotte.com', 'Lisa Harlotte'],
        ['https://wrappedinbondage.com', '/x-new/new-preview-list.php?page=%s&user=wrappedinbondage.com', 'Wrapped in Bondage'],
        ['https://ticklerotic.com', '/x-new/new-preview-list.php?page=%s&user=ticklerotic.com', 'Ticklerotic'],
        ['https://bondagecrossdresser.com', '/x-new/new-preview-list.php?page=%s&user=bondagecrossdresser.com', 'Bondage Crossdresser'],
        ['https://stellalibertyvideos.com', '/x-new/new-preview-list.php?page=%s&user=stellalibertyvideos.com', 'Stella Liberty'],
    ]

    selector_map = {
        'title': '//div[@class="title clear"]/h2/text()',
        'description': '//span[contains(@class,"description")]/text()',
        'date': '//span[contains(@class,"update_date")]/text()',
        'image': '//span[@class="model_update_thumb"]/img/@src',
        'performers': '//span[@class="tour_update_models"]/a/text()',
        'tags': '//span[@class="update_tags"]/a/text()',
        'external_id': r'updates\/(.*).html',
        'trailer': '',
        'pagination': '/categories/movies_%s_d.html#'
    }

    def start_requests(self):
        for link in self.start_urls:
            meta = {}
            meta['page'] = self.page
            meta['pagination'] = link[1]
            meta['site'] = link[2]
            yield scrapy.Request(url=self.get_next_page_url(link[0], self.page, link[1]),
                                 callback=self.parse,
                                 meta=meta,
                                 headers=self.headers,
                                 cookies=self.cookies)

    def parse(self, response):
        meta = response.meta
        scenes = self.get_scenes(response)
        count = 0
        for scene in scenes:
            count += 1
            yield scene
        if count:
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                meta['page'] = meta['page'] + 1
                pagination = meta['pagination']
                print('NEXT PAGE: ' + str(meta['page']))
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page'], pagination),
                                     callback=self.parse,
                                     meta=meta,
                                     headers=self.headers,
                                     cookies=self.cookies)

    def get_next_page_url(self, base, page, pagination):
        return self.format_url(base, pagination % page)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//li[contains(@class,"first")]')
        for scene in scenes:
            item = SceneItem()

            url = scene.xpath('./a/@href')
            if url:
                url = url.get()
                item['url'] = self.format_link(response, url)
            else:
                item['url'] = ''

            title = scene.xpath('.//h3/text()')
            if title:
                title = title.get()
                title = title.replace("*", "")
                item['title'] = string.capwords(title.strip())
            else:
                title = re.search(r'(setid=\d+)', item['url']).group(1)
                item['title'] = title.replace('=', ' ').title()
            item['title'] = self.cleanup_title(item['title'])

            image = scene.xpath('.//img/@src')
            if image:
                image = image.get().replace(" ", "%20")
                item['image'] = self.format_link(response, image.strip())
                item['id'] = re.search(r'.*/(.*)\.', item['image']).group(1)
                item['id'] = item['id'].replace("_tn", "").replace('%20', '')
                item['id'] = re.sub(r'[^a-zA-Z0-9-]', '', item['id'])
            else:
                item['image'] = None
                item['id'] = None

            item['image_blob'] = None

            if meta['site'] == "Brendas Bound":
                description = scene.xpath('.//span[contains(@style,"font-size: medium;")]/em/text()')
            else:
                description = scene.xpath('./a/div/p//text()')
            if description:
                description = description.getall()
                item['description'] = " ".join(description).replace('\xa0', '').strip()
                item['description'] = re.sub(r'\d{1,3} photos', '', item['description'], flags=re.IGNORECASE)
                item['description'] = re.sub(r'\d{1,3}:\d{1,3} video', '', item['description'], flags=re.IGNORECASE)
                item['description'] = re.sub('  ', ' ', item['description'])
                item['description'] = self.cleanup_description(item['description'])
            else:
                item['description'] = ''

            scenedate = re.search(r' (\w+ \d{1,2}, \d{4}) ', item['description'])
            if not scenedate:
                scenedate = re.search(r'(\d{2}\.\d{2}\.\d{2})', item['description'])

            if scenedate:
                item['date'] = self.parse_date(scenedate.group(1).strip()).isoformat()
            else:
                item['date'] = self.parse_date('today').isoformat()
            item['performers'] = self.site_performers(scene, meta)
            item['tags'] = self.site_tags(scene, meta)
            item['trailer'] = ''
            item['site'] = meta['site']
            item['parent'] = meta['site']
            item['network'] = 'XSiteAbility'

            if item['id']:
                days = int(self.days)
                if days > 27375:
                    filterdate = "0000-00-00"
                else:
                    filterdate = date.today() - timedelta(days)
                    filterdate = filterdate.strftime('%Y-%m-%d')

                if self.debug:
                    if not item['date'] > filterdate:
                        item['filtered'] = "Scene filtered due to date restraint"
                    print(item)
                else:
                    if filterdate:
                        if item['date'] > filterdate:
                            yield item
                    else:
                        yield item

    def site_performers(self, scene, meta):
        performers = []

        title = scene.xpath('.//h3/text()')
        if title:
            title = title.get().strip()
        else:
            title = ''

        if meta['site'] == "Ivan Boulder":
            if title:
                if ":" in title:
                    performer = re.sub(r':.*', '', title)
                    performer = performer.replace("&", ",")
                    performers = performer.split(",")

        if meta['site'] == "Girls Next Door Bondage":
            performer = scene.xpath('.//span[contains(@style, "color: #ff0000;")]/span/text()')
            if performer:
                performer = re.sub(r' as .*', '', performer.get())
                performers.append(performer)

        if meta['site'] == "Jim Hunters Lair":
            performer = scene.xpath('.//p/span[contains(@style,"font-size: small;")]/strong[contains(text(),"~")]/text()')
            if performer:
                performer = performer.get()
                performer = performer.lower().replace("~", "").replace("with", ",").strip()
                performers = performer.split(",")

        if meta['site'] == "Rachel Steele":
            performers.append('Rachel Steele')

        if meta['site'] == "Vivienne Velvet":
            performers.append('Vivienne Velvet')

        if meta['site'] == "Fayth on Fire":
            performers.append('Fayth on Fire')

        if meta['site'] == "Kaecie James":
            performers.append('Kaecie James')

        if meta['site'] == "Lauren Kiley":
            performers.append('Lauren Kiley')

        if meta['site'] == "Lisa Harlotte":
            performers.append('Lisa Harlotte')

        if meta['site'] == "Lynn Winters":
            performers.append('Lynn Winters')

        if meta['site'] == "MILF Gigi":
            performers.append('MILF Gigi')

        if meta['site'] == "Luna Dawn":
            performers.append('Luna Dawn')

        if meta['site'] == "Captive Chrissy Marie":
            performers.append('Chrissy Marie')

        if meta['site'] == "Caroline Pierce":
            performers.append('Caroline Pierce')

        if meta['site'] == "Jackie Bound":
            performers.append('Jackie Bound')

        if meta['site'] == "Christina Sapphire":
            performers.append('Christina Sapphire')

        if meta['site'] == "Stella Liberty":
            performers.append('Stella Liberty')

        if meta['site'] == "Ticklerotic":
            performers.append('Pandora Paramour')

        if meta['site'] == "AJ Marion":
            performers.append('AJ Marion')

        if meta['site'] == "Sydney Screams 4U":
            performers.append('Sydney Screams')

        if meta['site'] == "Desperate Pleasures":
            keywords = scene.xpath('.//p[contains(text(), "Keywords")]/text()')
            if keywords:
                keywords = keywords.get().lower().replace(" , ", ",")
                keywords = re.search(r'keywords:(.*)', keywords)
                if keywords:
                    keywords = keywords.group(1)
                    keywords = keywords.split(",")
                    performers.append(keywords[0])
            else:
                performer = scene.xpath('//p/span[contains(text(),"Starring")]/text()')
                if performer:
                    performer = performer.get().lower()
                    performer = performer.replace('starring', '').replace(':', '').replace(' and ', ',')
                    performers = performer.split(",")

        if meta['site'] == "Brendas Bound":
            performer = scene.xpath('.//em/strong/span[contains(text(),"With")]/text()')
            if performer:
                performer = performer.get().lower()
                performer = performer.replace("with", "").replace(" and", ",")
                performer = performer.replace("real life married couple", "")
                performers = performer.split(",")
                performers = list(map(lambda x: x.strip().title(), performers))

        if meta['site'] == "League of Amazing Women":
            performer = scene.xpath('.//p[contains(text(), "Starring")]/text()')
            if performer:
                performer = performer.get().lower()
                performer = performer.replace("starring", "").replace(" and", ",")
                performers = performer.split(",")
                performers = list(map(lambda x: x.strip().title(), performers))

        if meta['site'] == "Nyxons Bondage Files":
            starring = scene.xpath('.//p/strong[contains(text(), "starring")]/text()')
            if starring:
                starring = starring.get().lower().strip()
                starring = starring.replace("starring", "")
                performers = starring.split("&")
                performers = list(map(lambda x: x.strip().title(), performers))
                return performers

        if meta['site'] == "Old School Bondage":
            starring = scene.xpath('.//p/span[contains(@style,"color: #ff0000;")]//text()')
            if starring:
                starring = starring.get().lower().strip()
                print(f'Starring {starring}')
                starring = starring.replace('\xa0', ' ').replace(" and ", ",")
                starring = starring.replace('sahrye', 'enchantress sahrye')
                starring = re.sub('from .*', '', starring)
                starring = re.sub(' as .*', '', starring)
                performers = starring.split(",")
                performers = list(map(lambda x: x.strip().title(), performers))
                return performers

        desc = scene.xpath('./a/div/p//text()')
        if desc:
            desc = desc.getall()
            desc = title + "".join(desc).strip()
            desc = desc.lower()
            if "tomiko" in desc:
                performers.append('Tomiko')
            if "jolene" in desc:
                performers.append('Jolene Hexx')
            if "sinn" in desc:
                performers.append('Sinn Sage')
            if "dee williams" in desc:
                performers.append('Dee Williams')
            if "carmen" in desc:
                performers.append('Carmen Valentina')
            if "cheyenne" in desc:
                performers.append('Cheyenne Jewel')
            if "agatha" in desc:
                performers.append('Agatha Delicious')
            if "sandra" in desc:
                performers.append('Sandra Silvers')
            if "shannon" in desc:
                performers.append('Shannon Sterling')
            if "constance" in desc:
                performers.append('Constance Coyne')
            if "lisa" in desc:
                performers.append('Lisa Harlotte')
            if "lauren" in desc:
                performers.append('Lauren Kiley')
            if "lilmizz" in desc:
                performers.append('lilmizz unique')
            if "caroline" in desc:
                performers.append('Caroline Pierce')
            if "sydney" in desc:
                performers.append('Sydney Hale')
            if "serene" in desc:
                performers.append('Serene Isley')
            if "kendra" in desc:
                performers.append('Kendra Jade')
            if "candle" in desc:
                performers.append('Candle Boxx')
            if "arielle" in desc:
                performers.append('Arielle Lane')
            if "aj marion" in desc:
                performers.append('AJ Marion')
            if "isean" in desc:
                performers.append('Isean')
            if "crystal" in desc:
                performers.append('Crystal Frost')
            if "ludella" in desc:
                performers.append('Ludella')
            if "belle" in desc:
                performers.append('Belle Davis')
            if "claire" in desc and "lune" in desc:
                performers.append('Claire Dlune')
            if "nyxon" in desc:
                performers.append('Nyxon')
            if "vivienne velvet" in desc:
                performers.append('Vivienne Velvet')
            if "mia martinez" in desc:
                performers.append('Mia Martinez')
            if "gigi" in desc:
                performers.append('MILF Gigi')
            if "ruth cassidy" in desc:
                performers.append('ruth cassidy')
            if "kaecie james" in desc:
                performers.append('Kaecie James')
            if "summer peters" in desc:
                performers.append('Summer Peters')
            if "alexis taylor" in desc:
                performers.append('Alexis Taylor')
            if "reya fet" in desc:
                performers.append('Reya Fet')
            if "blair williams" in desc:
                performers.append('Blair Williams')
            if "lorelei" in desc:
                performers.append('Lorelei Mission')
            if "alex chance" in desc:
                performers.append('Alex Chance')
            if "nyssa nevers" in desc:
                performers.append('nyssa nevers')
            if "misty meaner" in desc:
                performers.append('misty meaner')
            if "whitney" in desc:
                performers.append('whitney morgan')
            if "adara jordin" in desc:
                performers.append('adara jordin')
            if "mia hope" in desc:
                performers.append('mia hope')
            if "kelly moore" in desc:
                performers.append('kelly moore')
            if "mikayla miles" in desc:
                performers.append('Mikayla Miles')
            if "vanessa" in desc:
                performers.append('Vanessa Davis')
            if "jackie bound" in desc:
                performers.append('Jackie Bound')
            if "wenona" in desc:
                performers.append('Wenona')
            if "wonder star" in desc:
                performers.append('wonder star')
            if "carissa montgomery" in desc:
                performers.append('carissa montgomery')
            if "ayla aysel" in desc:
                performers.append('Ayla Aysel')
            if "raven eve" in desc:
                performers.append('raven eve')
            if "sarah brooke" in desc:
                performers.append('sarah brooke')
            if "ashley lane" in desc:
                performers.append('ashley lane')
            if "rachel adams" in desc:
                performers.append('rachel adams')
            if "tina lee comet" in desc:
                performers.append('tina lee comet')
            if "stella liberty" in desc:
                performers.append('stella liberty')
            if "terramizu" in desc:
                performers.append('terramizu')
            if "pandora paramour" in desc:
                performers.append('pandora paramour')
            if "roxie rae" in desc:
                performers.append('roxie rae')
            if "vin glass" in desc:
                performers.append('vin glass')
            if "kody evans" in desc:
                performers.append('kody evans')
            if "lynn winters" in desc:
                performers.append('lynn winters')
            if "kitty quinn" in desc:
                performers.append('kitty quinn')
            if "terra mizu" in desc:
                performers.append('terra mizu')
            if "johnny starlight" in desc:
                performers.append('johnny starlight')
            if "quinn carter" in desc:
                performers.append('quinn carter')
            if "haley quinn" in desc:
                performers.append('haley quinn')
            if "sahrye" in desc:
                performers.append('enchantress sahrye')
            if "sydney screams" in desc:
                performers.append('Sydney Screams')
            if "tilly mcreese" in desc:
                performers.append('tilly mcreese')
            if "monica jade" in desc:
                performers.append('monica jade')
            if "claire irons" in desc:
                performers.append('claire irons')
            if "jackie daniels" in desc:
                performers.append('jackie daniels')
            if "gurl haggard" in desc:
                performers.append('gurl haggard')
            if "kimberly marvel" in desc:
                performers.append('kimberly marvel')
            if "amanda marie" in desc:
                performers.append('amanda marie')
            if "angela ryan" in desc:
                performers.append('angela ryan')
            if "lady jayne" in desc:
                performers.append('lady jayne')
            if "desiree de carlo" in desc:
                performers.append('desiree de carlo')
            if "wednesday harrington" in desc:
                performers.append('wednesday harrington')
            if "bella ink" in desc:
                performers.append('bella ink')
            if "izzy laurent" in desc:
                performers.append('izzy laurent')
            if "elaine hershey" in desc:
                performers.append('elaine hershey')
            if "kim chi" in desc:
                performers.append('kim chi')

        if '' in performers:
            performers.remove('')
        performers2 = []
        for performer in performers:
            performer = performer.lower()
            performer = re.sub(' as .*', '', performer)
            performers2.append(performer)
        performers = performers2

        performers = list(set(performers))
        performers = list(map(lambda x: x.strip().title(), performers))
        return performers

    def site_tags(self, scene, meta):
        if meta['site'] == "4Tomiko":
            tags = []
            desc = scene.xpath('./a/div/p//text()')
            if desc:
                desc = desc.getall()
                desc = "".join(desc).strip()
                desc = desc.lower()
                desc = re.search(r'fetish elements:(.*)', desc)
                if desc:
                    desc = desc.group(1)
                    desc = desc.replace('\xa0', '').strip()
                    tags = desc.split(",")
                    tags = list(map(lambda x: x.strip().title(), tags))
                    return tags

        if meta['site'] == "Sandra Silvers":
            return ['Bondage', 'Fetish']

        if meta['site'] == "Office Perils":
            return ['Bondage', 'Fetish']

        if meta['site'] == "Girls Next Door Bondage":
            return ['Bondage', 'Fetish']

        if meta['site'] == "Serene Isley":
            return ['Bondage', 'Fetish']

        if meta['site'] == "Maidens in Mayhem":
            return ['Bondage', 'Fetish']

        if meta['site'] == "Ivan Boulder":
            return ['Bondage', 'Fetish']

        if meta['site'] == "Captive Chrissy Marie":
            return ['Bondage', 'Fetish']

        if meta['site'] == "Vivienne Velvet":
            return ['Bondage', 'Fetish']

        if meta['site'] == "Fayth on Fire":
            return ['Bondage', 'Fetish']

        if meta['site'] == "Ivan Boulder":
            return ['Bondage', 'Fetish']

        if meta['site'] == "Jackie Bound":
            return ['Bondage', 'Fetish']

        if meta['site'] == "Bondage Crossdresser":
            return ['Bondage', 'Fetish', 'Crossdressing']

        if meta['site'] == "DP Stone Fetish":
            return ['Bondage', 'Fetish']

        if meta['site'] == "Lynn Winters":
            return ['Bondage', 'Fetish']

        if meta['site'] == "Wrapped in Bondage":
            return ['Bondage', 'Fetish']

        if meta['site'] == "Lisa Harlotte":
            return ['Bondage', 'Fetish']

        if meta['site'] == "Bondage Down South":
            return ['Bondage', 'Fetish']

        if meta['site'] == "Luna Dawn":
            return ['Bondage', 'Fetish']

        if meta['site'] == "Leggy Bondage":
            return ['Bondage', 'Fetish', 'Legs']

        if meta['site'] == "AJ Marion":
            return ['Bondage', 'Fetish']

        if meta['site'] == "Old School Bondage":
            return ['Bondage', 'Fetish']

        if meta['site'] == "Ticklerotic":
            return ['Bondage', 'Fetish', 'Tickling']

        if meta['site'] == "Kaecie James":
            return ['Bondage', 'Fetish']

        if meta['site'] == "College Captures":
            return ['Bondage', 'Fetish']

        if meta['site'] == "Hosed and Helpless":
            return ['Bondage', 'Fetish', 'Pantyhose', 'Cosplay', 'Roleplay']

        if meta['site'] == "BBW Bound":
            return ['Bondage', 'Fetish', 'BBW']

        if meta['site'] == "Christina Sapphire":
            return ['Interracial']

        if meta['site'] == "Tied in Heels":
            return ['Bondage', 'Fetish', 'Shoes', 'Boots']

        if meta['site'] == "Cinched and Secured":
            return ['Bondage', 'Fetish']

        if meta['site'] == "Lew Rubens":
            return ['Bondage', 'Fetish', 'Bondage / BDSM']

        if meta['site'] == "League of Amazing Women":
            return ['Bondage', 'Fetish', 'Superheroine', 'Cosplay']

        if meta['site'] == "Loreleis Bedroom Bondage":
            tags = []
            desc = scene.xpath('./a/div/p//text()')
            if desc:
                desc = desc.getall()
                desc = "".join(desc).strip()
                desc = desc.lower()
                tags2 = desc.split(",")
                for tag in tags2:
                    if not re.search(r'[^a-zA-Z- ]', tag):
                        if not len(tag.split()) > 2:
                            tags.append(tag)
                tags = list(map(lambda x: x.strip().title(), tags))
                return tags

        if meta['site'] == "Caroline Pierce":
            tags = []
            desc = scene.xpath('.//div[@class="album-block"]/p//text()')
            if desc:
                desc = desc.getall()
                desc = "".join(desc).strip().replace("&nbsp;", "").replace("<br />", " ")
                desc = desc.lower()
                tags2 = desc.split(",")
                for tag in tags2:
                    if not re.search(r'[^a-zA-Z- ]', tag):
                        if not len(tag.split()) > 2:
                            tags.append(tag)
                if '' in tags:
                    tags.remove('')
                tags = list(map(lambda x: x.strip().title(), tags))
                return tags

        if meta['site'] == "Sydney Screams 4U":
            tags = []
            desc = scene.xpath('.//p//text()')
            if desc:
                desc = desc.getall()
                desc = "".join(desc).strip()
                desc = desc.lower()
                desc = re.search('category:(.*)', desc)
                if desc:
                    desc = desc.group(1).strip()
                    tags2 = desc.split(",")
                    for tag in tags2:
                        if not re.search(r'[^a-zA-Z- ]', tag):
                            if not len(tag.split()) > 2:
                                tags.append(tag)
                    tags = list(map(lambda x: x.strip().title(), tags))
                    return tags

        if meta['site'] == "Desperate Pleasures":
            tags = []
            keywords = scene.xpath('.//p[contains(text(), "Keywords")]/text()')
            if keywords:
                keywords = keywords.get().lower().replace(" , ", ",")
                keywords = re.search(r'keywords:(.*)', keywords)
                if keywords:
                    keywords = keywords.group(1)
                    if "," in keywords:
                        keywords = keywords.split(",")
                        del keywords[0]
                        for keyword in keywords:
                            tags.append(keyword)
            categories = scene.xpath('.//p[contains(text(), "Categories")]/text()')
            if categories:
                categories = categories.get().lower().replace(" , ", ",")
                categories = re.sub(r'keyword.*', '', categories)
                categories = re.search(r'categories:(.*)', categories)
                if categories:
                    categories = categories.group(1)
                    categories = categories.split(",")
                    for category in categories:
                        tags.append(category)
            category = scene.xpath('.//p[contains(text(), "Category")]/text()')
            if category:
                category = category.get().lower().replace(" , ", ",")
                category = re.sub(r'keyword.*', '', category)
                category = re.search(r'category:(.*)', category)
                if category:
                    category = category.group(1)
                    category = category.split(",")
                    for category_item in categories:
                        tags.append(category_item)
                tags = list(set(tags))
                tags = list(map(lambda x: x.strip().title(), tags))
                tags = [string for string in tags if string != ""]
                return tags

        if meta['site'] == "Nyxons Bondage Files":
            tags = scene.xpath('.//p[strong[contains(text(), "starring")]]/following-sibling::p/strong/em/text()')
            if tags:
                tags = tags.get()
                tags = tags.split(",")
                tags = list(map(lambda x: x.strip().title(), tags))
                return tags

        if meta['site'] == "Stella Liberty":
            tags = scene.xpath('.//p[contains(text(),"Includes")]/text()')
            if tags:
                tags = tags.get()
                tags = tags.replace("Includes:", "")
                tags = tags.split(",")
                tags = list(map(lambda x: x.strip().title(), tags))
                return tags

        if meta['site'] == "Miss Whitney Morgan":
            tags = scene.xpath('.//p/span/strong[contains(text(),"Includes")]/text()')
            if tags:
                tags = tags.get()
                tags = tags.replace("Includes:", "")
                tags = tags.split(",")
                tags = list(map(lambda x: x.strip().title(), tags))
                return tags

        if meta['site'] == "Lauren Kiley":
            tags = scene.xpath('..//p[contains(text(),"Includes")]/text()')
            if tags:
                tags = tags.get()
                tags = tags.replace("Includes:", "")
                tags = tags.split(",")
                tags = list(map(lambda x: x.strip().title(), tags))
                return tags

        if meta['site'] == "Jim Hunters Lair":
            tags = scene.xpath('.//p/span[contains(@style,"font-size: small;")]/strong[not(contains(text(),"~"))]/text()')
            if tags:
                tags = tags.get()
                tags = tags.split(",")
                tags = list(map(lambda x: x.strip().title(), tags))
                return tags

        if meta['site'] == "Brendas Bound":
            tags = scene.xpath('.//em/strong/text()')
            if tags:
                tags = tags.get()
                tags = tags.split(",")
                tags = list(map(lambda x: x.strip().title(), tags))
                return tags

        return []
