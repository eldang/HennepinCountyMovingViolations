# HennepinCountyMovingViolations
List of moving violations given from 2010 to 2015. Includes location and date.

## Expanded addresses

I've tried doing some address regularisation so that geocoders do better with this.  `Hennepin County Moving Violations 2010-2015_regularised_addresses.csv` contains some added columns:

* parsed_address: just expands the `offloctn` string to a human-readable "A Ave & 2 Street" type format. 
* parsed_w_city: adds ", Minneapolis, Minnesota, USA" to the previous.  **Important note**: Not all of these addresses are actually in Minneapolis, so this one should probably be treated with suspicion.  I am experimenting....
* parsed_w_state: adds ", Minnesota, USA" to the string in `parsed_address`.  Probably too ambiguous for geocoding, but it should always return something.
* parsed_w_county_and_state: adds ", Hennpin County, Minnesota, USA" to the string in `parsed_address`.  This is the most unambiguous version I can make, but not all geocoders understand the county part.
