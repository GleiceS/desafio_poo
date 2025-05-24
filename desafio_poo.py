from abc import ABC, abstractmethod
from datetime import datetime

class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass

    @property
    def registrar(self, conta):
        pass

class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor
        
    def registrar(self, conta):
        if conta.sacar(self.valor):
            conta.extrato.adicionar_transacao(self)

class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor
        
    def registrar(self, conta):
        if conta.deposito(self.valor):
            conta.extrato.adicionar_transacao(self)


class Extrato:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes
    
    def adicionar_transacao(self, transacao):
        self._transacoes.append({
            "operacao": transacao.__class__.__name__,
            "valor": transacao.valor,
            "data": datetime.now().strftime("%d%m%Y %H:%M:%S")

        })

class Conta:
    def __init__(self, usuario, numero_conta):
        self._saldo = 0.0
        self._usuario = usuario
        self._numero_conta = numero_conta
        self._agencia = "0001"
        self._extrato = Extrato()

    @classmethod
    def nova_conta(cls, usuario, numero_conta):
        return cls(usuario, numero_conta)
    
    @property
    def saldo(self):
        return self._saldo
    
    @property
    def usuario(self):
        return self._usuario
    
    @property
    def numero_conta(self):
        return self._numero_conta
    
    @property
    def agencia(self):
        return self._agencia
    
    @property
    def extrato(self):
        return self._extrato
    
    def sacar(self, valor):
        if valor <= 0:
            print("\n❌ Valor inválido!")
            return False

        if valor > self._saldo:
            print("\n❌ Saldo insuficiente.")
            return False

        self._saldo -= valor
        print("\n✅ Saque realizado com sucesso!")
        
        return True
    
    def deposito(self, valor):
        if valor <= 0:
            print("\n❌ Valor inválido!")
            return False

        self._saldo += valor
        print(f"\n✅ Depósito de R$ {valor:.2f} realizado com sucesso!")
        return True
    
class ContaCorrente(Conta):
    def __init__(self, usuario, numero_conta, limite = 500, limite_saques = 3):
        super().__init__(usuario, numero_conta)
        self._limite = limite
        self._limite_saques = limite_saques

    def sacar(self, valor):
        saques_realizados = 0
        for transacao in self.extrato.transacoes:
            if transacao ["operacao"] =="Saque":
                saques_realizados += 1 

        if saques_realizados >= self._limite_saques:
            print("\n❌ Limite de saques excedido.")
            return False
        
        if valor > self._limite:
            print("\n❌ Valor excede o limite permitido por saque.")
            return False
        

        return super().sacar(valor)
    

    def __str__(self):
        return f"Titular: {self.usuario.nome}\nAgência: {self.agencia}\nConta Corrente: {self.numero_conta}"
    


class Usuario:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, numero_conta, transacao):
        transacao.registrar(numero_conta)

    def adicionar_conta(self, numero_conta):
        self.contas.append(numero_conta)


class PessoaFisica(Usuario):
    def __init__(self, cpf, nome, data_nascimento, endereco):
        super().__init__(endereco)
        self.cpf = cpf
        self.nome = nome
        self.data_nascimento = data_nascimento


def exibir_menu():
    sumario = """
    ============= MENU =============
    [d] Depositar
    [s] Sacar
    [e] Extrato
    [u] Novo Usuário
    [c] Nova Conta
    [l] Listar Contas
    [f] Finalizar
    ================================
    => """
    return input(sumario).strip().lower()


def filtrar_usuario(cpf, usuarios):
    for novo_usuario in usuarios:
        if novo_usuario.cpf == cpf:
            return novo_usuario
        
    return None

def criar_usuario(usuarios): #talvez seja Usuario, maiúsculo
    cpf = input("Por favor, informe seu CPF (somente números): ").strip()
    novo_usuario = filtrar_usuario(cpf, usuarios)

    if novo_usuario:
        print("\n❌ Já existe um usuário com esse CPF!")

    nome = input("Nome Completo: ").strip()
    data_nascimento = input("Data de Nascimento (dd/mm/AAAA): ").strip()
    endereco = input("Endereco Completo (logradouro, nº - bairro - cidade/UF): ").strip()

    novo_usuario = PessoaFisica(cpf, nome, data_nascimento, endereco)
    usuarios.append(novo_usuario)

    primeiro_nome = nome.split()[0]
    print(f"\n✅ Usuário {primeiro_nome} cadastrado com sucesso, seja bem vinda(o)!")

    
def criar_conta(usuarios, contas):
    cpf = input("Informe o CPF (apenas números) do titular da conta: ").strip()
    novo_usuario = filtrar_usuario(cpf, usuarios)

    if not novo_usuario:
        print("\n❌ Usuário não encontrado. Por favor, cadastre-se no nosso sistema.")
        return
    
    numero_conta = len(contas) + 1
    conta = ContaCorrente.nova_conta(novo_usuario, numero_conta)
    novo_usuario.adicionar_conta(conta)
    contas.append(conta)
    print(f"\n✅ Conta Corrente nº {numero_conta} criada com sucesso!")


def listar_contas(contas):
    for conta in contas:
        print("=" * 45)
        print(conta)

def realizar_saque(usuarios):
    cpf = input("\nInforme o CPF do usuario da conta: ")
    usuario = filtrar_usuario(cpf, usuarios)

    if not usuario or not usuario.contas:
        print("\n❌ Usuário ou conta não encontrado. Por favor, cadastre no nosso sistema.")
        return
    
    valor = float(input("\nPor favor, informe o valor para saque: "))
    transacao = Saque(valor)
    usuario.realizar_transacao(usuario.contas[0], transacao)


def realizar_deposito(usuarios):
    cpf = input("\nInforme o CPF do usuario da conta: ")
    usuario = filtrar_usuario(cpf, usuarios)

    if not usuario or not usuario.contas:
        print("\n❌ Usuário ou conta não encontrado. Por favor, cadastre no nosso sistema.")
        return
    
    valor = float(input("\nPor favor, informe o valor para deposito: "))
    transacao = Deposito(valor)
    usuario.realizar_transacao(usuario.contas[0], transacao)

    

def exibir_extrato(usuarios):
    cpf = input("\nInforme o CPF do usuario da conta: ")
    usuario = filtrar_usuario(cpf, usuarios)

    if not usuario or not usuario.contas:
        print("\n❌ Usuário ou conta não encontrado. Por favor, cadastre no nosso sistema.")
        return
    
    conta = usuario.contas[0]
    print("\n=============== EXTRATO ===============")
    for transacao in conta.extrato.transacoes:
        print(f"{transacao['data']} - {transacao['operacao']}: R$ {transacao['valor']:.2f}")
    print(f"\nSaldo: R$ {conta.saldo:.2f}")
    print("=======================================")

def main():
    usuarios = []
    contas = []

    while True:
          
        opcao = exibir_menu()

        if opcao == "s":
            realizar_saque(usuarios)

        elif opcao == "d":
            realizar_deposito(usuarios)

        elif opcao == "e":
            exibir_extrato(usuarios)

        elif opcao == "u":
            criar_usuario(usuarios)

        elif opcao == "c":
            criar_conta(usuarios, contas)

        elif opcao == "l":
            listar_contas(contas)

        elif opcao == "f":
            print("\n✅ Serviço finalizado. Obrigado por usar o sistema!")
            break

        else:
            print("\n❌ Opção inválida!")


main()


        

            

