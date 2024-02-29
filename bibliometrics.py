'''
Author: Matthew Rezkalla
Date: 2021-01-01
Description: Program to scrape PubMed of all the publications for each author in 'authors.txt'. Then the program goes to
scimagojr.com to find all the impact factor and h-index of the journal. Everything is separated with '|' , so when
converted to excel, use delimiter: '|' . Update 'authors.txt' for different authors.

If errors come up:
The program most likely has a problem with the name of the author or the number of publications they have (0-1)
'''

import bs4 as bs
from random import uniform
import requests
import time
import sys


# Researcher class
class Researcher:
    """
    Represents a researcher and their publications.

    Attributes:
        publications (list): A list of publication records.
        numOfPublications (int): The number of publications.

    """

    def __init__(self):
        """
        Initializes a new instance of the Researcher class.

        """
        self.publications = []
        self.numOfPublications = 0

    def addPublication(self, name, date, journal, citationCount, role, title, authList, impact, hIndex):
        """
        Adds a publication to the researcher's list of publications.

        Args:
            name (str): The name of the publication.
            date (str): The publication date.
            journal (str): The journal of the publication.
            citationCount (int): The citation count of the publication.
            role (str): The role of the researcher in the publication.
            title (str): The title of the publication.
            authList (list): A list of authors of the publication.
            impact (str): The impact factor of the publication's journal.
            hIndex (str): The h-index of the publication's journal.

        """
        pub = f'{title}|{date}|{name}|{str(authList)}|{role}|{str(citationCount)}|{journal}|{str(impact)}|{str(hIndex)}'
        self.publications.append(pub)

    def getPublications(self):
        """
        Returns the list of publications.

        Returns:
            list: A list of publication records.

        """
        return self.publications



# function to request a beautiful soup object (HTML page code from the URL given) and returns it.
def request(url):
    return bs.BeautifulSoup(requests.session().get(url, headers={'User-agent': 'Chrome/64.0.3282.186'}).text, 'html.parser')


# Function to find the metrics of an author
def getMetrics(author):
    """
    Finds all publications for the given author.

    Args:
        author (str): The name of the author.

    Returns:
        Researcher: An instance of the Researcher class containing the author's publications.

    """

    print('\nFinding all publications for: ' + author)
    R = Researcher()
    name = author.split(', ')

    # requesting PubMed search page for author
    # can edit the range using filter=years.2011 - whatever
    pubmed = request("https://www.ncbi.nlm.nih.gov/pubmed/?term=" + name[0].replace("'", "+") + "%2C+" +
                     name[1].replace("'", "+") + "%5BAuthor%5D&filter=years.2011-2020&sort=date&size=200")

    print("https://www.ncbi.nlm.nih.gov/pubmed/?term=" + name[0].replace("'", "+") + "%2C+" +
          name[1].replace("'", "+") + "%5BAuthor%5D&filter=years.2011-2020&sort=date&size=200")

    time.sleep(uniform(1, 2.3))  # scraping break

    # for each publication for the author, add it to authors publications
    for result in pubmed.find_all('div', class_='docsum-content'):

        article = request('https://pubmed.ncbi.nlm.nih.gov/' + result.find('a').get('href'))

        # getting title
        for word in article.find('h1', class_='heading-title').text.split('\n'):
            if word.strip():
                title = word
                break

        # getting journal and date
        journAndDate = article.find('div', class_='article-source').text.split('\n')
        journAndDate = list(filter(None, (journAndDate[2] + journAndDate[9]).split(' ')))

        i = 1
        for el in journAndDate[1:]:
            i += 1
            if el == '.':
                break
            else:
                journAndDate[0] += f' {el}'
        journAndDate[1] = ' '.join(journAndDate[i:]).split(';')  # date

        # finding impact factor of journal and h-index
        i = 1
        journalRanking = request(
            f'https://www.scimagojr.com/journalsearch.php?q={journAndDate[0]}'
        )

        # printing scimagojr lin
        # print('https://www.scimagojr.com/journalsearch.php?q=' + journAndDate[0].replace(' ', '+'))

        # if the journal was found
        if journalRanking.find('div', class_='search_results').find('a'):
            journalRanking = request(
                'https://www.scimagojr.com/' + journalRanking.find('div', class_='search_results').find('a').get(
                    'href'))

            hIndex = journalRanking.find('div', class_='hindexnumber').text
            table = journalRanking.find('div', class_='cell1x1 dynamiccell').table.findAll('tr')

            # impact factor
            for row in table:
                if str(row.text[:4]) == str(
                    journAndDate[1][0][:4]
                ) or i == len(table):
                    impactFactor = row.text[4:]
                    break
                else:
                    i += 1
        else:
            impactFactor = 'N/A'
            hIndex = 'N/A'

        role, counter, authList = 1, [1, 0], []  # second element count the number of authors
        authors = article.find('div', class_='authors-list')

        for auth in authors.findAll('span', class_='authors-list-item'):  # getting name
            au = auth.find('a', class_='full-name').text.split(' ')[-1] + ', ' + \
                 auth.find('a', class_='full-name').text.split(' ')[0][0]
            authList.append(au)

            if name[0].lower() in auth.find('a', class_='full-name').text.lower().split(' '):
                name.append(auth.find('a', class_='full-name').text)
                role = int(counter[0])
            else:
                counter[0] += 1

            counter[1] += 1

        role_mapping = {1: '1', 2: '2'}
        role = role_mapping.get(role, '3' if role != counter[1] else '4')

        R.addPublication(name[len(name) - 1], journAndDate[1][0], journAndDate[0], "", role, title[2:],
                         authList, impactFactor, hIndex)

    return R  # returning researcher object and all their publications


def main():  
    # list of Researcher objects
    researchers = []
    i = 0

    # open authors.txt and find all publications for each author, print to metrics.txt
    with open('authors.txt', 'r') as a:
        with open('metrics.txt', 'w') as m:
            for line in a:

                researchers.append(getMetrics(line))  # getting the metrics for given name

                publications = researchers[i].getPublications()

                print("Number of publications: ", str(len(publications)))

                # writing publications to metrics.txt
                for pub in publications:
                    print(pub)
                    m.write(pub + '\n')
                m.write('\n')
                i += 1

    sys.exit()


main()
