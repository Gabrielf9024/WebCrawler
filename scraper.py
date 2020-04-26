import re
from bs4 import BeautifulSoup
from nltk import word_tokenize
from reppy.robots import Robots
from urllib.parse import urlparse

site_dict = dict();

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    frontier_list = list()

    #fetches the robots.txt
    if check_if_valid(url):
        robot_link = get_link_robot(url);
        robot = Robots.fetch(robot_link);
        if (resp.status >= 200 and resp.raw_response != None):
            soup = BeautifulSoup(resp.raw_response.content,"html.parser")
            extract_tokens(soup)
            for link in soup.find_all('a'):
                if link.get('href') != None and robot.allowed(link.get('href'),'IR S20 33805012,43145172,61658242'):
                    frontier_list.append(link.get('href'));

    return frontier_list

def extract_tokens(soup):
    raw = soup.get_text()
    all_tokens = word_tokenize(raw)

    tokens = [t for t in all_tokens if re.match('^[A-Z]*[a-z0-9]*$',t) and len(t) > 1]
    # not complete
    # testing if i should use global variable or read from file
    
# Returns the link of the Robots.txt as a string
def get_link(url):
    parsed = urlparse(url)
    if(urlRegex.search(parsed.netloc) != None):
        return parsed.netloc + "/robots.txt";

#Checks if valid uci link and not a trap
def check_if_valid(url):

    try:
        parsed = urlparse(url)

        is_uci = False
        is_trap = True
        
        urlRegex = re.compile('(?:([a-zA-z]+[.]{0,1})*(ics.uci.edu)|(cs.uci.edu)|(informatics.uci.edu)|(stat.uci.edu)|(today.uci.edu/department/information_computer_sciences))')
        if(urlRegex.search(parsed.netloc) != None):
            is_uci = True
            
        pathRegex = re.compile('(/.+?)(?:\1)+|(\?|&)[\w\W]+|(calendar)')
        if(pathRegex.search(parsed.path) == None and parsed.query == ''):
            is_trap = False
            
        valid = (is_uci and is_trap == False)
        
        if valid == True:
            try:
                site_dict[parsed.netloc] = (1,list())
            except:
                if parsed.path not in site_dict[parsed.netloc][1]:
                    site_dict[parsed.netloc][0]++
                    site_dict[parsed.netloc][1].append(parsed.path)
                else:
                    valid = False

        return valid
    
    except TypeError:
        print ("check_if_valid internal error for ", parsed)
        raise
        
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
