# PubMed Bibliometrics Retrieval

Searches PubMed for all the publications for each author in ``` authors.txt ```, and adds them all too ``` metrics.txt ```. The program searches scimagojr.com for the journal for each publication. This is where it gathers the impact factor and h-index of the journal.

## Dependencies

```bash
pip install beautifulsoup4==4.9.3 requests==2.25.1 
```

## Usage

Scrape PubMed of all the publications for each author in 'authors.txt'. Then the program goes to
scimagojr.com to find all the impact factor and h-index of the journal. Everything is separated with '|' , so when
converted to excel, use delimiter: '|' . 

*** Update ``` authors.txt ``` for different authors. ***

## Potential Errors:
 - Author has an error in their name in the 'authors.txt' file
- Author has  0 - 1 publications; should to be done manually

## License

[MIT](https://choosealicense.com/licenses/mit/)