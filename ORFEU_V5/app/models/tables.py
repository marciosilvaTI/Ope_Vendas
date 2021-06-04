from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from app.models import recuperacao_senha


'''
Não esquecer de remover todos os comentários desnecessários.
    OBS:
    id 1 = Admin
    id 2 = Op. Caixa

NivelAcesso --> Devemos deixar os dois níveis de acessos já criados

Usuario --> Devemos criar o método de resetar a senha para uma senha padrão.
EX: 123@Orfeu



Cliente --> Devemos criar o método de atualizar a data da última compra,
valor dívida, status, cpf, observação (Verificar)

DetalhesVenda --> Devemos criar o método para atualizar o valor_produto


MovimentacaoCaixa --> Devemos criar o método para atualizar
o valor_movimentacao
'''


class NivelAcesso(db.Model):  # OK
    '''
        Essa classe serve para criarmos os níveis de acessos dos usuários,
    ou seja, se ele é um ADMINISTRADOR (Admin) ou OPERADOR DE CAIXA
    (Op. Caixa).
    '''
    __tablename__ = "nivel_acesso"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nivel_acesso = db.Column(db.String(20), nullable=False, unique=True)

    def __init__(self, nivel_acesso):
        self.nivel_acesso = nivel_acesso

    def __repr__(self):
        return "<NivelAcesso %r>" % self.id


class Usuario(db.Model, UserMixin):
    '''
        Essa classe serve para criarmos os usuários que terão acesso
    ao sistema.
    '''
    __tablename__ = "usuario"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(50), nullable=False)
    telefone = db.Column(db.String(11), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    login = db.Column(db.String(25), nullable=False, unique=True)
    senha = db.Column(db.String(128), nullable=False)
    status = db.Column(db.Boolean)
    recuperou_senha = db.Column(db.Boolean)
    inativado = db.Column(db.Boolean)

    id_nivel_acesso_id = db.Column(db.Integer,
                                   db.ForeignKey("nivel_acesso.id"),
                                   nullable=False)
    nivel_acesso = db.relationship('NivelAcesso')

    # Na hora de exibir os níveis de acesso, é necessário trocar o id pelo nome
    nome_nivel_acesso = ""

    # id_nivel_acesso_id não pode ficar como 2, pois pode ser que o id do Op.
    # Caixa não seja 2
    def __init__(self, nome, telefone, email, login, senha,
                 id_nivel_acesso_id=2):  # id 1 = Admin - id 2 = Op. Caixa
        self.nome = nome
        self.telefone = telefone
        self.email = email
        self.login = login
        self.senha = generate_password_hash(senha)
        self.status = True  # True = Desbloqueado - False = Bloqueado.
        self.id_nivel_acesso_id = id_nivel_acesso_id
        # True = Recuperou - False = Não Recuperou.
        self.recuperou_senha = False
        # True = Inativo - False = Ativo.
        self.inativado = False

    '''O método abaixo serve para criptografar a senha do usuário, fazendo com que
    os dados dele estejam mais seguros'''

    def criptografar_senha(self, senha):
        self.senha = generate_password_hash(senha)
        return self.senha

    '''O método abaixo serve para checarmos se a senha informada pelo o
    usuário de fato está correta, pois a função check_password_hash
    consegue descriptograr a senha.'''

    def descriptografar_senha(self, senha):
        return check_password_hash(self.senha, senha)

    # Tratar no front a exibição do status do usuário
    def exibir_nivel_acesso(self):
        if self.id_nivel_acesso_id == 1:
            return 'ADMINISTRADOR'  # TRUE
        return 'OPERADOR DE CAIXA'  # FALSE

    # Tratar no front a exibição do status do usuário
    def verificar_status(self):
        if self.status:
            return 'DESBLOQUEADO'  # TRUE
        return 'BLOQUEADO'  # FALSE

    def verificar_inativado(self):
        if self.inativado:
            return 'INATIVO'
        return 'ATIVO'

    def bloquear_usuario(self):
        self.status = False
        db.session.add(self)
        db.session.commit()
        # return self.verificar_status()

    def desbloquear_usuario(self):
        self.status = True
        db.session.add(self)
        db.session.commit()
        # return self.verificar_status()

    def resetar_usuario(self):
        self.senha = self.criptografar_senha('123@Orfeu')
        db.session.add(self)
        db.session.commit()
        # return self.verificar_status()

    # O método abaixo serve para alterar a senha quando o usuário
    # sabe a senha atual
    def alterar_senha(self, senha_atual, nova_senha):
        if self.descriptografar_senha(senha_atual):
            self.senha = self.criptografar_senha(nova_senha)
            db.session.add(self)
            db.session.commit()
            return 'Senha alterada com sucesso!'
        return 'Senha inválida!'

    # O método abaixo serve para alterar a senha quando o usuário
    # recebe a senha provisória
    def alterar_senha_provisoria(self, senha_provisoria, nova_senha):
        print(self.senha == senha_provisoria)
        if self.senha == senha_provisoria:
            self.senha = self.criptografar_senha(nova_senha)
            db.session.add(self)
            db.session.commit()
            return 'Senha alterada com sucesso!'
        return 'Senha inválida!'

    # O método abaixo nos ajudará a recuperar a senha por e-mail
    def esqueci_senha(self):
        senha_provisoria = recuperacao_senha.gerar_senha_aleatoria()
        self.senha = self.criptografar_senha(senha_provisoria)
        self.recuperou_senha = True
        db.session.add(self)
        db.session.commit()
        return recuperacao_senha.enviar_senha_email(self.email,
                                                    senha_provisoria)

    # O método abaixo muda o recuperou_senha para True, ou seja,
    # estamos dizendo que o usuário recuperou a senha e com isso o sistema
    # redirecionará o usuário para alterar a senha provisória
    def alterar_recuperou_senha(self):
        self.recuperou_senha = False
        db.session.add(self)
        db.session.commit()
        # return self.verificar_status()

    def inativar_usuario(self):
        self.inativado = True
        db.session.add(self)
        db.session.commit()
        # return self.verificar_status()

    def ativar_usuario(self):
        self.inativado = False
        db.session.add(self)
        db.session.commit()
        # return self.verificar_status()

    def serialized(self):
        return {
            'nome': self.nome,
            'id_nivel_acesso_id': self.id_nivel_acesso_id,
            'telefone': self.telefone,
            'email': self.email,
            'login': self.login,
        }

    def __repr__(self):
        return "<User %r>" % self.id


class Cliente(db.Model):
    '''
        Essa classe serve para criarmos os usuários que terão acesso
    ao sistema.
    '''
    __tablename__ = "cliente"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(50), nullable=False)
    telefone = db.Column(db.String(11), nullable=False, unique=True)
    data_pagamento = db.Column(db.DateTime, nullable=False)
    data_ultima_compra = db.Column(db.DateTime)
    valor_divida = db.Column(db.Float(2, 0))
    status = db.Column(db.Boolean)
    cpf = db.Column(db.String(11))
    observacao = db.Column(db.String(50))
    inativado = db.Column(db.Boolean)

    now = datetime.datetime.now()

    def __init__(self, nome, telefone, data_pagamento, cpf=None,
                 observacao=None):
        self.nome = nome
        self.telefone = telefone
        self.data_pagamento = data_pagamento
        self.data_ultima_compra = None
        self.valor_divida = 0
        self.status = True  # True = Pode comprar fiado - False = Não pode.
        self.cpf = cpf
        self.observacao = observacao
        self.inativado = False

    # Tratar no front a exibição do status do usuário
    def verificar_status(self):
        if self.status:
            return '100'  # TRUE
        return '999'  # FALSE

    def verificar_inativado(self):
        if self.inativado:
            return 'INATIVO'
        return 'ATIVO'

    def bloquear_cliente(self):
        self.status = False
        db.session.add(self)
        db.session.commit()
        # return self.verificar_status()

    def desbloquear_cliente(self):
        self.status = True
        db.session.add(self)
        db.session.commit()
        # return self.verificar_status()

    '''
        O método abaixo atualiza a data que o comerciante determinará para
    o cliente efetuar o pagamento da dívida
    '''

    def atualizar_data_pagamento(self, data):
        self.data_pagamento = data
        db.session.add(self)
        db.session.commit()

    '''
        O método abaixo atualizará a data que o cliente realizou
    a última compra.
    '''

    def atualizar_data_ultima_compra(self):
        self.data_ultima_compra = datetime.datetime(year=self.now.year,
                                                    month=self.now.month,
                                                    day=self.now.day,
                                                    hour=self.now.hour,
                                                    minute=self.now.minute,
                                                    second=self.now.second)
        db.session.add(self)
        db.session.commit()

    '''
        O método abaixo aumentará a dívida do cliente sempre que ele
    comprar fiado
    '''

    def aumentar_divida(self, valor):
        self.valor_divida += -(valor)
        db.session.add(self)
        db.session.commit()

    '''
        O método abaixo diminuirá a dívida do cliente sempre que ele
    efetuar um pagamento
    '''

    def diminuir_divida(self, valor):
        self.valor_divida += +(valor)
        db.session.add(self)
        db.session.commit()

    def inativar_cliente(self):
        self.inativado = True
        db.session.add(self)
        db.session.commit()
        # return self.verificar_status()

    def ativar_cliente(self):
        self.inativado = False
        db.session.add(self)
        db.session.commit()

        # return self.verificar_status()

    def serialized(self):
        data_pagamento = str(self.data_pagamento)
        return {
            'nome': self.nome,
            'telefone': self.telefone,
            'data_pagamento': data_pagamento,
            'cpf': self.cpf,
            'observacao': self.observacao,
        }


    def __repr__(self):
        return "<Cliente %r>" % self.id


class Categoria(db.Model):
    __tablename__ = "categoria"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome_categoria = db.Column(db.String(30), nullable=False, unique=True)

    def __init__(self, nome_categoria):
        self.nome_categoria = nome_categoria

    def serialized(self):
        return {
            'nome_categoria': self.nome_categoria,
        }

    def __repr__(self):
        return "<Categoria %r>" % self.id


class Marca(db.Model):
    __tablename__ = "marca"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome_marca = db.Column(db.String(30), nullable=False, unique=True)

    def __init__(self, nome_marca):
        self.nome_marca = nome_marca

    def serialized(self):
        return {
            'nome_marca': self.nome_marca,
        }

    def __repr__(self):
        return "<Marca %r>" % self.id


class Medida(db.Model):
    __tablename__ = "medida"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome_medida = db.Column(db.String(30), nullable=False, unique=True)

    def __init__(self, nome_medida):
        self.nome_medida = nome_medida

    def serialized(self):
        return {
            'nome_medida': self.nome_medida,
        }

    def __repr__(self):
        return "<Medida %r>" % self.id


class Produto(db.Model):
    __tablename__ = "produto"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    codigo_barras = db.Column(db.String(50), nullable=False, unique=True)
    descricao_produto = db.Column(db.String(40), nullable=False)
    quantidade_produto = db.Column(db.Integer, nullable=False)
    quantidade_minima = db.Column(db.Integer, nullable=False)
    preco_custo = db.Column(db.Float(2, 0), nullable=False)
    preco_venda = db.Column(db.Float(2, 0), nullable=False)
    valor_desconto = db.Column(db.Float(2, 0))
    quantidade_maxima = db.Column(db.Integer)
    peso_liquido = db.Column(db.Float)
    peso_bruto = db.Column(db.Float)

    id_categoria_id = db.Column(db.Integer, db.ForeignKey("categoria.id"),
                                nullable=False)
    categoria = db.relationship('Categoria')

    id_marca_id = db.Column(db.Integer, db.ForeignKey("marca.id"),
                            nullable=False)
    marca = db.relationship('Marca')

    id_medida_id = db.Column(db.Integer, db.ForeignKey("medida.id"),
                             nullable=False)
    medida = db.relationship('Medida')

    nome_categoria = ""
    nome_marca = ""
    nome_medida = ""

    '''
        Podemos criar uma categoria, marca e medida padrão, apenas para não
    obrigarmos que seja incluído qualquer um dos três'''

    def __init__(self, codigo_barras, descricao_produto, quantidade_produto,
                 quantidade_minima, preco_custo,
                 preco_venda, quantidade_maxima=None, peso_liquido=None,
                 peso_bruto=None, id_categoria_id=1, id_marca_id=1,
                 id_medida_id=1):  # id 1 = Padrão

        self.codigo_barras = codigo_barras
        self.descricao_produto = descricao_produto
        self.quantidade_produto = quantidade_produto
        self.quantidade_minima = quantidade_minima
        self.preco_custo = preco_custo
        self.preco_venda = preco_venda
        self.valor_desconto = 0
        self.quantidade_maxima = quantidade_maxima
        self.peso_liquido = peso_liquido
        self.peso_bruto = peso_bruto
        self.id_categoria_id = id_categoria_id
        self.id_marca_id = id_marca_id
        self.id_medida_id = id_medida_id

    def __repr__(self):
        return "<Produto %r>" % self.id

    # def adicionar_desconto(self, valor):
    #     self.valor_desconto = valor
    #     db.session.add(self)
    #     db.session.commit()

    def serialized(self):
        return {
            'codigo_barras': self.codigo_barras,
            'descricao_produto': self.descricao_produto,
            'quantidade_produto': self.quantidade_produto,
            'quantidade_minima': self.quantidade_minima,
            'preco_custo': self.preco_custo,
            'preco_venda': self.preco_venda,
            'valor_desconto': self.valor_desconto,
            'quantidade_maxima': self.quantidade_maxima,
            'peso_liquido': self.peso_liquido,
            'peso_bruto': self.peso_bruto,
            'id_categoria_id': self.id_categoria_id,
            'id_marca_id': self.id_marca_id,
            'id_medida_id': self.id_medida_id
        }


class Venda(db.Model):
    __tablename__ = "venda"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    data_venda = db.Column(db.DateTime)
    valor_total = db.Column(db.Float(2, 0))
    valor_desconto = db.Column(db.Float(2, 0))  # Desconto em toda venda
    cod_status_venda = db.Column(db.Integer, nullable=False)
    # Quando aplicar um desconto em toda venda
    observacao = db.Column(db.String(100))
    # Verificar se vamos colocar os atributos abaixo
    # troca = db.Column(db.String(50))
    # devolucao = db.Column(db.String(50))

    id_usuario_id = db.Column(
        db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    usuario = db.relationship('Usuario')

    id_cliente_id = db.Column(db.Integer, db.ForeignKey("cliente.id"))
    cliente = db.relationship('Cliente')

    now = datetime.datetime.now()

    def __init__(self, id_usuario_id):
        self.data_venda = datetime.datetime(year=self.now.year,
                                            month=self.now.month,
                                            day=self.now.day,
                                            hour=self.now.hour,
                                            minute=self.now.minute,
                                            second=self.now.second)
        self.valor_total = 0
        self.valor_desconto = 0
        self.cod_status_venda = 100  # 100 = Aberta(Nova venda)
        self.observacao = None
        self.id_usuario_id = id_usuario_id
        self.id_cliente_id = None
        # self.troca = ""
        # self.devolucao = ""

        # Cod_status_venda = 100 = Aberta(Nova venda)
        # Cod_status_venda = 200 - Fechada (Quando a venda ainda
        # não foi totalmente paga)
        # Cod_status_venda = 300 - Finalizada (Foi totalmente paga)
        #Cod_status_venda = 400 - Cancelada
    # OK
    def alterar_status_venda(self, cod_status_venda):
        self.cod_status_venda = cod_status_venda
        db.session.add(self)
        db.session.commit()

    def alterar_valor_desconto(self, valor_desconto):
        self.valor_desconto = valor_desconto
        # db.session.add(self)
        # db.session.commit()
    # OK

    def adicionar_cliente(self, id_cliente_id):
        self.id_cliente_id = id_cliente_id
        db.session.add(self)
        db.session.commit()

# session.query(MyClass).filter(MyClass.name == 'some name')
# session.query(MyClass).filter(MyClass.name == 'some name', MyClass.id > 5)
# session.query(MyClass).filter(MyClass.name == 'some name',
#                               MyClass.id > 5,
#                               MyClass.other == 'teste')
    def calcular_valor_total(self):
        detalhes_vendas = DetalhesVenda.query.filter(
            DetalhesVenda.id_venda_id == self.id)
        if detalhes_vendas:
            # print("Teste calcular_valor_total() ", detalhes_venda.valor_total)
            soma = 0
            for detalhe_venda in detalhes_vendas:
                # print(detalhe_venda.calcular_valor_total())
                soma += detalhe_venda.calcular_valor_itens()
                soma -= detalhe_venda.valor_desconto_adicional
            self.valor_total = soma - self.valor_desconto
            self.valor_total = round(self.valor_total, 2)
            # print("soma ", soma)
            # print("self.valor_total ", self.valor_total)
            return self.valor_total
            # db.session.add(self)
            # db.session.commit()

    # Talvez possamos juntar as funções calcular_valor_venda_sem_desconto e calcular_descontos
    def calcular_valor_venda_sem_desconto(self):
        detalhes_vendas = DetalhesVenda.query.filter(DetalhesVenda.id_venda_id == self.id)
        soma = 0
        for detalhe_venda in detalhes_vendas:
            soma += detalhe_venda.quantidade_produto * detalhe_venda.valor_produto
        # print(soma)
        soma = round(soma, 2)
        return soma

    def calcular_descontos(self):
        detalhes_vendas = DetalhesVenda.query.filter(DetalhesVenda.id_venda_id == self.id)
        soma = 0
        for detalhe_venda in detalhes_vendas:
            soma += (detalhe_venda.quantidade_produto * detalhe_venda.valor_desconto_produto) + detalhe_venda.valor_desconto_adicional
        valor_total_desconto = soma + self.valor_desconto
        valor_total_desconto = round(valor_total_desconto, 2)
        return valor_total_desconto

# desconto_detalhes_venda_01 = (detalhes_venda_01.quantidade_produto * detalhes_venda_01.valor_desconto_produto) + detalhes_venda_01.valor_desconto_adicional
# desconto_detalhes_venda_02 = (detalhes_venda_02.quantidade_produto * detalhes_venda_02.valor_desconto_produto) + detalhes_venda_02.valor_desconto_adicional
# desconto_detalhes_venda_04 = (detalhes_venda_04.quantidade_produto * detalhes_venda_04.valor_desconto_produto) + detalhes_venda_04.valor_desconto_adicional

# valor_total_desconto = desconto_detalhes_venda_01 + desconto_detalhes_venda_02 + desconto_detalhes_venda_04
# print(valor_total_desconto + venda01.valor_desconto)


    def alterar_observacao(self, observacao):
        self.observacao = observacao
        # db.session.add(self)
        # db.session.commit()

    def __repr__(self):
        return "<Venda %r>" % self.id


class DetalhesVenda(db.Model):
    __tablename__ = "detalhes_venda"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # numero_item = db.Column(db.Integer, nullable=False)
    quantidade_produto = db.Column(db.Integer, nullable=False)
    # descricao_produto = db.Column(db.String(50))
    valor_produto = db.Column(db.Float(2, 0))
    valor_desconto_produto = db.Column(db.Float(2, 0))
    valor_desconto_adicional = db.Column(db.Float(2, 0))
    # valor_total = db.Column(db.Float(2, 0))
    # Quando aplicar um desconto adicional
    observacao = db.Column(db.String(100))

    # Levamos os dois atributos abaixo para classe Venda
    # troca = db.Column(db.String(50))
    # devolucao = db.Column(db.String(50))

    id_venda_id = db.Column(
        db.Integer, db.ForeignKey("venda.id"), nullable=False)
    venda = db.relationship('Venda')

    id_produto_id = db.Column(
        db.Integer, db.ForeignKey("produto.id"), nullable=False)
    produto = db.relationship('Produto')

    def __init__(self, quantidade_produto, id_venda_id, id_produto_id):
        produto = Produto.query.get(id_produto_id)
        self.quantidade_produto = quantidade_produto
        self.valor_produto = produto.preco_venda
        self.valor_desconto_produto = produto.valor_desconto
        self.valor_desconto_adicional = 0
        # self.valor_total = 0
        self.observacao = None
        # self.troca = ""
        # self.devolucao = ""
        self.id_venda_id = id_venda_id
        self.id_produto_id = id_produto_id
    # OK

    def alterar_quantidade_produto(self, quantidade_produto):
        self.quantidade_produto = quantidade_produto
        # db.session.add(self)
        # db.session.commit()
        # self.calcular_valor_itens()
    # OK
    def calcular_valor_itens(self):
        valor_total = (self.quantidade_produto * (self.valor_produto - self.valor_desconto_produto))
        valor_total = round(valor_total, 2)
        return valor_total
        # db.session.add(self)
        # db.session.commit()
        # return self.valor_total

    # def calcular_valor_total_com_desconto_adicional(self):
    #     self.valor_total = self.valor_total - self.valor_desconto_adicional
    #     # db.session.add(self)
    #     # db.session.commit()
    #     return self.valor_total

    def alterar_valor_desconto_adicional(self, valor_desconto_adicional):
        self.valor_desconto_adicional = valor_desconto_adicional
        # db.session.add(self)
        # db.session.commit()

    def alterar_observacao(self, observacao):
        self.observacao = observacao
        # db.session.add(self)
        # db.session.commit()

    # def alterar_desconto(self, valor):  # Analisar possibilidade
    #     self.valor_desconto = valor
    #     db.session.add(self)
    #     db.session.commit()

    def __repr__(self):
        return "<DetalhesVenda %r>" % self.id


class TipoPagamento(db.Model):
    '''
        tipo_pagamento = DINHEIRO       = cod_tipo_pagamento = 1
        tipo_pagamento = CARTÃO DÉBITO  = cod_tipo_pagamento = 2
        tipo_pagamento = CARTÃO CRÉDITO = cod_tipo_pagamento = 3
        tipo_pagamento = FIADO          = cod_tipo_pagamento = 4
    '''
    __tablename__ = "tipo_pagamento"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tipo_pagamento = db.Column(db.String(15), nullable=False, unique=True)
    cod_tipo_pagamento = db.Column(db.Integer, nullable=False, unique=True)

    def __init__(self, tipo_pagamento, cod_tipo_pagamento):
        self.tipo_pagamento = tipo_pagamento
        self.cod_tipo_pagamento = cod_tipo_pagamento

    def __repr__(self):
        return "<TipoPagamento %r>" % self.id


# class StatusVenda(db.Model):
#     __tablename__ = "status_venda"
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     status_venda = db.Column(db.String(15), nullable=False, unique=True)
#     cod_status_venda = db.Column(db.Integer, nullable=False)

#     def __init__(self, status_venda, cod_status_venda):
#         self.status_venda = status_venda
#         self.cod_status_venda = cod_status_venda

#     def __repr__(self):
#         return "<StatusVenda %r>" % self.id


class DetalhesPagamento(db.Model):
    __tablename__ = "detalhes_pagamento"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    valor = db.Column(db.Float(2, 0))

    id_tipo_pagamento_id = db.Column(
        db.Integer, db.ForeignKey("tipo_pagamento.id"), nullable=False)
    tipo_pagamento = db.relationship('TipoPagamento')

    id_venda_id = db.Column(
        db.Integer, db.ForeignKey("venda.id"), nullable=False)
    venda = db.relationship('Venda')

    nome_tipo_pagamento = ""

    def __init__(self, valor, id_tipo_pagamento_id, id_venda_id):
        self.valor = valor
        self.id_tipo_pagamento_id = id_tipo_pagamento_id
        self.id_venda_id = id_venda_id

    def alterar_valor(self, valor):
        self.valor = valor
        db.session.add(self)
        db.session.commit()

    def alterar_id_tipo_pagamento_id(self, id_tipo_pagamento_id):
        self.id_tipo_pagamento_id = id_tipo_pagamento_id
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return "<DetalhesPagamento %r>" % self.id


class Justificativa(db.Model):
    __tablename__ = "justificativa"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    justificativa = db.Column(db.String(50), nullable=False, unique=True)

    def __init__(self, justificativa):
        self.justificativa = justificativa

    def __repr__(self):
        return "<Justificativa %r>" % self.id


class MovimentacaoCaixa(db.Model):
    __tablename__ = "movimentacao_caixa"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    valor_movimentacao = db.Column(db.Float(2, 0), nullable=False)
    data_movimentacao = db.Column(db.DateTime)
    status = db.Column(db.Boolean)

    observacao = db.Column(db.String(50))

    id_venda_id = db.Column(
        db.Integer, db.ForeignKey("venda.id"))
    venda = db.relationship('Venda')

    id_justificativa_id = db.Column(
        db.Integer, db.ForeignKey("justificativa.id"), nullable=False)
    justificativa = db.relationship('Justificativa')

    now = datetime.datetime.now()

# Criar método para atualizar o valor da movimentação em caixa
    def __init__(self, valor_movimentacao=0, observacao=None, id_venda_id=None,
                 id_justificativa_id=1):  # id 1 Padrão

        self.valor_movimentacao = valor_movimentacao
        self.data_movimentacao = datetime.datetime(year=self.now.year,
                                                   month=self.now.month,
                                                   day=self.now.day,
                                                   hour=self.now.hour,
                                                   minute=self.now.minute,
                                                   second=self.now.second)
        self.status = True  # True = Pago - False = Não Pago e saídas.
        self.observacao = observacao
        self.id_venda_id = id_venda_id
        self.id_justificativa_id = id_justificativa_id

    def __repr__(self):
        return "<MovimentacaoCaixa %r>" % self.id
