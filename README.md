# Python challenge

This is a command line script that receives a txt file and extracts the ip addresses inside the file.

Consults the GeoIP for each ip using the api https://json.geoiplookup.io
Consults RDAP information for each ip using the api https://rdap.arin.net

### **Dependencies:**

- python3
- python-requests

### **Usage:**

python ip_identifier.py -parameters

### **Parameters:**

- -f/--file: Specify the text file that will be parsed. **Required**.
- -g: Should retrieve the GEOIP information from the API. **Default: False**
- -r: Should retrieve the RDAP information from the API: **Default: False**
- -i: Start the interactive program.
- -q: Specify the ammount of ips you want to check: **Expected a number. If not specified will get all ips**
- --force: Clear cache before make the requests.

### Example:

- **_python ip_identifier.py -f list_of_ips.txt -g -r_**

  It will run the program and print the output from the geo_ip request and for the rdap requests

  - The informations about GeoIP will be stored in the file named **cached_geoip.json**
  - The informations about RDAP will be stored in the file name **cached_rdap.json**

  **Obs.: They will be used as cache. Its not the best approach but, it works.**

  **The errors will be logged in the file named errors.log**

## Tests

A few tests are available.
To run just execute the command:
**python -m unittest**
