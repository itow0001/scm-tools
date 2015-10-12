import subprocess
import os
import io
import sys
import time
import logging
import time
import atexit
import shlex
this_path = os.path.dirname(os.path.realpath(__file__))             # define global path for this file

def rsync(server,src,dest,option='pull',remote=True,excludes=[]):
    """ Performs an rsync of files; requires ssh keys setup.
    @param   server: username@server 
    @param      src: full path of src directory/file
    @param     dest: full path to dest directory
    @param   option: [pull] get file from a remote, [push] put a file from your server into a remote 
    @param   remote: [True] assumes we are working with a remote system, [False] assumes we are copying files locally 
    @param excludes: exclude directory, or file from array
    @note: --delete will delete files on dest if it does not match src
    """
    excludes_str = ""
    if excludes:
        for exclude in excludes:
            excludes_str = "%s --exclude=%s" % (excludes_str,exclude)
    if remote==True:
        if option=='pull':
            try:
                shell("sudo rsync -e \"ssh -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null -i /jenkins/.ssh/id_rsa \""
                      " -Pavz %s --delete %s:%s %s" % (excludes_str,server,src,dest),strict=True)
            except IOError as e:
                print "Error in rsync: %s" % (e)
        elif option=='push':
            try:
                shell("sudo rsync -e \"ssh -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null -i /jenkins/.ssh/id_rsa \""
                      " -Pavz %s --delete %s %s:%s" % (excludes_str,src,server,dest),strict=True)
            except IOError as e:
                print "Error in rsync: %s" % (e)
    elif remote==False:
        try:
            shell("sudo rsync -Pavz %s --delete %s %s" % (excludes_str,src,dest),strict=True)
        except IOError as e:
            print "Error in rsync: %s" % (e)
    else:
        print "Invalid option: %s" (option)

def ssh(server,cmd,key_path='/ifs/home/iitow/.ssh/id_rsa'):
    """ Run a single ssh command on a remote server
    @param server: username@servername
    @param cmd: single command you wish to run
    """
    try:
        output = shell("ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i %s %s \"%s\"" 
                       % (key_path,server,cmd),strict=True)
    except IOError as e:
        print "Error in ssh: %s" % (e)
    return output

def shell(cmd,verbose=True, strict=False,shell=False):
    """Run Shell commands  [Non Blocking, no Buffer, print live, log it] 
    @param cmd: String command
    @param verbose:bool
    @param strict:bool will exit based on code if enabled  
    @return:  {command, stdout, code} as dict
    """
    path      = os.path.dirname(os.path.realpath(__file__))
    stamp     = str(int(time.time()))
    temp_path = path+os.sep+".tmp_shell_"+stamp+".log"
    output    = ""
    #if verbose:
    print "\n[%s]\n" % (cmd)
    if shell==False:
        cmd = shlex.split(cmd)
    with io.open(temp_path, 'wb') as writer, io.open(temp_path, 'rb', 1) as reader:
        process = subprocess.Popen(cmd, stdout=writer,stderr=writer,shell=shell)# pass writer to process
        while process.poll() is None:                               # poll till done
            out = reader.read()
            output = output+out                                     # collect output in temp variable
            if verbose:
                sys.stdout.write(out)                               # write it to screen
            time.sleep(0.5)
        out = reader.read()
        output = output+out
        if verbose:
            sys.stdout.write(out)                                   # write out remaining info
    cmd_info = {'cmd':" ".join(cmd),'stdout':output,'code':process.returncode}
    #log_formatted = "COMMAND:[%s]\n%s[code:%s]" % (cmd_info.get("cmd"),output,cmd_info.get("code"))
    #logging.info(log_formatted)                                     # write temp output to log
    if os.path.isfile(temp_path):
        os.remove(temp_path)                                        # clean .tmp_shell files
    if strict==True and int(cmd_info.get("code")) > 0:              # exit if error is fatal & strict enabled
        print "\n [Fatal Error] %s \n" % (cmd_info.get("stdout"))
        os.sys.exit(int(cmd_info.get("code")))
    return cmd_info
def _exit_clean():
    """ cleans .tmp_shell files before exit
    """
    for file in os.listdir(this_path):
        if ".tmp_shell_" in file:
            file_remove = this_path+os.sep+file
            os.remove(file_remove)
atexit.register(_exit_clean)
