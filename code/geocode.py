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

# geocoding API - see https://github.com/geopy/geopy for info
import geopy
from geopy.geocoders import GoogleV3
from geopy.geocoders import Nominatim

# temp workaround until https://github.com/geopy/geopy/pull/183 is accepted
from mapzen_geocoder import Mapzen

import geocoder_keys

covered_area = {
  "minX": 44.78,
  "maxX": 45.26,
  "minY": -93.78,
  "maxY": -93.17
}

def main():
  print_with_timestamp("Starting run.")
  
  inputfile = "../Hennepin County Moving Violations 2010-2015_regularised_addresses.csv"
  verbosity = 8
  
  geolocators = [
    {
      "name": "Mapzen",
      "geocoder": Mapzen(api_key=geocoder_keys.mapzenkey, country_bias="USA"),
      "outfile": open("../geocoded_mapzen.csv", 'w'),
      "n_geocoded": 0
    },
    {
      "name": "Nominatim",
      "geocoder": Nominatim(),
      "outfile": open("../geocoded_nominatim.csv", 'w'),
      "n_geocoded": 0
    },
    {
      "name": "Google",
      "geocoder": GoogleV3(api_key=geocoder_keys.googlekey),
      "outfile": open("../geocoded_google.csv", 'w'),
      "n_geocoded": 0
    }
  ]
  
  
  with open(inputfile, 'rU') as f_in:
    reader = csv.DictReader(f_in, dialect="excel")
    for geolocator in geolocators:
      geolocator["writer"] = csv.DictWriter(geolocator["outfile"], reader.fieldnames + ["geocoded_string", "latitude", "longitude"], encoding="utf8")
      geolocator["writer"].writeheader()
    
    n_attempted = 0
    for row in reader:
      n_attempted += 1
      strings = [
        row["parsed_w_county_and_state"], 
        row["parsed_w_state"], 
        row["parsed_address"], 
        row["offloctn"],
        row["parsed_w_city"]
      ]
      
      for geolocator in geolocators:
        if geolocator["name"] != "Google" or n_attempted % 350 == 1:
          location, source, reason, string = geocoderecord([geolocator["geocoder"]], strings, verbosity)

          if location is not None:
            geolocator["n_geocoded"] +=1
            row["latitude"] = location.latitude
            row["longitude"] = location.longitude
            row["geocoded_string"] = string
          else:
            row["latitude"] = ""
            row["longitude"] = ""
            row["geocoded_string"] = ""
#            print "No result found by", geolocator["name"], "for", row["offloctn"], "/", row["parsed_address"]
#            print reason

          geolocator["writer"].writerow(row)
          if geolocator["n_geocoded"] % 100 == 0:
            print_with_timestamp(geolocator["name"] + " geocoded " + str(geolocator["n_geocoded"]) + " of " + str(n_attempted) + " addresses attempted so far.")
      
    for geolocator in geolocators:
      geolocator["outfile"].close()
    

  print_with_timestamp("Run complete.")


  
  
def geocoderecord(geolocators, strings, verbosity):
  failures = 0
  skiplist = []
  reason = ""
  for string in strings:
    for geolocator in geolocators:
      if geolocator not in skiplist:
        try:
          result = geolocator.geocode(string)
          valid_result, error_text = is_valid_result(result, 0.00000000000001)
          if not valid_result:
            result = None
            reason = reason + getgeocodername(geolocator) + " " + error_text + " for address " + string + "; "
        except geopy.exc.GeopyError as e:
          print getgeocodername(geolocator) + " returned error: " + str(e)
          skiplist.append(geolocator)
          result = None
          reason = reason + getgeocodername(geolocator) + " threw error " + str(e) + " for address " + string + "; "
        except:
          result = None
          reason = reason + getgeocodername(geolocator) + " returned nothing for address " + string + "; "
        if result is None:
          failures = failures + 1
          if failures >= verbosity:
            print "Failure #" + str(failures) + " no result for " + string + " from " + getgeocodername(geolocator)
        else:
#          print string, "found by", getgeocodername(geolocator)
          return result, getgeocodername(geolocator), reason, string
  return None, None, reason, None




def is_valid_result(location, tolerance):
#  for geocoder in null_coords.keys():
#    if calc_offset(null_coords[geocoder], location) < tolerance:
#      return False, "At " + geocoder + "'s NULL location"

  if location.latitude < covered_area["minX"]:
    return False, "S of covered area"
  elif location.latitude > covered_area["maxX"]:
    return False, "N of covered area"
  elif location.longitude < covered_area["minY"]:
    return False, "W of covered area"
  elif location.longitude > covered_area["maxY"]:
    return False, "E of covered area"

  return True, ""  
  
  
  
  
def getgeocodername(geolocator):
  locatorstr = str(geolocator)
  start = locatorstr.find("geopy.geocoders.")+16
  finish = locatorstr.find(" object at ")
  return locatorstr[start:finish]



def print_with_timestamp(msg):
  print time.ctime() + ": " + msg
  # explicitly flushing stdout makes sure that a .out file stays up to date -
  # else it can be hard to keep track of whether a background job is hanging
  sys.stdout.flush()



if __name__ == "__main__":
  sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
  sys.stdout = codecs.getwriter("UTF8")(sys.stdout)
  main()
