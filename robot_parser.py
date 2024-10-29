import re
import requests
from urllib.parse import urlparse, urljoin

class RobotParser:
    def __init__(self, url):
        self.domain_url = self.get_root_domain(url)  # make it an instance attribute
        self.robot_url = self.domain_url + "/robots.txt"  # make robot_url an instance attribute
        self.disallowed_paths, self.sitemaps = self.get_robots_content()

    def get_root_domain(self, passed_url):
        parsed_link = urlparse(passed_url)
        return parsed_link.scheme + "://" + parsed_link.netloc
    
    def get_robots_content(self):
        # fetch and parse robots.txt
        print("ROBOT URL", self.robot_url)
        try:
            response = requests.get(self.robot_url)
        except Exception as e:
            # Most likely SSLError, we aren't allowed/couldn't access robots.txt of url
            # Assigning self.disallowed_paths, self.sitemaps = [],[] because there is no info to use
            return [], [] 
        

        main_robot_txt = response.text

        # use regex to parse the robots.txt for disallowed paths and sitemaps
        disallowed_paths = re.findall(r"Disallow:\s*(.*)", main_robot_txt)
        sitemaps = re.findall(r"Sitemap:\s*(.*)", main_robot_txt)

        # clean up whitespace
        disallowed_paths = [path.strip() for path in disallowed_paths]
        sitemaps = [url.strip() for url in sitemaps]

        return disallowed_paths, sitemaps

    def is_allowed(self, url):
        # check if the URL path matches any disallowed paths
        # If disallowed paths are empty, then we 
        parsed_url = urlparse(url)
        for path in self.disallowed_paths:
            if parsed_url.path.startswith(path):
                return False
        return True