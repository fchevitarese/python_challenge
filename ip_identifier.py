import argparse
import multiprocessing
import pprint
import re
import sys
import time

import requests

geoip_information = dict()
rdap_information = dict()
ip_list = list()


def extract_ip(line):
    pattern = re.compile("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
    return re.findall(pattern, line)


def perform_http_request(url):
    try:
        result = requests.get(url, timeout=10)
        if result.status_code == 200:
            return result.json()
    except requests.exceptions.ConnectionError:
        return


def perform_rdap_request(ip_addr):
    tries = 0
    max_retries = 3
    print(f"Getting rdap information for ip: {ip_addr}")
    url = f"https://rdap.arin.net/registry/ip/{ip_addr}"

    try:
        result = perform_http_request(url)
        if result:
            return result
    except requests.exceptions.ConnectionError:
        if tries <= max_retries:
            print(f"Error on getting info about : {ip_addr}. Retrying...")
            tries += 1
            time.sleep(tries + 1)
            result = perform_http_request(url)
            if result:
                return result
        else:
            print(
                f"Max retries reached. Error on getting info about {ip_addr}"
            )
            return


def perform_geo_ip_request(ip_addr):
    print(f"Getting geo_ip information for ip: {ip_addr}")
    url = f"https://json.geoiplookup.io/{ip_addr}"

    result = perform_http_request(url)
    return result


def generate_geoip_information(result):
    ip = result["ip"]
    geoip_information[ip] = result


def generate_rdap_information(result):
    try:
        if not result:
            raise IndexError

        ip = result.get("links")[0]
        ip = extract_ip(ip.get("value"))[0]
        rdap_information[ip] = result
    except IndexError:
        print("Error on finding the ip address.")


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
    for i, ip in enumerate(ip_list):
        if i == 4:
            break

        if ip not in geoip_information and geo_process:
            pool.apply_async(
                perform_geo_ip_request,
                args=(ip,),
                callback=generate_geoip_information,
            )

        if ip not in rdap_information and rdap_process:
            pool.apply_async(
                perform_rdap_request,
                args=(ip,),
                callback=generate_rdap_information,
            )

    pool.close()
    pool.join()


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

    args = parser.parse_args()

    if not args.interactive:
        ip_list = parse_text_file(args.filename)

        if ip_list:
            identify_ips(
                ip_list, args.request_geo_data, args.request_rdap_data
            )

            print("**** GEO IP INFORMATION ****")
            pprint.pprint(geoip_information)

            print("\n\n ****  \n\n")

            print("**** RDAP INFORMATION ****")
            pprint.pprint(rdap_information)
    else:
        while True:
            runner(args.filename)
