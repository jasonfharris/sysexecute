## Purpose

The sysexecute python package allows the easier execution of system tasks. Part of this is an auto-formatting mechanism for variable substitution, part of this is being able to simply specify the execution options.

## Installation

You can install `sysexecute` from PyPi by simple:

```
pip install sysexecute
```

## Variable Substitution

Typically in python to format a string we might do something like:

```
val = 3
print("the value of val is {val}".format(val=val))
```

This is kind of long and redundant. If we already have a value for `val` then it should be able to just be subsitutied. In fact if we do

```
from sysexecute import *
val = 3
print (stringWithVars("the value of val is {val}"))
```

The bindings for the variables follow normal python scoping rules. This makes the execution statments a good bit more readable.

## Execution

Here is a typical execution

```
execute("ssh {machinIP} ls {thePath}")
```
assuming the variable `machineIP` and `thePath` have values. The normal output of this script gets piped to StdOut and StdErr, but if you want to capture these you can with something like:

```
(rc, stdout, stderr) = execute("ssh {machinIP} ls {thePath}", captureStdOutStdErr=True)
```

There are various keyword options you can specify like:
- `dryRun` : print what would be executed but don't actually execute anything
- `cwd` : change the directory from which the command will be executed
- `ignoreErrors`: Unless this is true a `sys.exit(returnCode)` will be issued if there is a non-zero return code.
- `shell`: if a shell should be used (defaults to `True`)
- `executable`: which shell to use (defaults to `/bin/bash`)

## Verbosity

Often in scripting we want to include debugging / info commentary depending on what level of verbosity we are requested to display. You can set the level of verboisty shown via eg:

```
set_defaults('verbosity',2)
```

Then in the following only the first two strings would be printed:

```
printWithVars1("success!")
printWithVars2("Machine {machineIP} was reached.")
printWithVars3("You might want to check that blah and blah.")
```


## Testing

To run the test suite you need `py.test` installed on your machine. Then you can simply execute:

```
cd tests
py.test
```

