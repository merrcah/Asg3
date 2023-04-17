%mkdir "ply" 
%cd "ply"
%rm "lex.py"
%rm "yacc.py"
!wget -q "https://raw.githubusercontent.com/dabeaz/ply/master/src/ply/lex.py"
!wget -q "https://raw.githubusercontent.com/dabeaz/ply/master/src/ply/yacc.py"
%cd "../"

__file__ = "asg3_startingpoint.ipynb"

# -----------------------------------------------------------------------------
# example.py
#
# Example of using PLY To parse the following simple grammar.
#
# Note that these example programs should be saved into a folder named tb under the names example1.bas, example2.bas, and example3.bas
#
#   EXAMPLE VALID PROGRAM: (note the extra blank line at the end)
#     10 LET A = 3
#     20 PRINT A
#     30 END
#
#
#   LONGER EXAMPLE PROGRAM:
#     10 INPUT A, B
#     20 LET T = 0
#     30 LET T = T + A
#     40 LET A = A + 1
#     50 IF A <= B THEN GOTO 30
#     60 PRINT "here is your total:", T 
#     70 END
#
#
#   INVALID PROGRAM: (you cannot goto a string! and varnames should only be 1 character long!)
#     10 IF A = B THEN GOTO "hello there"
#     20 LET ZZZZ = 0
#     30 END
#
#
#   TINY BASIC CONTEXT FREE GRAMMAR:
#
#  program ::= line line*
#  line ::= number statement CR  
#  statement ::= PRINT expr-list
#                IF expression relop expression THEN statement
#                GOTO expression
#                INPUT var-list
#                LET var = expression
#                GOSUB expression
#                RETURN
#                END
#  expr-list ::= (string|expression) (, (string|expression) )*
#  var-list ::= var (, var)*
#  expression ::= (+|-|ε) term ((+|-) term)* 
#  term ::= factor ((*|/) factor)*
#  factor ::= var | number | (expression)
#  var ::= A | B | C ... | Y | Z
#  number ::= digit digit*
#  digit ::= 0 | 1 | 2 | 3 | ... | 8 | 9
#  relop ::= < (>|=|ε) | > (<|=|ε) | =
#  string ::= " ( |!|#|$ ... -|.|/|digit|: ... @|A|B|C ... |X|Y|Z)* " 
#
# -----------------------------------------------------------------------------

from ply.lex import lex
from ply.yacc import yacc 

# helper func for reading in tiny basic example files
def readFile(filename):
  print('\nREADING FILE', filename)
  with open(filename, 'r') as file:
    return file.read()


# --- Tokenizer

# All tokens must be named in advance. 
tokens = ('PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'LPAREN', 'RPAREN', 'CR',
          'VAR', 'NUMBER', 'EQUALS', 'RELOP', 'COMMA', 'STRING')

# Ignored characters
t_ignore = ' \t'

# Token matching rules are written as regexs
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_EQUALS = r'='
t_COMMA = r','
t_RELOP = r'((<[>=]?)|(>[<=]?))'  # don't include equals by itself so that it matches separately when not part of relop
t_CR = r'[(\r|\n)(\r|\n)*]'  # one or more newline characters all get collapsed into a single CR
# because these strings HAVE to start/end with a quote, they should not match any of our keywords
t_STRING = r'\"([^"]|\\")*\"'

# TODO fill in the missing keywords in the list below ...
reserved = {
    'print': 'PRINT',
    'input': 'INPUT',
    'if': 'IF',
    'then': 'THEN',
    'let': 'LET',
    'goto': 'GOTO',
    'gosub': 'GOSUB',
    'return': 'RETURN',
    'end': 'END'
}


def t_VAR(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    # scan through all the reserved words and update the type
    t_lower = t.value.lower()
    t.type = reserved.get(t.value.lower(), 'VAR')
    if t.type == 'VAR' and len(t.value) > 1:
        print("var names can only be one character!")
    return t


# A function can be used if there is an associated action.
# Write the matching regex in the docstring.
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t


# Error handler for illegal characters
def t_error(t):
    print(f'Illegal character {t.value[0]!r}')
    t.lexer.skip(1)


# Build the lexer object
lexer = lex()


# --- Parser

# Write functions for each grammar rule which is
# specified in the docstring.

def p_program(p):
    '''
    program : linelist
    '''
    p[0] = p[1]


def p_linelist_single(p):
    '''
    linelist : line
    '''
    p[0] = (p[1])


def p_linelist_multiple(p):
    '''
    linelist : line linelist
    '''
    p[0] = (p[1]) + p[2]


def p_line(p):
    '''
    line : NUMBER statement CR
    '''
    p[0] = ('line', p[1], p[2])


def p_statement_print(p):
    '''
    statement : PRINT exprlist
    '''
    p[0] = ('print', p[2])


def p_statement_input(p):
    '''
    statement : INPUT varlist
    '''
    p[0] = ('input', p[2])


def p_varlist_single(p):
    '''
    varlist : VAR
    '''
    p[0] = ('var', p[1])


def p_varlist_multi(p):
    '''
    varlist : VAR COMMA varlist
    '''
    p[0] = ('var', p[1]) + p[3]


def p_statement_let(p):
    '''
    statement : LET VAR EQUALS expression
    '''
    p[0] = ('let', p[2], p[4])


def p_statement_if(p):
    '''
    statement : IF expression RELOP expression THEN statement
    '''
    p[0] = ('if', p[2], p[3], p[4], p[6])


def p_statement_if_equals(p):
    '''
    statement : IF expression EQUALS expression THEN statement
    '''
    p[0] = ('if', p[2], p[3], p[4], p[6])


def p_statement_goto(p):
    '''
    statement : GOTO expression
    '''
    p[0] = ('goto', p[2])


def p_statement_gosub(p):
    '''
    statement : GOSUB expression
    '''
    p[0] = ('gosub', p[2])

def p_statement_return(p):
    '''
    statement : RETURN
    '''
    p[0] = ('return',)

def p_statement_end(p):
    '''
    statement : END
    '''
    p[0] = ('end',)


# HINT: expressions were hard so I've done everything else for you already below
def p_exprlist_single(p):
    '''
    exprlist : expressionOrString
    '''
    p[0] = p[1]


def p_exprlist_multi(p):
    '''
    exprlist : expressionOrString COMMA exprlist
    '''
    p[0] = (p[1]) + (p[3])


def p_expressionOrString_expr(p):
    '''
    expressionOrString : expression
    '''
    p[0] = p[1]


def p_expressionOrString_str(p):
    '''
    expressionOrString : STRING
    '''
    p[0] = ('string', p[1])


#  expression ::= (+|-|ε) term ((+|-) term)*
def p_expression_termlist(p):
    '''
    expression : termlist
    '''
    p[0] = p[1]


def p_expression_termslistu(p):
    '''
    expression : PLUS termlist
               | MINUS termlist
    '''
    p[0] = ('unary', p[1], p[2])


def p_expression_termlist_single(p):
    '''
    termlist : term
    '''
    p[0] = p[1]


def p_expression_termlist_multi(p):
    '''
    termlist : term PLUS termlist
             | term MINUS termlist 
    '''
    p[0] = (p[2], p[1], p[3])


#  term ::= factor ((*|/) factor)*
def p_term(p):
    '''
    term : factorlist
    '''
    p[0] = p[1]


def p_factorlist_single(p):
    '''
    factorlist : factor
    '''
    p[0] = p[1]


def p_factorlist_multi(p):
    '''
    factorlist : factor TIMES factorlist
               | factor DIVIDE factorlist
    '''
    p[0] = (p[2], p[1], p[3])


# factor ::= var | number | (expression)
def p_factor_var(p):
    '''
    factor : VAR
    '''
    p[0] = ('var', p[1])


def p_factor_num(p):
    '''
    factor : NUMBER
    '''
    p[0] = ('number', p[1])


def p_factor_grouped(p):
    '''
    factor : LPAREN expression RPAREN
    '''
    p[0] = ('grouped', p[1])


def p_error(p):
    print(f'Syntax error at {p.value!r}')


# Build the parser
parser = yacc()

# THERE IS NO NEED TO MODIFY ANY OF THE CODE BELOW ... BUT IF IT ISN'T WORKING MAKE SURE YOU HAVE MOUNTED YOUR GOOGLE DRIVE
# AND CREATED A SUBFOLDER NAMED tb AND ADDED ALL THE EXAMPLE PROGRAMS FROM THE COMMENT AT THE TOP OF THIS FILE

# Let's parse some valid programs
# You must FIRST create these programs on your google drive in a subfolder named "tb"
program1 = readFile('/content/drive/MyDrive/tb/example1.bas')
ast = parser.parse(program1)
print(ast)

program2 = readFile('/content/drive/MyDrive/tb/example2.bas')
ast = parser.parse(program2)
print(ast)

# Now try an invalid program
program3 = readFile('/content/drive/MyDrive/tb/example3.bas')
ast = parser.parse(program3)
print(ast)

# helpful debugging code to see how the lexer is matching tokens
# sampleprogram = "PRINT \"Hello there\", T"
# lexer.input(sampleprogram)
# while True:
#  tok = lexer.token()
#  if not tok:
#      break      # no more tokens, break out of the loop   
#  print(tok)
