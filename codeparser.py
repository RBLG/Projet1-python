import pathlib
import re
from typing import Callable, List
from util import *
import patterns

#####################################################
#
#               SCOPE HANDLING CLASS
#
#####################################################

class Field:
    name:str
    vtype:type
    line:int #utilisable seulement si APRES cette ligne

    def __init__(self,nname:str,nvtype:type,nline:int):
        self.name=nname
        self.vtype=nvtype
        self.line=nline

class Import:
    name:str
    alias:str
    specific:List[str] #ce qui est importe,
    #-None pour un import sans from
    #-"*" pour un from avec tout
    #-"..." si un seul
    #-"[...]" si plusieurs
    def __init__(self,nname,nalias,nspecific):
        self.name=nname
        self.nalias=nalias
        if nalias is None:
            self.alias=nname
        self.specific=nspecific


class Scope:
    imports:List[Import]=[]
    globalfields:List[Field]=[]
    fields:List[Field]=[]

    def __init__(self,parent,isfuncscope:bool):
        if parent is None:
            return
        self.imports.append(parent.imports)
        self.globalfields.append(parent.globalfields)
        if not isfuncscope:
            self.fields.append(parent.fields)

#####################################################
#
#               FEEDBACK
#
#####################################################

class Problem:
    #nuput1:str
    #nuput2:str
    line:int
    explanation:str



#####################################################
#
#               FUNCTION
#
#####################################################

def parse_file(path:str)->List[Problem]:
    feedback:List[Problem]=[]
    text:str = pathlib.Path(path).read_text()
    lines:List[str]=text.split("\n")
    index=0
    parse_scope(lines,index,Scope(None,False),feedback)

##### type de ligne

def handle_import(line:str,index:int,scope:Scope,feedback:List[Problem]):
    match=re.search(patterns.IMPORT_AS,line)
    if match is None:
        return False
    name=match.group("module_name")
    alias=match.group("module_alias")
    nimport=Import(name,alias,None)
    scope.imports.append(nimport);

def handle_from_import(line:str,index:int,scope:Scope,feedback:List[Problem]):
    match=re.search(patterns.FROM_IMPORT,line)
    if match is None:
        return False
    name=match.group("module_name")
    specific=match.group("module_content")
    nimport=Import(name,None,specific)
    scope.imports.append(nimport);

def handle_class_declaration(line:str,index:int,scope:Scope,feedback:List[Problem]):
    match=re.search(patterns.DEF_CLASS,line)
    if match is None:
        return False

def handle_function_declaration(line:str,index:int,scope:Scope,feedback:List[Problem]):
    match=re.search(patterns.DEF_FUNC,line)
    if match is None:
        return False
    name=match.group("functon_name")
    paramsstr=match.group("parameters")
    rtntype=match.group("return_type")
    params=re.findall(patterns.FUNC_PARAMS,paramsstr)
    parameters=[]
    for param in params:
        parameters.append(param.group())
    #TODO check de type la
    nscope=Scope(scope,True)
    parse_scope(line,index,scope,feedback)

def handle_if(line:str,index:int,scope:Scope,feedback:List[Problem]):
    match=re.search(patterns.IF,line)
    if match is None:
        return False

def handle_else(line:str,index:int,scope:Scope,feedback:List[Problem]):
    match=re.search(patterns.ELSE,line)
    if match is None:
        return False

def handle_while(line:str,index:int,scope:Scope,feedback:List[Problem]):
    match=re.search(patterns.WHILE,line)
    if match is None:
        return False

def handle_for(line:str,index:int,scope:Scope,feedback:List[Problem]):
    match=re.search(patterns.FOR,line)
    if match is None:
        return False

def handle_return(line:str,index:int,scope:Scope,feedback:List[Problem]):
    pass

def detect_empty_line(line:str):
    pass

def detect_lone_keyword(line:str,index:int,scope:Scope,feedback:List[Problem]):
    pass

def handle_action_line(line:str,index:int,scope:Scope,feedback:List[Problem]):
    match=re.search(patterns.ACTION_LINE,line)
    if match is None:
        return False
    payload=LinePayload(scope,line,feedback)
    parse_next_nuput(payload)



#liste des etapes du parsing du control flow du code
steps=[detect_lone_keyword,         #R
       handle_import,               #R
       handle_from_import,          #R
       handle_class_declaration,    #R
       handle_function_declaration, #R
       handle_if,                   
       handle_else,                 
       handle_while,                
       handle_for,                  
       handle_action_line           
       ]

def parse_scope(lines:List[str],index:int,parentscope:Scope,feedback:List[Problem]):
    scope:Scope=Scope(parentscope,False)
    
    sindent:int=-1
    while True:
        line:str=lines[index]
        if detect_empty_line(line):
            continue
        lindent:int=len(re.search("^[\t ]*",line).group())
        if sindent<0:
            sindent=lindent
        if lindent<sindent:#si l'indentation diminue, c'est qu'on sort du scope
            break
        for step in steps:
            if step(line,index,scope,feedback):
                break
        index+=1
        if index<=len(lines):
            break
    print("scope: ",scope)
    print(scope.imports)
    print(scope.globalfields)
    print(scope.fields)

###########################################################################################
#
#                      ACTION LINE PARSING
#
###########################################################################################

class Nuput: #une node du graphe de code (mix input/ouput-> nuput)
    otype:type #type de retour
    code:str #le texte definissant le nuput et ses enfants
    
    def __init__(self,notype:type,ncode:str):
        self.otype=notype
        self.code=ncode

class LinePayload:
    scope:Scope
    remaining:str
    feedback:List[Problem]

    def __init__(self,nscope:Scope,nremaining:str,nfeedback:List[Problem]):
        self.scope=nscope
        self.remaining=nremaining
        self.feedback=nfeedback


#############################

def parse_next_nuput(payload:LinePayload):
    for step in nuput_steps:
        if step(payload):
            parse_next_operation(payload)
            break


def parse_next_operation(payload:LinePayload):
    for step in ops_steps:
        if step(payload):
            parse_next_nuput(payload)
            break

def parse_type_depth(payload:LinePayload):
    match=re.search(patterns.TYPE_DEPTH,payload.remaining)
    if match is None:
        return False
    type_name=match.group("type_name")
    remaining_type_depth=match.group("remaining_type_depth")
    if remaining_type_depth is not None:
        payload.remaining=remaining_type_depth
        result:any=parse_type_depth(payload)
        payload.remaining=""
    else :
        payload.remaining=match.group("remaining")
        #return remaining,type_name





### verticaux (operation)

def parse_function_call_ops(payload:LinePayload)->bool:
    match=re.search(patterns.PARENTHESIS_OPENING,payload.remaining)#(...
    if match is None:
        return False
    params:List[any]=[]
    for i in range (0,100):#while avec une limite. j'ai 0 envie d'avoir des prob de boucle infinie
        #devrait utiliser un while mais le for est plus clair pour la limite
        pass
        for step in ops_steps:
            if step(payload.remaining):
                break
        if parse_param_separator(payload):
            #ferme le nuput precedent 
            continue
        if parse_parenthesis_end(payload):
            break
    match=re.search(patterns.FUNC_CLOSING,payload.remaining)
    type_depth=match.group("remaining_type_depth")
    if type_depth is not None:
        parse_type_depth(type_depth)
    #return la liste des param

def parse_chaining_ops(payload:LinePayload)->bool:
    match=re.search(patterns.CHAIN,payload.remaining)#.
    if match is None:
        return False
    payload.remaining=match.group("remaining")
    #return remaining

def parse_operation_ops(payload:LinePayload)->bool:
    match=re.search(patterns.OPERATOR,payload.remaining)#+ ...
    if match is None:
        return False
    op=match.group("operator")
    payload.remaining=match.group("remaining")
    #return remaining, nuput avec solve des types basé sur l'operator (both bool si op boolean, both type si "is",etc)

def parse_bracket_ops(payload:LinePayload)->bool:
    match=re.search(patterns.BRACKET_OPENING,payload.remaining)#[...
    if match is None:
        return False
    payload.remaining=match.group("remaining")
    if parse_next_nuput(payload):
        pass
    payload.remaining=""#link a next nuput
    match=re.search(patterns.BRACKET_CLOSING,payload.remaining)#]...
    if match is None:
        pass #return problem
    #return remaining



ops_steps=[parse_function_call_ops,
           parse_chaining_ops,
           parse_operation_ops,
           parse_bracket_ops
           ]

## horizontaux (nuput)

def parse_parenthesis_nuput(payload:LinePayload)->bool:
    match=re.search(patterns.PARENTHESIS_OPENNING,payload.remaining)#(...
    if match is None:
        return False
    payload.remaining=match.group("remaining")
    parse_next_nuput(payload)
    if parse_parenthesis_end(payload):
        pass #return Problem "syntax issue"
    payload.remaining=match.group("remaining")
    #return remaining


def parse_var_nuput(payload:LinePayload)->bool:
    match=re.search(patterns.VAR_USE,payload.remaining)#var_name
    if match is None:
        return False
    varname=match.group("var_name")
    type_depth=match.group("unresolved_type_depth")
    if type_depth is not None:
        payload.remaining=type_depth
        type_depth_solved:any=parse_type_depth(payload)
    payload.remaining=match.group("remaining")
    #return remaining

def parse_string_literal(payload:LinePayload)->bool:
    match=re.search(patterns.STR_LIT,payload.remaining)#"..."
    if match is None:
        return False
    #return nuput 

def parse_number_literal(payload:LinePayload)->bool:
    match=re.search(patterns.NUM_LIT,payload.remaining)#09843...
    if match is None:
        return False
    #return nuput 

nuput_steps:Callable=[
           parse_parenthesis_nuput,
           parse_var_nuput,
           parse_string_literal,
           parse_number_literal
           ]

##closing

def parse_parenthesis_end(payload:LinePayload):
    match=re.search(patterns.PARENTHESIS_CLOSING,payload.remaining)
    return match is None

#special

def parse_param_separator(payload:LinePayload):
    match=re.search(patterns.COMMA,payload.remaining)#)...
    return match is None