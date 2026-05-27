import os
import json
import ctypes
import shutil
from sys import platform
from collections import defaultdict

from PySide6.QtGui import QImage, QPixmap
import PeakDeskSprite.conf as conf
from PeakDeskSprite.conf import PetData, TaskData, ActData, ItemData
from PeakDeskSprite import app_identity
from PeakDeskSprite.resource_paths import resource_root, resource_path
from PeakDeskSprite.runtime_paths import app_config_dir, runtime_data_dir
from PySide6 import QtCore

basedir = resource_root()
BASEDIR = basedir
conf.basedir = basedir

configdir = app_config_dir()
CONFIGDIR = configdir

DEFAULT_THEME_COL = "#009faa"
PREFERRED_DEFAULT_PET = "BestFriendsCodex"

LLM_BUBBLE_PRESETS = {
    "quiet": {
        "ambient_min_seconds": 180,
        "ambient_max_seconds": 360,
        "min_bubble_cooldown_seconds": 45,
        "pat_bubble_probability": 0.2,
        "scheduled_bubble_probability": 0.1,
    },
    "balanced": {
        "ambient_min_seconds": 60,
        "ambient_max_seconds": 120,
        "min_bubble_cooldown_seconds": 20,
        "pat_bubble_probability": 0.6,
        "scheduled_bubble_probability": 0.35,
    },
    "active": {
        "ambient_min_seconds": 30,
        "ambient_max_seconds": 90,
        "min_bubble_cooldown_seconds": 15,
        "pat_bubble_probability": 0.8,
        "scheduled_bubble_probability": 0.5,
    },
}
LLM_BUBBLE_PRESET_KEYS = tuple(LLM_BUBBLE_PRESETS.keys()) + ("custom",)

LLM_DEFAULT_CONFIG = {
    "enabled": False,
    "provider": "OpenAI",
    "base_url": "https://api.openai.com/v1",
    "model": "",
    "api_key_env_var": app_identity.LLM_API_KEY_ENV,
    "bubble_mode": "pat_random",
    "bubble_frequency_preset": "balanced",
    "ambient_enabled": True,
    "ambient_min_seconds": 60,
    "ambient_max_seconds": 120,
    "min_bubble_cooldown_seconds": 20,
    "pat_bubble_probability": 0.6,
    "scheduled_bubble_probability": 0.35,
    "temperature": 0.8,
    "max_tokens": 80,
    "chat_max_tokens": 800,
    "chat_stream_enabled": True,
    "timeout": 20,
    "max_reply_chars": 160,
    "max_chat_reply_chars": 4000,
    "system_prompt": (
        "You are a small desktop pet. Reply with one warm, playful, concise "
        "bubble message. Keep it under 40 Chinese characters or 25 English "
        "words. Do not mention that you are an AI model."
    ),
}

llm_provider_config = LLM_DEFAULT_CONFIG.copy()


def _read_json_file(path):
    with open(path, 'r', encoding='utf-8-sig') as file:
        return json.load(file)


RUNTIME_DATA_FILES = [
    'settings.json',
    'pet_data.json',
    'act_data.json',
    'task_data.json',
    'llm_secrets.json',
    'llm_chat_history.json',
    'version',
    'remindme.txt',
]


def _legacy_data_dirs():
    candidates = []
    for root in [resource_root(), os.getcwd()]:
        if root is None:
            continue
        candidates.append(os.path.abspath(os.path.join(root, 'data')))

    unique_candidates = []
    seen = set()
    for path in candidates:
        norm = os.path.normcase(os.path.normpath(path))
        if norm not in seen:
            seen.add(norm)
            unique_candidates.append(path)
    return unique_candidates


def _migrate_runtime_data():
    target_dir = os.path.abspath(runtime_data_dir(configdir))
    os.makedirs(target_dir, exist_ok=True)
    target_norm = os.path.normcase(os.path.normpath(target_dir))

    for source_dir in _legacy_data_dirs():
        if os.path.normcase(os.path.normpath(source_dir)) == target_norm:
            continue
        if not os.path.isdir(source_dir):
            continue

        for filename in RUNTIME_DATA_FILES:
            source_file = os.path.join(source_dir, filename)
            target_file = os.path.join(target_dir, filename)
            if os.path.isfile(source_file) and not os.path.exists(target_file):
                shutil.copy2(source_file, target_file)

PROJECT_URL = app_identity.PROJECT_URL
HELP_URL = app_identity.HELP_URL
DEVDOC_URL = app_identity.DEVDOC_URL
VERSION = "v0.8.5"
AUTHOR = "https://github.com/ChaozhongLiu"
CHARCOLLECT_LINK = app_identity.CHARCOLLECT_LINK
ITEMCOLLECT_LINK = app_identity.ITEMCOLLECT_LINK
PETCOLLECT_LINK = app_identity.PETCOLLECT_LINK

RELEASE_API = app_identity.RELEASE_API
RELEASE_URL = app_identity.RELEASE_URL
UPDATE_NEEDED = False

HP_TIERS = [0,50,80,100]
TIER_NAMES = ['Starving', 'Hungry', 'Normal', 'Energetic']
HP_INTERVAL = 2
LVL_BAR_V1 = [20, 120, 300, 600, 1200, 1800, 2400, 3200]
LVL_BAR = [20] + [120]*200
PP_HEART = 0.8
PP_COIN = 0.9
COIN_MU = 10
COIN_SIGMA = 5
PP_ITEM = 0.95
PP_AUDIO = 0.8
PP_BUBBLE = 0.15

# Depreciation when sell item to shop
ITEM_DEPRECIATION = 0.75

# Coin reward once a task is checked from Task Panel
SINGLETASK_REWARD = 200
# Coin reward every 5 task
FIVETASK_REWARD = 1500
# Multiply HP and FV effect if item is required by bubble `feed_required`
FACTOR_FEED_REQ = 5

HUNGERSTR = "Satiety"
FAVORSTR = "Favorability"

LINK_PERMIT = {"BiliBili":"https://space.bilibili.com/",
               "微博":"https://m.weibo.cn/profile/",
               "抖音": "https://www.douyin.com/user/",
               "GitHub":"https://github.com/",
               "爱发电":"https://afdian.net/a/",
               "TikTok":"https://www.tiktok.com/",
               "YouTube":"https://www.youtube.com/"}

ITEM_BGC = {'consumable': '#EFEBDF',
            'collection': '#e1eaf4',
            'Empty': '#f0f0ef',
            'dialogue': '#e1eaf4',
            'subpet': '#f6eae9',
            'autofeed': '#e7f1e4'}
ITEM_BGC_DEFAULT = '#EFEBDF'
ITEM_BDC = '#B1C790'

# when falling met the screen boundary, 
# it will be bounced back with this speed decay factor
SPEED_DECAY = 0.5
AUTOFEED_THRESHOLD = 60

def init():
    # computer system ==================================================
    global platform
    platform = platform

    # check if data directory exists ===================================
    _migrate_runtime_data()
    
    global pet_conf
    pet_conf = None

    # Image and animation related variable =============================
    global current_img, previous_img
    # Make img-to-show a global variable for multi-thread behaviors
    current_img = None #QPixmap()
    previous_img = None #Pixmap()
    global current_anchor, previous_anchor
    current_anchor = [0,0]
    previous_anchor = [0,0]

    global onfloor, draging, set_fall, playid
    global mouseposx1,mouseposx2,mouseposx3,mouseposx4,mouseposx5
    global mouseposy1,mouseposy2,mouseposy3,mouseposy4,mouseposy5
    global dragspeedx,dragspeedy,fixdragspeedx, fixdragspeedy, fall_right, gravity, prefall
    # Drag and fall related global variable
    onfloor = 1
    draging = 0
    set_fall = True # default is allow drag
    playid = 0
    mouseposx1,mouseposx2,mouseposx3,mouseposx4,mouseposx5=0,0,0,0,0
    mouseposy1,mouseposy2,mouseposy3,mouseposy4,mouseposy5=0,0,0,0,0
    dragspeedx,dragspeedy=0,0
    fixdragspeedx, fixdragspeedy = 1.0, 1.0
    fall_right = False
    gravity = 0.1
    prefall = 0

    global act_id, current_act, previous_act
    # Select animation to show
    act_id = 0
    current_act, previous_act = None, None

    global showing_dialogue_now
    showing_dialogue_now = False

    # size settings
    global size_factor, screen_scale, font_factor, status_margin, statbar_h, tunable_scale
    try:
        size_factor = 1.0 #ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
    except:
        size_factor = 1.0
    tunable_scale = 1.0

    # buff related arguments
    global HP_stop, FV_stop
    HP_stop = False
    FV_stop = False

    # sound volumn =====================================================
    global volume
    volume = 0.4

    # pet name =========================================================
    global petname
    petname = ''

    # which screen =====================================================
    global screens, current_screen
    screens = []
    current_screen = None

    # Always on top ====================================================
    global on_top_hint, pets
    on_top_hint = True

    # Translations ====================================================
    global lang_dict
    lang_dict = _read_json_file(resource_path('res', 'language', 'language.json'))

    # Settings =========================================================
    pets = get_petlist(resource_path('res', 'role'))
    init_settings()
    global default_pet
    if default_pet not in pets:
        default_pet = PREFERRED_DEFAULT_PET if PREFERRED_DEFAULT_PET in pets else pets[0]
    else:
        pets.remove(default_pet)
        pets.sort()
        pets = [default_pet] + pets
    save_settings()

    # Focus Timer
    global focus_timer_on
    focus_timer_on = False

    # Load in pet data ================================================
    global pet_data 
    pet_data = PetData(pets)

    # Load in task data ================================================
    global task_data 
    task_data = TaskData()

    # Init animation config data ================================================
    global act_data 
    act_data = ActData(pets)

    # Load in Language Choice ==========================================
    global language_code, translator
    change_translator(language_code)

    # Load in items data ==========================================
    global items_data, required_item
    items_data = None
    required_item = None



'''
def init_pet():
    global pet_data 
    pet_data = PetData()
    init_settings()
    save_settings()
'''


def init_settings():
    global file_path, settingGood
    file_path = os.path.join(runtime_data_dir(configdir), 'settings.json')

    global gravity, fixdragspeedx, fixdragspeedy, tunable_scale, scale_dict, volume, \
           language_code, on_top_hint, default_pet, defaultAct, themeColor, minipet_scale, \
           toaster_on, usertag_dict, auto_lock, bubble_on, llm_provider_config

    # check json file integrity
    try:
        _read_json_file(file_path)
        settingGood = True
    except:
        if os.path.isfile(file_path):
            settingGood = False
        else:
            settingGood = True

    if os.path.isfile(file_path) and settingGood:
        data_params = _read_json_file(file_path)

        fixdragspeedx, fixdragspeedy = data_params['fixdragspeedx'], data_params['fixdragspeedy']
        gravity = data_params['gravity']
        #tunable_scale = data_params['tunable_scale']
        volume = data_params['volume']
        language_code = data_params.get('language_code', QtCore.QLocale().name())
        on_top_hint = data_params.get('on_top_hint', True)
        default_pet = data_params.get('default_pet', pets[0])
        defaultAct = data_params.get('defaultAct', {})
        themeColor = data_params.get('themeColor', None)

        # Fix a bug version distributed to users =============
        if defaultAct is None:
            defaultAct = {}
        elif type(defaultAct) == str:
            defaultAct = {}

        for pet in pets:
            defaultAct[pet] = defaultAct.get(pet, None)
        #=====================================================

        # update for app <= v0.2.2 ===========================
        if language_code == 'CN':
            language_code = QtCore.QLocale().name()
        #=====================================================

        # v0.4.8 update ======================================
        global set_fall
        set_fall = data_params.get('set_fall', True)
        #=====================================================

        # v0.5.0 update ======================================
        # First time open v0.5.0, get the original 
        # tunable_scale as all default
        tunable_scale = data_params.get('tunable_scale', 1.0)
        # v0.5.0 tunable_scales are specified for each character
        scale_dict_tmp = data_params.get('scale_dict', {})
        scale_dict = {}
        for pet in pets:
            pet_scale = scale_dict_tmp.get(pet, tunable_scale)
            # Ensure type is int
            try:
                pet_scale = float(pet_scale)
            except:
                pet_scale = 1.0
            pet_scale = max( 0, min(5, pet_scale) )
            scale_dict[pet] = pet_scale
        tunable_scale = scale_dict[default_pet]

        # mini-pet scale settings
        minipet_scale = data_params.get('minipet_scale', defaultdict(dict))
        minipet_scale = check_dict_datatype(minipet_scale, dict, {})
        minipet_scale = defaultdict(dict, minipet_scale)
        for minipet, sdict in minipet_scale.items():
            minipet_scale[minipet] = check_dict_datatype(sdict, float, 1.0)
        #=====================================================

        # v0.5.3 Toaster can be turned off
        toaster_on = data_params.get('toaster_on', True)
        #=====================================================

        # v0.6.1 User Tag (how pet will call the user)
        usertag_dict_tmp = data_params.get('usertag_dict', {})
        usertag_dict = {}
        for pet in pets:
            usertag = usertag_dict_tmp.get(pet, '')
            usertag_dict[pet] = usertag

        # v0.6.5 stop HP & FV changes when screen locked
        auto_lock = data_params.get('auto_lock', False)
        #=====================================================

        # v0.6.7 Bubble can be turned off
        bubble_on = data_params.get('bubble_on', True)
        #=====================================================

        # LLM provider for dynamic dialogue bubbles
        llm_provider_config = _normalize_llm_config(data_params.get('llm_provider_config', {}))
        #=====================================================

    else:
        fixdragspeedx, fixdragspeedy = 1.0, 1.0
        gravity = 0.1
        volume = 0.5
        language_code = QtCore.QLocale().name()
        on_top_hint = True
        default_pet = pets[0]
        defaultAct = {}
        themeColor = None
        for pet in pets:
            defaultAct[pet] = defaultAct.get(pet, None)
        scale_dict = {}
        for pet in pets:
            scale_dict[pet] = 1.0
        tunable_scale = 1.0
        minipet_scale = defaultdict(dict)
        toaster_on = True
        bubble_on = True
        usertag_dict = {}
        auto_lock = False
        llm_provider_config = _normalize_llm_config({})
    check_locale()
    save_settings()

def _normalize_llm_config(data):
    config = LLM_DEFAULT_CONFIG.copy()
    if isinstance(data, dict):
        config.update({k: v for k, v in data.items() if k in config})

    config['enabled'] = bool(config.get('enabled', False))
    config['provider'] = str(config.get('provider') or 'OpenAI')
    config['base_url'] = str(config.get('base_url') or '')
    config['model'] = str(config.get('model') or '')
    config['api_key_env_var'] = str(config.get('api_key_env_var') or app_identity.LLM_API_KEY_ENV)
    config['bubble_mode'] = str(config.get('bubble_mode') or 'pat_random')
    config['bubble_frequency_preset'] = str(config.get('bubble_frequency_preset') or 'balanced')
    if config['bubble_frequency_preset'] not in LLM_BUBBLE_PRESET_KEYS:
        config['bubble_frequency_preset'] = 'custom'
    config['ambient_enabled'] = bool(config.get('ambient_enabled', True))
    config['chat_stream_enabled'] = bool(config.get('chat_stream_enabled', True))
    config['system_prompt'] = str(config.get('system_prompt') or LLM_DEFAULT_CONFIG['system_prompt'])

    try:
        config['temperature'] = float(config.get('temperature', 0.8))
    except Exception:
        config['temperature'] = 0.8
    config['temperature'] = max(0.0, min(2.0, config['temperature']))

    for key, default_value in [
        ('pat_bubble_probability', 0.6),
        ('scheduled_bubble_probability', 0.35),
    ]:
        try:
            config[key] = float(config.get(key, default_value))
        except Exception:
            config[key] = default_value
        config[key] = max(0.0, min(1.0, config[key]))

    for key, default_value, min_value, max_value in [
        ('ambient_min_seconds', 60, 10, 3600),
        ('ambient_max_seconds', 120, 10, 3600),
        ('min_bubble_cooldown_seconds', 20, 0, 600),
        ('max_tokens', 80, 10, 500),
        ('chat_max_tokens', 800, 10, 4000),
        ('timeout', 20, 1, 120),
        ('max_reply_chars', 160, 40, 500),
        ('max_chat_reply_chars', 4000, 200, 12000),
    ]:
        try:
            config[key] = int(config.get(key, default_value))
        except Exception:
            config[key] = default_value
        config[key] = max(min_value, min(max_value, config[key]))

    if config['ambient_min_seconds'] > config['ambient_max_seconds']:
        config['ambient_max_seconds'] = config['ambient_min_seconds']

    return config

def save_settings():
    global file_path, set_fall, gravity, fixdragspeedx, fixdragspeedy, scale_dict, volume, \
           language_code, on_top_hint, default_pet, defaultAct, themeColor, minipet_scale, \
           toaster_on, usertag_dict, auto_lock, bubble_on, llm_provider_config

    data_js = {'gravity':gravity,
               'set_fall': set_fall,
               'fixdragspeedx':fixdragspeedx,
               'fixdragspeedy':fixdragspeedy,
               'usertag_dict':usertag_dict,
               'scale_dict':scale_dict,
               'minipet_scale':minipet_scale,
               'volume':volume,
               'on_top_hint':on_top_hint,
               'toaster_on':toaster_on,
               'bubble_on':bubble_on,
               'default_pet':default_pet,
               'defaultAct':defaultAct,
               'language_code':language_code,
               'themeColor':themeColor,
               'auto_lock':auto_lock,
               'llm_provider_config':llm_provider_config
               }

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data_js, f, ensure_ascii=False, indent=4)

def get_petlist(dirname):
    folders = os.listdir(dirname)
    pets = []
    # subpets = []
    # v0.3.3 subpet now moved to folder: res/pet/
    for folder in folders:
        folder_path = os.path.join(dirname, folder)
        if folder != 'sys' and os.path.isdir(folder_path):
            pets.append(folder)
            #conf_path = os.path.join(folder_path, 'pet_conf.json')
            #conf = dict(json.load(open(conf_path, 'r', encoding='UTF-8')))
            #subpets += [i for i in conf.get('subpet',{}).keys()]
    pets = sorted(set(pets))
    #subpets = list(set(subpets))
    #for subpet in subpets:
    #    pets.remove(subpet)
    return pets

def change_translator(language_code):
    global translator
    if language_code == 'en_US':
        translator = None
    else:
        translator = QtCore.QTranslator()
        translator.load(QtCore.QLocale(language_code), "langs", ".", resource_path("res", "language"))

        global TIER_NAMES, HUNGERSTR, FAVORSTR
        TIER_NAMES = [translator.translate("others", i) for i in TIER_NAMES] #.encode('utf-8')
        HUNGER_trans = translator.translate("others", HUNGERSTR) #.encode('utf-8'))
        if HUNGER_trans:
            HUNGERSTR = HUNGER_trans
        FAVOR_trans = translator.translate("others", FAVORSTR) #.encode('utf-8'))
        if FAVOR_trans:
            FAVORSTR = FAVOR_trans

def check_locale():
    global language_code, lang_dict
    if language_code not in lang_dict.values():
        if language_code.split("_")[0] == 'zh':
            language_code = "zh_CN"
        else:
            language_code = "en_US"
            

def check_dict_datatype(raw_dict:dict, dtype, default_value):
    """
    Checks the datatype of values in a dictionary. If a value does not match the specified datatype, it is replaced with a default value.

    Parameters:
    raw_dict (dict): The dictionary to check.
    dtype (type): The expected datatype for the values.
    default_value: The value to replace if the datatype does not match.

    Returns:
    dict: A new dictionary with corrected datatypes.
    """
    return {k: (v if isinstance(v, dtype) else default_value) for k, v in raw_dict.items()}
