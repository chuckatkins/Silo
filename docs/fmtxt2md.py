#  \r \n   D   B   E   r   r   n   o  \r  \n   —  **  ** 
# DBShowErrors
# —Set the error reporting mode.
# Synopsis:
# void DBShowErrors (int level, void (*func)(char*))
# Fortran Equivalent:
# integer function dbshowerrors(level)
# Arguments:
# level
# Error reporting level. One of DB_ALL, DB_ABORT, DB_TOP, or DB_NONE.
# func
# Function pointer to an error-handling function.
# Returns:
# DBShowErrors returns nothing (void). It cannot fail.
# Description:
# The DBShowErrors function sets the level of error reporting done by Silo when it encounters an error. The following table describes the action taken upon error for different values of level.
# Ordinarily, error reporting from the HDF5 library is disabled. However, DBShowErrors also influences the behavior of error reporting from the HDF5 library.
# Error level value       DB_ALL  DB_ALL_AND_DRVR DB_ABORT        DB_TOP  DB_NONE
# Error action    Show all errors, beginning with the (possibly internal) routine that first detected the error and continuing up the call stack to the application.      Same as DB_ALL execpt also show error messages generated by the underlying driver library (PDB or HDF5).        Same as DB_ALL except abort is called after the error message is printed.       (Default) Only the top-level Silo functions issue error messages.       The library does not handle error messages. The application is responsible for checking the return values of the Silo functions and handling the error.

import re

# 
# Get all documentation lines from text file
#
def GetFileLines(fname):
    with open(fname) as txtfile:
        return txtfile.readlines()

#
# Begin a new API section (new md file)
#
def StartNewSection(i, s, lines):
    mdfile = open("Chapter2-Section%d.md"%s,"wt")
    s += 1
    hs = re.search(r'^[0-9]*\s*API Section\s*(.*)',lines[i])
    if len(hs.groups()) > 0:
        mdfile.write("## %s"%hs.groups()[0])
    else:
        mdfile.write("## Unknown")
    mdfile.write("\n\n")
    i += 1
    while i < len(lines) and \
        not re.search(r'^_visit_defvars\s*275$', lines[i]) and \
        not re.search(r'^dbmkptr\s*283$', lines[i]) and \
        not re.search(r'^Silo.Open$', lines[i]) and \
        not re.search(r'^DBGetComponentNames$', lines[i]) and \
        not re.search(r'^DB[A-Za-z0-9]*\s*[0-9]*$', lines[i]):
        as_sentences = re.sub(r'(?!\.\.)([\.!?]\s*(?!\)))',r'\1\n',lines[i])
        mdfile.writelines(as_sentences)
        i += 1
    mdfile.write("\n")
    return i, s, mdfile

"""
       (re.search(r'^DB[A-Za-z0-9_]*$', lines[i]) or \
        re.search(r'^json-c extensions$', lines[i]) or \
        re.search(r'^<DBfile>\.', lines[i]) or \
        re.search(r'^PMPIO_[A-Za-z]*', lines[i]) or \
        re.search(r'^_visit_[a-z_]*$', lines[i]) or \
        re.search(r'^AlphabetizeVariables$', lines[i]) or \
        re.search(r'^ConnectivityIsTimeVarying$', lines[i]) or \
        re.search(r'^MultivarToMultimeshMap_vars$', lines[i]) or \
        re.search(r'^MultivarToMultimeshMap_meshes$', lines[i]) or \
        re.search(r'^dbmkptr$', lines[i]) or \
        re.search(r'^dbrmptr$', lines[i]) or \
        re.search(r'^db.et2dstrlen$', lines[i]) or \
        re.search(r'^dbwrtfl$', lines[i]) or \
"""

def IsMethodHeader(i, lines):
    if i < len(lines)-1 and re.search(r'^—', lines[i+1]):
        return True
    return False

def ProcessSynopsis(mdfile, i, lines):
    i += 1
    mdfile.write("#### C Signature\n")
    mdfile.write("```\n")
    mdfile.write(lines[i])
    i += 1
    while i < len(lines) and not \
        (re.search(r'^Fortran Equivalent:$', lines[i]) or \
         re.search(r'^Returns:$', lines[i]) or \
         re.search(r'^Arguments:$', lines[i])):
        indented_line = '    ' + lines[i].strip()
        mdfile.write(indented_line)
        mdfile.write("\n")
        i += 1
    mdfile.write("```\n")
    if re.search(r'^Fortran Equivalent:$', lines[i]):
        i += 1
        if re.search(r'^None$', lines[i]):
            mdfile.write("#### Fortran Signature:\n")
            mdfile.write("```\n")
            mdfile.write("None\n")
            mdfile.write("```\n")
            i += 1
        else:
            mdfile.write("#### Fortran Signature\n")
            mdfile.write("```\n")
            fort_args = []
            fort_args_done = False
            while i < len(lines) and not \
                (re.search(r'^Returns:$', lines[i]) or \
                 re.search(r'^Arguments:$', lines[i])):
                fort_args += [w.strip(' \n') for w in lines[i].split(',') if len(w.strip(' \n'))>0]
                if not fort_args_done and re.search(r'[ \t,a-zA-Z0-9_]*\)$', lines[i]):
                    n = 4
                    ident = ""
                    while len(fort_args):
                        mdfile.write(ident + ', '.join(fort_args[:n]))
                        if fort_args[:n][-1][-1] != ')':
                            mdfile.write(",")
                        mdfile.write("\n")
                        fort_args = fort_args[n:]
                        n = 6
                        ident = "   "
                    fort_args = []
                    fort_args_done = True
                elif fort_args_done:
                    mdfile.write(lines[i].strip(' \n'))
                    mdfile.write("\n")
                i += 1
            mdfile.write("```\n")
    mdfile.write("\n")
    return i

def ProcessArgumentListBlock(mdfile, i, lines):
    i += 1
    args = []
    while i < len(lines) and not \
        (re.search(r'^Returns:$', lines[i]) or \
         re.search(r'^Description:$', lines[i])):
        if lines[i].strip() != '':
            args += [lines[i]]
        i += 1
    if len(args) < 2:
        mdfile.write("#### Arguments: None\n")
        return i
    if len(args) % 2 != 0:
        print("***ARGS PROBLEM***\n")
        print(args)
    # use non-breaking spaces to enforce table width
    #mdfile.write("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Arg name | Description&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;\n")
    #mdfile.write("------Arg name | Description--------------------------------------------------------------------------------\n")
    mdfile.write("Arg name | Description\n")
    mdfile.write(":--|:---\n")
    j = 0
    while j < len(args):
#        mdfile.write("* `%s` : %s\n"%(args[j].strip(), args[j+1].strip() if j+1<len(args) else "ARGS PROBLEM"))
#        mdfile.write("\n`%s` : %s\n"%(args[j].strip(), args[j+1].strip() if j+1<len(args) else "ARGS PROBLEM"))
        mdfile.write("`%s` | %s\n"%(args[j].strip(), args[j+1].strip() if j+1<len(args) else "ARGS PROBLEM"))
        j += 2
    mdfile.write("\n")
    print(lines[i])
    return i

def ProcessReturnBlock(mdfile, i, lines):
    i += 1
    retlines = []
    while i < len(lines) and not re.search(r'^Description:$', lines[i]):
        if lines[i].strip() != '' and lines[i].strip().lower()[:4] != 'none':
            retlines += [lines[i]]
        i += 1
    mdfile.write("#### Returned value:\n")
    if len(retlines):
        j = 0
        while j < len(retlines):
            mdfile.write(retlines[j].strip())
            mdfile.write("\n")
            j += 1
    else:
        mdfile.write("void");
    mdfile.write("\n")
    return i


def ProcessMethod(mdfile, i, lines):
    mdfile.write("### `%s()` - %s\n"%(lines[i][:-1], lines[i+1][1:]))
    i += 2
    while i < len(lines) and not IsMethodHeader(i, lines):
        if re.search(r'^Synopsis:$', lines[i]):
            i = ProcessSynopsis(mdfile, i, lines)
        if re.search(r'^Arguments:$', lines[i]):
            i = ProcessArgumentListBlock(mdfile, i, lines)
        if re.search(r'^Returns:$', lines[i]):
            i = ProcessReturnBlock(mdfile, i, lines)
        i += 1
    return i

#
# main program
#
lines = GetFileLines("Chapter2-man_pages2.txt")

s = 0
for i in range(len(lines)):
    if re.search(r'^[0-9]* API Section', lines[i]):
        i, s, mdfile = StartNewSection(i, s, lines)
    if IsMethodHeader(i, lines):
        i = ProcessMethod(mdfile, i, lines)