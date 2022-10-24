from sintatico import Sintatico

if __name__ == '__main__':
    print('Tradutor Toy \n')

    nome = input("Entre com o nome do arquivo: ")

    parser = Sintatico()
    ok = parser.traduz(nome)
    if ok:
        print("Arquivo sintaticamente correto.")

