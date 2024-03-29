import requests
import re
from instances.node import *
from typing import Set, List, Optional
from bs4 import BeautifulSoup
from consts import *
from copy import deepcopy
from instances.node import open_link_operation
from nltk.stem.snowball import SnowballStemmer

PAGE_LOAD_TIMEOUT = 2
MAX_DEPTH = 10

class WebPageLink(OperationNode):
    """An implementation of a webpage node representing a link on a webpage."""
    def __init__(self, 
                 absolute_url : str, 
                 visited_urls : Set[str], 
                 tree_depth : int, 
                 textual_name : str):
        super().__init__(
            operation=open_link_operation, 
            tree_depth=tree_depth, 
            textual_name=textual_name,
            alternative_id=absolute_url
            )
        self.absolute_url = absolute_url
        self.captured_urls = visited_urls.copy()
        self.expanded = False

    def expand(self, mode : int, params : {str, }, cache : {str, Node} = {}) -> List['Node']:
        """Expands the node by downloadning the page, 
        filtering out all links and creating children nodes for each link, 
        without expanding them."""

        remaining_depth = params['look_ahead_depth'] if mode == WORKER_MODE.LOOK_AHEAD else 1
        isolated_domain = params['isolated_domain'] if 'isolated_domain' in params else False
        
        if (mode == WORKER_MODE.KEYWORD_GEN_AND_MATCH):
            remaining_depth = MAX_DEPTH - self.tree_depth

        if (mode == WORKER_MODE.KEYWORD_GEN_AND_MATCH and self.tree_depth > MAX_DEPTH): ## recursion limit when generating tree based on keywords
            return []
        
        if (not self.expanded):
            try:
                page_content = requests.get(self.absolute_url, timeout=PAGE_LOAD_TIMEOUT).text ## get the content of the page
                a_tags = BeautifulSoup(page_content, 'html.parser').find_all('a') ## get all links from the page

                temp_links = {} ## temporary dictionary to store the links and their textual representation
                for link in a_tags:
                    if (
                        'href' in link.attrs 
                        and link.text.strip() != ''
                        and not self.__link_blacklisted(link.attrs['href'], base_url=self.absolute_url if isolated_domain else None)
                        ):
                        url = self.__get_absolute_url(link.attrs['href'], self.absolute_url)
                        if (url not in self.captured_urls):
                            temp_links[url] = re.sub('[\\n\\s]+',' ',link.text.strip())
                            self.captured_urls.add(url)

                if (mode == WORKER_MODE.KEYWORD_GEN_AND_MATCH): ## filtering when generating tree based on keywords
                    stemmer = SnowballStemmer("english", ignore_stopwords=True)
                    temp_links = {k: v for k, v in temp_links.items() if any(stemmer.stem(word.strip().casefold()) in params['keywords'] for word in v.split())} ## keywords are stripped and casefolded already
                
                if (mode == WORKER_MODE.MATCH_AND_FILTER): ## filtering when matching and filtering
                    stemmer = SnowballStemmer("english", ignore_stopwords=True)
                    keywords = [stemmer.stem(x.strip().casefold()) for x in params['query'].split()]
                    temp_links = {k: v for k, v in temp_links.items() if any(stemmer.stem(word.strip().casefold()) in keywords for word in v.split())}

                for link in temp_links.keys(): ## create children nodes, now with "self.captured_urls" having all the urls that are reachable from the current node
                    if (link in cache):
                        print(f"Found {link} in cache")
                        nodePage = deepcopy(cache[link])
                        nodePage.textual_name = temp_links[link]
                        nodePage.tree_depth = self.tree_depth + 1
                        self.children.append(nodePage)
                    else:
                        self.children.append(WebPageLink(link, self.captured_urls, self.tree_depth + 1, temp_links[link]))

                if (self.absolute_url not in cache): ## add current expanded node to the cache if not present already
                    cache[self.absolute_url] = self
                    
            except Exception as e:
                print(f"Error while expanding node {self.textual_name}: {e}")
                return []
        
        if (remaining_depth > 1): ## if remaining depth is 1, we are currently on the last page
            for child in self.children:
                new_params = deepcopy(params)
                new_params['look_ahead_depth'] = remaining_depth - 1
                child.expand(mode, new_params, cache)

        return self.children
                
    def get_final_str_desc(self):
        return f"{self.textual_name} : {self.alternative_id}"
    
    def __get_absolute_url(self, input : str, current_url : str | None) -> str:
        """Tries to merge the relative input url with the current url prefix to get the absolute url. 
        If no current url is provided, the input is returned."""

        result = ""
        
        if (current_url is None):
            return input
        
        if ('?' in current_url): ## remove the query string from the url
            current_url = current_url.split('?')[0]

        if ('#' in input): ## remove any anchors from the url
            input = input.split('#')[0]

        if (input.startswith('/')):  ## try to cut as much from the current url as possible
            current_split = [x for x in current_url.split('/') if x != '']
            input_split = [x for x in input.split('/') if x != '']
            
            for i in range(len(current_split)):
                if (len(input_split) == 0):
                    return current_url
                if (current_split[i] == input_split[0]):
                    input_split.pop(0)

            input = '/'.join(input_split)

            if (current_url.endswith('/')):
                result = current_url + input
            else:
                result = current_url + '/' + input
            
        elif (input.startswith('./')): ## just append the relative to the current
            result = current_url + input.strip('./')
        
        else: ## otherwise legit URL given
            result = input
        
        if (not result.endswith('/') ## always add the trailing slash if not present
            and not "." in result.split('/')[-1]): ## only except if file is given
            result += '/'

        return result
    
    def __link_blacklisted(self, url : str, base_url : str | None) -> bool:
        """Checks if the url is blacklisted. Blacklist is very basic."""
        ## keep relatives
        if (
            url.startswith('./')
            or (url != "/" and url.startswith('/'))
        ):
            return False
        
        ## filter out some basic stuff
        if (
            url == "/" 
            or url.startswith('#') 
            or url.startswith('mailto:') 
            or url.startswith('javascript:')
            or url.startswith('tel:')
            or (base_url is not None and not url.startswith(base_url))
            ):
            return True
        
        ## passed
        return False