import argparse
from typing import TypeVar, Generic

########################################################
#
#               GENERAL TOOLS
#
########################################################


T = TypeVar('T') 
class Option(Generic[T]):
    """concept de Rust qui enforce la verification de presence de la valeur"""
    none:bool=True
    val:T=None

    def __init__(self,nval=None) -> None:
        self.none = nval is None
        self.val = nval

import builtins
def get_type_by_name(type_name): 
    try: 
        return getattr(builtins, type_name) 
    except AttributeError: 
        return None 


########################################################
#
#               COMMAND LINE ARGUMENTS HANDLING
#
########################################################

class arguments:
    """groupe les arguments """
    path:str=None
    
#rust me manque
def get_args()->arguments:
    """recupere et verifie la validite des parametres"""
    parser = argparse.ArgumentParser(description='Detect type mismatch')
    ###args
    parser.add_argument("-p", "--path", required=True, dest="path")
    ###fin args
    
    #parsing
    pargs = parser.parse_args()
    args=arguments()

    ###transfert vers arguments
    args.path=pargs.path #argparse assure la presence de l'argument path, donc pas de check (?) 
    
    ###fin transfert
    return args



