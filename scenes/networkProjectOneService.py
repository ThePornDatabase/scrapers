import re
import string
from urllib.parse import urlencode
import datetime
import scrapy
from slugify import slugify
from tldextract import tldextract
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class ProjectOneServiceSpider(BaseSceneScraper):
    name = 'ProjectOneService'
    network = 'mindgeek'

    custom_settings = {'CONCURRENT_REQUESTS': '4',
                       # ~ 'AUTOTHROTTLE_ENABLED': 'True',
                       # ~ 'AUTOTHROTTLE_DEBUG': 'False',
                       # ~ 'DOWNLOAD_DELAY': '2',
                       'CONCURRENT_REQUESTS_PER_DOMAIN': '2',
                       }

    start_urls = [
        # ~ # Only need one starting URL per "site", pulls everything through common feed

        'https://www.babes.com',
        # 'https://www.babesunleashed.com',
        # 'https://www.elegantanal.com',
        # 'https://www.officeobsession.com',
        # 'https://www.stepmomlessons.com',

        # 'https://www.bellesafilms.com', # Removed from Mind Geek connections
        # 'https://www.bellesa.com',
        # 'https://www.bellesahouse.com',

        'https://www.bangbros.com',
        'https://www.biempire.com',
        'https://www.brazzersvr.com',
        'https://www.brazzers.com',
        # 'https://www.babygotboobs.com',
        # 'https://www.bigbuttslikeitbig.com',
        # 'https://www.bigtitsatschool.com',
        # 'https://www.bigtitsatwork.com',
        # 'https://www.bigtitsinsports.com',
        # 'https://www.bigtitsinuniform.com',
        # 'https://www.bigwetbutts.com',
        # 'https://www.brazzersexxtra.com',
        # 'https://www.brazzersvault.com',
        # 'https://www.bustyandreal.com',
        # 'https://www.cfnm.com',
        # 'https://www.daywithapornstar.com',
        # 'https://www.dirtymasseur.com',
        # 'https://www.doctoradventures.com',
        # 'https://www.hotandmean.com',
        # 'https://www.hotchicksbigasses.com',
        # 'https://www.jugfuckers.com',
        # 'https://www.milfslikeitbig.com',
        # 'https://www.mommygotboobs.com',
        # 'https://www.momsincontrol.com',
        # 'https://www.pornstarslikeitbig.com',
        # 'https://www.realwifestories.com',
        # 'https://www.shesgonnasquirt.com',
        # 'https://www.teenslikeitbig.com',
        # 'https://www.zzseries.com',

        'https://www.bromo.com',
        # 'https://www.bromoblackmaleme.com',
        # 'https://www.bromous.com',

        'https://www.dancingbear.com',
        'https://www.deviante.com',
        # 'https://www.eroticspice.com',
        # 'https://www.forgivemefather.com',
        # 'https://www.loveherass.com',
        # 'https://www.prettydirtyteens.com',
        # 'https://www.sexworking.com',

        'https://www.czechhunter.com/',
        'https://www.digitalplayground.com',
        'https://www.dilfed.com',
        # 'https://www.gilfed.com', API responses from this site are borked
        'https://www.erito.com',
        'https://www.fakehub.com',
        # 'https://www.fakeagent.com',
        # 'https://www.fakeagentuk.com',
        # 'https://www.fakecop.com',
        # 'https://www.fakedrivingschool.com',
        # 'https://www.fakehospital.com',
        # 'https://www.fakehostel.com',
        # 'https://www.faketaxi.com',
        # 'https://www.fakehuboriginals.com',
        # 'https://www.femaleagent.com',
        # 'https://www.femalefaketaxi.com',
        # 'https://www.publicagent.com',

        'https://www.guyselector.com',
        'https://www.iconmale.com',
        'https://www.letsdoeit.com',
        'https://www.men.com',
        'https://www.metrohd.com',
        # 'https://www.devianthardcore.com',
        # 'https://www.familyhookups.com',
        # 'https://www.girlgrind.com',
        # 'https://www.kinkyspa.com',
        # 'https://www.shewillcheat.com',

        'https://www.milehighmedia.com',
        # 'https://www.doghousedigital.com',
        # 'https://www.familysinners.com',
        # 'https://www.realityjunkies.com',
        # 'https://www.sweetheartvideo.com',
        # 'https://www.sweetsinner.com',

        'https://www.milfed.com',
        # 'https://www.cherrypop.com',
        # 'https://www.doghousedigital.com',    (Crossover with MileHighMedia)
        # 'https://www.familysinners.com',      (Crossover with MileHighMedia)
        # 'https://www.lesbianolderyounger.com',
        # 'https://www.milehighmedia.com',      (Crossover with MileHighMedia)
        # 'https://www.realityjunkies.com',     (Crossover with MileHighMedia)
        # 'https://www.sweetheartvideo.com',    (Crossover with MileHighMedia)
        # 'https://www.sweetsinner.com',        (Crossover with MileHighMedia)

        'https://www.mofos.com',
        # 'https://www.bustedbabysitters.com',
        # 'https://www.dontbreakme.com',
        # 'https://www.dronehunter.com',
        # 'https://www.girlsgonepink.com',
        # 'https://www.iknowthatgirl.com',
        # 'https://www.ingangwebang.com',
        # 'https://www.latinasextapes.com',
        # 'https://www.letstryanal.com',
        # 'https://www.milfslikeitblack.com',
        # 'https://www.mofosbsides.com',
        # 'https://www.mofoslab.com',
        # 'https://www.mofosworldwide.com',
        # 'https://www.pervsonpatrol.com',
        # 'https://www.pornstarvote.com',
        # 'https://www.projectrv.com',
        # 'https://www.publicpickups.com',
        # 'https://www.realslutparty.com',
        # 'https://www.sharemybf.com',
        # 'https://www.shesafreak.com',
        # 'https://www.strandedteens.com',
        # 'https://www.thesexscout.com',

        'https://www.nextdoorhobby.com',
        'https://www.noirmale.com',
        'https://www.propertysex.com',
        'https://www.realitydudesnetwork.com',
        'https://www.realitykings.com',
        # 'https://www.40inchplus.com',
        # 'https://www.8thstreetlatinas.com',
        # 'https://www.badtowtruck.com',
        # 'https://www.bignaturals.com',
        # 'https://www.bigtitsboss.com',
        # 'https://www.captainstabbin.com',
        # 'https://www.cfnmsecret.com',
        # 'https://www.crazyasiangfs.com',
        # 'https://www.crazycollegegfs.com',
        # 'https://www.cumfiesta.com',
        # 'https://www.daredorm.com',
        # 'https://www.eurosexparties.com',
        # 'https://www.extremeasses.com',
        # 'https://www.extremenaturals.com',
        # 'https://www.firsttimeauditions.com',
        # 'https://www.gfrevenge.com',
        # 'https://www.girlsofnaked.com',
        # 'https://www.happytugs.com',
        # 'https://www.hdlove.com',
        # 'https://www.hornybirds.com',
        # 'https://www.hotbush.com',
        # 'https://www.inthevip.com',
        # 'https://www.lilhumpers.com',
        # 'https://www.lookathernow.com',
        # 'https://www.mikeinbrazil.com',
        # 'https://www.mikesapartment.com',
        # 'https://www.milfhunter.com',
        # 'https://www.milfnextdoor.com',
        # 'https://www.momsbangteens.com',
        # 'https://www.momslickteens.com',
        # 'https://www.moneytalks.com',
        # 'https://www.monstercurves.com',
        # 'https://www.nofaces.com',
        # 'https://www.pure18.com',
        # 'https://www.recklessinmiami.com',
        # 'https://www.rkprime.com',
        # 'https://www.roundandbrown.com',
        # 'https://www.saturdaynightlatinas.com',
        # 'https://www.seemywife.com',
        # 'https://www.sneakysex.com',
        # 'https://www.streetblowjobs.com',
        # 'https://www.teenslovehugecocks.com',
        # 'https://www.welivetogether.com',
        # 'https://www.wivesinpantyhose.com',

        'https://www.seancody.com',
        'https://www.sexselector.com',
        'https://www.sexyhub.com',
        # 'https://www.danejones.com',
        # 'https://www.fitnessrooms.com',
        # 'https://www.girlfriends.com',
        # 'https://www.lesbea.com',
        # 'https://www.massagerooms.com',
        # 'https://www.momxxx.com',

        'https://www.squirted.com',
        'https://www.thegayoffice.com',
        # 'https://www.bigdicksatschool.com',
        # 'https://www.bromous.com', (Crossover with Bromo)
        # 'https://www.drillmyhole.com',
        # 'https://www.godsofmen.com',
        # 'https://www.jizzorgy.com',
        # 'https://www.menofuk.com',
        # 'https://www.realitydudes.com',
        # 'https://www.str8chaser.com',
        # 'https://www.str8togay.com',
        # 'https://www.toptobottom.com',

        'https://www.transangelsnetwork.com',
        # 'https://www.transangels.com',

        'https://www.transharder.com',  # Seems to be the same as TransAngels, but some additional
        'https://www.transsensual.com',  # Seems to be the same as TransAngels, but some additional
        'https://www.trueamateurs.com',
        'https://www.tube8vip.com',
        'https://www.twistys.com',
        # 'https://www.anettedawn.com',
        # 'https://www.featurefilm.com',
        # 'https://www.momknowsbest.com',
        # 'https://www.nicolegraves.com',
        # 'https://www.turningtwistys.com',
        # 'https://www.twistysteasers.com',
        # 'https://www.twistyshard.com',
        # 'https://www.whengirlsplay.com',

        'https://virtualporn.com',
        'https://www.voyr.com',
        'https://www.whynotbi.com',
    ]

    selector_map = {
        'external_id': 'scene\\/(\\d+)'
    }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, headers=self.headers, cookies=self.cookies,
                                 meta={'url': url})

    def parse(self, response):
        token = self.get_token(response)

        headers = {
            'instance': token,
        }

        response.meta['headers'] = headers
        response.meta['limit'] = 25
        # ~ response.meta['page'] = -1
        response.meta['page'] = self.page - 1
        response.meta['url'] = response.url

        return self.get_next_page(response)

    def get_scenes(self, response):
        scene_count = 0

        for scene in response.json()['result']:
            item = SceneItem()
            if scene['collections'] and len(scene['collections']):
                item['site'] = scene['collections'][0]['name']
            else:
                item['site'] = tldextract.extract(response.meta['url']).domain

            if "men.com" in response.url and item['site'] == 'tp':
                item['site'] = 'Twink Pop'

            if tldextract.extract(
                    response.meta['url']).domain == 'digitalplayground':
                item['site'] = 'digitalplayground'

            item['image'] = self.get_image(scene)

            item['image_blob'] = self.get_image_blob_from_link(item['image'])

            item['trailer'] = self.get_trailer(scene)
            if not item['trailer']:
                item['trailer'] = ''
            item['date'] = self.parse_date(scene['dateReleased']).isoformat()
            if "letsdoeit" in response.url:
                item['id'] = scene['spartanId']
            else:
                item['id'] = scene['id']
            item['network'] = self.network
            item['parent'] = tldextract.extract(response.meta['url']).domain

            if 'title' in scene:
                item['title'] = scene['title']
            else:
                item['title'] = item['site'] + ' ' + self.parse_date(scene['dateReleased']).strftime('%b/%d/%Y')

            if 'description' in scene:
                item['description'] = scene['description']
            else:
                item['description'] = ''

            item['performers'] = []
            item['performers_data'] = []
            if "actors" in scene and scene['actors']:
                for model in scene['actors']:
                    performer = string.capwords(model['name'])
                    performer_extra = {}
                    performer_extra['name'] = performer
                    performer_extra['site'] = "Mindgeek"
                    if "gender" in model and model['gender']:
                        performer_extra['extra'] = {}
                        performer_extra['extra']['gender'] = model['gender']
                    item['performers_data'].append(performer_extra)
                    item['performers'].append(performer)

            item['tags'] = []
            for tag in scene['tags']:
                item['tags'].append(tag['name'])

            if "isVR" in scene or "virtualporn" in response.url:
                if scene['isVR']:
                    item['tags'].append("VR")

            try:
                item['duration'] = scene['videos']['mediabook']['length']
            except Exception:
                item['duration'] = ''

            item['markers'] = []
            if "timeTags" in scene:
                for timetag in scene['timeTags']:
                    timestamp = {}
                    timestamp['name'] = self.cleanup_title(timetag['name'])
                    timestamp['start'] = str(timetag['startTime'])
                    timestamp['end'] = str(timetag['endTime'])
                    item['markers'].append(timestamp)
                    scene['tags'].append(timestamp['name'])
                item['markers'] = self.clean_markers(item['markers'])
                item['tags'] = list(map(lambda x: string.capwords(x.strip()), list(set(item['tags']))))

            # Deviante abbreviations
            if item['site'] == "fmf":
                item['site'] = "Forgive Me Father"
                item['parent'] = "Deviante"
            if item['site'] == "sw":
                item['site'] = "Sex Working"
                item['parent'] = "Deviante"
            if item['site'] == "pdt":
                item['site'] = "Pretty Dirty Teens"
                item['parent'] = "Deviante"
            if item['site'] == "lha":
                item['site'] = "Love Her Ass"
                item['parent'] = "Deviante"
            if item['site'] == "es":
                item['site'] = "Erotic Spice"
                item['parent'] = "Deviante"
            if item['site'] == "dlf":
                item['site'] = "DILFed"
                item['parent'] = "DILFed"
            if item['site'] == "ndhe":
                item['site'] = "Next Door Hobby"
                item['parent'] = "Next Door Hobby"
            if item['site'] == "zzvr":
                item['site'] = "Brazzers VR"
                item['parent'] = "Brazzers VR"

            siteurl = re.compile(r'\W')
            siteurl = re.sub(siteurl, '', item['site']).lower()
            brand = scene['brand'].lower().strip()

            if brand == "brazzers" or brand == "zzvr" or brand == "deviante" or brand == "bangbros" or brand == "bromo":
                item['url'] = f"https://www.{brand}.com/video/{scene['id']}/{slugify(item['title'])}"
            elif brand == "men":
                item['url'] = f"https://www.{brand}.com/sceneid/{scene['id']}/{slugify(item['title'])}"
            elif brand == "mofos" or brand == "realitykings" or brand == "sexyhub" or brand == "twistys" or brand == "babes":
                item['url'] = f"https://www.{brand}.com/scene/{scene['id']}/{slugify(item['title'])}"
            else:
                item['url'] = f"https://www.{siteurl}.com/scene/{scene['id']}/{slugify(item['title'])}"

            item['parent'] = string.capwords(item['parent'])

            yield_item = True
            if brand == "bangbros" and item['date'] < "2023-06-21" and "dancing" not in item['site'].lower():
                yield_item = False

            if item['site'] == "Sex Selector" and item['date'] < "2024-01-13":
                yield_item = False

            if item['site'] == "Virtual Porn" and item['date'] < "2024-06-07":
                yield_item = False

            if self.check_item(item, self.days) and yield_item:
                scene_count = scene_count + 1
                yield item

        if scene_count > 0:
            if 'page' in response.meta and (
                    response.meta['page'] % response.meta['limit']) < self.limit_pages:
                yield self.get_next_page(response)

    def get_next_page(self, response):
        meta = response.meta

        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        query = {
            'dateReleased': f"<{tomorrow}",
            'limit': meta['limit'],
            'type': 'scene',
            'orderBy': '-dateReleased',
            'offset': (meta['page'] * meta['limit']),
            'referrer': meta['url'],
            'adaptiveStreamingOnly': 'false',
        }
        meta = {
            'url': response.meta['url'],
            'headers': response.meta['headers'],
            'page': (response.meta['page'] + 1),
            'limit': response.meta['limit']
        }

        print('NEXT PAGE: ' + str(meta['page']))

        link = 'https://site-api.project1service.com/v2/releases?' + \
            urlencode(query)
        return scrapy.Request(url=link, callback=self.get_scenes,
                              headers=response.meta['headers'], meta=meta)
    def get_token(self, response):
        token = re.search('instance_token=(.+?);',
                          response.headers.getlist('Set-Cookie')[0].decode("utf-8"))
        return token.group(1)

    def get_image(self, scene):
        image_arr = []
        if 'card_main_rect' in scene['images'] and len(
                scene['images']['card_main_rect']):
            image_arr = scene['images']['card_main_rect']
        elif 'poster' in scene['images'] and len(scene['images']['poster']):
            image_arr = scene['images']['poster']

        sizes = ['xx', 'xl', 'lg', 'md', 'sm']
        for index in image_arr:
            image = image_arr[index]
            for size in sizes:
                if size in image:
                    return image[size]['url']

    def get_trailer(self, scene):
        for index in scene['videos']:
            trailer = scene['videos'][index]
            for size in ['720p', '576p', '480p', '360p', '320p', '1080p', '4k']:
                if size in trailer['files']:
                    return trailer['files'][size]['urls']['view']

    def clean_markers(self, markers):
        markers = sorted(markers, key=lambda k: (k['name'].lower(), int(k['start']), int(k['end'])))
        marker_final = []
        marker_work = markers.copy()
        marker2_work = markers.copy()
        for test_marker in marker_work:
            if test_marker in markers:
                for marker in marker2_work:
                    if test_marker['name'].lower().strip() == marker['name'].lower().strip():
                        test_start = int(test_marker['start'])
                        mark_start = int(marker['start'])
                        test_end = int(test_marker['end'])
                        mark_end = int(marker['end'])
                        if test_start < mark_start or test_start == mark_start:
                            test1 = mark_start - test_end
                            test2 = mark_start - test_start
                            if 0 < test1 < 60 or 0 < test2 < 60 or test1 == 0 or test2 == 0:
                                if mark_end > test_end:
                                    test_marker['end'] = marker['end']
                                    if marker in markers:
                                        markers.remove(marker)
                            if test_end > mark_start and mark_end > test_end:
                                test_marker['end'] = marker['end']
                                if marker in markers:
                                    markers.remove(marker)
                            if test_start < mark_start and (mark_end < test_end or test_end == mark_end):
                                if marker in markers:
                                    markers.remove(marker)
                marker2_work = markers.copy()

                if test_marker in markers:
                    marker_final.append(test_marker)
                    markers.remove(test_marker)
        marker_final = sorted(marker_final, key=lambda k: (int(k['start']), int(k['end'])))
        return marker_final
