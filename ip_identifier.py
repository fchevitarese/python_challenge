import argparse
import logging
import multiprocessing
import pprint
import re
import sys

import requests

from cache import CachedDict

geoip_information = dict()
rdap_information = dict()
ip_list = list()

geo_cache = CachedDict("geoip")
rdap_cache = CachedDict("rdap")

logging.basicConfig(
    filename="errors.log", format="%(asctime)s %(message)s", filemode="a+"
)
logger = logging.getLogger()
logger.setLevel(logging.ERROR)


def extract_ip(line):
    pattern = re.compile("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
    return re.findall(pattern, line)


def perform_http_request(url):
    result = requests.get(url, timeout=10)
    if result.status_code == 200:
        return result.json()
    else:
        logger.error(
            "Error on getting data on {0} with status {1}".format(
                url, result.status_code
            )
        )


def perform_rdap_request(ip_addr):
    print(f"Getting rdap information for ip: {ip_addr}")
    url = f"https://rdap.arin.net/registry/ip/{ip_addr}"

    if not rdap_cache.is_cached(ip_addr):
        try:
            result = perform_http_request(url)
            if result:
                return result
        except Exception as e:
            logger.error(e)
            logger.error(
                "Error on getting RDAP info for the ip {0}".format(ip_addr)
            )
            return


def perform_geo_ip_request(ip_addr):
    if not geo_cache.is_cached(ip_addr):
        try:
            print(f"Getting geo_ip information for ip: {ip_addr}")
            url = f"https://json.geoiplookup.io/{ip_addr}"

            result = perform_http_request(url)
            if result and result.get("success"):
                return result

            raise Exception(result)
        except Exception as e:
            logger.error(e)
            logger.error(
                "Error on getting GeoIP info for the ip {0}".format(ip_addr)
            )


def generate_geoip_information(result):
    for data in result:
        if data:
            ip = data.get("ip")
            geo_cache.do_cache(ip, data)


def generate_rdap_information(result):
    for data in result:
        if data:
            ip = data.get("links")[0]
            ip = extract_ip(ip.get("value"))[0]
            rdap_cache.do_cache(ip, data)


def parse_text_file(filename, close=True):
    ip_list = list()

    lines = filename.readlines()
    for line in lines:
        ip_list.extend(extract_ip(line))

    if close:
        filename.close()

    return list(set(ip_list))


def identify_ips(ip_list, geo_process=False, rdap_process=False):
    pool = multiprocessing.Pool()

    if geo_process:
        geo_information = pool.map(perform_geo_ip_request, ip_list)
        generate_geoip_information(geo_information)

    if rdap_process:
        rdap_information = pool.map(perform_rdap_request, ip_list)
        generate_rdap_information(rdap_information)


def runner(filename):
    global ip_list

    def help():
        print("\n")
        print("Available commands:")
        print(
            "    extract or e:  Extracts, count and show the ips of the given text file."
        )
        print(
            "    g or geoip  :  Execute the GeoIP requests for the ip list extracted. (You should extract them before)"
        )
        print(
            "    r or rdap   :  Execute the RDAP requests for the ip list extracted. (You should extract them before)"
        )
        print("    h or help   :  Show help information.")
        print("    q or quit   :  Exit")
        print("\n")

    command = input("Input a command: ")
    if command == "q" or command == "quit":
        sys.exit(0)
    if command == "h" or command == "help":
        help()
    elif command == "e" or command == "extract":
        print("Extract, count and show the list of ips")

        if not ip_list:
            ip_list = parse_text_file(filename, close=False)
        print(f"{len(ip_list)} ip's were found in the file.")

    elif command == "g" or command == "geoip":
        print("Performing Geo ip requests for the list of ip's")
        identify_ips(ip_list, geo_process=True)
        pprint.pprint(geoip_information)

    elif command == "r" or command == "rdap":
        print("Performin RDAP request for the list of ip's")
        identify_ips(ip_list, rdap_process=True)
        pprint.pprint(rdap_information)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f",
        "--file",
        dest="filename",
        help="Provide a file path",
        type=argparse.FileType("r"),
        required=True,
    )
    parser.add_argument(
        "-g",
        action="store_true",
        default=False,
        dest="request_geo_data",
        help="Retrieve geoip information",
    )
    parser.add_argument(
        "-r",
        action="store_true",
        default=False,
        dest="request_rdap_data",
        help="Retrieve RDAP information",
    )
    parser.add_argument(
        "-i",
        action="store_true",
        default=False,
        dest="interactive",
        help="Want to go interactive :)",
    )
    parser.add_argument(
        "-q",
        dest="max_ips",
        help="Max ip's that should be identified",
        type=int,
    )
    parser.add_argument(
        "--force",
        dest="force",
        action="store_true",
        default=False,
        help="Ignore cached results",
    )

    args = parser.parse_args()
    if not args.interactive:
        ip_list = parse_text_file(args.filename)
        if ip_list:
            if args.force:
                if args.request_geo_data:
                    geo_cache.clear_cache()

                if args.request_rdap_data:
                    rdap_cache.clear_cache()

            identify_ips(
                ip_list[: args.max_ips],
                geo_process=args.request_geo_data,
                rdap_process=args.request_rdap_data,
            )

            if args.request_geo_data:
                geoip_information.update(geo_cache.cache)
                print("**** GEO IP INFORMATION ****")
                pprint.pprint(geoip_information)
                print("\n\n ****  \n\n")

            if args.request_rdap_data:
                rdap_information.update(rdap_cache.cache)
                print("**** RDAP INFORMATION ****")
                pprint.pprint(rdap_information)
    else:
        while True:
            runner(args.filename)
