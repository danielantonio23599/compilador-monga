from sintatico import Sintatico
from lexico import Lexico

if __name__ == '__main__':
    print('Tradutor MONGA \n')

    nome = input("Entre com o nome do arquivo: ")
    pre = nome.split(' ')
    if pre[0] == '-t':
        lexico = Lexico('Teste/'+pre[1])
        lexico.gravaArquivo()
        print('Tabela de palavras reservadas exportada com sucesso!')
    else:
        parser = Sintatico()
        ok = parser.traduz('Teste/'+nome)
        if ok:
            print("Arquivo sintaticamente correto.")

