import Queue
import threading
import os
import urllib2

threads = 10

# 1) We begine by defining the remote target website and the local directory into 
# which we have downloaded and extracted the web application. 
# We also create a simple list of file extensions that we are not insterested in 
# fingerprinting. This list can be different depending on the target application. 
target = "http://www.blackhatpython.com"
directory = "/root/Downloads/joomla-3.1.1"
filters = [".jpg",".gif",".png",".css"]

os.chdir(directory)

# 2) The web_paths variable is our Queue object where we will store the files 
# that we'll attempt to locate on the remote server. 
web_paths = Queue.Queue()

# 3) We then use the os.walk function to walk through all of the files and directories 
# in the local web application directory. As we walk through the files and directories,
# we're building the full path to the target files and testing them against our filter list
# to make sure we are only looking for the file types we want. For each valid files we find
# locally, we add it to our web_paths Queue. 
for r,d,f in os.walk("."):
    for files in f:
        remote_path = "%s/%s" % (r, files)
        if remote_path.startswith("."):
            remote_path = remote_path[1:]
        if os.path.splitext(files)[1] not in filters:
            web_paths.put(remote_path)
        
            
def test_remote():
    while not web_paths.empty():  #4) 
        path = web_paths.get()
        url = "%s%s" % (target, path)
        
        request = urllib2.Request(url)
        try:
            response = urllib2.urlopen(request)
            content = response.read()
            
            print "[%d] => %s" % (response.code, path)  #5)
            response.close()
            
        except urllib2.HTTPError as error:  #6)
            print "Failed %s" % error.code
            pass

# 7) We are creating a number of threads (as set at the top of the file)
# that will each be called the test_remote function operates in a loop
# that will keep executing until the web_paths Queue is empty. 
# On each iteration of the loop, we grab a path from the Queue 4),
# add it to the target website's base path, and then attemp to retrieve it. 
# If we're successful in retrieving the file, we output the HTTP status code
# and the full path to the file 5). 
# If the file  is not found or is protected by an .htaccess file, this will cause
# urllib2 to throw an error, which we handle 6) so the loop can continue executing. 
for i in range(threads):
        print "Spawning thread: %d" % i
        t = threading.Thread(target=test_remote)
        t.start()
        
        