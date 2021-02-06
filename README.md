# Marvel Impossible Travel

This project uses the Marvel Developer API to pick a unique character and populate a databse file with that characters known mutual comic appearances through the years.


- For authentication, add apikeys to the file `.apikeys`

- To launch this project, simple run 

```
launchdocker.sh
```

The resulting database will live in the project folder at `spectrum.db`

Notes:

To save API calls, this project employs a character lookup table, which is populated with each paginated call to the Marvel Developer API portal, and has results of characters set to 100 results per call.

When a character lookup is called, the logic first looks to the local table, then if no data is found to the Developer API.

This keeps us well within the limits of the 3,000 calls per day limitation.