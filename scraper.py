import re
from bs4 import BeautifulSoup
from nltk import word_tokenize
from reppy.robots import Robots
from urllib.parse import urlparse

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link) and check_for_uci(link) and status_valid(resp)]

def extract_next_links(url, resp):
    frontier_list = list() 
    if (resp.raw_response != None and (resp.status >= 200 and resp.status <= 599)):
        soup = BeautifulSoup(resp.raw_response.content,"html.parser")
        for link in soup.find_all('a'):
            if link.get('href') != None and robot.allowed(link.get('href'),'IR S20 33805012,43145172,61658242'):
                frontier_list.append(link.get('href')); 
    return frontier_list

def extract_tokens(url, resp):
    soup = BeautifulSoup(resp.raw_response.content,'html.parser')
    raw = soup.get_text()
    all_tokens = word_tokenize(raw)

    tokens = [t for t in all_tokens if re.match('^[A-Z]*[a-z0-9]*$',t) and len(t) > 1]
    # not complete
    # testing if i should use global variable or read from file

def check_for_uci(url):
    parsed = urlparse(url)
    urlRegex = re.compile('^([\w|.]*)(ics.uci.edu|cs.uci.edu|informatics.uci.edu|stat.uci.edu|today.uci.edu/department/information_computer_sciences)$')
    if(re.match(urlRegex, parsed.netloc)):
        return True
    

def is_valid(url):
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise

# only crawls up urls with status 200
# may need to change this
def status_valid(resp):
    return resp.status == 200