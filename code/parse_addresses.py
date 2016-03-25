#! /usr/bin/env python
# coding: utf-8

# Script to parse addresses for future geocoding
# First attempt: can we just lean on Mapzen's Libpostal?
__author__ = "Eldan Goldenberg, March 2016"
# http://eldan.co.uk/ ~ @eldang ~ eldang@gmail.com

import codecs
from collections import OrderedDict
import math
import os
import sys
import time

# unicode-aware replacement for the standard Python csv module
import unicodecsv as csv  
# https://github.com/jdunck/python-unicodecsv

# address normalisation by https://github.com/openvenues/pypostal
from postal.expand import expand_address
from postal.parser import parse_address

def main():
  print_with_timestamp("Starting run.")
  
  inputfile = "../Hennepin County Moving Violations 2010-2015.csv"

  outputfile = inputfile[:-4] + "_regularised_addresses.csv"
  with open(outputfile, 'w') as f_out:
    with open(inputfile, 'rU') as f_in:
      reader = csv.DictReader(f_in, dialect="excel")
      writer = csv.DictWriter(f_out, reader.fieldnames + ["parsed_address", "parsed_w_city", "parsed_w_state", "parsed_w_county_and_state"], encoding="utf8")
      writer.writeheader()
      n = 0
      for row in reader:
        offloctn = row["offloctn"].lower().replace("n/b", "northbound").replace("e/b", "eastbound").replace("s/b", "southbound").replace("w/b", "westbound").replace("/", "&").replace("@", "&")
#        print offloctn
        addr = ""
        for loc in offloctn.split("&"):
          if addr != "":
            addr = addr + " & "
          for token in parse_address(loc + ", Hennepin County, Minnesota, USA"):
            if token[0] not in (u'hennepin county', u'minnesota', u'usa'):
              if token[1] in (u'suburb', u'city'):
                addr = addr + ", "
              addr = addr + token[0] + " "
#          print parse_address(loc + ", Hennepin County, Minnesota, USA")
#          print addr
        row["parsed_address"] = addr
        row["parsed_w_city"] = addr + "Minneapolis, Minnesota, USA"
        row["parsed_w_state"] = addr + ", Minnesota, USA"
        row["parsed_w_county_and_state"] = addr + ", Hennepin County, Minnesota, USA"
#        print row["parsed_address"]
        writer.writerow(row)
        n = n + 1
        if n % 10000 == 0:
          print_with_timestamp("Wrote " + str(n) + " rows so far.")

  print_with_timestamp("Run complete.")



def prettify_address(address):
  print expand_address(address)
  parts = parse_address(expand_address(address)[0])
  print parts
  prettified = ""
  for part in parts:
    prettified = prettified + part[0] + ", "
  return prettified[0:-2]      




def print_with_timestamp(msg):
  print time.ctime() + ": " + msg
  # explicitly flushing stdout makes sure that a .out file stays up to date -
  # else it can be hard to keep track of whether a background job is hanging
  sys.stdout.flush()



if __name__ == "__main__":
  sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
  sys.stdout = codecs.getwriter("UTF8")(sys.stdout)
  main()