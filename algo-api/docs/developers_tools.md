# Developer Tools and Commands

## JSON and jq utilities
- Export the NSE Instruments into CSV:
  ```bash
  jq -r 'map(select(.instrument_key == "NSE_INDEX|Nifty 50" or .underlying_key == "NSE_INDEX|Nifty 50")) | (.[0] | keys_unsorted) as $keys | $keys, map([.[ $keys[] ]])[] | @csv' NSE.json > NSE_NIFTY.csv
