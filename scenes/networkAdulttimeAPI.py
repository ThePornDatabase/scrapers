"""
Optimized version of networkAdulttimeAPI.py.

Architecture changes vs. the original:
  1. The 470-line if/elif chain in get_scenes() collapses to a single lookup
     against SITE_CONFIGS, which carries all per-site facts (URL, parent,
     network, URL format, extra tags, min_date, etc.) in one place.
  2. The 225-line if/elif chain in call_algolia() becomes a single dict lookup
     against ALGOLIA_BODIES. Sites that follow the common pattern (single
     availableOnSite filter) get DEFAULT_ALGOLIA_BODY for free without listing.
  3. start_urls is derived from SITE_CONFIGS — adding/disabling a site is
     one edit instead of two.
  4. match_site() reads from SITE_NAMES, the source of truth for display names.
"""
import base64
import re
import string
import requests
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


# ---------------------------------------------------------------------------
# Display-name lookup (slug -> human-readable name). Used by match_site() to
# translate Algolia `sitename` slugs (which include sub-site brands carried
# in by bundle queries) into human-readable display names. Expand as needed.
# ---------------------------------------------------------------------------
SITE_NAMES = {
    '21eroticanal': '21 Erotic Anal',
    '21footart': '21 Foot Art',
    '3rddegreefilms': '3rd Degree Films',
    'JaneDoePictures': 'Jane Doe Pictures',
    'TransgressiveFilms': 'Transgressive Films',
    'adamandevepictures': 'Adam and Eve Pictures',
    'adulttime': 'AdultTime',
    'alettaoceanempire': 'Aletta Ocean Empire',
    'allblackx': 'AllBlackX',
    'allgirlmassage': 'All Girl Massage',
    'analqueenalysa': 'Anal Queen Alysa',
    'analteenangels': 'Anal Teen Angels',
    'asgmaxpartners': 'ASG Max Partners',
    'asmrfantasy': 'ASMR Fantasy',
    'assholefever': 'Asshole Fever',
    'austinwilde': 'Austin Wilde',
    'babygotballs': 'Baby Got Balls',
    'bethecuck': 'Be The Cuck',
    'bigfatcreampie': 'Big Fat Creampie',
    'blacksonblondes': 'Blacks on Blondes',
    'blueangellive': 'Blue Angel Live',
    'bskow': 'BSKow',
    'bushybushy': 'Bushy Bushy',
    'buttplays': 'Buttplays',
    'cheatingwhorewives': 'Cheating Whore Wives',
    'clubsandy': 'Club Sandy',
    'codycummings': 'Cody Cummings',
    'coupleswapping': 'Couple Swapping',
    'creampiereality': 'Creampie Reality',
    'cummingmatures': 'Cumming Matures',
    'cumshotoasis': 'Cumshot Oasis',
    'cutiesgalore': 'Cuties Galore',
    'darkx': 'DarkX',
    'deepthroatfrenzy': 'Deepthroat Frenzy',
    'devilsfilmparodies': 'Devils Film Parodies',
    'devilsgangbangs': 'Devils Gangbangs',
    'dominatedgirls': 'Dominated Girls',
    'dpfanatics': 'DPFanatics',
    'eroticax': 'EroticaX',
    'femalesubmission': 'Female Submission',
    'flixcontentzero': 'See My Flixxx',
    'flixcontentzerotolerancefilms': 'See My Flixxx',
    'gapeland': 'Gapeland',
    'genderx': 'Gender X',
    'girlcore': 'Girlcore',
    'girlsunderarrest': 'Girls Under Arrest',
    'givemeteens': 'Give Me Teens',
    'hairyundies': 'Hairy Undies',
    'hardstop': 'Hard Stop',
    'hardx': 'HardX',
    'homepornreality': 'Home Porn Reality',
    'hotmilfclub': 'Hot MILF Club',
    'jerk-buddies': 'Jerk Buddies',
    'kissmefuckme': 'Kiss Me Fuck Me',
    'lesbianfactor': 'Lesbian Factor',
    'lesbianx': 'LesbianX',
    'lethalhardcore': 'Lethal Hardcore',
    'lethalhardcorevr': 'Lethal Hardcore VR',
    'letsplaylez': 'Lets Play Lez',
    'lewood': 'Lewood',
    'lezcuties': 'Lez Cuties',
    'mandyiskinky': 'Mandy Is Kinky',
    'marcusmojo': 'Marcus Mojo',
    'masonwyler': 'Mason Wyler',
    'massageparlor': 'Massage Parlor',
    'mightymistress': 'Mighty Mistress',
    'milkingtable': 'Milking Table',
    'momsonmoms': 'Moms on Moms',
    'mypervyfamily': 'My Pervy Family',
    'nakedyogalife': 'Naked Yoga Life',
    'nextdoorbuddies': 'Nextdoor Buddies',
    'nextdoorcasting': 'Nextdoor Casting',
    'nextdoorhomemade': 'Nextdoor Homemade',
    'nextdoorhookups': 'Nextdoor Hookups',
    'nextdoormale': 'Nextdoor Male',
    'nextdoororiginals': 'Nextdoor Originals',
    'nextdoorraw': 'Nextdoor Raw',
    'nextdoortwink': 'Nextdoor Twink',
    'nudefightclub': 'Nude Fight Club',
    'nurumassage': 'Nuru Massage',
    'oldyounglesbianlove': 'Old Young Lesbian Love',
    'oralexperiment': 'Oral Experiment',
    'outofthefamily': 'Out of the Family',
    'pansexualx': 'PansexualX',
    'peeandblow': 'Pee And Blow',
    'peternorth': 'Peter North',
    'pixandvideo': 'Pix And Video',
    'roddaily': 'Rod Daily',
    'samuelotoole': 'Samuel Otoole',
    'sextapelesbians': 'Sextape Lesbians',
    'sexwithkathianobili': 'Sex With Kathia Nobili',
    'shapeofbeauty': 'Shape of Beauty',
    'showersolos': 'Shower Solos',
    'sistertrick': 'Sister Trick',
    'speculumplays': 'Speculum Plays',
    'squirtalicious': 'Squirtalicious',
    'stagcollectivesolos': 'Stag Collective Solos',
    'strokethatdick': 'Stroke That Dick',
    'sweetsophiemoone': 'Sweet Sophie Moon',
    'switch-channel': 'Switch',
    'teachmefisting': 'Teach Me Fisting',
    'teensneaks': 'Teen Sneaks',
    'themikeandjoannashow': 'The Mike and Joanna Show',
    'tommydxxx': 'Tommy D XXX',
    'touchmywife': 'Touch My Wife',
    'transfrombrazil': 'Trans From Brazil',
    'transsexualangel': 'Transsexual Angel',
    'transsmuts': 'Trans Smuts',
    'truelesbian': 'True Lesbian',
    'truelesbian.com': 'True Lesbian',
    'trystanbull': 'Trystan Bull',
    'webyoung': 'Web Young',
    'welikegirls': 'We Like Girls',
    'wheretheboysarent': 'Where the Boys Arent',
    'withlovelexi-at-channel': 'With Love Lexi',
    'xempire': 'XEmpire',
    'zerotolerancefilms': 'Zero Tolerance',
    'zoliboy': 'Zoliboy',
}


def match_site(argument):
    a = (argument or '').lower()
    if a in SITE_NAMES:
        return SITE_NAMES[a]
    if a + '.com' in SITE_NAMES:  # original match_site used some 'foo.com' keys
        return SITE_NAMES[a + '.com']
    cfg = SITE_CONFIGS.get(a) or SITE_CONFIGS.get(a + '.com')
    if cfg and 'site' in cfg:
        return cfg['site']
    return argument


# ---------------------------------------------------------------------------
# Per-site config. Keys are *substrings* matched against the referrer URL
# (longest-match wins via resolve_site_config below).
#
# Fields:
#   url             : full crawl-target URL (omit for sub-site-only entries)
#   enabled         : set False to skip this site without removing the entry
#   parent          : item['parent'] override
#   site            : item['site'] override (otherwise match_site(scene['sitename']))
#   site_from       : take item['site'] from scene[<this field>] (e.g. 'serie_name')
#   network         : item['network'] override (default: 'Gamma Enterprises')
#   url_format      : 'sitename' (default), 'simple', or a literal segment like 'joeysilvera'
#   extra_tags      : list of tags to append (e.g. ['Gay'])
#   min_date        : skip scenes older than this YYYY-MM-DD
# ---------------------------------------------------------------------------
SITE_CONFIGS = {
    '21naturals': {'url': 'https://www.21naturals.com', 'parent': '21Naturals', 'site': '21Naturals'},
    '21sextreme': {'url': 'https://www.21sextreme.com', 'parent': '21Sextreme', 'site': '21Sextreme'},
    '21sextury': {'url': 'https://www.21sextury.com', 'parent': '21Sextury', 'site': '21Sextury'},
    'activeduty': {'url': 'https://www.activeduty.com', 'parent': 'Activeduty', 'site': 'Active Duty', 'min_date': '2023-02-20'},
    'adam-and-eve-pictures': {'url': 'https://www.adulttime.com/studio/adam-and-eve-pictures', 'parent': 'Adam And Eve Pictures'},
    'addicted2girls': {'url': 'https://www.addicted2girls.com', 'parent': 'Addicted2girls', 'site': 'Addicted2Girls'},
    'ageandbeauty': {'url': 'https://www.ageandbeauty.com', 'parent': 'Ageandbeauty', 'site': 'Age and Beauty'},
    'agentredgirl': {'url': 'https://www.agentredgirl.com', 'parent': 'Agentredgirl', 'site': 'Agent Red Girl'},
    'allblackx.com': {'url': 'https://www.allblackx.com', 'parent': 'XEmpire'},
    'asmr-fantasy': {'url': 'https://www.adulttime.com/series/asmr-fantasy', 'parent': 'Asmr Fantasy', 'site': 'ASMR Fantasy'},
    'bigfatcreampie': {'url': 'https://www.bigfatcreampie.com', 'parent': 'Bigfatcreampie'},
    'biphoria': {'url': 'https://www.biphoria.com', 'parent': 'BiPhoria', 'site': 'BiPhoria'},
    'blowpass': {'url': 'https://www.blowpass.com', 'parent': 'BlowPass'},
    'bskow': {'url': 'https://www.bskow.com', 'parent': 'Bskow'},
    'burningangel': {'url': 'https://www.burningangel.com', 'parent': 'Burning Angel', 'site': 'Burning Angel'},
    'bushybushy': {'url': 'https://www.bushybushy.com', 'parent': 'Bushybushy'},
    'buttman': {'url': 'https://www.buttman.com', 'parent': 'Buttman', 'site': 'Buttman'},
    'chaosmen': {'url': 'https://www.chaosmen.com', 'parent': 'Chaos Men', 'site': 'Chaos Men'},
    'clubinfernodungeon': {'url': 'https://www.clubinfernodungeon.com', 'parent': 'Clubinfernodungeon', 'site': 'Club Inferno Dungeon'},
    'couple-swapping': {'url': 'https://www.adulttime.com/series/couple-swapping', 'parent': 'Couple Swapping', 'site': 'Couple Swapping'},
    'cumshotoasis': {'url': 'https://www.cumshotoasis.com', 'parent': 'Cumshotoasis'},
    'currycreampie': {'url': 'https://www.currycreampie.com', 'parent': 'Curry Creampie', 'site': 'Curry Creampie'},
    'darkx': {'url': 'https://www.darkx.com', 'parent': 'Darkx'},
    'devilsfilm': {'url': 'https://www.devilsfilm.com', 'parent': 'Devils Film', 'site': 'Devils Film'},
    'devilstgirls': {'url': 'https://www.devilstgirls.com', 'parent': 'Devils T-Girls', 'site': 'Devils T-Girls'},
    'dfxtra': {'url': 'https://www.dfxtra.com', 'parent': 'dogfartnetwork', 'site_from': 'serie_name', 'network': 'dogfartnetwork'},
    'diabolic': {'url': 'https://www.diabolic.com', 'parent': 'Diabolic', 'site': 'Diabolic'},
    'downlowboys': {'url': 'https://www.downlowboys.com', 'parent': 'Downlow Boys', 'site': 'Downlow Boys', 'extra_tags': ['Gay']},
    'dpfanatics': {'url': 'https://www.dpfanatics.com', 'parent': 'DPFanatics'},
    'eroticax.com': {'url': 'https://www.eroticax.com', 'parent': 'XEmpire'},
    'evilangel': {'url': 'https://www.evilangel.com', 'parent': 'Evil Angel', 'site': 'Evil Angel', 'url_format': 'simple'},
    'falconstudios': {'url': 'https://www.falconstudios.com', 'parent': 'Falcon Studios', 'site_from': 'studio_name', 'network': 'Falcon Studios'},
    'famedigital': {'url': 'https://www.famedigital.com', 'parent': 'Fame Digital'},
    'fantasymassage': {'url': 'https://www.fantasymassage.com', 'parent': 'Fantasy Massage', 'site': 'Fantasy Massage'},
    'femboyish': {'url': 'https://www.femboyish.com', 'parent': 'Femboyish', 'site': 'Femboyish'},
    'filthykings': {'url': 'https://www.filthykings.com', 'parent': 'Filthy Kings', 'site_from': 'serie_name'},
    'footsiebabes': {'url': 'https://www.footsiebabes.com', 'parent': 'Footsie Babes', 'site': 'Footsie Babes'},
    'gangbangcreampie': {'url': 'https://www.gangbangcreampie.com', 'parent': 'Gangbang Creampie', 'site': 'Gangbang Creampie'},
    'genderxfilms': {'url': 'https://www.genderxfilms.com', 'parent': 'Genderxfilms', 'site': 'Gender X'},
    'girlfriendsfilms': {'url': 'https://www.girlfriendsfilms.com', 'parent': 'Girlfriends Films', 'site': 'Girlfriends Films'},
    'girlstryanal': {'url': 'https://www.girlstryanal.com', 'parent': 'Girls Try Anal', 'site': 'Girls Try Anal'},
    'girlsway': {'url': 'https://www.girlsway.com', 'parent': 'Girlsway', 'site': 'Girlsway', 'url_format': 'simple'},
    'gloryholesecrets': {'url': 'https://www.gloryholesecrets.com', 'parent': 'Gloryhole Secrets', 'site': 'Gloryhole Secrets', 'min_date': '2022-10-01'},
    'grandpasfuckteens': {'parent': 'Grandpas Fuck Teens', 'site': 'Grandpas Fuck Teens', 'min_date': '2019-02-06'},
    'grannyghetto': {'url': 'https://www.grannyghetto.com', 'parent': 'Granny Ghetto', 'site': 'Granny Ghetto'},
    'hardx.com': {'url': 'https://www.hardx.com', 'parent': 'XEmpire'},
    'hothouse': {'url': 'https://www.hothouse.com', 'parent': 'Hothouse', 'site': 'Hothouse'},
    'immorallive': {'url': 'https://www.immorallive.com', 'parent': 'Immoral Live', 'site': 'Immoral Live'},
    'interracialvision': {'url': 'https://www.interracialvision.com', 'parent': 'Interracialvision', 'site': 'Interracialvision'},
    'isthisreal': {'url': 'https://www.isthisreal.com', 'parent': 'Is This Real', 'site': 'Is This Real'},
    'jerk-buddies': {'url': 'https://www.jerk-buddies.com', 'parent': 'Jerk Buddies', 'min_date': '2024-04-01'},
    'jonnidarkkoxxx': {'url': 'https://www.jonnidarkkoxxx.com', 'parent': 'Jonni Darkko XXX', 'site': 'Jonni Darkko XXX', 'min_date': '2023-10-23'},
    'joymii': {'url': 'https://www.joymii.com', 'parent': 'Joymii', 'site': 'JoyMii'},
    'kiss-me-fuck-me': {'url': 'https://www.adulttime.com/series/kiss-me-fuck-me', 'parent': 'Kiss Me Fuck Me'},
    'ladygonzo': {'url': 'https://www.ladygonzo.com', 'parent': 'Ladygonzo', 'site': 'Lady Gonzo'},
    'lesbianx.com': {'url': 'https://www.lesbianx.com', 'parent': 'XEmpire'},
    'lethalhardcore': {'url': 'https://www.lethalhardcore.com', 'parent': 'Lethal Hardcore'},
    'lethalhardcorevr': {'url': 'https://www.lethalhardcorevr.com', 'parent': 'Lethal Hardcore VR', 'site': 'Lethal Hardcore VR'},
    'lez-be-bad': {'url': 'https://www.adulttime.com/series/lez-be-bad', 'parent': 'Lez Be Bad', 'site': 'Lez Be Bad'},
    'lustygrandmas': {'parent': 'Lusty Grandmas', 'site': 'Lusty Grandmas', 'min_date': '2019-02-01'},
    'maskurbate': {'url': 'https://www.maskurbate.com', 'parent': 'Maskurbate', 'site': 'Maskurbate', 'min_date': '2023-11-22'},
    'milkingtable': {'url': 'https://www.milkingtable.com', 'parent': 'Milkingtable'},
    'mixedx': {'url': 'https://www.mixedx.com', 'parent': 'Mixedx', 'site': 'Mixed X'},
    'modeltime': {'url': 'https://www.modeltime.com', 'parent': 'Modeltime', 'site': 'Model Time'},
    'moderndaysins': {'url': 'https://www.moderndaysins.com', 'parent': 'Moderndaysins', 'site': 'Modern Day Sins'},
    'mommysgirl': {'url': 'https://www.mommysgirl.com', 'parent': 'Mommysgirl', 'site': 'Mommys Girl'},
    'naked-yoga-life': {'url': 'https://www.adulttime.com/series/naked-yoga-life', 'parent': 'Naked Yoga Life'},
    'nextdoorstudios': {'url': 'https://www.nextdoorstudios.com', 'parent': 'Next Door Studios', 'site': 'Nextdoor Studios'},
    'nudefightclub': {'url': 'https://www.nudefightclub.com', 'parent': 'Nudefightclub'},
    'oopsie': {'url': 'https://www.adulttime.com/series/oopsie', 'parent': 'Oopsie'},
    'peternorth': {'url': 'https://www.peternorth.com', 'parent': 'Peter North'},
    'povthis': {'url': 'https://www.povthis.com', 'parent': 'Povthis', 'site': 'POV This'},
    'prettydirty': {'url': 'https://www.prettydirty.com', 'parent': 'Prettydirty', 'site': 'Pretty Dirty'},
    'pridestudios': {'url': 'https://www.pridestudios.com', 'parent': 'Pride Studios'},
    'puretaboo': {'url': 'https://www.puretaboo.com', 'parent': 'Puretaboo', 'site': 'Pure Taboo'},
    'ragingstallion': {'url': 'https://www.ragingstallion.com', 'parent': 'Ragingstallion', 'site': 'Raging Stallion Studios'},
    'roccosiffredi': {'url': 'https://www.roccosiffredi.com', 'parent': 'Roccosiffredi', 'site': 'Rocco Siffredi'},
    'seemyflixxx': {'url': 'https://www.seemyflixxx.com', 'parent': 'SeeMyFlixxx', 'site': 'SeeMyFlixxx'},
    'shapeofbeauty': {'url': 'https://www.shapeofbeauty.com', 'parent': 'Shape of Beauty'},
    'she-wants-him': {'url': 'https://www.adulttime.com/series/she-wants-him', 'parent': 'She Wants Him'},
    'shower-solos': {'url': 'https://www.adulttime.com/series/shower-solos', 'parent': 'Shower Solos'},
    'soapymassage': {'url': 'https://www.soapymassage.com', 'parent': 'Soapymassage', 'site': 'Soapy Massage'},
    'spankbanggold': {'url': 'https://www.spankbanggold.com', 'parent': 'Spankbang Gold', 'site_from': 'serie_name'},
    'strapattackers': {'url': 'https://www.strapattackers.com', 'parent': 'Evil Angel', 'site': 'Strap Attackers', 'url_format': 'joeysilvera'},
    'switch': {'url': 'https://www.adulttime.com/series/switch', 'parent': 'Switch', 'site': 'Switch'},
    'tabooheat': {'url': 'https://www.tabooheat.com', 'parent': 'Tabooheat', 'site': 'Taboo Heat'},
    'teen-sneaks': {'url': 'https://www.adulttime.com/series/teen-sneaks', 'parent': 'Teen Sneaks'},
    'the-mike-and-joanna-show': {'url': 'https://www.adulttime.com/series/the-mike-and-joanna-show', 'parent': 'The Mike And Joanna Show'},
    'thebrats': {'url': 'https://www.thebrats.com', 'parent': 'Thebrats', 'site': 'The Brats'},
    'transfixed': {'url': 'https://www.transfixed.com', 'parent': 'Transfixed', 'site': 'Transfixed'},
    'transsexualangel': {'url': 'https://www.transsexualangel.com', 'parent': 'Evil Angel'},
    'transsexualroadtrip': {'url': 'https://www.transsexualroadtrip.com', 'parent': 'Transsexualroadtrip', 'site': 'Transsexual Roadtrip'},
    'trickyspa': {'url': 'https://www.trickyspa.com', 'parent': 'Trickyspa', 'site': 'Tricky Spa'},
    'truelesbian': {'url': 'https://www.truelesbian.com', 'parent': 'Truelesbian'},
    'tsfactor': {'url': 'https://www.tsfactor.com', 'parent': 'TS Factor', 'site': 'TS Factor', 'url_format': 'evilangel'},
    'vivid': {'url': 'https://www.vivid.com', 'parent': 'Vivid'},
    'wicked': {'url': 'https://www.wicked.com', 'parent': 'Wicked', 'site': 'Wicked', 'url_format': 'simple'},
    'with-love-lexi': {'url': 'https://www.adulttime.com/series/with-love-lexi', 'parent': 'With Love Lexi', 'site': 'With Love Lexi'},
    'xempire': {'url': 'https://www.xempire.com', 'parent': 'XEmpire'},
    'zerotolerance': {'url': 'https://www.zerotolerancefilms.com', 'parent': 'Zero Tolerance'},
}


# Sites that share the same XEmpire parent block in the original
XEMPIRE_HOSTS = ('xempire', 'allblackx', 'darkx', 'eroticax', 'hardx', 'lesbianx')


# Date-floor rules unrelated to a single site key (move from end of get_scenes)
EXTRA_MIN_DATES = [
    # (predicate(item, scene, referrer) -> bool, min_date 'YYYY-MM-DD')
    # --- cross-cutting: by URL ---
    (lambda item, *_: 'mypervyfamily' in (item.get('url') or ''), '2021-10-06'),
    # --- cross-cutting: by network ---
    (lambda item, *_: 'Falcon Studios' in (item.get('network') or ''), '2023-04-01'),
    # --- bundle sub-sites: by item['site'] (mypervyfamily / Filthy* family) ---
    (lambda item, *_: 'Filthy Blowjobs' in (item.get('site') or ''), '2021-09-14'),
    (lambda item, *_: 'Filthy Massage'  in (item.get('site') or ''), '2021-09-28'),
    (lambda item, *_: 'Filthy Newbies'  in (item.get('site') or ''), '2021-09-21'),
    (lambda item, *_: 'Filthy POV'      in (item.get('site') or ''), '2021-10-05'),
    (lambda item, *_: 'Filthy Taboo'    in (item.get('site') or ''), '2021-10-09'),
    # --- bundle sub-sites: TS Factor family ---
    (lambda item, *_: 'TS Factor' in (item.get('site') or ''), '2021-11-24'),
    # --- bundle sub-sites: 21Sextreme family (Lusty Grandmas etc.) ---
    (lambda item, *_: 'Lusty Grandmas'      in (item.get('site') or ''), '2019-02-01'),
    (lambda item, *_: 'Grandpas Fuck Teens' in (item.get('site') or ''), '2019-02-06'),
    (lambda item, *_: 'Baby Got Balls'      in (item.get('site') or ''), '2008-05-04'),
    (lambda item, *_: 'Creampie Reality'    in (item.get('site') or ''), '2006-10-04'),
    (lambda item, *_: 'Cumming Matures'     in (item.get('site') or ''), '2009-12-01'),
    (lambda item, *_: 'Dominated Girls'     in (item.get('site') or ''), '2013-08-26'),
    (lambda item, *_: 'Home Porn Reality'   in (item.get('site') or ''), '2010-06-18'),
    (lambda item, *_: 'Mandy Is Kinky'      in (item.get('site') or ''), '2008-04-30'),
    (lambda item, *_: 'Mighty Mistress'     in (item.get('site') or ''), '2014-05-20'),
    (lambda item, *_: 'Teach Me Fisting'    in (item.get('site') or ''), '2019-01-29'),
    (lambda item, *_: 'Zoliboy'             in (item.get('site') or ''), '2018-03-18'),
    (lambda item, *_: 'Pee And Blow'        in (item.get('site') or ''), '2009-12-16'),
    (lambda item, *_: 'Speculum Plays'      in (item.get('site') or ''), '2007-09-07'),
]


# ---------------------------------------------------------------------------
# Algolia request bodies. Keys are referrer URL substrings (same matching as
# SITE_CONFIGS). Values are JSON strings with `{page}` placeholders.
# Sites not present here get DEFAULT_ALGOLIA_BODY.
# ---------------------------------------------------------------------------
DEFAULT_ALGOLIA_BODY = '{{"requests":[{{"indexName":"all_scenes_latest_desc","analytics":true,"analyticsTags":["component:searchlisting","section:freetour","site:{slug}","context:videos","device:desktop"],"clickAnalytics":true,"facetingAfterDistinct":true,"facets":["categories.url_name"],"filters":"(upcoming:\'0\') AND availableOnSite:{slug}","highlightPostTag":"__/ais-highlight__","highlightPreTag":"__ais-highlight__","hitsPerPage":60,"maxValuesPerFacet":1000,"page":{page},"query":""}}]}}'

# Per-site Algolia body overrides for non-default cases.
# Use {page} for the page number.
# Port the remaining unique bodies from networkAdulttimeAPI.py here.
ALGOLIA_BODIES = {
    '21naturals': '{"requests":[{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page={page}&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facets=%5B%22availableOnSite%22%2C%22sitename%22%5D&tagFilters=&facetFilters=%5B%5B%22availableOnSite%3A21naturals%22%2C%22availableOnSite%3A21eroticanal%22%2C%22availableOnSite%3A21footart%22%5D%5D"},{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&hitsPerPage=1&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=availableOnSite"}]}',
    '21sextury': '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=1000&page={page}&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&facets=%5B%22categories.name%22%2C%22availableOnSite%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%2C%5B%22availableOnSite%3A21sextury%22%2C%22availableOnSite%3Aanalteenangels%22%2C%22availableOnSite%3Alezcuties%22%2C%22availableOnSite%3Aalettaoceanempire%22%2C%22availableOnSite%3Aassholefever%22%2C%22availableOnSite%3Afootsiebabes%22%2C%22availableOnSite%3Aanalqueenalysa%22%2C%22availableOnSite%3Ablueangellive%22%2C%22availableOnSite%3Abuttplays%22%2C%22availableOnSite%3Acheatingwhorewives%22%2C%22availableOnSite%3Aclubsandy%22%2C%22availableOnSite%3Acutiesgalore%22%2C%22availableOnSite%3Adeepthroatfrenzy%22%2C%22availableOnSite%3Agapeland%22%2C%22availableOnSite%3Ahotmilfclub%22%2C%22availableOnSite%3Aletsplaylez%22%2C%22availableOnSite%3Aonlyswallows%22%2C%22availableOnSite%3Apixandvideo%22%2C%22availableOnSite%3Asexwithkathianobili%22%2C%22availableOnSite%3Asweetsophiemoone%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=1000&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=upcoming&facetFilters=%5B%5B%22availableOnSite%3A21sextury%22%2C%22availableOnSite%3Aanalteenangels%22%2C%22availableOnSite%3Alezcuties%22%2C%22availableOnSite%3Aalettaoceanempire%22%2C%22availableOnSite%3Aassholefever%22%2C%22availableOnSite%3Afootsiebabes%22%2C%22availableOnSite%3Aanalqueenalysa%22%2C%22availableOnSite%3Ablueangellive%22%2C%22availableOnSite%3Abuttplays%22%2C%22availableOnSite%3Acheatingwhorewives%22%2C%22availableOnSite%3Aclubsandy%22%2C%22availableOnSite%3Acutiesgalore%22%2C%22availableOnSite%3Adeepthroatfrenzy%22%2C%22availableOnSite%3Agapeland%22%2C%22availableOnSite%3Ahotmilfclub%22%2C%22availableOnSite%3Aletsplaylez%22%2C%22availableOnSite%3Aonlyswallows%22%2C%22availableOnSite%3Apixandvideo%22%2C%22availableOnSite%3Asexwithkathianobili%22%2C%22availableOnSite%3Asweetsophiemoone%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=1000&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=availableOnSite&facetFilters=%5B%5B%22upcoming%3A0%22%5D%5D"}]}',
    'switch': '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=1000&page={page}&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Amembers%22%2C%22site%3Aadulttime%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22isVR%22%2C%22video_formats%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%2C%22hasPpu%22%2C%22ppu_infos%22%2C%22action_tags%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=(content_tags%3A\'trans\'%20OR%20content_tags%3A\'straight\'%20OR%20content_tags%3A\'lesbian\'%20OR%20content_tags%3A\'gay\'%20OR%20content_tags%3A\'bisex\')&facets=%5B%22hasSubtitle%22%2C%22categories.name%22%2C%22video_formats.format%22%2C%22length_range_15min%22%2C%22actors.name%22%2C%22subtitles.languages%22%2C%22availableOnSite%22%2C%22upcoming%22%2C%22serie_name%22%2C%22network.lvl0%22%5D&tagFilters=&facetFilters=%5B%5B%22serie_name%3ASwitch%22%5D%2C%5B%22upcoming%3A0%22%5D%5D"}]}',
    'with-love-lexi': '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=1000&page={page}&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Amembers%22%2C%22site%3Aadulttime%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=(content_tags%3A\'trans\'%20OR%20content_tags%3A\'straight\'%20OR%20content_tags%3A\'lesbian\'%20OR%20content_tags%3A\'gay\'%20OR%20content_tags%3A\'bisex\')&facets=%5B%22hasSubtitle%22%2C%22categories.name%22%2C%22video_formats.format%22%2C%22length_range_15min%22%2C%22actors.name%22%2C%22subtitles.languages%22%2C%22availableOnSite%22%2C%22upcoming%22%2C%22serie_name%22%2C%22network.lvl0%22%5D&tagFilters=&facetFilters=%5B%5B%22serie_name%3AWith%20Love%2C%20Lexi%22%5D%2C%5B%22upcoming%3A0%22%5D%5D"}]}',
    'allblackx.com': '{"requests":[{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page={page}&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&filters=&facets=%5B%22availableOnSite%22%2C%22categories.name%22%5D&tagFilters=&facetFilters=%5B%5B%22availableOnSite%3Aallblackx%22%5D%5D"}]}',
    'blowpass': '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=10&page={page}&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Ablowpass%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22isVR%22%2C%22video_formats%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%2C%22hasPpu%22%2C%22ppu_infos%22%2C%22action_tags%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=(NOT%20categories.name%3A\'Partner%20Scenes\'%20AND%20NOT%20categories.name%3A\'Compilation\')&facets=%5B%22availableOnSite%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%2C%5B%22availableOnSite%3Athroated%22%2C%22availableOnSite%3Aonlyteenblowjobs%22%2C%22availableOnSite%3A1000facials%22%2C%22availableOnSite%3Aimmorallive%22%2C%22availableOnSite%3Amommyblowsbest%22%2C%22availableOnSite%3Asunlustxxx%22%2C%22availableOnSite%3Asquirtingorgies%22%2C%22availableOnSite%3Ablowbanged%22%2C%22availableOnSite%3Ablowpass%22%2C%22availableOnSite%3Ablowpasspartners%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Ablowpass%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22isVR%22%2C%22video_formats%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%2C%22hasPpu%22%2C%22ppu_infos%22%2C%22action_tags%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=false&filters=(NOT%20categories.name%3A\'Partner%20Scenes\'%20AND%20NOT%20categories.name%3A\'Compilation\')&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=upcoming&facetFilters=%5B%5B%22availableOnSite%3Athroated%22%2C%22availableOnSite%3Aonlyteenblowjobs%22%2C%22availableOnSite%3A1000facials%22%2C%22availableOnSite%3Aimmorallive%22%2C%22availableOnSite%3Amommyblowsbest%22%2C%22availableOnSite%3Asunlustxxx%22%2C%22availableOnSite%3Asquirtingorgies%22%2C%22availableOnSite%3Ablowbanged%22%2C%22availableOnSite%3Ablowpass%22%2C%22availableOnSite%3Ablowpasspartners%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Ablowpass%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22isVR%22%2C%22video_formats%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%2C%22hasPpu%22%2C%22ppu_infos%22%2C%22action_tags%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=false&filters=(NOT%20categories.name%3A\'Partner%20Scenes\'%20AND%20NOT%20categories.name%3A\'Compilation\')&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=availableOnSite&facetFilters=%5B%5B%22upcoming%3A0%22%5D%5D"}]}',
    'chaosmen': '{"requests":[{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page={page}&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&filters=&facets=%5B%22categories.name%22%5D&tagFilters="}]}',
    'devilsfilm': '{"requests":[{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page={page}&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facets=%5B%22availableOnSite%22%2C%22categories.name%22%5D&tagFilters=&facetFilters=%5B%5B%22availableOnSite%3Adevilsfilm%22%2C%22availableOnSite%3Asquirtalicious%22%2C%22availableOnSite%3Ahairyundies%22%2C%22availableOnSite%3Alesbianfactor%22%2C%22availableOnSite%3Adevilsfilmparodies%22%2C%22availableOnSite%3Agivemeteens%22%2C%22availableOnSite%3Aoutofthefamily%22%2C%22availableOnSite%3Adevilsgangbangs%22%2C%22availableOnSite%3AJaneDoePictures%22%2C%22availableOnSite%3Adevilstgirls%22%5D%5D"},{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&hitsPerPage=1&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=availableOnSite"}]}',
    'dfxtra': '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=1000&page={page}&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Amembers%22%2C%22site%3Adfxtra%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=(content_tags%3A\'straight\'%20OR%20content_tags%3A\'lesbian\')&facets=%5B%22channels.name%22%2C%22categories.name%22%2C%22actors.name%22%2C%22video_formats.format%22%2C%22length_range_15min%22%2C%22availableOnSite%22%2C%22categories.name%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%5D"}]}',
    'eroticax.com': '{"requests":[{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page={page}&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&filters=&facets=%5B%22availableOnSite%22%2C%22categories.name%22%5D&tagFilters=&facetFilters=%5B%5B%22availableOnSite%3Aeroticax%22%5D%5D"}]}',
    'falconstudios': '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&page={page}&clickAnalytics=true&facets=%5B%5D&tagFilters=&facetFilters=%5B%22sitename%3A-nakedsword%22%2C%22categories.name%3A-Behind%20The%20Scenes%22%2C%22categories.name%3A-Compilation%22%2C%22categories.name%3A-Enhanced%22%2C%22upcoming%3A0%22%2C%5B%22availableOnSite%3Afalconstudios%22%2C%22availableOnSite%3Ahothouse%22%2C%22availableOnSite%3Afalconstudiospartners%22%5D%5D"}]}',
    'famedigital': '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=10&page={page}&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Afamedigital%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=&facets=%5B%22availableOnSite%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%2C%5B%22availableOnSite%3Asilverstonedvd%22%2C%22availableOnSite%3Asilviasaint%22%2C%22availableOnSite%3Adevilsfilm%22%2C%22availableOnSite%3Awhiteghetto%22%2C%22availableOnSite%3Apeternorth%22%2C%22availableOnSite%3Aterapatrick%22%2C%22availableOnSite%3Afamedigital%22%2C%22availableOnSite%3Aroccosiffredi%22%2C%22availableOnSite%3Alesbianfactor%22%2C%22availableOnSite%3Amyteenoasis%22%2C%22availableOnSite%3Adaringsex%22%2C%22availableOnSite%3Alowartfilms%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Afamedigital%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=false&filters=&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=upcoming&facetFilters=%5B%5B%22availableOnSite%3Asilverstonedvd%22%2C%22availableOnSite%3Asilviasaint%22%2C%22availableOnSite%3Adevilsfilm%22%2C%22availableOnSite%3Awhiteghetto%22%2C%22availableOnSite%3Apeternorth%22%2C%22availableOnSite%3Aterapatrick%22%2C%22availableOnSite%3Afamedigital%22%2C%22availableOnSite%3Aroccosiffredi%22%2C%22availableOnSite%3Alesbianfactor%22%2C%22availableOnSite%3Amyteenoasis%22%2C%22availableOnSite%3Adaringsex%22%2C%22availableOnSite%3Alowartfilms%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Afamedigital%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=false&filters=&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=availableOnSite&facetFilters=%5B%5B%22upcoming%3A0%22%5D%5D"}]}',
    'fantasymassage': '{"requests":[{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page={page}&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facets=%5B%22availableOnSite%22%2C%22sitename%22%5D&tagFilters=&facetFilters=%5B%5B%22availableOnSite%3Anurumassage%22%2C%22availableOnSite%3Aallgirlmassage%22%2C%22availableOnSite%3Asoapymassage%22%2C%22availableOnSite%3Amassage-parlor%22%2C%22availableOnSite%3Amilkingtable%22%2C%22availableOnSite%3Afantasymassage%22%2C%22availableOnSite%3Atrickyspa%22%5D%5D"},{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&hitsPerPage=1&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=availableOnSite"}]}',
    'femboyish': '{"requests":[{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page={page}&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&filters=&facets=%5B%22availableOnSite%22%2C%22categories.name%22%5D&tagFilters=&facetFilters=%5B%5B%22availableOnSite%3Afemboyish%22%5D%5D"},{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&filters=&hitsPerPage=1&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=availableOnSite"}]}',
    'footsiebabes': '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=10&page={page}&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Afootsiebabes%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=&facets=%5B%22availableOnSite%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%2C%5B%22availableOnSite%3Afootsiebabes%22%2C%22availableOnSite%3A21footart%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Afootsiebabes%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=false&filters=&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=upcoming&facetFilters=%5B%5B%22availableOnSite%3Afootsiebabes%22%2C%22availableOnSite%3A21footart%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Afootsiebabes%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=false&filters=&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=availableOnSite&facetFilters=%5B%5B%22upcoming%3A0%22%5D%5D"}]}',
    'gangbangcreampie': '{"requests":[{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page={page}&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facets=%5B%22availableOnSite%22%2C%22categories.name%22%5D&tagFilters=&facetFilters=%5B%5B%22availableOnSite%3Agangbangcreampie%22%5D%5D"},{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&hitsPerPage=1&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=availableOnSite"}]}',
    'girlsway': '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=1000&page={page}&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&facets=%5B%22categories.name%22%2C%22availableOnSite%22%2C%22upcoming%22%2C%22sitename%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%2C%5B%22availableOnSite%3Alesbianfactor%22%2C%22availableOnSite%3Aallgirlmassage%22%2C%22availableOnSite%3Awebyoung%22%2C%22availableOnSite%3Agirlsway%22%2C%22availableOnSite%3Asextapelesbians%22%2C%22availableOnSite%3Agirlstryanal%22%2C%22availableOnSite%3Alezcuties%22%2C%22availableOnSite%3Asquirtinglesbian%22%2C%22availableOnSite%3Aoldyounglesbianlove%22%2C%22availableOnSite%3Agirlcore%22%2C%22availableOnSite%3Awelikegirls%22%2C%22availableOnSite%3Alesbianrevenge%22%2C%22availableOnSite%3Amomsonmoms%22%2C%22availableOnSite%3Awheretheboysarent%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=1000&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=upcoming&facetFilters=%5B%5B%22availableOnSite%3Alesbianfactor%22%2C%22availableOnSite%3Aallgirlmassage%22%2C%22availableOnSite%3Awebyoung%22%2C%22availableOnSite%3Agirlsway%22%2C%22availableOnSite%3Asextapelesbians%22%2C%22availableOnSite%3Agirlstryanal%22%2C%22availableOnSite%3Alezcuties%22%2C%22availableOnSite%3Asquirtinglesbian%22%2C%22availableOnSite%3Aoldyounglesbianlove%22%2C%22availableOnSite%3Agirlcore%22%2C%22availableOnSite%3Awelikegirls%22%2C%22availableOnSite%3Alesbianrevenge%22%2C%22availableOnSite%3Amomsonmoms%22%2C%22availableOnSite%3Awheretheboysarent%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=1000&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=availableOnSite&facetFilters=%5B%5B%22upcoming%3A0%22%5D%5D"}]}',
    'gloryholesecrets': '{"requests":[{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page={page}&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&filters=&facets=%5B%22availableOnSite%22%2C%22categories.name%22%5D&tagFilters=&facetFilters=%5B%5B%22availableOnSite%3Agloryholesecrets%22%5D%5D"},{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&filters=&hitsPerPage=1&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=availableOnSite"}]}',
    'hardx.com': '{"requests":[{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page={page}&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&filters=&facets=%5B%22availableOnSite%22%2C%22categories.name%22%5D&tagFilters=&facetFilters=%5B%5B%22availableOnSite%3Ahardx%22%5D%5D"}]}',
    'isthisreal': '{"requests":[{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page={page}&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facets=%5B%22availableOnSite%22%2C%22sitename%22%5D&tagFilters=&facetFilters=%5B%5B%22availableOnSite%3Atrickyspa%22%2C%22availableOnSite%3Asextapelesbians%22%2C%22availableOnSite%3Agirlsunderarrest%22%2C%22availableOnSite%3Abethecuck%22%2C%22availableOnSite%3Asistertrick%22%2C%22availableOnSite%3Aisthisreal%22%5D%5D"},{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&hitsPerPage=1&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=availableOnSite"}]}',
    'lesbianx.com': '{"requests":[{"indexName":"all_scenes","params":"query=&maxValuesPerFacet=1000&page={page}&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&filters=&facets=%5B%22availableOnSite%22%2C%22categories.name%22%5D&tagFilters=&facetFilters=%5B%5B%22availableOnSite%3Alesbianx%22%5D%5D"}]}',
    'nextdoorstudios': '{"requests":[{"indexName":"all_scenes","params":"query=&hitsPerPage=36&maxValuesPerFacet=1000&page={page}&analytics=true&analyticsTags=%5B%22device%3Adesktop%22%2C%22instantsearch%22%2C%22site%3Anextdoorstudios%22%2C%22section%3Afreetour%22%2C%22page%3Avideos%22%5D&clickAnalytics=true&filters=NOT%20categories.category_id%3A4631%20AND%20NOT%20site_id%3A107%20AND%20NOT%20site_id%3A%20118%20AND%20NOT%20serie_name%3A\'Member%20Compilations\'&facets=%5B%22categories.name%22%2C%22actors.name%22%2C%22sitename%22%2C%22length_range_15min%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%5D"},{"indexName":"all_scenes","params":"query=&hitsPerPage=1&maxValuesPerFacet=1000&page=0&analytics=false&analyticsTags=%5B%22device%3Adesktop%22%2C%22instantsearch%22%2C%22site%3Anextdoorstudios%22%2C%22section%3Afreetour%22%2C%22page%3Avideos%22%5D&clickAnalytics=false&filters=NOT%20categories.category_id%3A4631%20AND%20NOT%20site_id%3A107%20AND%20NOT%20site_id%3A%20118%20AND%20NOT%20serie_name%3A\'Member%20Compilations\'&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=upcoming"}]}',
    'pridestudios': '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=10&page={page}&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Apridestudios%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=&facets=%5B%22availableOnSite%22%2C%22sitename%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Apridestudios%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=false&filters=&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=upcoming"}]}',
    'seemyflixxx': '{"requests":[{"indexName":"all_scenes_latest_desc","analytics":true,"analyticsTags":["component:searchlisting","section:freetour","site:seemyflixxx","context:videos","device:desktop"],"clickAnalytics":true,"facetingAfterDistinct":true,"filters":"(upcoming:\'0\')","highlightPostTag":"__/ais-highlight__","highlightPreTag":"__ais-highlight__","hitsPerPage":60,"page":{page},"query":""}]}',
    'transfixed': '{"requests":[{"indexName":"all_scenes_latest_desc","params":"analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Atransfixed%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&clickAnalytics=true&facetingAfterDistinct=true&facets=%5B%22categories.url_name%22%2C%22sitename%22%5D&filters=(content_tags%3A\'trans\')%20AND%20(upcoming%3A\'0\')%20AND%20availableOnSite%3Adevilsfilm%20OR%20availableOnSite%3Aburningangel%20OR%20availableOnSite%3Apuretaboo%20OR%20availableOnSite%3Atransfixed%20OR%20availableOnSite%3Awelikegirls%20OR%20availableOnSite%3Acaughtfapping%20OR%20availableOnSite%3ABeingTrans247%20OR%20availableOnSite%3ATransgressiveFilms-channel%20OR%20availableOnSite%3Amuses-channel%20OR%20availableOnSite%3Adolls-channel&highlightPostTag=__%2Fais-highlight__&highlightPreTag=__ais-highlight__&hitsPerPage=60&maxValuesPerFacet=1000&page={page}&query=&tagFilters="}]}',
    'transsexualangel': '{"requests":[{"indexName":"all_scenes_latest_desc","params":"analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Atranssexualangel%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&clickAnalytics=true&facetingAfterDistinct=true&facets=%5B%22categories.url_name%22%5D&filters=(categories.name%3A\'Trans\')%20AND%20(compilation%3A\'0\')%20AND%20(NOT%20categories.name%3A\'Member%20Compilation\')%20AND%20(compilation%3A\'0\')%20AND%20(upcoming%3A\'0\')%20AND%20availableOnSite%3Aevilangel%20OR%20availableOnSite%3Atranssexualangel&highlightPostTag=__%2Fais-highlight__&highlightPreTag=__ais-highlight__&hitsPerPage=60&maxValuesPerFacet=1000&page={page}&query=&tagFilters="}]}',
    'tsfactor': '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=10&page={page}&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Atsfactor%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=&facets=%5B%22availableOnSite%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%2C%5B%22availableOnSite%3Ashemaleidol%22%2C%22availableOnSite%3Atsfactor%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Atsfactor%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=false&filters=&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=upcoming&facetFilters=%5B%5B%22availableOnSite%3Ashemaleidol%22%2C%22availableOnSite%3Atsfactor%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Atsfactor%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=false&filters=&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=availableOnSite&facetFilters=%5B%5B%22upcoming%3A0%22%5D%5D"}]}',
    'vivid': '{"requests":[{"indexName":"all_scenes_latest_desc","params":"analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Atour1%22%2C%22site%3Avivid%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&clickAnalytics=true&facetingAfterDistinct=true&facets=%5B%22categories.url_name%22%2C%22sitename%22%5D&filters=(upcoming%3A\'0\')%20AND%20availableOnSite%3Avividgirls%20OR%20availableOnSite%3A65inchhugeasses%20OR%20availableOnSite%3Ablackwhitefuckfest%20OR%20availableOnSite%3Abrandnewfaces%20OR%20availableOnSite%3Agirlswhofuckgirls%20OR%20availableOnSite%3Amomisamilf%20OR%20availableOnSite%3Anastystepfamily%20OR%20availableOnSite%3Anineteen%20OR%20availableOnSite%3Aorgytrain%20OR%20availableOnSite%3Apetited%20OR%20availableOnSite%3Avivid%20OR%20availableOnSite%3Avividceleb%20OR%20availableOnSite%3Avividclassic%20OR%20availableOnSite%3Atsdivas%20OR%20availableOnSite%3Awheretheboysarent%20OR%20availableOnSite%3Athebrats&highlightPostTag=__%2Fais-highlight__&highlightPreTag=__ais-highlight__&hitsPerPage=60&maxValuesPerFacet=1000&page={page}&query=&tagFilters="}]}',
    'xempire': '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=10&page={page}&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Axempire%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=compilation%3A%200&facets=%5B%22availableOnSite%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%2C%5B%22availableOnSite%3Aeroticax%22%2C%22availableOnSite%3Ahardx%22%2C%22availableOnSite%3Adarkx%22%2C%22availableOnSite%3Alesbianx%22%2C%22availableOnSite%3Axempire%22%2C%22availableOnSite%3Aallblackx%22%2C%22availableOnSite%3Axempirepartners%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Axempire%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=false&filters=compilation%3A%200&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=upcoming&facetFilters=%5B%5B%22availableOnSite%3Aeroticax%22%2C%22availableOnSite%3Ahardx%22%2C%22availableOnSite%3Adarkx%22%2C%22availableOnSite%3Alesbianx%22%2C%22availableOnSite%3Axempire%22%2C%22availableOnSite%3Aallblackx%22%2C%22availableOnSite%3Axempirepartners%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=10&page=0&analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Afreetour%22%2C%22site%3Axempire%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22action_tags%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=false&filters=compilation%3A%200&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=availableOnSite&facetFilters=%5B%5B%22upcoming%3A0%22%5D%5D"}]}',
    'zerotolerance': '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=1000&page={page}&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&facets=%5B%22categories.name%22%2C%22serie_name%22%2C%22actors.name%22%2C%22availableOnSite%22%2C%22upcoming%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=1000&page=0&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=false&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=upcoming"}]}',
}


# ---------------------------------------------------------------------------
# Skip rules — sites whose scenes always get filtered out by the original
# ---------------------------------------------------------------------------
SKIP_SITENAME_SUBSTRINGS = ('evilangelpartner', 'nudefightclub')


def resolve_site_config(referrer_url):
    """Return the (key, config) for the first SITE_CONFIGS entry whose key
    appears in `referrer_url`. XEmpire family is special-cased."""
    if any(host in referrer_url for host in XEMPIRE_HOSTS):
        return 'xempire', {'parent': 'XEmpire'}
    for key, cfg in SITE_CONFIGS.items():
        if key in referrer_url:
            return key, cfg
    return None, {}


def build_url(site_key, scene, base_url, format_url):
    """Construct item['url'] using the site's url_format rule."""
    cfg = SITE_CONFIGS.get(site_key, {})
    fmt = cfg.get('url_format', 'sitename')
    if fmt == 'simple':
        path = f"/en/video/{scene['url_title']}/{scene['clip_id']}"
    elif fmt == 'sitename':
        path = f"/en/video/{scene['sitename']}/{scene['url_title']}/{scene['clip_id']}"
    else:  # literal segment
        path = f"/en/video/{fmt}/{scene['url_title']}/{scene['clip_id']}"
    return format_url(base_url, path)


# ---------------------------------------------------------------------------
# Spider
# ---------------------------------------------------------------------------
class AdultTimeAPISpider(BaseSceneScraper):
    name = 'AdulttimeAPI'
    network = 'Gamma Enterprises'

    start_urls = [cfg['url'] for cfg in SITE_CONFIGS.values() if cfg.get('enabled', True) and 'url' in cfg]

    image_sizes = ['1920x1080', '1280x720', '960x544', '638x360', '201x147', '406x296', '307x224']
    trailer_sizes = ['1080p', '720p', '4k', '540p', '480p', '360p', '240p', '160p']

    custom_scraper_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.62',
        'CONCURRENT_REQUESTS': 4,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 4,
        'MEDIA_ALLOW_REDIRECTS': True,
    }

    selector_map = {
        'external_id': r'(\d+)$',
        'pagination': '/en/videos?page=%s',
    }

    # ------------------------------------------------------------------
    # Bootstrap
    # ------------------------------------------------------------------
    async def start(self):
        if not getattr(self, 'start_urls', None):
            raise AttributeError('start_urls missing')
        page = int(self.page) - 1
        for link in self.start_urls:
            url = link if '/series/' in link else self.get_next_page_url(link, page + 1)
            yield scrapy.Request(url, callback=self.parse_token, meta={'page': page, 'url': link})

    def get_next_page_url(self, base, page):
        # A handful of sites use a different pagination URL pattern
        alt = ('isthisreal', 'touchmywife', 'zerotolerance', 'povthis', 'tabooheat', 'puretaboo', 'pridestudios', 'prettydirty', 'gangbangcreampie')
        pagination = '/en/videos/page/%s' if any(x in base for x in alt) else self.get_selector_map('pagination')
        if int(page) == 1:
            return self.format_url(base, '/en/videos')
        return self.format_url(base, pagination % page)

    def parse_token(self, response):
        token = re.search(r'"apiKey":"(.*?)"', response.text).group(1)
        return self.call_algolia(response.meta['page'], token, response.meta['url'])

    def parse(self, response, **kwargs):
        if response.status != 200:
            return

        test_mode = self.settings.getbool('test')
        if test_mode:
            elapsed = response.meta.get('download_latency', 0)
            try:
                hits = response.json()['results'][0]['hits']
            except Exception:
                hits = []
            print(f"[TEST] site={response.meta['url']:<55} api_time={elapsed:5.2f}s  scenes_in_response={len(hits):4d}")

        count = 0
        for scene in self.get_scenes(response):
            count += 1
            yield scene

        # In test mode: don't paginate, only the first page
        if test_mode:
            return

        if count and 'page' in response.meta and response.meta['page'] < self.limit_pages:
            yield self.call_algolia(response.meta['page'] + 1, response.meta['token'], response.meta['url'])

    # ------------------------------------------------------------------
    # Scene parsing
    # ------------------------------------------------------------------
    def get_scenes(self, response):
        referrer_url = response.meta['url']
        site_key, cfg = resolve_site_config(referrer_url)

        force_update = bool(self.settings.get('force_update'))
        force_fields = (self.settings.get('force_fields') or '').split(',')

        hits = response.json()['results'][0]['hits']
        if self.settings.getbool('test'):
            hits = hits[:5]  # process only first 5 scenes per site in test mode

        for scene in hits:
            item = self.init_scene()

            # date / id / title / description / tags / duration / director / markers
            self._populate_basics(item, scene, force_update, force_fields)

            if not self.check_item(item, self.days):
                continue

            # site / parent / network / url
            self._populate_site_fields(item, scene, site_key, cfg, referrer_url)

            # performers
            self._populate_performers(item, scene, force_update, force_fields)

            # date floors and skip rules
            if self._should_skip(item, scene, referrer_url, cfg):
                continue
            if any(x in scene['sitename'] for x in SKIP_SITENAME_SUBSTRINGS):
                continue

            yield self.check_item(item, self.days)

    # ----- helpers -----

    def _populate_basics(self, item, scene, force_update, force_fields):
        release_date = scene.get('release_date')
        if release_date and self.parse_date(release_date):
            item['date'] = self.parse_date(release_date).strftime('%Y-%m-%d')

        if not force_update or 'image' in force_fields:
            item['image'] = ''
            for size in self.image_sizes:
                if size in scene.get('pictures', {}):
                    item['image'] = 'https://images-fame.gammacdn.com/movies' + scene['pictures'][size]
                    break
            item['image_blob'] = self.get_image_blob_from_link(item['image']) if item['image'] else ''
        else:
            item['image'] = ''
            item['image_blob'] = ''

        item['trailer'] = ''
        for size in self.trailer_sizes:
            if scene.get('trailers') and size in scene['trailers']:
                item['trailer'] = scene['trailers'][size]
                break

        item['id'] = scene['objectID'].split('-')[0]
        title = scene.get('title') or scene.get('movie_title') or ''
        item['title'] = string.capwords(title)
        item['description'] = scene.get('description') or scene.get('_highlightResult', {}).get('description', {}).get('value', '') or ''

        item['tags'] = list(filter(None, [c['name'] for c in scene.get('categories', [])]))
        item['duration'] = str(scene.get('length', ''))

        directors = scene.get('directors') or []
        if directors:
            item['director'] = directors[0]['name']

        item['markers'] = []
        for action in scene.get('action_tags') or []:
            marker = {'name': action['name'], 'start': str(action['timecode'])}
            if marker['name'] not in item['tags']:
                item['tags'].append(marker['name'])
            item['markers'].append(marker)

    def _populate_site_fields(self, item, scene, site_key, cfg, referrer_url):
        # site_from wins (e.g. spankbanggold uses scene['serie_name']).
        # Otherwise: match_site translates the scene's sitename (handles bundle sub-sites
        # like '21sextury' → 'assholefever' → 'Asshole Fever'). If match_site returns
        # the slug unchanged (no translation found), fall back to cfg['site'] — that
        # covers single sites whose sub-sitenames aren't in SITE_NAMES (e.g. jonnidarkkoxxx
        # returning 'analtrixxx' → label as 'Jonni Darkko XXX').
        if 'site_from' in cfg:
            item['site'] = scene.get(cfg['site_from'], '')
        else:
            sitename = scene.get('sitename', '')
            translated = match_site(sitename)
            if translated == sitename and 'site' in cfg:
                item['site'] = cfg['site']
            else:
                item['site'] = translated

        item['parent'] = cfg.get('parent', item['site'])
        item['network'] = cfg.get('network', self.network)
        item['url'] = build_url(site_key, scene, referrer_url, self.format_url)

        for tag in cfg.get('extra_tags', []):
            if tag not in item['tags']:
                item['tags'].append(tag)

    def _populate_performers(self, item, scene, force_update, force_fields):
        item['performers'] = []
        item['performers_data'] = []
        for performer in scene.get('actors') or []:
            name = performer['name']
            if ' ' not in name:
                name = f"{name} {performer['actor_id']}"
            item['performers'].append(name)

            perf = {'name': name, 'site': item['site']}
            gender = performer.get('gender')
            if gender:
                if gender.title() == 'Shemale':
                    gender = 'Transgender Female'
                perf['extra'] = {'gender': gender.title()}
            perf['image'] = f"https://transform.gammacdn.com/actors/{performer['actor_id']}/{performer['actor_id']}_500x750.jpg?width=500&height=750&format=webp"
            if not force_update or 'performers' in force_fields:
                req = requests.get(perf['image'])
                if req.ok:
                    perf['image_blob'] = base64.b64encode(req.content).decode('utf-8')
            item['performers_data'].append(perf)

    def _should_skip(self, item, scene, referrer_url, cfg):
        # per-config min_date
        if cfg.get('min_date') and item.get('date', '') < cfg['min_date']:
            return True
        # cross-cutting min-date rules
        for predicate, min_date in EXTRA_MIN_DATES:
            if predicate(item, scene, referrer_url) and item.get('date', '') < min_date:
                return True
        # Old Young Lesbian Love is returned both from Girlsway and 21Sextreme — only pull from Girlsway
        if 'oldyounglesbianlove' in scene['sitename'] and '21sextreme' in referrer_url:
            return True
        return False

    # ------------------------------------------------------------------
    # Algolia request
    # ------------------------------------------------------------------
    def call_algolia(self, page, token, referrer):
        # Choose the agent string that matches the referrer (preserved from original)
        if 'ragingstallion' in referrer:
            agent = 'Algolia%20for%20JavaScript%20(3.35.1)%3B%20Browser%20(lite)%3B%20react%20(17.0.2)%3B%20react-instantsearch%20(5.7.0)%3B%20JS%20Helper%202.26.0'
        elif 'falconstudios' in referrer:
            agent = 'Algolia%20for%20vanilla%20JavaScript%203.27.1%3BJS%20Helper%202.26.0'
        else:
            agent = 'Algolia%20for%20JavaScript%20(3.35.1)%3B%20Browser%20(lite)%3B%20react%20(16.14.0)%3B%20react-instantsearch%20(5.7.0)%3B%20JS%20Helper%202.26.0'

        algolia_url = f'https://tsmkfa364q-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent={agent}&x-algolia-application-id=TSMKFA364Q&x-algolia-api-key={token}'

        # Resolve the body: a per-site override, or fall back to the default
        site_key, _ = resolve_site_config(referrer)
        if site_key in ALGOLIA_BODIES:
            # ported bodies have raw JSON braces; only {page} is a placeholder
            jbody = ALGOLIA_BODIES[site_key].replace('{page}', str(page))
        else:
            # default has braces escaped as {{ }}; .format() handles {slug} and {page}
            slug = re.sub(r'^https?://(www\.)?', '', referrer).split('.')[0]
            jbody = DEFAULT_ALGOLIA_BODY.format(slug=slug, page=page)

        headers = {
            'Content-Type': 'application/json',
            'Referer': self.get_next_page_url(referrer, page),
        }
        if 'falconstudios' in referrer:
            headers['Referer'] = 'https://www.falconstudios.com'

        return scrapy.Request(url=algolia_url, method='POST', body=jbody, meta={'token': token, 'page': page, 'url': referrer}, callback=self.parse, headers=headers)
