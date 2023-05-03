#!python3

# Based on - https://www.mediawiki.org/wiki/API:REST_API/Reference
import re
import sys
import requests
import readline #import readline for "input()" to handle arrow keys

class Wikipedia:
    def __init__(self):
        self.NAME = "WIKIPEDIA"
        self.API_URL = "https://en.wikipedia.org/w/rest.php/v1"
        self.cleanregexp = re.compile('<.*?>')
        self.searchmode = self.searchtitle
        #self.searchmode = self.searchpage

    def cleanhtml(self,raw_html):
        return re.sub(self.cleanregexp, '', raw_html)

    def callapi(self,endpoint, params={}):
        url = f"{self.API_URL}/{endpoint}"
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            raise(f"Error {response.status_code}")

    # https://www.mediawiki.org/wiki/API:REST_API/Reference#Page_object
    def getpageurl(self,key):
        responsejson = self.callapi(f"page/{key}/bare")
        if responsejson is not None:
            return responsejson["html_url"]
        
    # https://www.mediawiki.org/wiki/API:REST_API/Reference#Search_pages
    # Searches wiki page titles and contents for the provided search terms, and returns matching pages. 
    def searchpage(self, query, limit=3):
        responsejson = self.callapi(f"search/page", {'q': query, 'limit': limit})
        if responsejson is not None:
            pages = responsejson["pages"]
            outtxt=""
            for page in pages:
                key = page['key']
                outtxt = outtxt + '\n' + f"{page['title']}: {page['description']} "
                outtxt = outtxt + '\n' + f"{self.cleanhtml(page['excerpt'])} " 
                outtxt = outtxt + '\n' + self.getpageurl(key)
                outtxt = outtxt + '\n' + '--'
            return outtxt

    # https://www.mediawiki.org/wiki/API:REST_API/Reference#Autocomplete_page_title
    # Searches wiki page titles matching the beginning of a title and the provided search terms.
    def searchtitle(self, query, limit=3):
        responsejson = self.callapi(f"search/title", {'q': query, 'limit': limit})
        if responsejson is not None:
            pages = responsejson["pages"]
            outtxt=""
            for page in pages:
                outtxt = outtxt + '\n' + (f"{page['title']}: {page['description']} - {self.getpageurl(page['key'])}")
            return outtxt

    def getresponse(self, query):
        return self.searchmode(query)

    def cliloop(self, prompt):
        answer=""
        if prompt != "":
            answer = self.getresponse(prompt)
        while True:
            print(answer)
            user_input = input(f"{self.NAME}> ").strip()
            if user_input in ["quit", "exit", "bye", "engine"]:
                break
            else:
                prompt = user_input.strip()
            if len(prompt)>0:
                answer = self.getresponse(prompt)
        return answer

if __name__ == "__main__":
    args = sys.argv[1:]
    engine = Wikipedia()
    prompt=""
    if len(args) > 0:
        prompt = args[0]
    engine.cliloop(prompt)