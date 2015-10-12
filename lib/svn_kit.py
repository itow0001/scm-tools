'''
Created on Oct 7, 2015

@author: iitow
'''
import pysvn, logging,sys, inspect, os
sys.path.append('../../utils')
from terminal import shell
class Client(object):
    """Represents a generic svn client
    """
    def __init__(self,username,password,workspace,base_url,verbose=True):
        """ This class is a handles all client svn calls
        @param username: user to login to svn
        @param password: password to be used
        @param workspace: local directory to perform the work
        @param base_url: base svn url example. https://svn.west.isilon.com   
        """
        self.username = username
        self.password = password
        self.workspace= workspace
        self.base_url = base_url
        self.verbose  = verbose
        self.log      = self._logable(self.workspace,verbose=verbose)
        self.client   = self._setup_client()
        self.LOG_MESSAGE= ''
    
    #### private definitions ####
    def _logable(self,workspace,verbose=True):
        """ setup logging
        """
        log_name = "svn"
        filename = "%s/%s.log" % (workspace,log_name)
        if not os.path.exists(filename):
            with open(filename, "w+") as f:
                pass
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('\n\n[%(asctime)s]\n<%(levelname)s>\n%(message)s')
        if verbose:
            sh = logging.StreamHandler(sys.stdout)
            sh.setLevel(logging.DEBUG)
            sh.setFormatter(formatter)
            logger.addHandler(sh)
        fh = logging.FileHandler(filename, mode='a', encoding=None, delay=False)
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        return logger
    
    def _setup_client(self):
        """Setup the client authentication
        """
        client = pysvn.Client()
        def _login(*args):
            return True, self.username, self.password, False
        def _ssl_server_trust_prompt():
            return False, 1, True
        client.callback_get_login = _login
        client.callback_ssl_server_trust_prompt = _ssl_server_trust_prompt
        return client
    
    def _set_message(self,msg):
        """Set the message of a commit
        """
        def _message():
            return True, msg
        self.client.callback_get_log_message = _message

    #### public definitions ####  
    def copy(self,origin_ext,new_ext,revision,message):
        """Create a branch from existing branch
        @param origin_ext: branch url extention example. repo/onefs/branches/BR_7_2_0
        @param new_ext:  branch url extention example. repo/onefs/branches/BR_FOO_BAR
        @param revision: revisions number as string
        @param message: message you wish to include in branch copy
        @return: boolean
        """
        origin_url = "%s/%s/" % (self.base_url,origin_ext)
        new_url    = "%s/%s" % (self.base_url,new_ext)
        if self.verbose:
            self.log.info("(%s)\n%s\n%s" % (inspect.stack()[0][3],origin_url,new_url))
        self._set_message(message)
        try:
            self.client.copy(origin_url, new_url, 
                        src_revision=pysvn.Revision(pysvn.opt_revision_kind.number, int(revision)))
            return True
        except Exception as e:
            self.log.error(e)
        return False
            
    def checkout(self,src_ext):
        """Checkout branch to local
        @param src_ext: extention of url path you wish to include
        @return: boolean
        """
        src_url = "%s/%s" % (self.base_url,src_ext)
        workspace = "%s/%s" % (self.workspace,src_url.rsplit('/',1)[1])
        
        if self.verbose:
            self.log.info("(%s)\n%s\n%s" % (inspect.stack()[0][3],src_url,workspace))
        try:
            self.client.checkout(src_url,workspace)
            return True
        except Exception as e:
            self.log.error(e)
        return False
    
    def checkin(self,local_path,message):
        """Checkin local to remote
        @param local_path: local repo path
        @param message: This is the message you wish to include with checkin
        @return: boolean
        """
        if self.verbose:
            self.log.info("(%s)\n%s\n%s" % (inspect.stack()[0][3],local_path,message))
        try:
            new_rev = self.client.checkin(local_path,log_message=message)
            new_rev = new_rev.number
            return True
        except Exception as e:
            self.log.error(e)
        return False
    
    def merge(self,src_ext,local_path,revision):
        """Merges a single revision
        @param src_ext: branch extention you wish to merge from
        @param local_path: your local repo
        @param revision: revision of src extention you wish to merge from
        @return: boolean 
        """
        src_url = "%s/%s" % (self.base_url,src_ext)
        if self.verbose:
            self.log.info("(%s)\n%s\n%s" % (inspect.stack()[0][3],src_url,local_path))
        try:
            self.client.merge_peg(src_url,
                      pysvn.Revision(pysvn.opt_revision_kind.number,int(revision) - 1),
                      pysvn.Revision(pysvn.opt_revision_kind.number,int(revision)),
                      pysvn.Revision(pysvn.opt_revision_kind.head),local_path, notice_ancestry=True)
            if self.has_conflict(local_path):
                return True
        except Exception as e:
            self.log.error(e)
        return False
    
    def has_conflict(self,local_path):
        """ Does the local repo have a checkin conflict?
        @param local_path: local repo path
        @return: boolean
        """
        if self.verbose:
            self.log.info("(%s)\n%s" % (inspect.stack()[0][3],local_path))
        try:
            info = self.client.info2(local_path, recurse=False)
            if not info[0][1]['wc_info']['conflict_work']:
                self.log.error("conflict found in %s" % (local_path))
                return False
        except Exception as e:
            self.log.error(e)
        return True
    
    def is_path(self,local_path):
        """ Is this local path a repo?
        @param local_path: Path to repository 
        @return: boolean
        """
        try:
            info = self.client.info2(local_path, recurse=False)
            return True
        except Exception as e:
            return False
            
    def revision_diff(self,src_ext,revision):
        """ Provides a diff from a revision of previous
        @param src_ext: general the base of a repo
        @param revision: revision number as string
        @return: String
        """
        repo_base = "%s/%s" % (self.base_url,src_ext)
        if self.verbose:
            self.log.info("(%s)\n%s" % (inspect.stack()[0][3],revision))
        try:
            revision_diff = self.client.diff(self.workspace, repo_base,
                revision1=pysvn.Revision(pysvn.opt_revision_kind.number,int(revision) -1),
                revision2=pysvn.Revision(pysvn.opt_revision_kind.number,int(revision)))
            return revision_diff
        except Exception as e:
            self.log.error(e)
        return ""
    
    def revision_log(self,src_ext,revision):
        """ provides the log of a local repo 
        @param src_ext: generally the base of the repo example. repo/onefs
        @param revision: revision number as string
        @return: String 
        """
        repo_base = "%s/%s" % (self.base_url,src_ext)
        if self.verbose:
            self.log.info("(%s)\n%s\n%s" % (inspect.stack()[0][3],repo_base,revision))
        try:
            log = self.client.log(repo_base,
                      revision_start=pysvn.Revision(pysvn.opt_revision_kind.number,int(revision)),
                      revision_end=pysvn.Revision(pysvn.opt_revision_kind.number,int(revision)))
            if len(log) >=1:
                return log[0]['message']
        except Exception as e:
            self.log.error(e)
        return ""
    
    def delete_local(self,local_path):
        """ Deletes a local svn repo 
        @param local_path: path to the repository 
        @return: boolean
        """
        if self.is_path(local_path):
            shell("rm -rf %s" % local_path,verbose=False)
            return True
        else:
            self.log.error("Not an svn repo %s" % (local_path))
            return False
