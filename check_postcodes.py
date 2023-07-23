#! /usr/bin/env python3

# Quick script to scrape the Hackney parking-permit site to check which
# postcodes are likely to be affected by the parking charges, especially
# those which are about to have hefty parking costs for motorbikes
#
# Expects one argument, the path to a CSV file, which must have a postcode
# as the first field on each row.
#
# Writes out another CSV file, to `./hackney-zones.csv`, which has a postcode
# as the first field and a status as a second, on each line. Those statuses:
#
# * car-free - in a car-free zone (and so likely to have a charge soon)
# * not-car-free - not in a car-free zone
# * not-cpz - not even in a CPZ (I'm not convinced any non-cpz aren't also not-car-free)
# * unknown-postcode - invalid or not-in-hackney postcode
# * error - there was an error somewhere
#

import requests
import json
import re
import time
import unicodecsv # python3-unicodecsv
import sys

# Car-free:
#postcode = 'N1 7GH'
# Not-car-free
#postcode = 'E1 6AX'
# Error
#postcode = 'E1 6AW'


def main():

  results = dict()

  input_csv = sys.argv[1]
  output_csv = './hackney_zones.csv'
  print("Input: " + input_csv)

  with open(output_csv, 'w', buffering=1) as output:
    with open(input_csv, 'rb') as input:
      r = unicodecsv.reader(input, encoding='utf-8-sig')
      for line in r:
        postcode = line[0]
        print()
        print(postcode)
        result = check_postcode(postcode)
        print(postcode + ", " + result, file=output)
        print(postcode + ", " + result)
        print()
        results[postcode] = result
        time.sleep(2)


def check_postcode(postcode):
  print('Checking postcode: "' + postcode + '"')
  session = requests.Session()

  headers = {'User-agent': 'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0'}

  url = "https://permits.hackney.gov.uk/control/applyPermitHackney"
  postdata = {'product_id': 'RESIDENT', 'channelType': 'WEB_SALES_CHANNEL'}
  session.post(url, postdata)

  url = "https://permits.hackney.gov.uk/control/getAvailablePermitAddressList"
  postdata = {'postalCode': postcode, 'productId': 'RESIDENT'}
  response = session.post(url, postdata)
  addresses = json.loads(response.text)
  addresslist = json.loads(addresses['llpgAddressList'])
  if addresses['numberOfResults'] < 1:
    print("Unknown postcode")
    return 'unknown-postcode'
  uprn = addresslist[0]['uprn']
  print("uprn: '" + uprn + "'")

  url = 'https://permits.hackney.gov.uk/control/resPermStage3'
  encoded_postcode = re.sub(' ', '+', postcode)
  postdata = {'main_product_id': 'RESIDENT', 'uprn': uprn, 'isWaitingList': '', 'CUSTOMER_POSTAL_CODE':encoded_postcode, 'MANUAL_POSTCODE':'', 'cpzAddressNotFound':'Y' }
  response = session.post(url, postdata)

  page = response.text

  if re.search('Our records show that your address', page):
    print('car-free')
    return 'car-free'
  elif re.search('We will try to confirm that you live at the address stated in your application automatically', page):
    print('not-car-free')
    return 'not-car-free'
  elif re.search("We don't have a record of this address being in a parking zone in Hackney", page):
    print('not-cpz')
    return('not-cpz')
  else:
    print('error')
    return 'error'
  exit()

main()
