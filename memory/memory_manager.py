import json
import os
import threading
from pathlib import Path

from memory.vector_instance import get_vector_memory
from memory.manager import MemoryManager


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = PROJECT_ROOT / "memory" / "user_profile.json"
HISTORY_PATH = PROJECT_ROOT / "memory" / "chat_history.json"
SUMMARY_PATH = PROJECT_ROOT / "memory" / "memory_summary.json"


class _LegacyMemoryManager:
    def __init__(self):

        self.vector_memory = get_vector_memory()

        self._profile_cache = None
        self._profile_mtime = None
        self._history_cache = None
        self._history_mtime = None
        self._summary_cache = None
        self._summary_mtime = None
        self._cache_lock = threading.RLock()


    def _clone(self, data):

        if isinstance(data, dict):

            return dict(data)

        if isinstance(data, list):

            return list(data)

        return data


    def _load_json_cached(self, path, cache_name, mtime_name, default):

        with self._cache_lock:

            if not os.path.exists(path):

                return self._clone(default)


            mtime = os.path.getmtime(path)
            cached = getattr(self, cache_name)
            cached_mtime = getattr(self, mtime_name)


            if cached is not None and cached_mtime == mtime:

                return self._clone(cached)


            with open(
                path,
                "r",
                encoding="utf-8"
            ) as f:

                data = json.load(f)


            setattr(self, cache_name, self._clone(data))
            setattr(self, mtime_name, mtime)

            return self._clone(data)


    def _update_cache(self, path, cache_name, mtime_name, data):

        with self._cache_lock:

            setattr(self, cache_name, self._clone(data))

            if os.path.exists(path):

                setattr(
                    self,
                    mtime_name,
                    os.path.getmtime(path)
                )


    def save_vector_memory(self,text):

        self.vector_memory.add_memory(
            text
        )


    def load_profile(self):

        default_profile = {

            "name":"",
            "learning":"",
            "project":"",
            "likes":""

         }


        if not os.path.exists(PROFILE_PATH):

            self.save_profile(default_profile)

            return default_profile


        profile = self._load_json_cached(
            PROFILE_PATH,
            "_profile_cache",
            "_profile_mtime",
            default_profile
        )


        for key,value in default_profile.items():

            if key not in profile:

                profile[key]=value


        return profile


    def update_profile(self,new_data):

        profile=self.load_profile()

        for key,value in new_data.items():

            if value and str(value).strip():

                profile[key]=value.strip()


        self.save_profile(profile)


    def save_profile(self, profile):

        with open(
            PROFILE_PATH,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                profile,
                f,
                ensure_ascii=False,
                indent=4
            )

        self._update_cache(
            PROFILE_PATH,
            "_profile_cache",
            "_profile_mtime",
            profile
        )


    def load_history(self):

        if not os.path.exists(HISTORY_PATH):

            return []


        return self._load_json_cached(
            HISTORY_PATH,
            "_history_cache",
            "_history_mtime",
            []
        )


    def save_history(self, history):

        with open(
            HISTORY_PATH,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                history,
                f,
                ensure_ascii=False,
                indent=4
            )

        self._update_cache(
            HISTORY_PATH,
            "_history_cache",
            "_history_mtime",
            history
        )


    def trim_history(self, history, max_messages=20):

        if len(history) > max_messages:

            history = history[-max_messages:]

        return history


    def load_summary(self):

        if not os.path.exists(SUMMARY_PATH):

            return {}


        return self._load_json_cached(
            SUMMARY_PATH,
            "_summary_cache",
            "_summary_mtime",
            {}
        )


    def save_summary(self, summary):

        with open(
            SUMMARY_PATH,
            "w",
            encoding="utf-8"
        ) as f:


            json.dump(
                summary,
                f,
                ensure_ascii=False,
                indent=4
            )

        self._update_cache(
            SUMMARY_PATH,
            "_summary_cache",
            "_summary_mtime",
            summary
        )


    def load_all_memory(self):

        return {

            "profile": self.load_profile(),

            "summary": self.load_summary(),

            "history": self.load_history()

        }
