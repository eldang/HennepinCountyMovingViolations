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
from postal.parser import parse_address

def main():
  print_with_timestamp("Starting run.")
  
  inputfile = "../Hennepin County Moving Violations 2010-2015.csv"
  interstates = ["494", "694", "394", "35w", "94"]
  us_highways = ["12", "169", "212"]
  state_routes = ["62", "77", "100", "101", "610"]
  directions = ["nb", "northbound", "eb", "eastbound", "sb", "southbound", "wb", "westbound"]

  outputfile = inputfile[:-4] + "_regularised_addresses.csv"
  with open(outputfile, 'w') as f_out:
    with open(inputfile, 'rU') as f_in:
      reader = csv.DictReader(f_in, dialect="excel")
      writer = csv.DictWriter(f_out, reader.fieldnames + ["parsed_address", "parsed_w_city", "parsed_w_state", "parsed_w_county_and_state"], encoding="utf8")
      writer.writeheader()
      n = 0
      for row in reader:
        offloctn = row["offloctn"].lower().replace("n/b", "").replace("e/b", "").replace("s/b", "").replace("w/b", "").replace("nb ", "").replace("eb ", "").replace("sb ", "").replace("wb ", "").replace(" nb", "").replace(" eb", "").replace(" sb", "").replace(" wb", "").replace("(", "").replace(")", "").replace("/", "&").replace("@", "&").replace(" from ", "&").replace(" at ", "&").replace("&&", "&")
#        print offloctn
        addr = ""
        for loc in offloctn.split("&"):
          if addr != "":
            addr = addr + " & "
          found = False
          for interstate in interstates:
            if loc.strip() == interstate:
              addr += "I-" + interstate
#              print loc, "||", row["offloctn"], "||", addr
              found = True
              break
          if not found:
            for hwy in us_highways:
              if loc.strip() == hwy:
                addr += "US-" + hwy
#                print loc, "||", row["offloctn"], "||", addr
                found = True
                break
          if not found:
            for rte in state_routes:
              if loc.strip() == rte:
                addr += "SR-" + rte
#                print loc, "||", row["offloctn"], "||", addr
                found = True
                break     
          if not found:
            newpart = ""
            for token in parse_address(loc + ", Hennepin County, Minnesota, USA"):
              if token[0] not in (u'hennepin county', u'minnesota', u'usa'):
                if newpart != "":
                  if token[1] in (u'suburb', u'city'):
                    newpart += ", "
                  else:
                    newpart += " "
                newpart += token[0]
                  
            addr = addr + newpart
#          print parse_address(loc + ", Hennepin County, Minnesota, USA")
#          print addr
        addr = addr.replace("cr ", "County Road").replace("co rd ", "County Road")
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
 




def print_with_timestamp(msg):
  print time.ctime() + ": " + msg
  # explicitly flushing stdout makes sure that a .out file stays up to date -
  # else it can be hard to keep track of whether a background job is hanging
  sys.stdout.flush()



if __name__ == "__main__":
  sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
  sys.stdout = codecs.getwriter("UTF8")(sys.stdout)
  main()