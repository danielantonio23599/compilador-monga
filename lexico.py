"""

 Linguagem Monga

    Gramatica::

    program : { definition }

    definition : def-variable | def-function | def-type

    def-variable : VAR ID ':' type ';'

    type : ID

    def-type : TYPE ID '=' typedesc ;

    typedesc : ID | '[' typedesc ']' | '{' { field } '}'

    field : ID ':' type ';' ;

    def-function : FUNCTION ID '(' parameters ')' [':' type] block

    parameters : [ parameter { ',' parameter } ]

    parameter : ID ':' type

    block : '{' { def-variable } { statement } '}'

    statement : IF cond block [ ELSE block ]
              | WHILE cond block
              | var '=' exp ';'
              | RETURN [ exp ] ';'
              | call ';'
              | '@' exp ';'
              | block

    var : ID | exp '[' exp ']' | exp '.' ID

    exp : NUMERAL
        | var
        | '(' exp ')'
        | call
        | exp AS type
        | NEW type [ '[' exp ']' ]
        | '-' exp
        | exp '+' exp
        | exp '-' exp
        | exp '*' exp
        | exp '/' exp
        | cond '?' exp ':' exp

    cond :  '(' cond ')'
        | exp '==' exp
        | exp '~=' exp
        | exp '<=' exp
        | exp '>=' exp
        | exp '<' exp
        | exp '>' exp
        | '!' cond
        | cond '&&' cond
        | cond '||' cond

    call : ID '(' explist ')'

    explist : [ exp { ',' exp } ]

    Comentarios::

    iniciam com # ate o fim da linha

"""

from os import path

class TipoToken:
    OPENCOCH = (1, '[')
    CLOSECOCH = (2, ']')
    ATRIB = (3, '=')
    OPENCHAVE = (4, '{')
    CLOSECHAVE = (5, '}')
    PTOVIRG = (6, ';')
    DOISPTO = (7, ':')
    OPENPAR = (8, '(')
    CLOSEPAR = (9, ')')
    IF = (10, 'if')
    ELSE = (11, 'else')
    RETURN = (12, 'return')
    FUNCTION = (13, 'function')
    TYPE = (14, 'type')
    VAR = (15, 'var')
    WHILE = (16, 'while')
    ARROBA = (17, '@')
    CONVERT = (18, 'as')
    NEW = (19, 'new')
    INT = (20, 'int')
    FLOAT = (21, 'float')
    ID = (22, 'id')
    ADD = (23, '+')
    MULT = (24, '*')
    SUB = (25, '-')
    DIVI = (26, '/')
    COND = (26, '?')
    COMPARA = (28, '==')
    DIFER = (29, '~=')
    MENORIQ = (30, '<=')
    MAIORIQ = (31, '>=')
    MENORQ = (32, '<')
    MAIORQ = (33, '>')
    NEGACAO = (34, '!')
    AND = (35, '&&')
    OR = (36, '||')
    VIRG = (37, ',')
    NUM = (38, 'numero')
    STRUCT = (39, 'struct')
    ERROR = (39, 'erro')
    FIMARQ = (40, '$')

class Token:
    def __init__(self, tipo, lexema):
        self.tipo = tipo
        (const, msg) = tipo
        self.const = const
        self.msg = msg
        self.lexema = lexema

class Lexico:
    # dicionario de palavras reservadas
    reservadas = {'as': TipoToken.CONVERT,
                  'else': TipoToken.ELSE,
                  'function': TipoToken.FUNCTION,
                  'if': TipoToken.IF,
                  'new': TipoToken.NEW,
                  'return': TipoToken.RETURN,
                  'type': TipoToken.TYPE,
                  'var': TipoToken.VAR,
                  'while': TipoToken.WHILE
                  }

    def __init__(self, nomeArquivo):
        self.nomeArquivo = nomeArquivo
        self.arquivo = None
        # fila de caracteres 'deslidos' pelo ungetChar
        self.buffer = ''

    def abreArquivo(self):
        if not self.arquivo is None:
            print('ERRO: Arquivo ja aberto')
            quit()
        elif path.exists(self.nomeArquivo):
            self.arquivo = open(self.nomeArquivo, "r")
        else:
            print('ERRO: Arquivo "%s" inexistente.' % self.nomeArquivo)
            quit()

    def fechaArquivo(self):
        if self.arquivo is None:
            print('ERRO: Nao ha arquivo aberto')
            quit()
        else:
            self.arquivo.close()

    def getChar(self):
        if self.arquivo is None:
            print('ERRO: Nao ha arquivo aberto')
            quit()
        elif len(self.buffer) > 0:
            c = self.buffer[0]
            self.buffer = self.buffer[1:]
            return c
        else:
            c = self.arquivo.read(1)
            # se nao foi eof, pelo menos um car foi lido
            # senao len(c) == 0
            if len(c) == 0:
                return None
            return c

    def ungetChar(self, c):
        if not c is None:
            self.buffer = self.buffer + c

    def getAteTokenNulo(self):
        lexema = ''
        car = None
        while(True):
            lexema = lexema + car
            if car is None or (not car.isdigit()):
                # terminou o numero
                self.ungetChar(car)
                return lexema

    def getToken(self):
        operadores = {'[', ']', '}', '{', ':', ';', '+', '*', '(', ')', ',', '=', '/', '-', '~', '!', '|', '@', '&', '<', '>', '?'}
        lexema = ''
        estado = 1
        car = None
        while (True):
            if estado == 1:
                # estado inicial que faz primeira classificacao
                car = self.getChar()
                if car is None:
                    return Token(TipoToken.FIMARQ, '<eof>')
                elif car in {' ', '\t', '\n'}:
                    pass
                elif car.isalpha():
                    estado = 2 # caracter
                elif car.isdigit():
                    estado = 3 # digito
                elif car in operadores:
                    estado = 4
                elif car == '#':
                    estado = 5
                else:
                    return Token(TipoToken.ERROR, '<' + car + '>')
            elif estado == 2:
                # estado que trata nomes (identificadores ou palavras reservadas)
                lexema = lexema + car
                car = self.getChar()
                if car is None or (not car.isalnum()):
                    # terminou o nome
                    self.ungetChar(car)
                    if lexema in Lexico.reservadas:
                        return Token(Lexico.reservadas[lexema], lexema)
                    else:
                        return Token(TipoToken.ID, lexema)
            elif estado == 3:
                lexema = lexema + car
                car = self.getChar()
                # estado que trata numero hexadecimal
                if car == 'x':
                   lexema = lexema + self.getAteTokenNulo() # busca o restante do hexadecimal
                # estado que trata numeros
                if car is None or (not car.isdigit()) or car == '.':
                    # terminou o numero
                    self.ungetChar(car)
                    return Token(TipoToken.NUM, lexema)
            elif estado == 4:
                # estado que trata outros tokens primitivos comuns
                lexema = lexema + car
                if car == '=':
                    car = self.getChar()
                    if car == '=':
                        lexema = lexema + car
                        return Token(TipoToken.COMPARA, lexema)
                    elif car is None :
                        self.ungetChar(car)
                        return Token(TipoToken.ATRIB, lexema)
                    else:
                        return Token(TipoToken.ERROR, '<' + car + '>')
                elif car == ';':
                    return Token(TipoToken.PTOVIRG, lexema)
                elif car == ':':
                    return Token(TipoToken.DOISPTO, lexema)
                elif car == '[':
                    return Token(TipoToken.OPENCOCH, lexema)
                elif car == ']':
                    return Token(TipoToken.CLOSECOCH, lexema)
                elif car == '{':
                    return Token(TipoToken.OPENCHAVE, lexema)
                elif car == '}':
                    return Token(TipoToken.CLOSECHAVE, lexema)
                elif car == '+':
                    return Token(TipoToken.ADD, lexema)
                elif car == '-':
                    return Token(TipoToken.SUB, lexema)
                elif car == '/':
                    return Token(TipoToken.DIVI, lexema)
                elif car == '*':
                    return Token(TipoToken.MULT, lexema)
                elif car == '?':
                    return Token(TipoToken.COND, lexema)
                elif car == '(':
                    return Token(TipoToken.OPENPAR, lexema)
                elif car == ')':
                    return Token(TipoToken.CLOSEPAR, lexema)
                elif car == '@':
                    return Token(TipoToken.ARROBA, lexema)
                elif car == '!':
                    return Token(TipoToken.NEGACAO, lexema)
                elif car == ',':
                    return Token(TipoToken.VIRG, lexema)
                elif car == '<':
                    car = self.getChar()
                    if car == '=': # verifica menor igual (<=)
                        lexema = lexema + car
                        return Token(TipoToken.MENORIQ, lexema)
                    elif car is None:
                        self.ungetChar(car)
                        return Token(TipoToken.MENORQ, lexema)
                    else:
                        return Token(TipoToken.ERROR, '<' + car + '>')
                elif car == '>':
                    car = self.getChar()
                    if car == '=': # verifica maior igual (>=)
                        lexema = lexema + car
                        return Token(TipoToken.MAIORIQ, lexema)
                    elif car is None:
                        self.ungetChar(car)
                        return Token(TipoToken.MAIORQ, lexema)
                    else:
                        return Token(TipoToken.ERROR, '<' + car + '>')
                elif car == '~':
                    car = self.getChar()
                    if car == '=':  # verifica diferente (~=)
                        lexema = lexema + car
                        return Token(TipoToken.DIFER, lexema)
                    else:
                        return Token(TipoToken.ERROR, '<' + car + '>')
                elif car == '&':
                    car = self.getChar()
                    if car == '&':  # verifica oprerador de and (&&)
                        lexema = lexema + car
                        return Token(TipoToken.AND, lexema)
                    else:
                        return Token(TipoToken.ERROR, '<' + car + '>')
                elif car == '|':
                    car = self.getChar()
                    if car == '|':  # verifica operador de or (||)
                        lexema = lexema + car
                        return Token(TipoToken.OR, lexema)
                    else:
                        return Token(TipoToken.ERROR, '<' + car + '>')
            elif estado == 5:
                # consumindo comentario
                while (not car is None) and (car != '\n'):
                    car = self.getChar()
                estado = 1


if __name__== "__main__":

   #nome = input("Entre com o nome do arquivo: ")
   nome = 'exemplo.toy'
   lex = Lexico(nome)
   lex.abreArquivo()

   while(True):
       token = lex.getToken()
       print("token= %s , lexema= (%s)" % (token.msg, token.lexema))
       if token.const == TipoToken.FIMARQ[0]:
           break
   lex.fechaArquivo()