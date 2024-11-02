from configparser import ConfigParser
from argparse import ArgumentParser

from utils.server_registration import get_cache_server
from utils.config import Config
from crawler import Crawler
from scraper import wordCount
from report import Report

def main(config_file, restart):
    global wordCount

    cparser = ConfigParser()
    cparser.read(config_file)
    config = Config(cparser)
    config.cache_server = get_cache_server(config, restart)
    crawler = Crawler(config, restart)
    crawler.start()

    
    commonWords = wordCount.getTopFifty() # retrieves top 50 words with their assoc. counts [(word, count), ...]
    maxUrl = wordCount.getMaxWordsUrl() # retrievs the url with the most tokens in a tuple ('url', token_count)

    # add questions 2 and 3 to the report file and add questions 1 and 4 manually through worker.log observations
    with open('report.txt', 'w') as report:
        question2 = f"URL with the longest word count: {maxUrl[0]} with a total of {maxUrl[1]} words."
        report.write(question2)

        question3 = "TOP 50 Most Common Words (DESC):\n"
        for word, count in commonWords:
            question3 += f"\t{word} --> {count}\n"
        report.write(question3)






if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--restart", action="store_true", default=False)
    parser.add_argument("--config_file", type=str, default="config.ini")
    args = parser.parse_args()
    main(args.config_file, args.restart)
    
