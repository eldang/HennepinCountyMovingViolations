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

  outputfile = inputfile[:-4] + "_expanded_addresses.csv"
  with open(outputfile, 'w') as f_out:
    with open(inputfile, 'rU') as f_in:
      reader = csv.DictReader(f_in, dialect="excel")
      writer = csv.DictWriter(f_out, reader.fieldnames + ["parsed_address"], encoding="utf8")
      writer.writeheader()
      n = 0
      for row in reader:
        addr = row["offloctn"].replace("&", " & ").replace("/", " & ").replace("@", " & ")
        addr = addr + ", Hennepin County, Minnesota, USA"
        row["parsed_address"] = prettify_address(addr)
        writer.writerow(row)
        n = n + 1
        if n % 5000 == 0:
          print_with_timestamp("Wrote " + str(n) + " rows so far.")

  print_with_timestamp("Run complete.")



def prettify_address(address):
  parts = parse_address(expand_address(address)[0])
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