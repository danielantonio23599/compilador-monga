
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
    IF = (10, 'IF')
    ELSE = (11, 'ELSE')
    RETURN = (12, 'RETURN')
    FUNCTION = (13, 'FUNCTION')
    TYPE = (14, 'type')
    VAR = (15, 'VAR')
    WHILE = (16, 'WHILE')
    PRINT = (17, '@')
    CONVERT = (18, 'as')
    NEW = (19, 'new')
    PORCEN = (20, '%')
    INT = (21, 'int')
    ID = (22, 'id')
    ADD = (23, '+')
    MULT = (24, '*')
    SUB = (25, '-')
    DIVI = (26, '/')
    FLOAT = (27, 'float')
    COMPARA = (28, '==')
    DIFER = (29, '!=')
    MENORIQ = (30, '<=')
    MAIORIQ = (31, '>=')
    MENORQ = (32, '<')
    MAIORQ = (33, '>')
    NEGACAO = (34, '!')
    AND = (35, '&&')
    OR = (36, '||')
    VIRG = (37, ',')
    NUM = (38, 'numero')
    ERROR = (39, 'erro')
    FIMARQ = (40, '$')
    PONTO = (41, '.')

class Token:
    def __init__(self, tipo, lexema, linha):
        self.tipo = tipo
        (const, msg) = tipo
        self.const = const
        self.msg = msg
        self.lexema = lexema
        self.linha = linha

class Lexico:
    # dicionario de palavras reservadas
    reservadas = {'as': TipoToken.CONVERT,
                  'ELSE': TipoToken.ELSE,
                  'IF': TipoToken.IF,
                  'new': TipoToken.NEW,
                  'RETURN': TipoToken.RETURN,
                  'VAR': TipoToken.VAR,
                  'int': TipoToken.INT,
                  'float': TipoToken.FLOAT,
                  'FUNCTION': TipoToken.FUNCTION,
                  'WHILE': TipoToken.WHILE
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
            # fila de caracteres 'deslidos' pelo ungetChar
            self.buffer = ''
            self.linha = 1
        else:
            print('ERRO: Arquivo "%s" inexistente.' % self.nomeArquivo)
            quit()

    def fechaArquivo(self):
        if self.arquivo is None:
            print('ERRO: Nao ha arquivo aberto')
            quit()
        else:
            self.arquivo.close()

    def getCharIs(self):
        c = self.getChar()
        if c == ' ':
           c = self.getCharIs()
        else:  return c

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
        operadores = {'[', ']', '}', '{', ':', '.', ';', '+', '*', '(', ')', ',', '=', '/', '-', '~', '!', '|', '@', '&', '<', '>', '?'}
        lexema = ''
        estado = 1
        car = None
        while (True):
            if estado == 1:
                # estado inicial que faz primeira classificacao
                car = self.getChar()
                if car is None:
                    return Token(TipoToken.FIMARQ, '<eof>', self.linha)
                elif car in {' ', '\t', '\n'}:
                    if car == '\n':
                        self.linha = self.linha + 1
                elif car.isalpha():
                    estado = 2 # caracter
                elif car.isdigit():
                    estado = 3 # digito
                elif car in operadores:
                    estado = 4
                elif car == '#':
                    estado = 5
                else:
                    return Token(TipoToken.ERROR, '<' + car + '>', self.linha)
            elif estado == 2:
                # estado que trata nomes (identificadores ou palavras reservadas)
                lexema = lexema + car
                car = self.getChar()
                if car is None or (not car.isalnum()):
                    # terminou o nome
                    self.ungetChar(car)
                    if lexema in Lexico.reservadas:
                        if lexema == 'int' or lexema == 'float' :
                            return Token(TipoToken.TYPE, lexema, self.linha)
                        return Token(Lexico.reservadas[lexema], lexema, self.linha)
                    else:
                        return Token(TipoToken.ID, lexema, self.linha)
            elif estado == 3:
                lexema = lexema + car
                car = self.getChar()
                # estado que trata numero hexadecimal
                if car == 'x':
                   lexema = lexema + self.getAteTokenNulo() # busca o restante do hexadecimal
                # estado que trata numeros
                if car is None or (not car.isdigit()) and not car == '.':
                    # terminou o numero
                    self.ungetChar(car)
                    return Token(TipoToken.NUM, lexema, self.linha)
            elif estado == 4:
                # estado que trata outros tokens primitivos comuns
                lexema = lexema + car
                if car == '=':
                    car = self.getChar()
                    if car == '=':
                        lexema = lexema + car
                        return Token(TipoToken.COMPARA, lexema, self.linha)
                    elif car is None or car == ' ' :
                        self.ungetChar(car)
                        return Token(TipoToken.ATRIB, lexema, self.linha)
                    else:
                        return Token(TipoToken.ERROR, '<' + car + '>', self.linha)
                elif car == ';':
                    return Token(TipoToken.PTOVIRG, lexema, self.linha)
                elif car == ':':
                    return Token(TipoToken.DOISPTO, lexema, self.linha)
                elif car == '.':
                    return Token(TipoToken.PONTO, lexema, self.linha)
                elif car == '[':
                    return Token(TipoToken.OPENCOCH, lexema, self.linha)
                elif car == ']':
                    return Token(TipoToken.CLOSECOCH, lexema, self.linha)
                elif car == '{':
                    return Token(TipoToken.OPENCHAVE, lexema, self.linha)
                elif car == '}':
                    return Token(TipoToken.CLOSECHAVE, lexema, self.linha)
                elif car == '+':
                    return Token(TipoToken.ADD, lexema, self.linha)
                elif car == '-':
                    return Token(TipoToken.SUB, lexema, self.linha)
                elif car == '/':
                    return Token(TipoToken.DIVI, lexema, self.linha)
                elif car == '*':
                    return Token(TipoToken.MULT, lexema, self.linha)
                elif car == '%':
                    return Token(TipoToken.PORCEN, lexema, self.linha)
                elif car == '(':
                    return Token(TipoToken.OPENPAR, lexema, self.linha)
                elif car == ')':
                    return Token(TipoToken.CLOSEPAR, lexema, self.linha)
                elif car == '@':
                    return Token(TipoToken.PRINT, lexema, self.linha)
                elif car == '!':
                    car = self.getChar()
                    if car == '=': # verifica menor igual (!=)
                        lexema = lexema + car
                        return Token(TipoToken.DIFER, lexema, self.linha)
                    elif car == ' ':
                        return Token(TipoToken.NEGACAO, lexema, self.linha)
                    else:
                        return Token(TipoToken.ERROR, '<' + car + '>', self.linha)
                elif car == ',':
                    return Token(TipoToken.VIRG, lexema, self.linha)
                elif car == '<':
                    car = self.getChar()
                    if car == '=': # verifica menor igual (<=)
                        lexema = lexema + car
                        return Token(TipoToken.MENORIQ, lexema, self.linha)
                    elif car == ' ':
                        return Token(TipoToken.MENORQ, lexema, self.linha)
                    else:
                        return Token(TipoToken.ERROR, '<' + car + '>', self.linha)
                elif car == '>':
                    car = self.getChar()
                    if car == '=': # verifica maior igual (>=)
                        lexema = lexema + car
                        return Token(TipoToken.MAIORIQ, lexema, self.linha)
                    elif car == ' ':
                        return Token(TipoToken.MAIORQ, lexema, self.linha)
                    else:
                        return Token(TipoToken.ERROR, '<' + car + '>', self.linha)
                elif car == '~':
                    car = self.getChar()
                    if car == '=':  # verifica diferente (~=)
                        lexema = lexema + car
                        return Token(TipoToken.DIFER, lexema, self.linha)
                    else:
                        return Token(TipoToken.ERROR, '<' + car + '>', self.linha)
                elif car == '&':
                    car = self.getChar()
                    if car == '&':  # verifica oprerador de and (&&)
                        lexema = lexema + car
                        return Token(TipoToken.AND, lexema, self.linha)
                    else:
                        return Token(TipoToken.ERROR, '<' + car + '>', self.linha)
                elif car == '|':
                    car = self.getChar()
                    if car == '|':  # verifica operador de or (||)
                        lexema = lexema + car
                        return Token(TipoToken.OR, lexema, self.linha)
                    else:
                        return Token(TipoToken.ERROR, '<' + car + '>', self.linha)
            elif estado == 5:
                # consumindo comentario
                while (not car is None) and (car != '\n'):
                    car = self.getChar()
                self.ungetChar(car)
                estado = 1


if __name__== "__main__":

   #nome = input("Entre com o nome do arquivo: ")
   nome = 'Teste/array.monga'
   lex = Lexico(nome)
   lex.abreArquivo()

   while(True):
       token = lex.getToken()
       print("token= %s , lexema= (%s)" % (token.msg, token.lexema))
       if token.const == TipoToken.FIMARQ[0]:
           break
   lex.fechaArquivo()