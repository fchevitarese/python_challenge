"""Implements a json/dict file caching"""
import json


class CachedDict(object):
    def __init__(self, method):
        self.method = method
        self.cache = self.read_cache()

    def read_cache(self):
        cache = {}
        try:
            with open(f"cached_{self.method}.json", "r") as f_cache:
                cache = json.loads(str(f_cache.read()))
            f_cache.close()
        except FileNotFoundError:
            with open(f"cached_{self.method}.json", "w+") as f_cache:
                f_cache.write(json.dumps({}))
            f_cache.close()

        return cache

    def is_cached(self, ip):
        return ip in self.cache

    def write_cache(self):
        with open(f"cached_{self.method}.json", "w") as f_cache:
            f_cache.write(json.dumps(self.cache))
        f_cache.close()

    def clear_cache(self):
        self.cache = {}
        with open(f"cached_{self.method}.json", "w") as f_cache:
            f_cache.write(json.dumps({}))
        f_cache.close()

    def do_cache(self, ip, data):
        if not self.is_cached(ip):
            self.cache[ip] = data
            self.write_cache()

    def do_uncache(self, ip):
        if self.is_cached(ip):
            del self.cache[ip]
            self.write_cache()
