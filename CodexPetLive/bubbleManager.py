import os
import re
import json
import random
import time
from PySide6.QtCore import QObject, QThread, Signal, QTimer

import CodexPetLive.settings as settings
from CodexPetLive.llm_client import generate_bubble_reply
basedir = settings.BASEDIR
_NO_FALLBACK = object()

"""
List of buble behavior
-------------------------
1. Favorability
    - fv_lvlup
    - fv_drop

2. HP (Satiety)
    - hp_low
    - hp_zero

3. Feed
    - feed_done
    - feed_required [1]

4. patpat
    - pat_focus
    - pat_frequent
    - pat_random [2]

[1] The 'icon' is configured within the code, please keep it as null
[2] To cusomize this, add any number of pat_random_[0-9]* in configuration file
    


Config Structure
-------------------------
{
    BEHAVIOR: {
        "icon": "system",
        "message": "The text shown in the bubble",
        "countdown": 300, # if specified, a countdown will be triggered and shown on the bubble
        "start_audio" "system", # the string points to the note_type in note_icon.json
        "end_audio": null
    }
}

"""

# TODO: feed_required 相关翻译 更新开发文档


class LLMReplyThread(QThread):
    done = Signal(dict, str, name="done")

    def __init__(self, config, event_name, fallback_message, pet_name, usertag, language_code, bubble_dict, parent=None):
        super().__init__(parent)
        self.config = config.copy()
        self.event_name = event_name
        self.fallback_message = fallback_message
        self.pet_name = pet_name
        self.usertag = usertag
        self.language_code = language_code
        self.bubble_dict = bubble_dict.copy()

    def run(self):
        try:
            reply = generate_bubble_reply(
                self.config,
                event_name=self.event_name,
                fallback_message=self.fallback_message,
                pet_name=self.pet_name,
                usertag=self.usertag,
                language_code=self.language_code,
            )
            self.done.emit(self.bubble_dict, reply)
        except Exception:
            self.done.emit(self.bubble_dict, self.fallback_message)


class BubbleManager(QObject):
    """
    Class to manage all behaviors of bubbleText
    """

    register_bubble = Signal(dict, name='register_bubble')

    attr_list = ["icon", "message", "countdown", "start_audio", "end_audio"]

    bubble_hp_tier = {0: ["fv_drop", "hp_zero", "feed_required"],
                      1: ["hp_low", "feed_required"],
                      2: ["hp_low", "feed_required"]}

    def __init__(self,
                 parent=None):
        super().__init__(parent=parent)
        self.bubble_conf = self.load_bubble_config()
        self.llm_threads = []
        self.llm_request_in_flight = False
        self._last_llm_bubble_at = 0
        self.ambient_timer = QTimer(self)
        self.ambient_timer.setSingleShot(True)
        self.ambient_timer.timeout.connect(self._trigger_ambient_llm_bubble)
        self.refresh_ambient_timer()


    def load_bubble_config(self) -> dict:
        system_conf_file = os.path.join(basedir, 'res/icons/bubble_conf.json')
        pet_bb_conf_file = os.path.join(basedir, f'res/role/{settings.petname}/note/bubble_conf.json')
        bubble_conf = self._read_bubble_conf(system_conf_file)

        # Load any changes made in pet config
        if os.path.exists(pet_bb_conf_file):
            pet_bb_conf = self._read_bubble_conf(pet_bb_conf_file, fallback={})
            bubble_conf = self._merge_pet_bubble_conf(bubble_conf, pet_bb_conf)

        return bubble_conf

    def _read_bubble_conf(self, path, fallback=_NO_FALLBACK):
        try:
            with open(path, 'r', encoding='utf-8-sig') as f:
                data = json.load(f)
            if not isinstance(data, dict):
                raise ValueError("bubble config root must be an object")
            return data
        except Exception:
            if fallback is _NO_FALLBACK:
                raise
            return fallback

    def _merge_pet_bubble_conf(self, bubble_conf, pet_bb_conf):
        try:
            merged_conf = {k: v.copy() for k, v in bubble_conf.items()}
            for k, v in pet_bb_conf.items():
                if not isinstance(v, dict):
                    continue
                if k in merged_conf:
                    merged_conf[k].update(v)
                else:
                    merged_conf[k] = self._format_bubble_type_conf(v)
            return merged_conf
        except Exception:
            return bubble_conf
    
    def _format_bubble_type_conf(self, bubble_type_conf):
        final_conf = {}
        for k in self.attr_list:
            v = bubble_type_conf.get(k, None)
            final_conf[k] = v
        return final_conf

    def trigger_bubble(self, bb_type):
        original_bb_type = bb_type
        bubble_dict = self.bubble_conf.get(bb_type, {}).copy()
        if not bubble_dict:
            return
        
        if bb_type == "feed_required":
            bubble_dict = self.prepare_feed_required()
            if not bubble_dict:
                return
        
        # change bubble type like 'pat_random_1' into 'pat_random'
        bubble_type = "_".join(bb_type.split("_")[:2])
        bubble_dict['bubble_type'] = bubble_type

        # Translate message
        message = bubble_dict.get('message', '')
        message = self.tr(message)

        # Change the nickname of user
        message = self._replace_usertag(message)
        bubble_dict['message'] = message

        if not settings.bubble_on:
            return

        if self._should_generate_llm_bubble(original_bb_type, bubble_type, message):
            if not self._request_llm_bubble(original_bb_type, bubble_type, bubble_dict, message):
                self.register_bubble.emit(bubble_dict)
        else:
            self.register_bubble.emit(bubble_dict)

    def trigger_scheduled(self):
        # Randomly select bubble type
        cand_bubbles = self.bubble_hp_tier.get(settings.pet_data.hp_tier, [])
        if not cand_bubbles:
            return
        bb_type = random.choice(cand_bubbles)
        self.trigger_bubble(bb_type)
    
    def trigger_patpat_random(self):
        candidates = [k for k in self.bubble_conf.keys() if k.startswith("pat_random_")]
        if candidates:
            bb_type = random.choice(candidates)
            self.trigger_bubble(bb_type)
        elif self._llm_enabled() and settings.llm_provider_config.get('bubble_mode') == 'pat_random':
            self.trigger_llm_bubble('pat_random')

    def trigger_llm_bubble(self, event_name='manual', respect_cooldown=True):
        if not settings.bubble_on or not self._llm_enabled():
            return
        if respect_cooldown and not self._can_start_llm_request():
            return

        bubble_dict = {
            'icon': None,
            'message': self.tr("Thinking..."),
            'countdown': None,
            'timeout': 3,
            'start_audio': None,
            'end_audio': None,
            'bubble_type': 'llm_pending',
            'log': False,
        }
        self.register_bubble.emit(bubble_dict)

        result_bubble = {
            'icon': None,
            'message': '',
            'countdown': None,
            'start_audio': None,
            'end_audio': None,
            'bubble_type': 'llm_reply',
            'log': False,
        }
        self._request_llm_bubble(event_name, 'llm_reply', result_bubble, '', respect_cooldown=respect_cooldown)

    def refresh_ambient_timer(self):
        if self.ambient_timer.isActive():
            self.ambient_timer.stop()
        self._schedule_next_ambient_bubble()

    def _ambient_enabled(self):
        config = getattr(settings, 'llm_provider_config', {})
        return bool(settings.bubble_on and self._llm_enabled() and config.get('ambient_enabled', True))

    def _schedule_next_ambient_bubble(self):
        if not self._ambient_enabled():
            self.ambient_timer.start(30 * 1000)
            return
        config = settings.llm_provider_config
        min_seconds = int(config.get('ambient_min_seconds', 60))
        max_seconds = int(config.get('ambient_max_seconds', 120))
        if max_seconds < min_seconds:
            max_seconds = min_seconds
        delay_seconds = random.randint(min_seconds, max_seconds)
        self.ambient_timer.start(delay_seconds * 1000)

    def _trigger_ambient_llm_bubble(self):
        try:
            self.trigger_llm_bubble('ambient', respect_cooldown=True)
        finally:
            self._schedule_next_ambient_bubble()

    def prepare_feed_required(self):
        # Check if hp and fv are already full
        hp_full = settings.pet_data.hp >= ((settings.HP_TIERS[-1]-1)*settings.HP_INTERVAL)
        fv_full = (settings.pet_data.fv_lvl == (len(settings.LVL_BAR)-1)) and (settings.pet_data.fv==settings.LVL_BAR[settings.pet_data.fv_lvl])
        if hp_full and fv_full:
            return {}
        
        bubble_dict = self.bubble_conf['feed_required'].copy()

        # List all candidate items
        all_items = settings.items_data.item_dict.keys()
        candidate_items = [i for i in all_items if settings.items_data.item_dict[i]['item_type'] == 'consumable']
        # exclude dislike items
        dislike_items = set(settings.pet_conf.item_dislike.keys())
        candidate_items = [i for i in candidate_items if i not in dislike_items and i != 'coin']
        # exclude items with negative effect
        candidate_items = [i for i in candidate_items if settings.items_data.item_dict[i]['effect_HP'] > 0 or settings.items_data.item_dict[i]['effect_FV'] > 0]
        # check if list empty
        if not candidate_items:
            return {}
        # Choose one
        selected_item = random.choice(candidate_items)
        
        # Update the bubble_dict
        bubble_dict['icon'] = selected_item
        bubble_dict['item'] = selected_item
        bubble_dict['message'] = self.tr(bubble_dict['message'])
        bubble_dict['message'] = bubble_dict['message'].replace("ITEMNAME", f"[{selected_item}]")

        return bubble_dict
    
    def add_usertag(self, bubble_dict:dict, position:str = 'front', send:bool = False):
        # add USERTAG in string
        message = bubble_dict.get('message', '')
        if position == 'front':
            message = f'USERTAG {message}'
        elif position == 'end':
            message = f'{message} USERTAG'

        # replace usertag
        message = self._replace_usertag(message)
        bubble_dict['message'] = message

        if send and settings.bubble_on:
            if self._should_generate_llm_bubble('greeting', 'greeting', message):
                bubble_dict['bubble_type'] = 'greeting'
                if not self._request_llm_bubble('greeting', 'greeting', bubble_dict, message):
                    self.register_bubble.emit(bubble_dict)
            else:
                self.register_bubble.emit(bubble_dict)
        else:
            return bubble_dict

    def _llm_enabled(self):
        config = getattr(settings, 'llm_provider_config', {})
        return bool(config.get('enabled', False))

    def _can_emit_llm_bubble(self):
        cooldown = int(settings.llm_provider_config.get('min_bubble_cooldown_seconds', 20))
        if cooldown <= 0:
            return True
        return (time.monotonic() - self._last_llm_bubble_at) >= cooldown

    def _can_start_llm_request(self):
        return not self.llm_request_in_flight and self._can_emit_llm_bubble()

    def _mark_llm_bubble_sent(self):
        self._last_llm_bubble_at = time.monotonic()

    def _should_generate_llm_bubble(self, original_bb_type, bubble_type, message):
        if not self._llm_enabled():
            return False

        mode = settings.llm_provider_config.get('bubble_mode', 'pat_random')
        if mode == 'all':
            return True
        if mode == 'all_empty':
            return not bool((message or '').strip())
        if mode == 'pat_random':
            return original_bb_type.startswith('pat_random') or bubble_type == 'pat_random'
        return False

    def _request_llm_bubble(self, original_bb_type, bubble_type, bubble_dict, fallback_message, respect_cooldown=True):
        if self.llm_request_in_flight:
            return False
        if respect_cooldown and not self._can_emit_llm_bubble():
            return False
        self.llm_request_in_flight = True
        self._mark_llm_bubble_sent()
        config = settings.llm_provider_config.copy()
        bubble_dict = bubble_dict.copy()
        bubble_dict['bubble_type'] = 'llm_reply' if bubble_type in ('llm_reply', 'pat_random') else bubble_type
        if bubble_dict['bubble_type'] == 'llm_reply':
            bubble_dict['log'] = False
        usertag = settings.usertag_dict.get(settings.petname, "")
        thread = LLMReplyThread(
            config,
            event_name=original_bb_type,
            fallback_message=fallback_message,
            pet_name=settings.petname,
            usertag=usertag,
            language_code=settings.language_code,
            bubble_dict=bubble_dict,
            parent=self,
        )
        thread.done.connect(self._emit_llm_bubble)
        thread.finished.connect(lambda t=thread: self._cleanup_llm_thread(t))
        self.llm_threads.append(thread)
        thread.start()
        return True

    def _emit_llm_bubble(self, bubble_dict, message):
        message = self._replace_usertag(message)
        bubble_dict['message'] = message or self.tr("I am here with you.")
        if settings.bubble_on:
            self.register_bubble.emit(bubble_dict)

    def _cleanup_llm_thread(self, thread):
        if thread in self.llm_threads:
            self.llm_threads.remove(thread)
        self.llm_request_in_flight = False
        thread.deleteLater()
    
    def _replace_usertag(self, message):
        usertag = settings.usertag_dict.get(settings.petname, "")
        if usertag:
            message = message.replace('USERTAG', usertag)
        else:
            message = message.replace('USERTAG', usertag)
        message = message.strip(' ')
        # Remove consecutive spaces
        message = re.sub(r'\s{2,}', ' ', message)
        return message
    
    def _trigger_HP(self):
        return
    
    def _trigger_FV(self):
        return
    
    def _trigger_feed(self):
        return
    
    def _trigger_focus(self):
        return
