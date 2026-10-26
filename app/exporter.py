import json
import os
import sys
import xml.etree.ElementTree as ET

import redis

# Function that reads in the XML file and converts it into a python data 
# structure
def parse_xml(xml_path):
    # Reading in our xml file and setting our root
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Search for all subdomains using findall() and store them in a list.
    subdomains = [
        element.text.strip()
        for element in root.findall("./subdomains/subdomain")
        if element.text
    ]

    # Likewise we extract cookie information (while also validating that our
    # cookies list contains all require information), and store the cookie
    # information as entries into a dictionary
    cookies = {}
    for element in root.findall("./cookies/cookie"):
        name = element.get("name")
        host = element.get("host")
        value = element.text

        if not name or not host or value is None:
            raise ValueError("Cookie is missing required information")

        cookies[f"cookie:{name}:{host}"] = value.strip()

    return subdomains, cookies


# Converts the subdomain list to a JSON which writes all key-value pairs
# into Redis
def export_to_redis(xml_path, client):
    # Use parse_xml to extract the subdomains and cookies from our xml 
    # file
    subdomains, cookies = parse_xml(xml_path)

    # Create a new dictionary where we store our subdomains as a JSON formatted 
    # string as well as the cookies extracted which we will use to set our 
    # key-value pairs in Redis.
    data = {"subdomains": json.dumps(subdomains)}
    data.update(cookies)

    # Set the key-value pairs with redis mset()
    client.mset(data)

    return list(data.keys())


def main():
    # Handling our command line arguments with the option for a 
    # verbose setting, '-v', as required 
    verbose = "-v" in sys.argv
    arguments = [arg for arg in sys.argv[1:] if arg != "-v"]

    # handling the case where we do not have the requisite number of
    # parameters.
    if len(arguments) != 1:
        print("Usage: export.sh [-v] /path/to/xml")
        sys.exit(1)

    xml_path = arguments[0]

    # Connect to our redis server
    client = redis.Redis(
        host=os.getenv("REDIS_HOST", "redis"),
        port=6379,
        decode_responses=True
    )

    # Create our key-value pairs within the redis server
    keys = export_to_redis(xml_path, client)

    if verbose:
        for key in keys:
            print(key)

    print(f"Successfully exported {len(keys)} keys to Redis.")

if __name__ == "__main__":
    main()