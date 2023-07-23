# hackney-parking

These are some scripts and, more importantly, generated CSVs to help with the campaign against
Hackney's plans for motorbike charging.

## The CSVs:

* `hackney_postcodes.csv` - Every possible postcode in Hackney, produced by taking each Hackney
  first-part, and generating every valid second-part

* `hackney-zones.csv` - All the postcodes from the above, and whether they are unknown, or in a
  `car-free` or a `not-car-free` zone. This was produced by `check_postcodes.py`

## The Scripts

`check_postcodes.py` was written first, and goes through the postcodes list to get the state of
each; producing `hackney-zones.csv`.

Based on the results of that, it was hastily modified into `check_addresses.py` which reads
`hackney-zones.csv` and gets the details of every address in each postcode; writing
`hackney-addresses.csv`.

If you're interested in recreating this, you'd be mad to not just modify check_addresses.py to read
hackney_postcodes.csv directly and filter out non-existent addresses as it find them, though.
