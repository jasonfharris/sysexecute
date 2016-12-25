import sys
import os.path
import time
import inspect
import subprocess
import threading
import Queue
from .common import *
import re

__version__ = "1.0.5"


# --------------------------------------------------------------------------------------------------------------------------
# Argument Parsing
# --------------------------------------------------------------------------------------------------------------------------

exectue_defaults = {
    'permitShowingStdOut': True,
    'permitShowingStdErr': True,
    'captureStdOutStdErr': False,
    'ignoreErrors': False,
    'cwd': os.path.abspath('.'),
    'shell': True,
    'executable': '/bin/bash',
    'verbosity': 1,
    'dryrun': False,
    'colorize': True
}

def set_defaults(key, val):
    global exectue_defaults
    exectue_defaults[key] = val



# --------------------------------------------------------------------------------------------------------------------------
# getBindings
# --------------------------------------------------------------------------------------------------------------------------

def getBindings(varList, startLevel=0):
    """Given a list of identifiers as strings, construct the dictonary of the identifiers as keys and the evaluated values of
    the ientifiers as the values. Ie something like {id:full_lookup(id) for id in identifiers}. full_lookup here is looking
    up the value of an identifier by looking at all the bindings at every level in the call stack.
    Return (bindings,unbound) where the bindings is the dictionary of found bindings and the set of unbound identifiers."""
    varsToFind = set(varList)
    bindings = {}
    
    # We start at the level of the caller of getBindings
    frame = inspect.currentframe()
    try:
        for i in xrange(startLevel+1):
            frame = frame.f_back
    except:
        raise Exception("bindings: startLevel {} is too high\n".format(startLevel))
    
    # while we have a current frame look through it for our identifiers
    while frame:
        frameLocals = frame.f_locals
        localKeys = set(varsToFind).intersection(frameLocals)
        for v in localKeys:
            bindings[v]=frameLocals[v]
        varsToFind -= localKeys
        if not varsToFind:
            return (bindings,varsToFind)

        frameGlobals = frame.f_globals
        globalKeys = set(varsToFind).intersection(frameGlobals)
        for v in globalKeys:
            bindings[v]=frameGlobals[v]
        varsToFind -= localKeys
        if not varsToFind:
            return (bindings,varsToFind)

        frame = frame.f_back

    return (bindings,varsToFind)    

_reFormatVar = re.compile("\{(\w*)(:[<>=^]?\d+)?\}")
def getFormatBindings(s, startLevel=0):
    matches = re.findall(_reFormatVar,s)
    identifiers = [match[0] for match in matches]  # we are only interested in the identifier part in the above regex
    (bindings,unbound) = getBindings(identifiers,startLevel+1)
    unbound = list(set(identifiers)- set(bindings))

    if unbound:
        raise Exception("formatBindings: found unbound variables {unbound} for string {s}\n".format(unbound=unbound,s=s))
    return bindings



# --------------------------------------------------------------------------------------------------------------------------
# Command Execution
# --------------------------------------------------------------------------------------------------------------------------

class _AsynchronousFileReader(threading.Thread):
    '''
    Helper class to implement asynchronous reading of a file
    in a separate thread. Pushes read lines on a queue to
    be consumed in another thread.
    '''
    
    def __init__(self, fd, queue):
        assert isinstance(queue, Queue.Queue)
        assert callable(fd.readline)
        threading.Thread.__init__(self)
        self._fd = fd
        self._queue = queue
 
    def run(self):
        '''The body of the tread: read lines and put them on the queue.'''
        for line in iter(self._fd.readline, ''):
            self._queue.put(line)
 
    def eof(self):
        '''Check whether there is no more content to expect.'''
        return not self.is_alive() and self._queue.empty()

def _AsynchronouslyGetProcessOutput(formattedCmd, printStdOut, printStdErr, **kwargs):
    ''' Asynchronously read the process '''
    opts = filterKWArgsForFunc(kwargs, subprocess.Popen)
    opts['stdout'] = subprocess.PIPE
    opts['stderr'] = subprocess.PIPE
    process = subprocess.Popen(formattedCmd, **opts)

    # Launch the asynchronous readers of the process' stdout and stderr.
    stdout_queue = Queue.Queue()
    stdout_reader = _AsynchronousFileReader(process.stdout, stdout_queue)
    stdout_reader.start()
    stderr_queue = Queue.Queue()
    stderr_reader = _AsynchronousFileReader(process.stderr, stderr_queue)
    stderr_reader.start()

    stdOutLines = []
    stdErrLines = []
    # Check the queues if we received some output (until there is nothing more to get).
    while not stdout_reader.eof() or not stderr_reader.eof():
        # Show what we received from standard output.
        while not stdout_queue.empty():
            line = stdout_queue.get()
            stdOutLines.append(line)
            if printStdOut:
                print line.rstrip()
 
        # Show what we received from standard error.
        while not stderr_queue.empty():
            line = stderr_queue.get()
            stdErrLines.append(line)
            if printStdErr:
                print colored(line.rstrip(),'red')
 
        # Sleep a bit before asking the readers again.
        time.sleep(.05)
 
    # Let's be tidy and join the threads we've started.
    stdout_reader.join()
    stderr_reader.join()
 
    # Close subprocess' file descriptors.
    process.stdout.close()
    process.stderr.close()
    process.wait()

    stdOut = ''.join(stdOutLines)
    stdErr = ''.join(stdErrLines)
    return (process.returncode, stdOut, stdErr)


#returns (returncode, stdout, stderr)
def execute(cmd, verbosityThreshold = 1, **kwargs):
    '''execute the passed in command in the shell'''
    global exectue_defaults
    opts = merge(exectue_defaults, kwargs)              # the options computed from the default options together with the passed in options.
    subopts = filterKWArgsForFunc(opts, subprocess.Popen)
    formattedCmd = cmd.format(**getFormatBindings(cmd,1))

    shouldPrint = opts['verbosity'] >= verbosityThreshold
    isDryrun = opts['dryrun']

    if shouldPrint:
        msg = "would execute:" if isDryrun else "executing:"
        pre = "("+subopts['cwd']+")" if (subopts['cwd'] != exectue_defaults['cwd']) else ""
        print "{pre}{msg} {formattedCmd}".format(pre=pre, formattedCmd=formattedCmd, msg=msg)
    if isDryrun:
        return (0, None, None)

    printStdOut = shouldPrint and opts['permitShowingStdOut']
    printStdErr = shouldPrint and opts['permitShowingStdErr']
    returnCode = 0
    if opts['captureStdOutStdErr']:
        (returnCode, stdOut, stdErr) = _AsynchronouslyGetProcessOutput(formattedCmd, printStdOut, printStdErr, **subopts)    
    else:
        subopts['stdout'] = None if printStdOut else subprocess.PIPE
        subopts['stderr'] = None if printStdErr else subprocess.PIPE
        process = subprocess.Popen(formattedCmd, **subopts)
        res = process.communicate()
        returnCode = process.returncode
        stdOut = res[0]
        stdErr = res[1]

    if returnCode and not opts['ignoreErrors']:
        print colored('Command {} failed with return code {}!'.format(cmd, returnCode),'red')
        sys.exit(returnCode)
    
    # always print any errors
    return (returnCode, stdOut, stdErr)


# These different execute levels will print out the information at different verbosity levels
def execute0(_cmd, **kwargs): return execute(_cmd,0,**kwargs)
def execute1(_cmd, **kwargs): return execute(_cmd,1,**kwargs)
def execute2(_cmd, **kwargs): return execute(_cmd,2,**kwargs)
def execute3(_cmd, **kwargs): return execute(_cmd,3,**kwargs)
def execute4(_cmd, **kwargs): return execute(_cmd,4,**kwargs)


# --------------------------------------------------------------------------------------------------------------------------
# stringWithVars
# --------------------------------------------------------------------------------------------------------------------------

def stringWithVars(s):
    return s.format(**getFormatBindings(s,1))



# --------------------------------------------------------------------------------------------------------------------------
# printWithVars
# --------------------------------------------------------------------------------------------------------------------------

def printWithVars(s, color='black', verbosityThreshold = 1, **kwargs):
    global exectue_defaults
    opts = merge(exectue_defaults, kwargs)              # the options computed from the default options together with the passed in options.
    if opts['verbosity'] < verbosityThreshold:
        return
    prefix = 'would print:' if opts['dryrun'] else ''
    stringToPrint = prefix + (s.format(**getFormatBindings(s,1)))
    if (color == 'black') or not opts['colorize']:
        print stringToPrint
    else:
        print colored(stringToPrint, color)

def printWithVars0(_s, color='black', **kwargs) : printWithVars(_s, color, 0, **kwargs)
def printWithVars1(_s, color='black', **kwargs) : printWithVars(_s, color, 1, **kwargs)
def printWithVars2(_s, color='black', **kwargs) : printWithVars(_s, color, 2, **kwargs)
def printWithVars3(_s, color='black', **kwargs) : printWithVars(_s, color, 3, **kwargs)
def printWithVars4(_s, color='black', **kwargs) : printWithVars(_s, color, 4, **kwargs)



# --------------------------------------------------------------------------------------------------------------------------
# printEnvironmentInformation
# --------------------------------------------------------------------------------------------------------------------------

def printEnvironmentInformation(parseArgs, verbosityThreshold, *variables, **kwargs):
    verbosity = getattr(parseArgs, 'verbosity', 2)
    if verbosity >=verbosityThreshold:
        d = vars(parseArgs)
        (bindings,unbound) = getBindings(variables,2)
        d.update(bindings)
        prettyPrintDictionary(d)
        print ""

def printEnvironmentInformation0(_parseArgs,*args,**kwargs): return printEnvironmentInformation(_parseArgs,0,*args,**kwargs)
def printEnvironmentInformation1(_parseArgs,*args,**kwargs): return printEnvironmentInformation(_parseArgs,1,*args,**kwargs)
def printEnvironmentInformation2(_parseArgs,*args,**kwargs): return printEnvironmentInformation(_parseArgs,2,*args,**kwargs)
def printEnvironmentInformation3(_parseArgs,*args,**kwargs): return printEnvironmentInformation(_parseArgs,3,*args,**kwargs)



# --------------------------------------------------------------------------------------------------------------------------
# sleepWithVisualization
# --------------------------------------------------------------------------------------------------------------------------

def sleepWithVisualization(n):
    t = 0
    sys.stdout.write(stringWithVars('Sleeping for {n} seconds: '))
    while t < n:
        t += 1
        sys.stdout.write('.')
        sys.stdout.flush()
        time.sleep(1)
    sys.stdout.write('\n')
    sys.stdout.flush()
    
        