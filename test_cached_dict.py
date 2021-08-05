import unittest

from cache import CachedDict


class TestCachedDict(unittest.TestCase):
    def setUp(self):
        self.data = {"192.168.0.1": {"location": "somewhere"}}
        self.ip_list = ["192.168.0.1", "192.168.0.2", "192.168.100.1"]
        self.cache = CachedDict("geoip")

    def test_is_not_cached(self):
        for ip in self.ip_list:
            self.assertFalse(self.cache.is_cached(ip))

    def test_is_cached(self):
        self.cache.do_cache("192.168.0.1", self.data)
        self.assertTrue(self.cache.is_cached("192.168.0.1"))
        self.cache.clear_cache()

    def test_uncache_data(self):
        self.cache.do_cache("192.168.0.1", self.data)
        self.assertTrue(self.cache.is_cached("192.168.0.1"))
        self.cache.do_uncache("192.168.0.1")
        self.assertFalse(self.cache.is_cached("192.168.0.1"))
        self.cache.clear_cache()


if __name__ == "__main__":
    unittest.main()
