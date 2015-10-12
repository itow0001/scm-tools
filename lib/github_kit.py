'''
Created on Oct 8, 2015

@author: iitow
'''
import sys
sys.path.append('../utils')
from rest_kit import Restful
from argparse import ArgumentParser
import json

class Github(object):
    def __init__(self, base_url,auth_file,verbose=False):
        self.token    = self._get_auth(auth_file).get("token")
        self.base_url = base_url
        self.base_api = "https://%s:x-oauth-basic@%s/api/v3" % (self.token,base_url)
        self.rest     = Restful(self.base_api)
        #self.roots    = self.url_roots(verbose)
#### Private Definitions ####
    def _get_auth(self,auth_file):
        try:
            with open(auth_file, 'r') as file:
                auth = json.load(file)
            self.token = auth.get('token')   
        except Exception as e:
            print "[Error] auth_file at path <%s>" % (auth_file)
            print e
            sys.exit(1)
        return auth
    def _pprint(self,data):
        if type(data) is list:
            for d in data:
                self._pprint(d)
        else:
            for key,value in data.iteritems():
                if type(value) is dict:
                    print key
                    self._pprint(value)
                else:
                    print '{:>40} : {:<50}'.format(key,str(value))
    def _prep_urls(self,_urls_dict):
        url_exts = {}
        for key,url in _urls_dict.iteritems():
            url = str(url)
            if self.base_url in url:
                url = url.split(self.base_url,1)[1].replace("/api/v3/","")
            url_exts[key]=url
        return url_exts
    def _find_replace(self,str,vars,url_dict):
        for key,token in vars.iteritems():
            if key in str:
                str = str.replace(key,token).replace('}','')
                url_dict.append(str)
        return url_dict
    def _add_vars(self,url,vars):
        print vars
        new_url = []
        if url:
            url = url.split("{")
            print url
            for value in url:
                if '}' in value:
                    self._find_replace(value, vars, new_url)
                else:
                    new_url.append(value)
            return ''.join(new_url)
        return ''
#### Public Definitions ####  
    def get(self,ext_url,verbose=False):
        print "[ext_url] "+ext_url
        output = json.loads( self.rest.send("GET",ext_url,verbose=False))
        if verbose:
            self._pprint(output)
        return output
    

    
    
    
    
    
    
    
