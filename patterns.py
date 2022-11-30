import regex

# petit trick pour avoir des pattern regex sur plusieurs lignes
def format(pattern: str) -> str:
    return regex.sub("\r?\n *", "", pattern)


#######################################################################################
#
#                   LINE CONTENT DETECTION
#
#######################################################################################

# match le format "  import module_name as module_alias"
# capture "module_name" et "module_alias"
IMPORT_AS: str = format(
    r"""
^[\t ]*
import
[\t ]+
(?P<module_name>[a-zA-Z0-9_]+)
(?:
    [\t ]+
    as
    [\t ]+
    (?P<module_alias>[a-zA-Z0-9_]+)
)?
[\t ]*
;?
(?:\#.*)?$
"""
)

# match le format "  from module_name import ..."
# capture "module_name" et "..."
FROM_IMPORT: str = format(
    r"""
^[\t ]*
from
[\t ]+
(?P<module_name>[a-zA-Z0-9_]+)
[\t ]+
import
[\t ]+
(?P<module_content>.*?)
[\t ]*
;?
(?:\#.*)?$
"""
)

# match le format "  class class_name(parent_name):"
# capture "class_name" et "parent_name"
DEF_CLASS: str = format(
    r"""
^[\t ]*
class
[\t ]+
(?P<class_name>[a-zA-Z0-9_]+)
(?:
    \(
    (?P<parent_name>
        [a-zA-Z0-9_]+
        (?:
            \[
            [a-zA-Z0-9_]+
            \]
        )?
    )
    \)
)?
[\t ]*
\:
[\t ]*
;?
(?:\#.*)?$
"""
)

# match le format "  def func_name(params)->return_type:
# capture "func_name", "params" et "return type"
DEF_FUNC: str = format(
    r"""
^[\t ]*
def
[\t ]+
(?P<func_name>[a-zA-Z0-9_]+)
[\t ]*
\(
[\t ]*
(?P<param_depth>
  (?P<item>
    [^()"#]*+
    "[^"]*"
    |
    [^()#]*+
    (?:
      \(
      (?&item)?
      \)
    )?
  )*
  [^()\#]*
)
[\t ]*
\)
[\t ]*
(?:
    ->
    (?P<return_type_sig>
        (?P<return_type>[a-zA-Z0-9_]+)
        [\t ]*
        (?:
            \[
            [\t ]*
            (?P<type_depth>
                (?P<item2>
                    [^\[\]"#]*+
                    "
                    [^"]*+
                    "
                    |
                    [^\[\]#]*+
                    (?:
                        \[
                        (?&item2)?
                        \]
                    )?
                )*
                [^\[\]\#\t ]*
            )
            [\t ]*
            \]
        )?
    )
    [\t ]*
)?
\:
[\t ]*
;?
(?:\#.*)?$
"""
)

#
# detecte une ligne vide
EMPTY: str = format(r"^[\t ]*;?$")

#
#
LONE_KEYWORD: str = format(
    r"""
^[\t ]*
(?P<keyword>
    (?:pass)|
    (?:return)|
    (?:break)|
    (?:continue)
)
[\t ]*
;?
(?:\#.*)?$
"""
)

#
#
RETURN_SET: str = format(
    r"""
^[\t ]*
return
[\t ]+
(?P<return_content>\S+?)
[\t ]*
;?
(?:\#.*)?$
"""
)

# match les if et else if
#
IF: str = format(
    r"""


"""
)

#
#
ELSE: str = format(
    r"""


"""
)

#
#
WHILE: str = format(
    r"""


"""
)

#
#
FOR: str = format(
    r"""


"""
)

# match une ligne contenant des appels de fonctions, des affectation de variable, etc
#
ACTION_LINE = format(
    r"""
^[\t ]*
(?P<content>.*?)
[\t ]*
;?
(?:\#.*)?$
"""
)

#######################################################################################
#
#                   NUPUT DETECTION
#
#######################################################################################

# matche
#
DEEP_PARENTHESIS: str = format(
    """
^\(
[\t ]*
(?P<depth>
  (?P<item>
    [^()"#]*+
    "[^"]*"
    |
    [^()#]*+
    (?:
      \(
      (?&item)?
      \)
    )?
  )*
  [^()\#\t ]*
)
[\t ]*
\)
[\t ]*
(?P<remaining>.*)
"""
)


#
#
CHAIN: str = format(
    r"""
^\.
[\t ]*
(?P<remaining>.*)
"""
)

#
#
OPERATOR: str = format(
    r"""
^
(?P<operator>
    &|
    \^|
    \||
    <<|
    >>|
    ~|
    \+=?|
    -=?|
    %=?|
    /{1,2}=?|
    ={1,2}|
    !=|
    \*{1,2}=?|
    <>|
    >=?|
    <=?|
    and|
    or|
    is(:?[\t ]*not)?|
    (:?not[\t ]*)?in
)
[\t ]*
(?P<remaining>.*)
"""
)

# match une declaration ou un appel a une variable
#
VAR_USE: str = format(
    r"""
^(?P<var_name>[a-zA-Z0-9_]+)
(?:
    [\t ]*
    \:
    (?P<type_sig>
        [\t ]*
        (?P<type_name>[a-zA-Z0-9_]+)
        (?:
            [\t ]*
            \[
            [\t ]*
            (?P<type_depth>
                (?P<item>
                    [^\[\]"#]*+
                    "
                    [^"]*+
                    "
                    |
                    [^\[\]#]*+
                    (?:
                        \[
                        (?&item)?
                        \]
                    )?
                )*
                [^\[\]\#\t ]*
            )
            [\t ]*
            \]
        )?
    )
)?
[\t ]*
(?P<remaining>.*)
"""
)

# match une declaration ou un appel a une variable
#
TYPE_DEPTH: str = format(
    r"""
^
(?P<type_sig>
    (?P<type_name>[a-zA-Z0-9_]+)
    [\t ]*
    (?:
        \[
        [\t ]*
        (?P<depth>
            (?P<item>
                [^\[\]"#]*+
                "[^"]*"
                |
                [^\[\]#]*+
                (?:
                    \[
                    (?&item)?
                    \]
                )?
            )*
            [^\[\]\#\t ]*
        )
        [\t ]*
        \]
    )?
)
[\t ]*
(?P<remaining>.*)
"""
)

# matche une descente dans les bracket
#
BRACKET: str = format(
    r"""
^
\[
[\t ]*
(?P<depth>
  (?P<item>
    [^\[\]"#]*+
    "[^"]*"
    |
    [^\[\]#]*+
    (?:
      \[
      (?&item)?
      \]
    )?
  )*
  [^\[\]\#]*
)
[\t ]*
\]
[\t ]*
(?P<remaining>.*)
"""
)

COMMA: str = format(
    r"""
^,
[\t ]*
(?P<remaining>.*)
"""
)


#
#
STR_LIT: str = format(
    r"""
^
(?P<literal>r?\".*?\")
[\t ]*
(?P<remaining>.*)
"""
)

#
#
NUM_LIT: str = format(
    r"""
^(?P<literal>
    0x[0-9a-fA-F]+|
    0b[0-1]+|
    0o[0-7]+|
    [0-9]+
)
[\t ]*
(?P<remaining>.*)
"""
)
