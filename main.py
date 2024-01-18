import json
import requests
import sys
# from flask import Flask, render_template, request
# from flask_cors import CORS, cross_origin
from bs4 import BeautifulSoup
import traceback
from urllib.parse import urljoin, urlparse
import logging
from datetime import datetime, timedelta
# app = Flask(__name__)
# CORS(app)
# # Configure logging settings
# app.logger.setLevel(logging.DEBUG)

# Create a file handler to write logs to a file
# file_handler = logging.FileHandler('app.log')
# file_handler.setLevel(logging.DEBUG)

# # Define the log format
# log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# file_handler.setFormatter(log_format)
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Add the file handler to the logger
# app.logger.addHandler(file_handler)

class TreeNode:
    def __init__(self, url):
        self.url = url
        self.status = None
        self.children = []
class ScraperCode:
    def __init__(self):

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.5',
            # Add more headers if needed
        }
        self.visited = set()
        self.i=0
        self.appLog=logging

    def get_all_links(self,url):
        try:
            self.appLog.info("Getting All Link Lists")
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        except requests.RequestException as e:
            self.appLog.error("No Link found: %s, Error is : %s",str(e), traceback.format_exc())
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        links = [a.get('href') for a in soup.find_all('a', href=True)]
        return links

    def is_absolute(self,url):
        return bool(urlparse(url).netloc)

    def get_absolute_url(self,base_url, relative_url):
        return urljoin(base_url, relative_url)

    def findSibling(self,node, test_url,status):
        for child in node:
            # if 'carson-coffman.jpg' in child.url:
            #     self.appLog.info('with image')
            #     self.appLog.info('child URL->'+child.url)
            #     self.appLog.info('test_url->'+test_url+" "+child.url==test_url)
            #     self.appLog.info('with image')
            # else:
            #     self.appLog.info('child URL->'+child.url)
            #     self.appLog.info('test_url->'+test_url+child.url==test_url)
            # if not status:
            #     print('child URL',child.url)
            #     print('test_url',test_url,child.url==test_url)
            if child.url==test_url:
                # print("False")
                return False
        return True
    def checkValidLink(self, parent_url, child):
        if parent_url==child[:child.find("#")]:
            return False
        return True
    def check_links_recursive(self,url, node):
        
        if url in self.visited:
            return
        self.visited.add(url)
        self.appLog.info("visiting: %s",url)
        if "https://www.socket.net" != url[:22]:
            return

        links = self.get_all_links(url)
        for link in links:
            if not self.is_absolute(link):
                absolute_url = self.get_absolute_url(url, link)
            else:
                absolute_url = link
            if "https://www.socket.net" != absolute_url[:22]:
                continue
            if absolute_url not in self.visited:
                # self.visited.add(absolute_url)
                try:
                    with requests.Session() as session:
                        response = session.head(absolute_url, allow_redirects=True, timeout=10)
                        response.raise_for_status() 

                        absolute_url = response.url

                        self.i+=1
                        if absolute_url not in self.visited:
                            if response.status_code == 200 and "https://www.socket.net" == absolute_url[:22] and self.findSibling(node.children,absolute_url,True):
                                # self.appLog.info("parent->"+node.url)
                                child_node = TreeNode(absolute_url)
                                node.children.append(child_node)
                                child_node.status = True
                                # print(final_destination)
                                print("scrapping...")
                                
                                # if self.i<2000 and 
                                if self.checkValidLink(node.url,absolute_url):
                                    self.check_links_recursive(absolute_url, child_node)


                except requests.RequestException as e:
                    if absolute_url not in self.visited and self.findSibling(node.children,absolute_url,False):
                        # self.appLog.info("parent->"+node.url+" False")
                        child_node = TreeNode(absolute_url)
                        node.children.append(child_node)
                        child_node.status = False
                        # if absolute_url[-4:]=='.jpg':
                        #     print(absolute_url)
                        self.i+=1
                    self.appLog.error("No Link found: %s, Error is : %s",str(e), traceback.format_exc())
                else:
                    continue
def traverse(node):
    if node.children==[]:
        return
    for n in node.children:
        if not n.status:
            print(n.url)
        traverse(n)
global errorPath
errorPath=""
    
def print_paths_with_false_status(node, current_path=[]):
    current_path.append(node.url)

    if node.status is False:
        global errorPath
        errorPath+="@Status is False at path: "+"-> ".join(current_path)
        logging.error("Error Link: %s",node.url)

    for child in node.children:
        print_paths_with_false_status(child, current_path.copy())
# @app.route("/", methods=["POST"])
def startScraper():
# Example usage:
    starting_url = 'https://www.socket.net'
    # visited.add(starting_url)
    logging.info("starting Scraper")
    root_node = TreeNode(starting_url)
    root_node.status = True
    obj=ScraperCode()
    obj.check_links_recursive(starting_url, root_node)
    return root_node

class TreeNodeJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, TreeNode):
            return {
                "value": o.url,
                "status":o.status,
                "children": [self.default(child) for child in o.children]
            }
        return super().default(o)



# Function to print the tree structure
# def print_tree(node, indent=0):
#     print("  " * indent + f"{node.url} - {'Broken' if node.status is False else 'OK'}")
#     for child in node.children:
#         print_tree(child, indent + 1)

# print_tree(root_node)

if __name__ == '__main__':
    # app.run(debug=True)
    
    sys.setrecursionlimit(3500)
    print("starting scraping...")
    root=startScraper()
    print("\nScrapping Completed...")
    # traverse(root)
    print_paths_with_false_status(root)
    # json_data = json.dumps(root, cls=TreeNodeJSONEncoder)
    # f=open("tree.json","w")
    # f.write(json_data)
    # f.close()
    print("tree file saved successfully")
    f=open("error.json","w")
    json_data = json.dumps(errorPath.split("@"))

    f.write(json_data)
    f.close()
    # app.run()
# else:
#     application = app