from sintatico import Sintatico

if __name__ == '__main__':
    print('Tradutor MONGA \n')

    nome = input("Entre com o nome do arquivo: ")
    pre = nome.split(' ')
    if pre[0] == '-t':
        parser = Sintatico()
        ok = parser.traduz('Teste/' + pre[1])
        if ok:
            print("Arquivo sintaticamente correto.")
        export = input("Entre com o nome do arquivo de exportacao: ")
        parser.exportarTabSimbolos('Teste/'+export)
        print('Tabela de simbolos exportada com sucesso!')
    else:
        parser = Sintatico()
        ok = parser.traduz('Teste/'+nome)
        if ok:
            print("Arquivo sintaticamente correto.")

