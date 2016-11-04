import inspect


# --------------------------------------------------------------------------------------------------------------------------
# Text utilities
# --------------------------------------------------------------------------------------------------------------------------

_ColorsDictionary = {
    'grey':30,    'red':31,    'green':32,    'yellow':33,    'blue':34,    'magenta':35,    'cyan':36,    'white':37,
    'on_grey':40, 'on_red':41, 'on_green':42, 'on_yellow':44, 'on_blue':44, 'on_magenta':45, 'on_cyan':46, 'on_white':47,
    'bold':1, 'dark':2, 'underline':4, 'blink':5, 'reverse':7, 'concealed':8
}

def colored(text, *attrs):
    prefix = ''
    for attr in attrs:
        if attr in _ColorsDictionary:
            prefix += '\033[%dm' % _ColorsDictionary[attr]
    return prefix+text+"\033[00m"



# --------------------------------------------------------------------------------------------------------------------------
# Filtering utilities
# --------------------------------------------------------------------------------------------------------------------------

def _getValidArgList(f):
    if inspect.isfunction(f): 
        return inspect.getargspec(f)[0]
    if hasattr(f, '__init__'):
        return inspect.getargspec(f.__init__)[0]
    raise Exception("Unknown object")

def filterKWArgsForFunc(kwargs, f):
    '''Yield a reduced set of kwargs of only the valid keyword arguments for the function / constructor f'''
    return dict([(k, v) for k, v in kwargs.iteritems() if k in _getValidArgList(f)])

def listIntersection(L1,L2):
    L2set = set(L2)
    return [a for a in L1 if a in L2set]

def listRemove(L1,L2):
    L2set = set(L2)
    return [a for a in L1 if a not in L2set]

def listComplement(L1,L2):
    L2set = set(L2)
    L1set = set(L1)
    return listRemove(L1,L2) + listRemove(L2,L1)

def duplicateElements(L):
    seen = set()
    duplicated = set()
    for x in L:
        if x not in seen:
            seen.add(x)
        else:
            duplicated.add(x)
    return duplicated



# --------------------------------------------------------------------------------------------------------------------------
# Pretty Printing utilities
# --------------------------------------------------------------------------------------------------------------------------

def prettyPrintDictionary(d):
    '''Pretty print a dictionary as simple keys and values'''
    maxKeyLength = 0
    maxValueLength = 0
    for key, value in d.iteritems():
        maxKeyLength = max(maxKeyLength, len(key))
        maxValueLength = max(maxValueLength, len(key))
    for key in sorted(d.keys()):
        print ("%"+str(maxKeyLength)+"s : %-" + str(maxValueLength)+ "s") % (key,d[key])



# --------------------------------------------------------------------------------------------------------------------------
# System utilities
# --------------------------------------------------------------------------------------------------------------------------

def merge(*dicts):
    '''Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.'''
    result = {}
    for d in dicts:
        result.update(d)
    return result

def flatten(lst):
    """flatten([["a","btr"],"b", [],["c",["d",["e"], []]]]) will return ['a', 'btr', 'b', 'c', 'd', 'e']"""
    def flatten_aux(item, accumulated):
        if type(item) != list:
            accumulated.append(item)
        else:
            for l in item:
                flatten_aux(l, accumulated)
    accumulated = []
    flatten_aux(lst,accumulated)
    return accumulated

def quiet(code, *args):
    '''Return the result of evaluating the given code with the given arguments catching any
    exceptions and returning False if an exception occurs'''
    try:
        return code(*args)
    except:
        pass
    return False

def getValidAttr(obj, attr, default):
    ans = getattr(obj, attr, default)
    return ans if ans else default
        
