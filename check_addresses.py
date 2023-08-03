#! /usr/bin/env python3

# Quick script to scrape the Hackney parking-permit site to check which
# addresses are likely to be affected by the parking charges, especially
# those which are about to have hefty parking costs for motorbikes
#
# Expects one argument, the path to a CSV file, that's been output by
# ./check_postcodes.py, because we thought to do this only after having run
# that.
#
# Writes out _another_ CSV file, to `./hackney-adddresses.csv`, which has six
# fields:
#
# * state:    the car-free/not-car-free from the earlier CSV; this skips those
#             that hackney doesn't think exists
# * postcode: the postcode
# * address:  'addr1' from hackney's response; the address minus the postcode
# * uprn:     the UPRN of the address; a unique locator for each address
# * zCode:    I don't know, but it's in the response back from the site
# * cpzCode:  I assume the code of the CPZ, but also just here because we have it
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
  output_csv = './hackney_addresses.csv'
  print("Input: " + input_csv)

  with open(output_csv, 'wb') as output:
    with open(input_csv, 'rb') as input:
      i = unicodecsv.reader(input, encoding='utf-8-sig')
      o = unicodecsv.DictWriter(output, fieldnames=['state','postcode','address','uprn','zCode','cpzCode'])
      o.writeheader()
      for line in i:
        postcode = line[0]
        state = line[1].strip()
        print()
        print(postcode)
        if state == 'unknown-postcode' or state == 'error':
          print(state + "; skipping")
          continue

        results = check_postcode(postcode)
        for result in results:
          print(result)
          o.writerow(result)
          print()
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
    return {}

  results = []
  for address in addresslist:
    addr = address['address1']
    uprn = address['uprn']

    print("uprn: '" + uprn + "'")
    print("addr: '" + addr + "'")
    url = 'https://permits.hackney.gov.uk/control/resPermStage3'
    encoded_postcode = re.sub(' ', '+', postcode)
    postdata = {'main_product_id': 'RESIDENT', 'uprn': uprn, 'isWaitingList': '', 'CUSTOMER_POSTAL_CODE':encoded_postcode, 'MANUAL_POSTCODE':'', 'cpzAddressNotFound':'Y' }
    response = session.post(url, postdata)

    page = response.text

    if re.search('Our records show that your address', page):
      state = 'car-free'
    elif re.search('We will try to confirm that you live at the address stated in your application automatically', page):
      state = 'not-car-free'
    elif re.search("We don't have a record of this address being in a parking zone in Hackney", page):
      state = 'not-cpz'
    else:
      state = 'error'



    result = {
      'postcode': postcode,
      'state': state,
      'address': addr,
      'uprn': uprn,
      'cpzCode': address['cpzCode'],
      'zCode': address['zCode']
    }
    results.append(result)
  return results

main()
