from lexico import TipoToken as tt, Token, Lexico
from tabela import TabelaSimbolos
from semantico import Semantico

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
            self.deuErro = False
            self.lex = Lexico(nomeArquivo)
            self.lex.abreArquivo()
            self.tokenAtual = self.lex.getToken()

            # inicio reconhecimento do fonte
            self.tabsimb = TabelaSimbolos()
            self.semantico = Semantico()
            self.program()
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
            # quit()
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

    def salvaLexema(self):
        return self.tokenAtual.lexema

    def salvaLinha(self):
        return self.tokenAtual.linha

    def testaVarNaoDeclarada(self, var, linha):
        if not self.tabsimb.existeIdent(var):
            self.deuErro = True
            msg = "Variavel " + var + " nao declarada."
            self.semantico.erroSemantico(msg, linha)
    def testaIndiceTipoInt(self, linha, indice):
        if not type(indice) == int:
            self.deuErro = True
            msg = "indice do vetor " + indice + " com TYPE diferente de int."
            self.semantico.erroSemantico(msg, linha)


    ##################################################################
    # Segue uma funcao para cada variavel da gramatica
    ##################################################################

    def program(self):
        self.definition()
        if self.tokenEsperadoEncontrado(tt.FIMARQ):
            pass
        else:
            self.program()

    def definition(self):
        if self.tokenEsperadoEncontrado(tt.VAR):
          self.variable()
        elif self.tokenEsperadoEncontrado(tt.FUNCTION):
            self.function()

    def variable(self):
        self.consome(tt.VAR)
        var = self.salvaLexema()
        self.consome(tt.ID)
        self.consome(tt.DOISPTO)
        tipo = self.type()
        self.consome(tt.TYPE)
        self.consome(tt.PTOVIRG)
        if not self.tabsimb.existeIdent(var):
            if tipo == 'int':
                self.tabsimb.declaraIdent(var, 0)
            elif tipo == 'float':
                self.tabsimb.declaraIdent(var, 0.0)
            else: self.tabsimb.declaraIdent(var, None);

    def function(self):
        self.consome(tt.FUNCTION)
        var = self.salvaLexema()
        self.consome(tt.ID)
        self.consome(tt.OPENPAR)
        self.parameters()
        self.consome(tt.CLOSEPAR)
        if self.tokenEsperadoEncontrado(tt.DOISPTO):
            self.consome(tt.DOISPTO)
            tipo = self.type()
            self.consome(tt.TYPE)
            if not self.tabsimb.existeIdent(var):
                if tipo == 'int':
                    self.tabsimb.declaraIdent(var, 0)
                elif tipo == 'float':
                    self.tabsimb.declaraIdent(var, 0.0)
                else:
                    self.tabsimb.declaraIdent(var, None)
        self.block()

    def parameters(self):
        if self.tokenEsperadoEncontrado(tt.ID):
            self.parameter()
            self.consomeParameter()

    def consomeParameter(self):
        if self.tokenEsperadoEncontrado(tt.VIRG):
            self.consome(tt.VIRG)
            self.parameter()
            self.consomeParameter()

    def parameter(self):
        var = self.salvaLexema()
        self.consome(tt.ID)
        self.consome(tt.DOISPTO)
        tipo = self.type()
        self.consome(tt.TYPE)
        if not self.tabsimb.existeIdent(var):
            if tipo == 'int':
                self.tabsimb.declaraIdent(var, 0)
            elif tipo == 'float':
                self.tabsimb.declaraIdent(var, 0.0)
            else:
                self.tabsimb.declaraIdent(var, None)

    def block(self):
        self.consome(tt.OPENCHAVE)
        self.consomeVAR()
        self.consomeStatament()
        self.consome(tt.CLOSECHAVE)

    def consomeVAR(self):
        if self.tokenEsperadoEncontrado(tt.VAR):
            self.variable()
            self.consomeVAR()
    def consomeStatament(self):
        if not self.tokenEsperadoEncontrado(tt.CLOSECHAVE):
            self.statement()
            self.consomeStatament()

    def statement(self):
        if self.tokenEsperadoEncontrado(tt.IF):
            self.consome(tt.IF)
            self.exp()
            self.block()
            self.consomeElse()
        elif self.tokenEsperadoEncontrado(tt.WHILE):
            self.consome(tt.WHILE)
            self.exp()
            self.block()
        elif self.tokenEsperadoEncontrado(tt.RETURN):
            self.consome(tt.RETURN)
            self.consomeExp()
            self.consome(tt.PTOVIRG)
        elif self.tokenEsperadoEncontrado(tt.ID):
            var = self.salvaLexema()
            linha = self.salvaLinha()
            self.consome(tt.ID)
            if self.tokenEsperadoEncontrado(tt.OPENPAR):
                self.call()
            elif self.tokenEsperadoEncontrado(tt.ATRIB):
                self.testaVarNaoDeclarada(var,linha)
                valor = self.exp()
                if not self.tabsimb.existeIdent(var):
                    self.tabsimb.declaraIdent(var, valor)
                else:
                    self.tabsimb.atribuiValor(var, valor)
            elif self.tokenEsperadoEncontrado(tt.OPENCOCH):
                self.consome(tt.OPENCOCH)
                var = self.exp()
                self.testaIndiceTipoInt(linha,var)
                self.consome(tt.CLOSECOCH)
                self.consome(tt.ATRIB)
                self.exp()
            elif self.tokenEsperadoEncontrado(tt.PONTO):
                self.consome(tt.PONTO)
                var = self.salvaLexema()
                linha = self.salvaLinha()
                self.testaVarNaoDeclarada(var,linha)
                self.consome(tt.ID)
                self.consome(tt.ATRIB)
                self.exp()
            self.consome(tt.PTOVIRG)
        elif self.tokenEsperadoEncontrado(tt.PRINT):
            self.consome(tt.PRINT)
            var = self.exp()
            print(var)
            self.consome(tt.PTOVIRG)
        elif self.tokenEsperadoEncontrado(tt.OPENCHAVE):
            self.block()
        else:
            var = self.var()
            self.consome(tt.ATRIB)
            valor = self.exp()
            self.consome(tt.PTOVIRG)
            if not self.tabsimb.existeIdent(var):
                self.tabsimb.declaraIdent(var, valor)
            else:
                self.tabsimb.atribuiValor(var, valor)

    def pegaVarExistente(self):
        var = self.salvaLexema()
        linha = self.salvaLinha()
        self.consome(tt.ID)
        self.testaVarNaoDeclarada(var, linha)
        valor = self.tabsimb.pegaValor(var)
        return valor

    #var : ID | exp '[' exp ']' | exp '.' ID retona o valor de ID
    def var(self):
        if self.tokenEsperadoEncontrado(tt.ID):
            return self.pegaVarExistente()
        else:
            self.exp()
            if self.tokenEsperadoEncontrado(tt.OPENCOCH):
                self.consome(tt.OPENCOCH)
                self.exp()
                self.consome(tt.CLOSECOCH)
            else:
                self.consome(tt.PONTO)
                var = self.salvaLexema()
                linha = self.salvaLinha()
                self.consome(tt.ID)
                self.testaVarNaoDeclarada(var, linha)
                valor = self.tabsimb.pegaValor(var)
                return valor

    def consomeElse(self):
        if self.tokenEsperadoEncontrado(tt.ELSE):
            self.consome(tt.ELSE)
            self.block()
            self.consomeElse()

    def type(self):
        if self.tokenEsperadoEncontrado( tt.ID ):
            self.consome(tt.ID)
        elif self.tokenEsperadoEncontrado(tt.TYPE):
            return self.tokenAtual.lexema

    def consomeExp(self):
        if not self.tokenEsperadoEncontrado(tt.PTOVIRG):
            return self.exp()

    # <exp> -> <atrib> retona valor, 1 ,0
    def exp(self):
       return self.atrib()

    # <atrib> -> <or> <restoAtrib> retorna valor
    def atrib(self):
        var = self.OR()
        return self.restoAtrib(var)

    def OR(self):
        var = self.AND(1)
        return self.restoOR(var)

    def AND(self, val):
        valor = self.NOT(val)
        return self.restoAnd(valor)

    def add(self):
        val = self.mult()
        return self.restoAdd(val)

    def restoAdd(self, valor):
        if self.tokenEsperadoEncontrado(tt.ADD):
            self.consome(tt.ADD)
            valor2 = self.mult()
            return self.restoAdd(valor + valor2)
        elif self.tokenEsperadoEncontrado(tt.SUB):
            self.consome(tt.SUB)
            valor2 = self.mult()
            return  self.restoAdd(valor - valor2)
        else: return valor

    def restoOR(self, var):
        if self.tokenEsperadoEncontrado(tt.OR):
            self.consome(tt.OR)
            var2 = self.AND(1)
            var2 = self.restoOR(var2)
            if (var + var2) > 0:
                return 1
            else:
                return 0
        else: return var


    def restoAnd(self, val):
        if self.tokenEsperadoEncontrado(tt.AND):
            self.consome(tt.AND)
            val2 = self.NOT(1)
            return self.restoAnd(val2 * val)
        else:
            return val


    #retona o valor negado, na qantidade de vezes correta, caso não encontre retona o valor inicial
    def NOT(self, val):
        if self.tokenEsperadoEncontrado(tt.NEGACAO):
            self.consome(tt.NEGACAO)
            if val == 1:
                return self.NOT(0)
            else: return self.NOT(1)
        else: return self.rel()

    def rel(self):
        val2 = self.add()
        return self.restoRel(val2)

    def restoRel(self, val):
        if self.tokenEsperadoEncontrado(tt.COMPARA):
            self.consome(tt.COMPARA)
            val2 = self.add()
            if val == val2:
                return 1
            else: return 0
        elif self.tokenEsperadoEncontrado(tt.DIFER):
            self.consome(tt.DIFER)
            val2 = self.add()
            if val != val2:
                return 1
            else:
                return 0
        elif self.tokenEsperadoEncontrado(tt.MENORQ):
            self.consome(tt.MENORQ)
            val2 = self.add()
            if val < val2:
                return 1
            else:
                return 0
        elif self.tokenEsperadoEncontrado(tt.MENORIQ):
            self.consome(tt.MENORIQ)
            val2 = self.add()
            if val <= val2:
                return 1
            else:
                return 0
        elif self.tokenEsperadoEncontrado(tt.MAIORQ):
            self.consome(tt.MAIORQ)
            val2 = self.add()
            if val > val2:
                return 1
            else:
                return 0
        elif self.tokenEsperadoEncontrado(tt.MAIORIQ):
            self.consome(tt.MAIORIQ)
            val2 = self.add()
            if val >= val2:
                return 1
            else:
                return 0
        else: return val

    #<mult> -> <uno> <restoMult> retorna valor
    def mult(self):
        val1 = self.uno(0)
        return self.restoMult(val1)

    # <restoMult> -> '*' <uno> <restoMult>
    #             |  '/' <uno> <restoMult>
    #             |  '%' <uno> <restoMult> | lambda
    def restoMult(self, val):
        if self.tokenEsperadoEncontrado(tt.MULT):
            self.consome(tt.MULT)
            val2 = self.uno(0)
            return self.restoMult(val * val2)
        elif self.tokenEsperadoEncontrado(tt.DIVI):
            self.consome(tt.DIVI)
            val2 = self.uno(0)
            return self.restoMult(val / val2)
        elif self.tokenEsperadoEncontrado(tt.PORCEN):
            self.consome(tt.PORCEN)
            val2 = self.uno(0)
            return self.restoMult(val % val2)
        else: return val

    #<uno> -> '+' <uno> | '-' <uno> | <fator>
    def uno(self, valor):
        if self.tokenEsperadoEncontrado(tt.ADD):
            self.consome(tt.ADD)
            valor + self.uno(valor)
            return valor
        elif self.tokenEsperadoEncontrado(tt.SUB):
            self.consome(tt.SUB)
            valor - self.uno(valor)
            return valor
        else:
            return self.fator()

    #<fator> -> 'NUMint' | 'NUMfloat' | '(' <atrib> ')'
    def fator(self):
        if self.tokenEsperadoEncontrado(tt.OPENPAR):
            self.consome(tt.OPENPAR)
            valor = self.atrib()
            self.consome(tt.CLOSEPAR)
            return valor
        elif self.tokenEsperadoEncontrado(tt.NUM):
            num = self.salvaLexema()
            self.consome(tt.NUM)
            if num.find('.')>0 :
                return float(num)
            else:
                return int(num)
        elif self.tokenEsperadoEncontrado(tt.ID):
            return self.pegaVarExistente()


    def restoAtrib(self, val):
        if self.tokenEsperadoEncontrado(tt.ATRIB):
            self.consome(tt.ATRIB)
            val2 = self.atrib()
            self.tabsimb.atribuiValor(val, val2)
            return val2
        else: return val

    #explist : [ exp { ',' exp } ]
    def explist(self):
        if self.tokenEsperadoEncontrado( tt.CLOSEPAR ):
            pass
        else:
            self.exps()

    def exps(self):
        self.exp()
        if self.tokenEsperadoEncontrado(tt.VIRG):
            self.consome(tt.VIRG)
            self.exps()

    #call : ID '(' explist ')'
    def call(self):
        val = self.salvaLexema()
        linha = self.salvaLinha()
        self.testaVarNaoDeclarada(val, linha)
        self.consome(tt.ID)
        self.consome(tt.OPENPAR)
        self.explist()
        self.consome(tt.CLOSEPAR)

if __name__== "__main__":

   nome = 'Teste/exemplo.monga'
   parser = Sintatico()
   parser.traduz(nome)
