import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup, Comment
import database as db

# list of valid domains to check for
valid_domains = [
    "ics.uci.edu",
    "cs.uci.edu",
    "informatics.uci.edu",
    "stat.uci.edu",
    "today.uci.edu/department/information_computer_sciences"
]

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    """
    Implementation required.
    url: the URL that was used to get the page
    resp.url: the actual url of the page
    resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    resp.error: when status is not 200, you can check the error here, if needed.
    resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
            resp.raw_response.url: the url, again
            resp.raw_response.content: the content of the page!
    Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    """
    # unique_links = set()

    # ensures that the status is ok
    # if resp.status != 200: 
    #     print(f'An error has occured: Received response status {resp.status} for URL {url}')
    #     return list()
    
    # # ensures that the content is not empty
    # if not resp.raw_response or not resp.raw_response.content:
    #     print(f'There is no content find this URL {url}')
    #     return list()
    
    # soup_obj = BeautifulSoup(resp.raw_response.content, "lxml")

    # # removes all comment from the html file
    # for comment in soup_obj.find_all(text = lambda text: isinstance(text, Comment)):
    #     comment.extract()

    # # removes all <script> and <style> tags
    # for tag_element in soup_obj.find_all(['script', 'style']):  
    #     tag_element.extract()

    # # raw_text = soup_obj.get_text()
    # # main_text = re.sub('\s+', ' ', raw_text)

    # for link in soup_obj.find_all('a'):
    #     current_link = link.get('href')
    #     if current_link:
    #         parsed_link = urlparse(current_link)
    #         link_without_fragment = urlunparse(parsed_link._replace(fragment=''))
    #         unique_links.add(link_without_fragment)

    # checks status status of the response
    if resp.status < 400 and resp.status >= 300:
        try:
            return list(resp.raw_response.url)
        except:
            pass # skips the url completely
    if (not resp.raw_response) or (not resp.raw_response.content) or (resp.status != 200) or (url in db.crawled_links) or (url in db.blacklist_links): # checks if its blanks or have been crawled already
        return list()

    soup_obj = BeautifulSoup(resp.raw_response.content, "html.parser")

    # removes all comment from the html file
    for comment in soup_obj.find_all(text = lambda text: isinstance(text, Comment)):
        comment.extract()

    # removes all <script> and <style> tags
    for tag_element in soup_obj.find_all(['script', 'style']):  
        tag_element.extract()

    # gets the actual text inside the HTML file
    raw_text = soup_obj.get_text()
    main_text = re.sub('\s+', ' ', raw_text)

    # checks if the file has low contextual value
    if len(main_text) < 150:
        db.blacklist_url.add(url)
        return list()

    links = db.find_unique_links(soup_obj)
    return list(links)


    




def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)

        # conditions that would lead to the current link invalid
        if parsed.scheme not in set(["http", "https"]): # ensures that it is using a secure scheme
            return False
        
        if parsed.netloc not in valid_domains: 
            return False
        
        if any(substring in url for substring in ("?share=", "pdf", "redirect", "#comment", "#respond", "#comments")):
            return False
        
        if re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower()): return False
        
        # url is valid if it passes all the conditions above
        return True

    except TypeError:
        print ("TypeError for ", parsed)
        raise
