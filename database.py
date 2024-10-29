from urllib.parse import urlparse, urlunparse
from bs4 import BeautifulSoup, Comment

class Database:
    crawled_links = set() # keeps track of the URLs that have been crawled
    unique_links = set() # keeps track of all the unique ones, removes the fragment
    blacklist_links = set() # keeps track of all sites to completely avoid due to either being low content or being a trap
    events_links = set() # keeps track of all the links with the /events to avoid the calendar trap

    @classmethod
    def find_unique_links(cls, soup_obj):
        main_set = set() # collects all of the links to be crawled
        # iterates through soup obj to find and filter through the links
        for link in soup_obj.find_all('a'):
            current_link = link.get('href')
            if current_link: # removes fragment if current link is not empty string
                parsed_link = urlparse(current_link)
                link_without_fragment = urlunparse(parsed_link._replace(fragment='')) # defragmented version
                if (link_without_fragment not in cls.unique_links):
                    main_set.add(parsed_link)
                    cls.unique_links.add(link_without_fragment)

        return main_set
