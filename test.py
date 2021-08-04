import unittest

from ip_identifier import extract_ip


class TestIPWereFound(unittest.TestCase):
    def test_extract_ip_from_string(self):
        """Tests if can extract the ips from the string"""
        data = """Lorem ipsum dolor sit amet, 244.36.171.60 adipiscing elit. Pellentesque finibus massa vitae augue 81.44.150.240, vitae faucibus quam pellentesque. Aenean condimentum risus at justo suscipit bibendum. Curabitur consequat tempus bibendum. Vestibulum bibendum sagittis odio, in fermentum velit auctor eget. Etiam mollis aliquet semper. Sed id turpis  ac nulla congue rhoncus. 40.82.106.5 facilisis sem augue, sit amet consequat lacus  pellentesque sed. Fusce non posuere ligula. Praesent nec lorem nisl. Integer suscipit efficitur nibh consectetur malesuada."""

        expected_data = ["244.36.171.60", "81.44.150.240", "40.82.106.5"]
        result = extract_ip(data)

        self.assertEqual(expected_data, result)


if __name__ == "__main__":
    unittest.main()
