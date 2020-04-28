import re
from bs4 import BeautifulSoup
from nltk import word_tokenize
from reppy.robots import Robots
from urllib.parse import urlparse

# This library can be found online at http://ekzhu.com/datasketch/index.html
from datasketch import MinHash, MinHashLSH

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

site_dict = dict()
sub_list = list()
freq = {}
largest_url = ('',0)

# This is the master MinHash that all documents are added into / checked against
# We change the threshold to be the percent minimum a text needs to match
# in similarity in order to be deemed 'too similar'
#lsh = MinHashLSH(threshold=0.9,num_perm=5000)
#site_count = 0

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    global site_count
    #global lsh
    frontier_list = list()

    #fetches the robots.txt
    if check_if_valid(url):
        robot_link = get_link_robot(url);
        robot = Robots.fetch(robot_link);
        if (resp.status == 200 and resp.raw_response != None):
            soup = BeautifulSoup(resp.raw_response.content,"html.parser")
            extract_tokens(url,soup)
            for link in soup.find_all('a'):
                if link.get('href') != None and robot.allowed(link.get('href'),'IR S20 33805012,43145172,61658242'):
                    frontier_list.append(link.get('href'));

    return frontier_list

def extract_tokens(url,soup):    
    global freq
    global stop_words
    global largest_url
    global html_junk
    global site_dict
    global sub_list
    
    raw = soup.get_text()
    all_tokens = word_tokenize(raw)
    size = 0

    for t in all_tokens:
        t = t.lower()
        if re.match('^[a-zA-Z]+[a-z0-9]+$',t) and t not in stop_words and t not in html_junk:
            size += 1
            if t in freq:
                freq[t] += 1
            else:
                freq[t] = 1

    if size > largest_url[1]:
        open('largest_info.txt','w').close()
        largest_file = open('largest_info.txt','w')
        largest_file.write('{} {}\n'.format(url,size))
        largest_file.close()
        largest_url = (url,size)

    descending = sorted(freq.items(), key=lambda x:x[1],reverse=True)
    open('tokens.txt','w').close() # clears previous dict
    token_file = open('tokens.txt','w')

    counter = 1
    sites_num = 0
    subd_list = []
    for key in site_dict.keys():
        sites_num += site_dict[key]

    if len(sub_list) > 0:
        for keys in sub_list:
            subd_list.append((keys,site_dict[keys]))
            
    token_file.write("sites crawled: " + str(sites_num)+ "\n")
    token_file.write("sub domains: " + str(sorted(subd_list))+ "\n")
    for t,c in descending: # writes token freq in txt file
        token_file.write("{}. {} {}\n".format(counter,t,c))
        counter += 1
    token_file.close()
    
# Returns the link of the Robots.txt as a string
def get_link_robot(url):
    parsed = urlparse(url)
    return parsed.scheme +'://' + parsed.netloc + "/robots.txt";



# Checks the text against the master
# Returns true if too similar
def too_similar(text1: str) -> bool:
    data1 = re.split(r'\W+', text1)

    # Create the MinHash using the text
    mh = MinHash(num_perm=5000)
    for word in data1:
        mh.update(word.encode('utf8'))

    # Check the text for similarity. Result is a list of similar texts
    result = lsh.query(mh)

    # Return true if result is not empty i.e. If there are similarities with past texts
    return not result == []



#Checks if valid uci link and not a trap
def check_if_valid(url):
    global site_dict
    global sub_list
    parsed = urlparse(url)

    is_uci = False
    is_trap = True
    is_sub = False
    
    urlRegex = re.compile('((ics.uci.edu)|(cs.uci.edu)|(informatics.uci.edu)|(stat.uci.edu)|(today.uci.edu/department/information_computer_sciences))')
    if(urlRegex.search(parsed.netloc) != None):
        is_uci = True

    SubRegex = re.compile('\b(?!uci|edu|informatics|cs|stat|today|www)\b\w+.')
    if(SubRegex.search(parsed.netloc) != None):
        is_sub = True
        sub_list.append(parsed.netloc)
        
    pathRegex = re.compile('(calendar|page|\d{4}/\d{2}|#\w+)')
    if(pathRegex.search(parsed.path) == None and parsed.query == ''):
        is_trap = False
        
    valid = (is_uci and is_trap == False)
    #########################################################################################################
    # i think its better to have a tuple (int (frequency),list of paths(/jhsjdfhjh/akdjhfkjla), subdomain (true or false) ))# site_dict[parsed.netloc] = (1,[parsed.path], false)
    if valid == True:
        try:
            site_dict[parsed.netloc] = 1
        except:
            site_dict[parsed.netloc] +=1
    #################################################################################################################

    return valid
        
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
