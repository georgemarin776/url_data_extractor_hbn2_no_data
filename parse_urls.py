import urllib.parse
from iso_country_codes import CC

class URL:
    def __init__(self, url):
        self.initial_url = url
        self.url = url
        self.domain = None
        self.path = None
        self.query_params = {}
        self.language = None
        self.slash_products_path = None


        self.product_name = None
        self.product_category = None
        self.parse_url()

    def parse_url(self):
        # parse the url and set the domain, path, and query_params
        url_parsed = urllib.parse.urlparse(self.url)
        self.url = urllib.parse.unquote(self.url)
        self.domain = url_parsed.hostname
        self.path = url_parsed.path
        self.query_params = urllib.parse.parse_qs(url_parsed.query, keep_blank_values=True)

        # get substring from path ending with '/products/' if it exists
        if '/products/' in self.url:
            self.slash_products_path = self.url[:self.url.index('/products/') + len('/products/')]

        for value in self.query_params.values():
            if value[0].upper() in CC:
                self.language = CC[value[0].upper()]
                break
        
        # split path by '/' and iterate from end to start
        if self.language == None:
            path_parts = self.path.split('/')
            for part in reversed(path_parts):
                # if len is 2 search in CC
                if len(part) == 2 and part.upper() in CC:
                    self.language = CC[part.upper()]
                    break

        # split domain by '.' and iterate from end to start
        if self.language == None and self.domain != None:
            domain_parts = self.domain.split('.')
            for part in reversed(domain_parts):
                if part.upper() in CC:
                    self.language = CC[part.upper()]
                    break

    def __str__(self):
        return f"Domain: {self.domain}\nPath: {self.path}\nQuery Params: {self.query_params}\nLanguage: {self.language}\n"