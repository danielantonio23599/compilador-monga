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

from lexico import TipoToken as tt, Token, Lexico

class Sintatico:

    def __init__(self):
        self.lex = None
        self.tokenAtual = None
        self.deuErro = False
        # campos utilizados no modo panico
        self.modoPanico = False
        self.tokensDeSincronismo = [tt.PTOVIRG, tt.FIMARQ]

    def traduz(self, nomeArquivo):
        if not self.lex is None:
            print('ERRO: Já existe um arquivo sendo processado.')
        else:
            self.lex = Lexico(nomeArquivo)
            self.lex.abreArquivo()
            self.tokenAtual = self.lex.getToken()

            # inicio reconhecimento do fonte
            self.F()
            self.consome( tt.FIMARQ )
            # fim do reconhecimento do fonte

            self.lex.fechaArquivo()
            return not self.deuErro

    def tokenEsperadoEncontrado(self, token):
        (const, msg) = token
        if self.tokenAtual.const == const:
            return True
        else:
            return False

    def consome(self, token):
        if not self.modoPanico and self.tokenEsperadoEncontrado(token):
            # tudo seguindo de acordo
            self.tokenAtual = self.lex.getToken()
        elif not self.modoPanico:
            # agora deu erro, solta msg e entra no modo panico
            self.modoPanico = True
            self.deuErro = True
            (const, msg) = token
            print('ERRO DE SINTAXE [linha %d]: era esperado "%s" mas veio "%s"'
               % (self.tokenAtual.linha, msg, self.tokenAtual.lexema))
            #quit()
            procuraTokenDeSincronismo = True
            while procuraTokenDeSincronismo:
                self.tokenAtual = self.lex.getToken()
                for tk in self.tokensDeSincronismo:
                    (const, msg) = tk
                    if self.tokenAtual.const == const:
                        # tokenAtual eh um token de sincronismo
                        procuraTokenDeSincronismo = False
                        break
        elif self.tokenEsperadoEncontrado(token):
            # chegou no ponto de sincronismo :)
            self.tokenAtual = self.lex.getToken()
            self.modoPanico = False
        else:
            # so continua, consumindo e consumindo...
            pass

    ##################################################################
    # Segue uma funcao para cada variavel da gramatica
    ##################################################################

    def F(self):
        self.C()
        self.Rf()

    def Rf(self):
        if self.tokenEsperadoEncontrado( tt.FIMARQ ):
            pass
        else:
            self.C()
            self.Rf()

    def C(self):
        if self.tokenEsperadoEncontrado( tt.READ ):
            self.R()
        elif self.tokenEsperadoEncontrado( tt.PRINT ):
            self.P()
        else:
            self.A()

    def A(self):
        self.consome( tt.IDENT )
        self.consome( tt.ATRIB )
        self.E()
        self.consome( tt.PTOVIRG )

    def R(self):
        self.consome( tt.READ )
        self.consome( tt.OPENPAR )
        self.consome( tt.IDENT )
        self.consome( tt.CLOSEPAR )
        self.consome( tt.PTOVIRG )

    def P(self):
        self.consome( tt.PRINT )
        self.consome( tt.OPENPAR )
        self.consome( tt.IDENT )
        self.consome( tt.CLOSEPAR )
        self.consome( tt.PTOVIRG )

    def E(self):
        self.M()
        self.Rs()

    def Rs(self):
        if self.tokenEsperadoEncontrado( tt.ADD ):
            self.consome( tt.ADD )
            self.M()
            self.Rs()
        else:
            pass

    def M(self):
        self.Op()
        self.Rm()

    def Rm(self):
        if self.tokenEsperadoEncontrado( tt.MULT ):
            self.consome( tt.MULT )
            self.Op()
            self.Rm()
        else:
            pass

    def Op(self):
        if self.tokenEsperadoEncontrado( tt.OPENPAR ):
            self.consome( tt.OPENPAR )
            self.E()
            self.consome( tt.CLOSEPAR )
        else:
            self.consome( tt.NUM )

if __name__== "__main__":

   nome = 'exemplo.toy'
   parser = Sintatico()
   parser.traduz(nome)
