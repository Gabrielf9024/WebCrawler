import re
from bs4 import BeautifulSoup
from nltk import word_tokenize
from reppy.robots import Robots
from urllib.parse import urlparse

stop_words = {'about','above','after','again','against','all','am','an','and','any','are',
            'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between',
            'both', 'but', 'by', 'cannot', 'could', 'did', 'do', 'does', 'doing', 'down', 'during', 'each', 
            'few', 'for', 'from','further', 'had', 'has', 'have', 'having', 'he',
            'her', 'here', 'hers', 'herself', 'him', 'himself', 'his', 'how'
            'if', 'in', 'into', 'is', 'it', 'its', 'itself', 'me', 'more', 'most', 'my', 'myself'
            'no', 'nor', 'not', 'of', 'off', 'on', 'once', 'only', 'or', 'other', 'ought', 'our', 'ours',
            'ourselves', 'out', 'over', 'own', 'same', 'she', 'should', 'so', 'some', 'such', 'than', 'that', 'the',
            'their', 'theirs', 'them', 'themselves', 'then', 'there', 'these', 'they', 'this', 'those', 'through',
            'to', 'too', 'under', 'until', 'up', 'very', 'was', 'we', 'were', 'what', 'when', 'where', 'which', 
            'while', 'who', 'whom', 'why', 'with', 'would', 'you', 'your', 'yours', 'yourself', 'yourselves'}
html_junk = {'http', 'https', 'function', 'return', 'important','var', 'ariel', 'emoji', 'tex2jax'} # i will add more


def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    frontier_list = list()

    #fetches the robots.txt
    robot_link = get_link_robot(url);
    if robot_link != None:
        robot = Robots.fetch(robot_link);
        if (resp.raw_response != None and resp.status >= 200 and check_for_trap(url) == False):
            soup = BeautifulSoup(resp.raw_response.content,"html.parser")
            extract_tokens(soup)
            for link in soup.find_all('a'):
                if link.get('href') != None and check_if_valid(url) and check_for_trap(url) == False and robot.allowed(link.get('href'),'IR S20 33805012,43145172,61658242'):
                    frontier_list.append(link.get('href'));

    return frontier_list

def extract_tokens(soup):
    freq = {}
    token_file = open('tokens.txt','r')
    for line in token_file: # works ok, i will try to make it better
        t,c = line.split()
        freq[t] = int(c)
    token_file.close()

    raw = soup.get_text()
    all_tokens = word_tokenize(raw)

    for t in all_tokens:
        t = t.lower()
        if re.match('^[a-zA-Z]+[a-z0-9]+$',t) and t not in stop_words and t not in html_junk:
            if t in freq:
                freq[t] += 1
            else:
                freq[t] = 1

    descending = sorted(freq.items(), key=lambda x:x[1],reverse=True)
    open('tokens.txt','w').close() # clears previous dict
    token_file = open('tokens.txt','w')

    for t,c in descending: # writes token freq in txt file
        token_file.write("{} {}\n".format(t,c))
    token_file.close()


#Checks whether the url is a trap
def check_for_trap(url):
    parsed = urlparse(url)
    urlRegex = re.compile('(/.+?)(?:\1)+|(\?|&)[\w\W]+|(calendar)')
    if(urlRegex.search(parsed.netloc) == None):
        return False
    else:
        return True

    
# Returns the link of the Robots.txt as a string
def get_link(url):
    parsed = urlparse(url)
    urlRegex = re.compile('(?:[a-zA-z]+[.]{0,1})*(ics.uci.edu|cs.uci.edu|informatics.uci.edu|stat.uci.edu|today.uci.edu/department/information_computer_sciences)')
    if(urlRegex.search(parsed.netloc) != None):
        x,y = urlRegex.search(parsed.netloc).span();
        return parsed.netloc[:y] + "/robots.txt";
    return None

#Checks if valid uci link
def check_if_valid(url):
    parsed = urlparse(url)
    urlRegex = re.compile('(?:[a-zA-z]+[.]{0,1})*(ics.uci.edu|cs.uci.edu|informatics.uci.edu|stat.uci.edu|today.uci.edu/department/information_computer_sciences)')
    if(urlRegex.search(parsed.netloc) != None):
        return True
    return False

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
