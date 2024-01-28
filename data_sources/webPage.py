from email.mime import base
import requests
import re
from instances.node import *
from typing import Set, List, Optional
from bs4 import BeautifulSoup

PAGE_LOAD_TIMEOUT = 2

click_operation = Operation('click', 'clicks on the link')

class WebPageLink(OperationNode):
    """An implementation of a webpage node representing a link on a webpage."""
    def __init__(self, absolute_url : str, visited_urls : Set[str], tree_depth : int, textual_name : str, optional_content : Optional[NodeContent] = None):
        super().__init__(click_operation, tree_depth, textual_name, optional_content, absolute_url)
        self.absolute_url = absolute_url
        self.captured_urls = visited_urls.copy()

    def expand(self, mode : int) -> List['Node']:
        """Expands the node by downloadning the page, 
        filtering out all links and creating children nodes for each link, 
        without expanding them."""
        try:
            page_content = requests.get(self.absolute_url, timeout=PAGE_LOAD_TIMEOUT).text ## get the content of the page
            a_tags = BeautifulSoup(page_content, 'html.parser').find_all('a') ## get all links from the page
            
            temp_links = {} ## temporary dictionary to store the links and their textual representation
            for link in a_tags:
                if (
                    'href' in link.attrs 
                    and link.text.strip() != ''
                    and not self.__link_blacklisted(link.attrs['href'], base_url=None)
                    ):
                    url = self.__get_absolute_url(link.attrs['href'], self.absolute_url)
                    if (url not in self.captured_urls):
                        temp_links[url] = re.sub('[\n\s]+',' ',link.text.strip())
                        self.captured_urls.add(url)

            for link in temp_links.keys(): ## create children nodes, now with "self.captured_urls" having all the urls that are reachable from the current node
                self.children.append(WebPageLink(link, self.captured_urls, self.tree_depth + 1, temp_links[link]))
            return self.children
        
        except Exception as e:
            print(f"Error while expanding node {self.textual_name}: {e}")
            return []
        
    def get_final_str_desc(self):
        return f"{self.textual_name} : {self.alternative_id}"
    
    def __get_absolute_url(self, input : str, current_url : str | None) -> str:
        """Tries to merge the relative input url with the current url prefix to get the absolute url. 
        If no current url is provided, the input is returned."""
        if (current_url is None):
            return input
        
        if ('?' in current_url):
            current_url = current_url.split('?')[0]

        if ('#' in input):
            input = input.split('#')[0]

        if (input.startswith('/')):
            return current_url + input.strip('/')
        elif (input.startswith('./')):
            return current_url + input.strip('./')
        else:
            return input
    
    def __link_blacklisted(self, url : str, base_url : str | None) -> bool:
        """Checks if the url is blacklisted. Blacklist is very basic."""
        if (
            url == "/" 
            or url.startswith('#') 
            or url.startswith('mailto:') 
            or url.startswith('javascript:')
            or (base_url is not None and not url.startswith(base_url))
            ):
            return True
        else:
            return False