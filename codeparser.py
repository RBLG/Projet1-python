import pathlib
from types import FunctionType
from typing import Callable, List
from util import *
import patterns
import regex

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
    code:str
    line:int
    description:str

    def __init__(self,ncode:str,nline:int,ndesc:str):
        self.code=ncode
        self.line=nline
        self.description=ndesc



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
    match=regex.search(patterns.IMPORT_AS,line)
    if match is None:
        return False
    name=match.group("module_name")
    alias=match.group("module_alias")
    nimport=Import(name,alias,None)
    scope.imports.append(nimport);
    return True

def handle_from_import(line:str,index:int,scope:Scope,feedback:List[Problem]):
    match=regex.search(patterns.FROM_IMPORT,line)
    if match is None:
        return False
    name=match.group("module_name")
    specific=match.group("module_content")
    nimport=Import(name,None,specific)
    scope.imports.append(nimport);
    return True

def handle_class_declaration(line:str,index:int,scope:Scope,feedback:List[Problem]):
    match=regex.search(patterns.DEF_CLASS,line)
    if match is None:
        return False
    return True

def handle_function_declaration(line:str,index:int,scope:Scope,feedback:List[Problem]):
    match=regex.search(patterns.DEF_FUNC,line)
    if match is None:
        return False
    name=match.group("func_name")
    paramsstr=match.group("param_depth")
    rtntype=match.group("return_type_sig")
    params=regex.findall(patterns.FUNC_PARAMS,paramsstr)
    parameters=[]#TODO remove?
    for param in params:
        paramstr=param.group()
        parameters.append(paramstr)
        payload=LinePayload(scope,paramstr,feedback)
        result:any=parse_next_nuput(payload)
    nscope=Scope(scope,True)
    parse_scope(line,index,scope,feedback)
    return True

def handle_if(line:str,index:int,scope:Scope,feedback:List[Problem]):
    match=regex.search(patterns.IF,line)
    if match is None:
        return False
    return True

def handle_else(line:str,index:int,scope:Scope,feedback:List[Problem]):
    match=regex.search(patterns.ELSE,line)
    if match is None:
        return False
    return True

def handle_while(line:str,index:int,scope:Scope,feedback:List[Problem]):
    match=regex.search(patterns.WHILE,line)
    if match is None:
        return False
    return True

def handle_for(line:str,index:int,scope:Scope,feedback:List[Problem]):
    match=regex.search(patterns.FOR,line)
    if match is None:
        return False
    return True

def handle_return(line:str,index:int,scope:Scope,feedback:List[Problem]):
    match=regex.search(patterns.RETURN_SET,line)
    if match is None:
        return False
    return True

def detect_empty_line(line:str):
    match=regex.search(patterns.EMPTY,line)
    return match is not None

def detect_lone_keyword(line:str,index:int,scope:Scope,feedback:List[Problem]):
    pass

def handle_action_line(line:str,index:int,scope:Scope,feedback:List[Problem]):
    match=regex.search(patterns.ACTION_LINE,line)
    if match is None:
        return False
    parse_horizontality(scope,line,feedback)
    return True



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
        lindent:int=len(regex.search("^[\t ]*",line).group())
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
class RawType: #classe custom plutot que utiliser "type" pour handle les types non reconnu
    sign:str #la signature du type, le nom plus les parametres de type [...]
    rtype:type #le type si reconnu par python comme un type existant

    def __init__(self,nsign:str,nline:int):
        self.sign =nsign
        self.rtype=get_type_by_name(nsign)


class Raw:
    pass

#operation parse mais dont l'ordre dans l'horizontalite n'est pas encore detectee
class RawOperation(Raw):
    priority:int # 99-appel de fonction,80-puissance(**) 50-multiplication(*), 10-addition(+)
    #si plus, voir https://pythongeeks.org/python-operator-precedence/
    take_before:bool
    take_after:bool
    
    def process():
        raise Exception("undefined RawOperation")

    def __init__(self,npriority,nprocess:FunctionType):
        self.priority=npriority

class RawNuput(Raw):
    otype:RawType
    code:str

    def __init__(ntype:RawType,ncode:str,ninputs:List[Raw],nprocess:FunctionType):
        pass


class Nuput: #un bloc de code retournant une valeur (mix input/ouput-> nuput)
    outtype:RawType #type de retour
    code:str #le texte definissant le nuput et ses enfants
   
    def __init__(self,notype:type,ncode:str):
        self.otype=notype
        self.code=ncode


class Operation(Nuput):
    inputs:List[Nuput]
    #index qui lie les differents nuputs pour le check de type.
    typelinks:List[tuple[int,int]] #les val negatives sont spéciales (-1=output) (?)

#############################

#contexte du parsing
class LinePayload:
    scope:Scope #les variables actuellement accessible
    remaining:str #ce qui reste a parser de la ligne
    feedback:List[Problem]#la liste des problemes rencontre durant le parsing et a ouput

    def __init__(self,nscope:Scope,nremaining:str,nfeedback:List[Problem]):
        self.scope=nscope
        self.remaining=nremaining
        self.feedback=nfeedback


#############################
# afin de parser le flow d'un morceau de code, je me base sur deux concept:
# -l'horizontalite: aka quand une operation est ajoute a la suite d'un code retournant une valeur,
#  c'est a dire les appels de fonction, les operateur logique, etc
# 
# -la profondeur: aka quand on ouvre des parentheses, des bracket, {}, <>, "", etc,
#  c'est par exemple les parametres de fonction, les types generique dans le annotations de type
# 
# le parsing de l'horizontalite se deroule en deux etape:
#  - le parsing des bloc retournant une valeur (les nuputs)
#  - le parsing des operateur
#  le parseur alterne donc entre les deux jusqu'a une plus trouver de match
# 
# le parsing de la profondeur se passe en detectant la profondeur dans des parenthese, etc et en repetant
#  la detection de l'horizontalite mais cette fois ça entre les parentheses
#############################
def parse_horizontality(nscope,nremaining,nfeedback)->Nuput:
    chain:List[Raw]=[]
    payload=LinePayload(nscope,nremaining,nfeedback)
    for i in range (0,100): #limite pour eviter les boules infinie
        rtn:Nuput        = parse_next_nuput(payload)
        if rtn is None:
            break
        chain.append(rtn)
        rtn2:RawOperation= parse_next_operation(payload)
        if rtn2 is None:
            break
        chain.append(rtn2)
    return resolve_operation_chain()

def resolve_operation_chain():
    pass


#parsing de l'horizontalite partie 1: parse les nuputs
def parse_next_nuput(payload:LinePayload)->Nuput:
    for step in nuput_steps:
        result=step(payload)
        if result is not None:
            return result
    return None


#parsing de l'horizontalite partie 2: parse les operateurs
def parse_next_operation(payload:LinePayload)->RawOperation:
    for step in ops_steps:
        result=step(payload)
        if result is not None:
            return result
    return None


#############################
#parse les annotations de types.
#du a la possibilite de chaque type d'avoir des type generique,
#il est necessaire de performer une regex recursive pour assurer que il y a le meme nombre de
#bracket entrant "[", que sortant "]".
#techniquement il faudrait utiliser la fonction recursivement pour avoir un objet avec une structure
# du type [nom1;[nom2;[nom3;...]]] mais c'est hors scope du projet
#############################
def parse_type_depth(payload:LinePayload)->RawType:
    match=regex.search(patterns.TYPE_DEPTH,payload.remaining)
    if match is None:
        return None
    type_name=match.group("type_name")
    type_sig=match.group("type_sig")
    type_depth=match.group("depth")
    if type_depth is not None:
        #payload2=LinePayload(payload.scope,type_depth,payload.feedback)
        #payload.remaining=type_depth
        #result:any=parse_type_depth(payload)
        pass
    
    payload.remaining=match.group("remaining")
    #return remaining,type_name
    return RawType(type_sig)


### verticaux (operation) ###
#ne parse pas "func(...)" mais "(...)", vu que techniquement une fonction est un objet et peut etre dans une variable
def parse_function_call_ops(payload:LinePayload)->Nuput:
    match=regex.search(patterns.DEEP_PARENTHESIS,payload.remaining)#(...
    if match is None:
        return None
    depth=match.group("depth")
    payload.remaining=match.group("depth")

    #on parse les parametres
    payload2=LinePayload(payload.scope,depth,payload.feedback)
    params:List[Nuput]=[]
    for i in range (0,100):#limite pour eviter les boules infinie
        result= parse_horizontality(payload2.remaining)
        if result is None:
            #payload.feedback.append(TODO "parametres terminé par une virgule")
            break
        params.append(result)
        if not parse_separator(payload):
            break
        
    match=regex.search(patterns.FUNC_CLOSING,payload.remaining)
    type_depth=match.group("remaining_type_depth")
    type=None
    if type_depth is not None:
        type=parse_type_depth(type_depth)
    return RawNuput(type,"TODO",params,process_function) #TODO le traitement

def process_function(rnuput:RawNuput):
    pass


#parse un point ("."), par exemple pour les appel de fonction on la recup de variable dans un objet
def parse_chaining_ops(payload:LinePayload)->RawOperation:
    match=regex.search(patterns.CHAIN,payload.remaining)#.
    if match is None:
        return None
    payload.remaining=match.group("remaining")
    return RawOperation()

def parse_operation_ops(payload:LinePayload)->bool:
    match=regex.search(patterns.OPERATOR,payload.remaining)#+ ...
    if match is None:
        return False
    op=match.group("operator")
    payload.remaining=match.group("remaining")
    #return nuput avec solve des types basé sur l'operator (both bool si op boolean, both type si "is",etc)
    return True

def parse_bracket_ops(payload:LinePayload)->bool:
    match=regex.search(patterns.BRACKET,payload.remaining)#[...]
    if match is None:
        return False
    payload.remaining=match.group("remaining")
    depth=match.group("depth")
    nuputs=[]
    payload2=LinePayload(payload.scope,depth,payload.feedback)
    for i in range(0,100):
        item:any=parse_next_nuput(payload2)
        nuputs.append(item)
        if parse_separator(payload2):
            break
    #return ?
    return True


ops_steps=[parse_function_call_ops,
           parse_chaining_ops,
           parse_operation_ops,
           parse_bracket_ops
           ]

## horizontaux (nuput)

def parse_parenthesis_nuput(payload:LinePayload)->bool:
    match=regex.search(patterns.DEEP_PARENTHESIS,payload.remaining)#(...)
    if match is None:
        return False
    depth=match.group("depth")
    payload2:LinePayload=LinePayload(payload.scope,depth,payload.feedback)
    inside:any=parse_next_nuput(payload2)
    payload.remaining=match.group("remaining")
    #return remaining
    return True


def parse_var_nuput(payload:LinePayload)->bool:
    match=regex.search(patterns.VAR_USE,payload.remaining)#var_name:type[...]
    if match is None:
        return False
    varname=match.group("var_name")
    type_sig=match.group("type_sig")
    #type_depth=match.group("type_depth")
    
    payload.remaining=match.group("remaining")
    #return remaining
    return True

def parse_string_literal(payload:LinePayload)->bool:
    match=regex.search(patterns.STR_LIT,payload.remaining)#"string"
    if match is None:
        return False
    #return nuput 
    return True

def parse_number_literal(payload:LinePayload)->bool:
    match=regex.search(patterns.NUM_LIT,payload.remaining)#09843...
    if match is None:
        return False
    #return nuput 
    return True

nuput_steps:Callable=[
           parse_parenthesis_nuput,
           parse_var_nuput,
           parse_string_literal,
           parse_number_literal
           ]

##special

def parse_separator(payload:LinePayload):
    match2=regex.search(patterns.COMMA,payload.remaining)
    if match2 is not None:
        payload.remaining=match2.group("remaining")
    return match2 is None
