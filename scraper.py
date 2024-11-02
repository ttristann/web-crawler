
import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup, Comment
from database import Database as db
from robot_parser import RobotParser 
from hash_content import ContentHashManager

# list of valid domains to check for
# valid_domains = [
#     ".ics.uci.edu",
#     ".cs.uci.edu",
#     ".informatics.uci.edu",
#     ".stat.uci.edu",
#     ".today.uci.edu/department/information_computer_sciences"
# ]

def scraper(url, resp):
    # checks for duplicates
    # Check if resp is valid and has a raw_response
    if not resp or resp.raw_response is None:
        print(f"No valid response received for URL: {url}")
        return []  # Skip this URL or handle the error appropriately

    # Now check if raw_response has content
    if resp.raw_response.content is None:
        print(f"No content in response for URL: {url}")
        return []  # Skip this URL or handle the error appropriately

        
    hash_manager = ContentHashManager()
    content_hash = hash_manager.generate_hash(resp.raw_response.content)
    if hash_manager.is_duplicate(url, content_hash):
        print("A DUPLICATE IS FOUND")
        db.blacklist_links.add(url)
        return list()

    # checks for /events to check for calendar trap
    if "/events" in url:
        if len(db.events_links) < 300:
            db.events_links.add(url)
            print(f"EVENTS ADDED - CURRENT LENGTH: {len(db.events_links)}")
        else: 
            print("EVENTS EXCEEDED")
            return list()

    # continues if the content of the url is unique
    links = extract_next_links(url, resp)
    valid_links = []
    robot_parsers = {}

    for link in links:
        if is_valid(link):
            # # get the root domain of the current link
            # root_domain = f"{urlparse(link).scheme}://{urlparse(link).netloc}"

            # # check if RobotParser for this root domain already exists
            # if root_domain not in robot_parsers:
            #     robot_parsers[root_domain] = RobotParser(root_domain)  # create and cache the RobotParser

            # current_robot = robot_parsers[root_domain]

            # # check if link is allowed by robots.txt and add to valid links if so
            # if current_robot.is_allowed(link):
            valid_links.append(link)

            # # append sitemaps (once per domain) to valid_links
            # valid_links.extend(current_robot.sitemaps)
    # print(f"CURRENT LENGTH OF CRAWLED LINKS: {len(db.crawled_links)} --------------------------------") # noticed that when the crawler gets interuppted, it loses track of some of crawled links
    return valid_links

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
    # checks status status of the response
    if resp.status < 400 and resp.status >= 300:
        try:
            return list(resp.raw_response.url)
        except:
            pass # skips the url completely
    if (not resp.raw_response) or (not resp.raw_response.content) or (resp.status != 200) or (url in db.crawled_links) or (url in db.blacklist_links): # checks if its blanks or have been crawled already
        return list()

    soup_obj = BeautifulSoup(resp.raw_response.content, "html.parser")

    # ensures that calendar days with no content are ignored
    if url in db.events_links and "no" in soup_obj.get_text(strip=True).lower():
        db.blacklist_links.add(url)
        print("NO RESULTS")
        return list()

    # removes all comment from the html file
    for comment in soup_obj.find_all(text = lambda text: isinstance(text, Comment)):
        comment.extract()

    # removes all <script> and <style> tags
    for tag_element in soup_obj.find_all(['script', 'style']):  
        tag_element.extract()

    # gets the actual text inside the HTML file
    raw_text = soup_obj.get_text(strip=True)
    main_text = re.sub(r"[^A-Za-z0-9\s]+", "", raw_text)

    if not _is_low_contextual_value(main_text, soup_obj.find_all()):
        db.blacklist_links.add(url)
        return list()

    ### TODO: need to accomodate to find unique links with fragments while using the database class
    ### this code has to stay here -> urlparse has be called here if not, it goes into error that i dont know how to fix
    main_set = set() # collects all of the links to be crawled
    # iterates through soup obj to find and filter through the links
    for link in soup_obj.find_all('a'):
        current_link = link.get('href')
        full_link = urlparse(current_link).geturl()
        main_set.add(full_link)
    
    return list(main_set)

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)

        # conditions that would lead to the current link invalid
        if parsed.scheme not in set(["http", "https"]): # ensures that it is using a secure scheme
            return False
        
        # if parsed.netloc not in valid_domains: 
        #     return False
        # if not re.match('\S*.ics.uci.edu$|\S*.cs.uci.edu$|\S*.informatics.uci.edu$|\S*.stat.uci.edu$|\S*today.uci.edu/department/information_computer_sciences$', parsed.netloc):
        url_pattern = r'^(https?://)?([a-zA-Z0-9-]+\.)?(ics\.uci\.edu|cs\.uci\.edu|informatics\.uci\.edu|stat\.uci\.edu|today\.uci\.edu/department/information_computer_sciences)/.*$'
        if not re.match(url_pattern, parsed.netloc):
            return False
        

        if url in db.blacklist_links: 
            return False
        
        if any(substring in url for substring in ("?share=", "pdf", "redirect", "#comment", "#respond", "#comments")):
            return False

        if url.endswith("ical=1"): # this is to avoid the link that downsloads the calendar
            print("detected calendar download link")
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
        # url can be added to the scraped
        if (url):
            db.crawled_links.add(url)

        return True

    except TypeError:
        print ("TypeError for ", parsed)
        raise

def _is_low_contextual_value(soup_text, soup_tags):
    # tokenizes all of the text inside a html 
    text_tokens = _custom_tokenize(soup_text)

    # compares the lengths to determine if low context
    # if rate < 95% for text-to-HTML, it is low context
    total_length = len(text_tokens) + len(soup_tags)
    if total_length == 0:
        return True  # handle cases with no content by considering them low context

    text_ratio = len(text_tokens) / total_length
    html_ratio = len(soup_tags) / total_length

    # return true if the HTML or text ratio indicates low context
    return not (text_ratio > .95 or html_ratio > .95)

def _custom_tokenize(text):
    # use regex to split the text into tokens
    # this regex will match words and ignore punctuation
    # acts a replacement to nltk
    return re.findall(r'\b\w+\b', text)