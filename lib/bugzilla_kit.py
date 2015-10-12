import sys
import json
import xmlrpclib
import socket
import errno
class XMLRPCErr(Exception):
    """setup the error message for viewing"""
    def __init__(self, msg, rc):
        self.msg = msg
        self.rc = rc
    def __str__(self):
        return self.msg

class Bug(object):
    def __init__(self,username,password,base_url):
        """ A representation of a bugzilla bug capable of communicated via xmlrpc with bugzilla
        @param username: bugzilla login 
        @param password: bugzilla credentials
        @param base_url: base url from which to initiate communication example. https://bugs.west.isilon.com  
        """
        self.username = username
        self.password = password 
        self.base_api = "%s/xmlrpc.cgi" % base_url
        self.server = xmlrpclib.ServerProxy(self.base_api)
        self.sock = socket
        self.sock.setdefaulttimeout(30)
    def create(self,product,component,summary,version,desc):
        """ Let create a new bugzilla bug
        @param product: name of the product category
        @param component: sub component contained in the component field
        @param summary: this will be the headline of the bug 
        @param version: may be '---'
        @param desc: General description of the bug
        @return: dictionary containing the id:<bug number>
        @note: Use the web gui to find these values.
        if not version its generally '---'    
        """
        msg = ''
        try:
            msg = self.server.Bug.create({'Bugzilla_login': self.username,
                                            'Bugzilla_password':    self.password,
                                            'product':              product,
                                            'component':            component,
                                            'summary':              summary,
                                            'version':              version,
                                            'description':          desc})
        except Exception as err:
            rc = 100
            raise XMLRPCErr(str(err), rc)
        except Exception as err:
            rc = 101
            errmsg = "socket error: " + str(err)
            if err[0]==errno.ECONNREFUSED:
                errmsg = 'Connection Refused ' + errmsg
            raise XMLRPCErr(errmsg, rc)
        except Exception as err:
            rc = 102
            raise XMLRPCErr('Unknown or network error: ' + str(err), rc)
        finally:
            self.sock.setdefaulttimeout(None)      #sets the default back
        return msg    
    def add_comment(self,bug_id,comment):
        """ This adds a comment to an existing bug
        @param bug_id: the bugzilla bug number
        @param comment: the comment you wish to add to the bug
        @return: Dictionary of associated comment id
        """
        msg = ''
        try:
            msg = self.server.Bug.add_comment({'Bugzilla_login': login,
                'Bugzilla_password':pw , 'id': bug_id, 'comment': comment})
        except Exception as err:
            rc = 100
            raise XMLRPCErr(str(err), rc)
        except Exception as err:
            rc = 101
            errmsg = "socket error: " + str(err)
            if err[0]==errno.ECONNREFUSED:
                errmsg = 'Connection Refused ' + errmsg
            raise XMLRPCErr(errmsg, rc)
        except Exception as err:
            rc = 102
            raise XMLRPCErr('Unknown or network error: ' + str(err), rc)
        finally:
            self.sock.setdefaulttimeout(None)      #sets the default back
        return msg
