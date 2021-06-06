# from flask import Blueprint
import json
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from app import app, db, login_manager
from datetime import timedelta
from app.models.forms import LoginForm
from app.models.tables import NivelAcesso, Usuario
from app.models.tables import Cliente
from app.models.tables import Categoria, Marca, Medida, Produto
from app.models.tables import Venda, TipoPagamento, DetalhesPagamento,\
    DetalhesVenda
from app.models.tables import Justificativa, MovimentacaoCaixa
from datetime import datetime
import os

# app.id_usuario = 1


@login_manager.user_loader
def get_user(user_id):
    app.id_usuario = user_id
    return Usuario.query.filter_by(id=user_id).first()


'''
    A linha abaixo direciona o usuário para tela de login, caso ele não tenha
    logado, ou seja, tenha tentado acessar o conteúdo diretamente.
'''
login_manager.login_view = "login"

'''
    A linha abaixo nos permite personalizar a mensagem que o usuário receberá
    após tentar acessar uma página privada sem logar.
'''

login_manager.login_message = u"Você precisa logar para acessar o conteúdo da página!"


login_manager.session_protection = "strong"


# Preciso colocar outro conteúdo na página index.

@app.route("/")
@app.route("/index")
def index():
    return redirect(url_for('login'))


@app.route("/vendas_cadastradas")
def vendas_cadastradas():
    vendas = Venda.query.all()
    return render_template("vendas_cadastradas.html", vendas=vendas)

# @app.route('/teste_login')
# def teste_login():
#     usuario = Usuario.query.get(3)
#     return str(usuario.descriptografar_senha('LyKUe6XD'))


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(
            login=form.login.data).first()
        if usuario and usuario.descriptografar_senha(form.senha.data):
            if usuario.status:
                if not usuario.inativado:
                    if usuario.recuperou_senha:
                        return render_template('alterar_senha_usuario.html',
                                               usuario=usuario)
                    if form.lembrar_me.data:
                        login_user(usuario, remember=True,
                                   duration=timedelta(days=2))
                    else:
                        login_user(usuario)
                    return redirect(url_for('usuarios_cadastrados'))
                flash("Usuário encontra-se inativado!")
                return redirect(url_for('login'))
            flash("Usuário encontra-se bloqueado!")
            return redirect(url_for('login'))
        else:
            flash("Dados inválidos!")
            return redirect(url_for('login'))
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route("/usuarios_cadastrados")
@login_required
def usuarios_cadastrados():
    usuarios = Usuario.query.all()
    niveis = NivelAcesso.query.all()
    return render_template("usuarios_cadastrados.html", usuarios=usuarios,
                           niveis=niveis)


@app.route("/add_usuario", methods=['GET', 'POST'])
@login_required
def add_usuario():
    if request.method == 'POST':
        usuarios = Usuario.query.all()
        for u in usuarios:
            if u.email == request.form['email']:
                flash("Esse e-mail já existe!")
                return redirect(url_for('add_usuario_full'))
            if u.login == request.form['login']:
                flash("Esse login já existe!")
                return redirect(url_for('add_usuario_full'))
        usuario = Usuario(request.form['nome'], request.form['telefone'],
                          request.form['email'],
                          request.form['login'],
                          request.form['senha'],
                          request.form['id_nivel_acesso_id'])
        db.session.add(usuario)
        db.session.commit()
        return redirect(url_for('usuarios_cadastrados'))
    return render_template('add_usuario.html')


@app.route("/add_usuario_full")
@login_required
def add_usuario_full():
    niveis = NivelAcesso.query.all()
    return render_template('add_usuario.html', niveis=niveis)


@app.route("/edit_usuario/<int:id>", methods=['GET', 'POST'])
@login_required
def edit_usuario(id):
    usuario = Usuario.query.get(id)
    if request.method == 'POST':
        usuarios = Usuario.query.all()
        for u in usuarios:
            if u.id != usuario.id:
                #  Se o email já existir mandar de volta para o index
                if u.email == request.form['email']:
                    # print('Esse e-mail já foi cadastrado')
                    return redirect(url_for('produtos_cadastrados'))
                #  Se o login já existir mandar de volta para o index
                if u.login == request.form['login']:
                    # print('Esse login já foi cadastrado')
                    return redirect(url_for('produtos_cadastrados'))
        usuario.nome = request.form['nome']
        usuario.telefone = request.form['telefone']
        usuario.email = request.form['email']
        usuario.login = request.form['login']
        # if request.form['senha'] == "":
        #     usuario.senha = usuario.senha
        # else:
        #     usuario.senha = usuario.criptografar_senha(request.form['senha'])
        usuario.id_nivel_acesso_id = request.form['id_nivel_acesso_id']
        db.session.commit()
        return usuarios_cadastrados()
    if usuario:
        niveis = NivelAcesso.query.all()
        nivel = NivelAcesso.query.get(usuario.id_nivel_acesso_id)
        usuario.nome_nivel_acesso = nivel.nivel_acesso
        return json.dumps(usuario.serialized())
        print('Não existe esse usuario método GET!!!')
    return redirect(url_for('usuarios_cadastrados'))


@app.route("/deletar_usuario/<int:id>")
@login_required
def deletar_usuario(id):
    usuario = Usuario.query.get(id)
    return render_template('deletar_usuario.html', usuario=usuario)


@app.route("/delete_user/<int:id>")
@login_required
def delete_user(id):
    usuario = Usuario.query.get(id)
    if usuario:
        db.session.delete(usuario)
        db.session.commit()
        # print('Usuário apagado com sucesso! ')
        return redirect(url_for('usuarios_cadastrados'))
    # print('Não existe esse ID')
    return redirect(url_for('usuarios_cadastrados'))


@app.route("/bloquear_usuario/<int:id>")
@login_required
def bloquear_usuario(id):
    usuario = Usuario.query.get(id)
    if usuario:
        usuario.bloquear_usuario()
        # print('Usuário Bloqueado')
        flash(f'O usuário {usuario.nome} foi bloqueado!')
        return usuarios_cadastrados()
    # print('Não existe esse Usuario')
    return usuarios_cadastrados()


@app.route("/inativar_usuario/<int:id>")
@login_required
def inativar_usuario(id):
    usuario = Usuario.query.get(id)
    if usuario:
        usuario.inativar_usuario()
        flash(f'O usuário {usuario.nome} foi inativado!')
        # print('Usuário desbloqueado')
        return usuarios_cadastrados()
    # print('Não existe esse Usuario')
    return usuarios_cadastrados()


@app.route("/ativar_usuario/<int:id>")
@login_required
def ativar_usuario(id):
    usuario = Usuario.query.get(id)
    if usuario:
        usuario.ativar_usuario()
        # print('Usuário Bloqueado')
        flash(f'O usuário {usuario.nome} foi ativado!')
        return usuarios_cadastrados()
    # print('Não existe esse Usuario')
    return usuarios_cadastrados()


@app.route("/desbloquear_usuario/<int:id>")
@login_required
def desbloquear_usuario(id):
    usuario = Usuario.query.get(id)
    if usuario:
        usuario.desbloquear_usuario()
        flash(f'O usuário {usuario.nome} foi desbloqueado!')
        # print('Usuário desbloqueado')
        return usuarios_cadastrados()
    # print('Não existe esse Usuario')
    return usuarios_cadastrados()


@app.route("/resetar_usuario/<int:id>")
@login_required
def resetar_usuario(id):
    usuario = Usuario.query.get(id)
    if usuario:
        usuario.resetar_usuario()
        flash(
            f'A senha do usuário {usuario.nome} foi resetada para 123@Orfeu!')
        # print('Usuário desbloqueado')
        return usuarios_cadastrados()
    # print('Não existe esse Usuario')
    return usuarios_cadastrados()


@app.route("/recuperar_senha_email", methods=['GET', 'POST'])
def recuperar_senha_email():
    if request.method == 'POST':
        usuarios = Usuario.query.all()
        for usuario in usuarios:
            if usuario.email == request.form['email']:
                msg = usuario.esqueci_senha()
                return render_template('mensagens_erro.html', msg=msg)
        return render_template('mensagens_erro.html', msg='E-mail não localizado!')
    return redirect(url_for('login'))


@app.route("/alterar_senha_2/<int:id>", methods=['GET', 'POST'])
def alterar_senha_2(id):
    if request.method == 'POST':
        usuario = Usuario.query.get(id)
        if usuario:
            usuario.alterar_senha_provisoria(
                usuario.senha, request.form['senha'])
            usuario.alterar_recuperou_senha()
            flash("Senha alterada!")
            return redirect(url_for('login'))
    return render_template('mensagens_erro.html', msg='Erro! Precisa ser método POST')


# usuario1 = Usuario.query.get(1)
# usuario1.recuperou_senha = False
# db.session.commit()
# usuario2 = Usuario.query.get(2)
# usuario2.recuperou_senha = True
# db.session.commit()
# usuario3 = Usuario.query.get(3)
# usuario3.recuperou_senha = True
# db.session.commit()


# @app.route("/mensagens_erro")
# def mensagens_erro():
#     return render_template('mensagens_erro.html')

@app.route("/op_caixa")
@login_required
def op_caixa():
    return render_template('op_caixa.html')


@app.route("/add_cliente_full")
@login_required
def add_cliente_full():
    return render_template('add_cliente.html')


@app.route("/add_cliente", methods=['GET', 'POST'])
@login_required
def add_cliente():
    if request.method == 'POST':
        clientes = Cliente.query.all()
        for c in clientes:
            if c.telefone == request.form['telefone']:
                flash("Esse telefone já está associado a outro cliente!")
                return redirect(url_for('clientes_cadastrados'))
            if request.form['cpf'] != "" and c.cpf == request.form['cpf']:
                flash("Esse CPF já está associado a outro cliente!")
                return redirect(url_for('clientes_cadastrados'))
        cliente = Cliente(request.form['nome'], request.form['telefone'],
                          request.form['data_pagamento'],
                          request.form['cpf'],
                          request.form['observacao'])
        db.session.add(cliente)
        db.session.commit()
        flash(f"O Cliente {cliente.nome} foi criado com sucesso!")
        return redirect(url_for('clientes_cadastrados'))
    return render_template('add_cliente.html')


@app.route("/clientes_cadastrados")
@login_required
def clientes_cadastrados():
    clientes = Cliente.query.all()
    return render_template("clientes_cadastrados.html", clientes=clientes)


@app.route("/edit_cliente/<int:id>", methods=['GET', 'POST'])
@login_required
def edit_cliente(id):
    cliente = Cliente.query.get(id)
    if request.method == 'POST':
        clientes = Cliente.query.all()
        for c in clientes:
            if c.id != cliente.id:
                if c.telefone == request.form['telefone']:
                    flash("Esse telefone já está associado a outro cliente!")
                    return redirect(url_for('clientes_cadastrados'))
                if request.form['cpf'] != "" and c.cpf == request.form['cpf']:
                    flash("Esse CPF já está associado a outro cliente!")
                    return redirect(url_for('clientes_cadastrados'))
        cliente.nome = request.form['nome']
        cliente.telefone = request.form['telefone']
        if request.form['data_pagamento'] == "":
            cliente.data_pagamento = cliente.data_pagamento
        else:
            cliente.data_pagamento = request.form['data_pagamento']
        cliente.cpf = request.form['cpf']
        cliente.observacao = request.form['observacao']
        # cliente.aumentar_divida(150.00)
        # cliente.diminuir_divida(300.00)
        # cliente.atualizar_data_ultima_compra()
        db.session.commit()
        flash(f"O Cliente {cliente.nome} foi alterado com sucesso!")
        return clientes_cadastrados()
    if cliente:
        return json.dumps(cliente.serialized())
        print('Não existe esse cliente método GET!!!')
    return redirect(url_for('clientes_cadastrados'))


@app.route("/deletar_cliente/<int:id>")
@login_required
def deletar_cliente(id):
    cliente = Cliente.query.get(id)
    return render_template('deletar_cliente.html', cliente=cliente)


@app.route("/delete_cli/<int:id>")
@login_required
def delete_cli(id):
    cliente = Cliente.query.get(id)
    if cliente:
        db.session.delete(cliente)
        db.session.commit()
        # print('Cliente apagado com sucesso! ')
        return redirect(url_for('clientes_cadastrados'))
    # print('Não existe esse ID')
    return redirect(url_for('clientes_cadastrados'))


@app.route("/bloquear_cliente/<int:id>")
@login_required
def bloquear_cliente(id):
    cliente = Cliente.query.get(id)
    if cliente:
        cliente.bloquear_cliente()
        # print('Cliente Bloqueado')
        flash(f'O cliente {cliente.nome} Não pode comprar fiado!')
        return clientes_cadastrados()
    # print('Não existe esse Usuario')
    return clientes_cadastrados()


@app.route("/desbloquear_cliente/<int:id>")
@login_required
def desbloquear_cliente(id):
    cliente = Cliente.query.get(id)
    if cliente:
        cliente.desbloquear_cliente()
        flash(f'O cliente {cliente.nome} Pode comprar fiado!')
        # print('Cliente desbloqueado')
        return clientes_cadastrados()
    # print('Não existe esse Usuario')
    return clientes_cadastrados()


@app.route("/inativar_cliente/<int:id>")
@login_required
def inativar_cliente(id):
    cliente = Cliente.query.get(id)
    if cliente:
        cliente.inativar_cliente()
        print('inativar_cliente')
        flash(f'O cliente {cliente.nome} foi inativado!')
        return clientes_cadastrados()
    return clientes_cadastrados()


@app.route("/ativar_cliente/<int:id>")
@login_required
def ativar_cliente(id):
    cliente = Cliente.query.get(id)
    if cliente:
        cliente.ativar_cliente()
        flash(f'O cliente {cliente.nome} foi ativado!')
        return clientes_cadastrados()
    return clientes_cadastrados()

# codigo_barras, descricao_produto, quantidade_produto,
#                  quantidade_minima, preco_custo,
#                  preco_venda, quantidade_maxima=None, peso_liquido=None,
#                  peso_bruto=None, id_categoria_id=1, id_marca_id=1,
#                  id_medida_id=1


@app.route("/add_produto", methods=['GET', 'POST'])
@login_required
def add_produto():
    if request.method == 'POST':
        produtos = Produto.query.all()
        for p in produtos:
            if p.codigo_barras == request.form['codigo_barras']:
                flash('Esse código de produto já existe!!!')
                return redirect(url_for('add_produto_full'))

            if p.descricao_produto == request.form['descricao_produto'] and p.id_marca_id == int(request.form['id_marca']):
                marca = Marca.query.get(p.id_marca_id)
                flash(
                    f'Jé existe um produto chamado {p.descricao_produto} associado a marca {marca.nome_marca}!!!')
                return redirect(url_for('add_produto_full'))

        produto = Produto(request.form['codigo_barras'], request.form['descricao_produto'], request.form['quantidade_produto'], request.form['quantidade_minima'], str(request.form['preco_custo']).replace(",", "."), str(request.form['preco_venda']).replace(
            ",", "."), request.form['quantidade_maxima'], float(request.form['peso_liquido'].replace(",", ".")), float(request.form['peso_bruto'].replace(",", ".")), request.form['id_categoria'], request.form['id_marca'], request.form['id_medida'])
        db.session.add(produto)
        db.session.commit()
        flash("Produto cadastrado com sucesso.")
        return redirect(url_for('produtos_cadastrados'))
    return redirect(url_for('produtos_cadastrados'))


@app.route("/edit_produto/<int:id>", methods=['GET', 'POST'])
@login_required
def edit_produto(id):
    produto = Produto.query.get(id)
    if request.method == 'POST':
        if produto:
            produtos = Produto.query.all()
            for p in produtos:
                if p.id != produto.id:
                    if p.codigo_barras == request.form['codigo_barras']:
                        flash('Esse código de produto já existe!!!')
                        return redirect(url_for('produtos_cadastrados'))
                    if p.descricao_produto == request.form['descricao_produto'] and p.id_marca_id == int(request.form['id_marca_id']):
                        marca = Marca.query.get(p.id_marca_id)
                        flash(
                            f'Jé existe um produto chamado {p.descricao_produto} associado a marca {marca.nome_marca}!!!')
                        return redirect(url_for('produtos_cadastrados'))

            produto.codigo_barras = request.form['codigo_barras']
            produto.descricao_produto = request.form['descricao_produto']
            produto.quantidade_produto = request.form['quantidade_produto']
            produto.quantidade_minima = request.form['quantidade_minima']
            produto.quantidade_maxima = request.form['quantidade_maxima']

            produto.peso_liquido = str(
                request.form['peso_liquido']).replace(",", ".")

            produto.peso_bruto = str(
                request.form['peso_bruto']).replace(",", ".")

            produto.preco_custo = str(
                request.form['preco_custo']).replace(",", ".")

            produto.preco_venda = str(
                request.form['preco_venda']).replace(",", ".")

            produto.valor_desconto = str(
                request.form['valor_desconto']).replace(",", ".")

            produto.id_categoria_id = request.form['id_categoria_id']
            produto.id_marca_id = request.form['id_marca_id']
            produto.id_medida_id = request.form['id_medida_id']
            db.session.commit()
            flash(
                f"O Produto {produto.descricao_produto} foi alterado com sucesso!")
            return redirect(url_for('produtos_cadastrados'))

        print('Não existe esse produto método POST!!!')
        return redirect(url_for('produtos_cadastrados'))
    if produto:
        categorias = Categoria.query.all()
        marcas = Marca.query.all()
        medidas = Medida.query.all()
        # Verificar para criar uma função para as linhas abaixo pois estão
        # se repetindo em outras partes do código
        categoria = Categoria.query.get(produto.id_categoria_id)
        marca = Marca.query.get(produto.id_marca_id)
        medida = Medida.query.get(produto.id_medida_id)
        produto.nome_categoria = categoria.nome_categoria
        produto.nome_marca = marca.nome_marca
        produto.nome_medida = medida.nome_medida
        return json.dumps(produto.serialized())
        print('Não existe esse produto método GET!!!')
    return redirect(url_for('produtos_cadastrados'))


@app.route("/produtos_cadastrados")
@login_required
def produtos_cadastrados():
    categorias = Categoria.query.all()
    marcas = Marca.query.all()
    medidas = Medida.query.all()
    produtos = Produto.query.all()
    for p in produtos:
        categoria = Categoria.query.get(p.id_categoria_id)
        marca = Marca.query.get(p.id_marca_id)
        medida = Medida.query.get(p.id_medida_id)
        p.nome_categoria = categoria.nome_categoria
        p.nome_marca = marca.nome_marca
        p.nome_medida = medida.nome_medida
    return render_template("produtos_cadastrados.html", produtos=produtos,
                           categorias=categorias, marcas=marcas,
                           medidas=medidas)


@app.route("/categorias_cadastradas")
@login_required
def categorias_cadastradas():
    categorias = Categoria.query.all()
    return render_template("categorias_cadastradas.html",
                           categorias=categorias)


@app.route("/marcas_cadastradas")
@login_required
def marcas_cadastradas():
    marcas = Marca.query.all()
    return render_template("marcas_cadastradas.html", marcas=marcas)


@app.route("/medidas_cadastradas")
@login_required
def medidas_cadastradas():
    medidas = Medida.query.all()
    return render_template("medidas_cadastradas.html", medidas=medidas)


@app.route("/deletar_produto/<int:id>")
@login_required
def deletar_produto(id):
    produto = Produto.query.get(id)
    # Criar uma função para fazer as linha de código abaixo,
    # pois elas se repetem em mais de uma rota
    categoria = Categoria.query.get(produto.id_categoria_id)
    marca = Marca.query.get(produto.id_marca_id)
    medida = Medida.query.get(produto.id_medida_id)
    produto.nome_categoria = categoria.nome_categoria
    produto.nome_marca = marca.nome_marca
    produto.nome_medida = medida.nome_medida
    return render_template('deletar_produto.html', produto=produto)


@app.route("/delete/<int:id>")
@login_required
def delete(id):
    produto = Produto.query.get(id)
    db.session.delete(produto)
    db.session.commit()
    return redirect(url_for('produtos_cadastrados'))


@app.route("/add_produto_full")
@login_required
def add_produto_full():
    categorias = Categoria.query.all()
    marcas = Marca.query.all()
    medidas = Medida.query.all()
    return render_template('add_produto.html', categorias=categorias,
                           marcas=marcas, medidas=medidas)


@app.route("/add_categoria", methods=['GET', 'POST'])
@login_required
def add_categoria():
    if request.method == 'POST':
        categorias = Categoria.query.all()
        for c in categorias:
            if c.nome_categoria == request.form['nome_categoria']:
                flash("Categoria já existe!!!")
                return redirect(url_for('listar_categorias'))
        categoria = Categoria(request.form['nome_categoria'])
        db.session.add(categoria)
        db.session.commit()
        flash("Categoria Cadastrada!!!")
        return redirect(url_for('listar_categorias'))


@app.route("/edit_categoria/<int:id>", methods=['GET', 'POST'])
@login_required
def edit_categoria(id):
    categoria = Categoria.query.get(id)
    if request.method == 'POST':
        categorias = Categoria.query.all()
        for c in categorias:
            if c.id != categoria.id:
                if c.nome_categoria == request.form['nome_categoria']:
                    flash("Categoria já existe!!!")
                    return categorias_cadastradas()
        categoria.nome_categoria = request.form['nome_categoria']
        db.session.commit()
        flash("Categoria Alterada!!!")
        return categorias_cadastradas()
    if categoria:
        return json.dumps(categoria.serialized())
    print('Não existe essa categoria método GET!!!')
    return categorias_cadastradas()


@app.route("/delete_categoria/<int:id>")
@login_required
def delete_categoria(id):
    categoria = Categoria.query.get(id)
    db.session.delete(categoria)
    db.session.commit()
    return redirect(url_for('listar_categorias'))


@app.route("/listar_categorias")
@login_required
def listar_categorias():
    categorias = Categoria.query.all()
    return render_template('add_categoria.html', categorias=categorias)


@app.route("/add_marca", methods=['GET', 'POST'])
@login_required
def add_marca():
    if request.method == 'POST':
        marcas = Marca.query.all()
        for m in marcas:
            if m.nome_marca == request.form['nome_marca']:
                flash("Marca já existe!!!")
                return redirect(url_for('listar_marcas'))
        marca = Marca(request.form['nome_marca'])
        db.session.add(marca)
        db.session.commit()
        flash("Marca Cadastrada!!!")
        return redirect(url_for('listar_marcas'))
    return redirect(url_for('listar_marcas'))


@app.route("/edit_marca/<int:id>", methods=['GET', 'POST'])
@login_required
def edit_marca(id):
    marca = Marca.query.get(id)
    if request.method == 'POST':
        marcas = Marca.query.all()
        for m in marcas:
            if m.id != marca.id:
                if m.nome_marca == request.form['nome_marca']:
                    flash("Marca já existe!!!")
                    return redirect(url_for('listar_marcas'))
        marca.nome_marca = request.form['nome_marca']
        db.session.commit()
        flash("Marca Alterada!!!")
        return marcas_cadastradas()
    if marca:
        return json.dumps(marca.serialized())
    print('Não existe essa marca método GET!!!')
    return redirect(url_for('produtos_cadastrados'))


@app.route("/delete_marca/<int:id>")
@login_required
def delete_marca(id):
    marca = Marca.query.get(id)
    db.session.delete(marca)
    db.session.commit()
    return redirect(url_for('listar_marcas'))


@app.route("/listar_marcas")
@login_required
def listar_marcas():
    marcas = Marca.query.all()
    return render_template('add_marca.html', marcas=marcas)


@app.route("/add_medida", methods=['GET', 'POST'])
@login_required
def add_medida():
    if request.method == 'POST':
        medidas = Medida.query.all()
        for m in medidas:
            if m.nome_medida == request.form['nome_medida']:
                flash("Medida já existe!!!")
                return redirect(url_for('listar_medidas'))
        medida = Medida(request.form['nome_medida'])
        db.session.add(medida)
        db.session.commit()
        flash("Medida Cadastrada!!!")
        return redirect(url_for('listar_medidas'))
    return redirect(url_for('listar_medidas'))


@app.route("/edit_medida/<int:id>", methods=['GET', 'POST'])
@login_required
def edit_medida(id):
    medida = Medida.query.get(id)
    if request.method == 'POST':
        medidas = Medida.query.all()
        for m in medidas:
            if m.id != medida.id:
                if m.nome_medida == request.form['nome_medida']:
                    flash("Medida já existe!!!")
                    return redirect(url_for('listar_medidas'))
        medida.nome_medida = request.form['nome_medida']
        db.session.commit()
        flash("Medida Alterada!!!")
        return medidas_cadastradas()
    if medida:
        return json.dumps(medida.serialized())
    print('Não existe essa medida método GET!!!')
    return redirect(url_for('produtos_cadastrados'))


@app.route("/delete_medida/<int:id>")
@login_required
def delete_medida(id):
    medida = Medida.query.get(id)
    db.session.delete(medida)
    db.session.commit()
    return redirect(url_for('listar_medidas'))


@app.route("/listar_medidas")
@login_required
def listar_medidas():
    medidas = Medida.query.all()
    return render_template('add_medida.html', medidas=medidas)


@app.route("/tipo_pagamento")
@login_required
def tipo_pagamento():
    tipo_pagamentos = TipoPagamento.query.all()
    return render_template('tipo_pagamento.html',
                           tipo_pagamentos=tipo_pagamentos)


@app.route("/add_venda", methods=['GET', 'POST'])
@login_required
def add_venda():
    # Inserir uma nova venda
    dataVenda = datetime
    usuario = app.id_usuario
    # Na table StatusVenda, devemos sempre passar o msm cod_status_venda
    # para tornar universal o código.
    statusVenda = 100
    novaVenda = Venda(dataVenda, 0, usuario, statusVenda)
    db.session.add(novaVenda)
    # Retornar o ID da nova venda
    id = db.session.flush()
    db.session.commit()
    venda = Venda.query.get(id)
    return render_template('novaVenda.html', venda=venda)

# DEF consultar produtos na venda (formulário de itens da venda)
# Função de calcular os itens da venda - retornar uma str com o valor total


def consultar_prod_venda(id_venda):
    produtos = DetalhesVenda.query.get(id_venda)
    vltotal = 0
    for p in produtos:
        vltotal += p.valor_total
    return render_template("novaVenda.html", produtos=produtos,
                           venda=id_venda, vltotal=vltotal)

# DEF add produto na venda (formulario de incluir item na venda)


@app.route("/add_prod_venda", methods=['GET', 'POST'])
@login_required
def add_prod_venda(quantidade_prod, cod_barras, id_venda):
    produto = Produto.query.get(cod_barras)
    detalheVenda = DetalhesVenda.query.get(id_venda)
    if produto.cod_barras != "":
        produtoVenda = DetalhesVenda(max(detalheVenda.numero_item) + 1,
                                     quantidade_prod,
                                     produto.descricao_produto,
                                     produto.valor_produto, 0,
                                     quantidade_prod * produto.valor_produto)
        db.session.add(produtoVenda)
        db.session.commit()
    consultar_prod_venda(id_venda)

# DEF fechar_venda (Botão Fechar)
    # > Chamar DEF alterar_status_venda e passar o
    # cod_status_venda de fechar(200)
    # Direcionar para a tela de Pagamento(Passar o Id_Venda, Valor Total)


@app.route("/fechar_venda", methods=['GET', 'POST'])
@login_required
def fechar_venda(Id_Venda, ValorTotal):
    alterar_status_venda(Id_Venda, 200)
    renderiza_pagamento(Id_Venda, ValorTotal, 0, ValorTotal)


@app.route("/cancelar_venda", methods=['GET', 'POST'])
@login_required
def cacelar_venda(Id_Venda):
    alterar_status_venda(Id_Venda, 400)
    return render_template("vendas.html")


# DEF alterar_status_venda(cancelar/fechar) a venda
    # Cod_status_venda(100 - Aberta(Nova venda), 200 - Fechado,
    # 300 - Finalizado, 400 - Cancelado)
    # Update tabela venda com o status recebido
def alterar_status_venda(id_venda, cod_status):
    venda = Venda.query.get(id_venda)
    venda.cod_status_venda = cod_status
    db.session.commit()


# DEF para add valor no DetalhesPagamento (Salvar)
@app.route("/add_valor_pagamento", methods=['GET', 'POST'])
@login_required
def add_valor_detalhespgto(id_venda, id_tipo_pgto, valorpago, valortotal):
    detalhepgto = DetalhesPagamento(valorpago, id_tipo_pgto, id_venda)
    db.session.add(detalhepgto)
    db.session.commit()
    consultar_valor_detalhespgto(id_venda, valortotal)


# DEF para consultar o valor que já foi add no DetalhesPagamento
# (Valor pago e restante)
def consultar_valor_detalhespgto(id_venda, valortotal):
    valorespagos = DetalhesPagamento.query.get(id_venda)
    valorpagototal = 0
    for v in valorespagos:
        valorpagototal += v.valor
    valorrestante = valortotal - valorpagototal
    renderiza_pagamento(id_venda, valortotal, valorpagototal, valorrestante)


def renderiza_pagamento(id_venda, valortotal, valorpago, valorrestante):
    return render_template("pagamento.html", idvenda=id_venda,
                           valortotal=valortotal, valorpago=valorpago,
                           valorrestante=valorrestante)


# DEF finalizar a venda com o pagamento (tela de pgto)
    # > Chamar DEF alterar_status_venda e passar o cod_status_venda
    # de finalizado(300)
@app.route("/finalizar_venda", methods=['GET', 'POST'])
@login_required
def finalizar_venda(Id_Venda):
    alterar_status_venda(Id_Venda, 300)
    return render_template("vendas.html")

# Fazer HTML vendas.html(igual o de produtos_cadastrados)
# e o pagamento.html(vide garrancho no caderno kkkkk)


# DEF listar todas as vendas (tela de lista com botão de nova venda
# e detalhes da venda)

# DEF exibir dados da venda (modal) - Botão Detalhes Venda


'''
print("# ********************** TESTES NÍVEL DE ACESSO ********************** #")
# nivel_acesso
admin = NivelAcesso('ADMINISTRADOR')  # ID 1
db.session.add(admin)
db.session.commit()
# admin = NivelAcesso.query.get(1)

print('ADMINISTRADOR: ', admin)
print('ADMINISTRADOR: ', admin.nivel_acesso)



op_caixa_01 = NivelAcesso('OPERADOR DE CAIXA')  # ID 2
db.session.add(op_caixa_01)
db.session.commit()
# op_caixa_01 = NivelAcesso.query.get(2)
print('OPERADOR DE CAIXA: ', op_caixa_01)
print('OPERADOR DE CAIXA: ', op_caixa_01.nivel_acesso)
op_caixa_01
print(100 * '*')
'''
'''
print()
print()
print()
'''
'''

print("# ********************** TESTES USUARIO ********************** #")
# nome, telefone, email, login, senha, id_nivel_acesso_id=2

admin = NivelAcesso.query.get(1)
user_maria = Usuario('Maria', '11989898989',
                     'andriah.albuquerque@gmail.com', 'maria', '123', admin.id)
db.session.add(user_maria)
db.session.commit()


user_maria = Usuario.query.get(1)
print('USUÁRIO 01 ID: ', user_maria)
print('USUÁRIO 01 NOME: ', user_maria.nome)
print('USUÁRIO 01 TELEFONE: ', user_maria.telefone)
print('USUÁRIO 01 EMAIL: ', user_maria.email)
print('USUÁRIO 01 LOGIN: ', user_maria.login)
print('USUÁRIO 01 SENHA: ', user_maria.senha)
print('USUÁRIO 01 STATUS: ', user_maria.status)
print('USUÁRIO 01 ID_NIVEL_ACESSO_ID: ', user_maria.id_nivel_acesso_id)
# f USUÁRIO
'''

'''
user_maria.bloquear_usuario()
print('USUÁRIO 01 STATUS BLOQUEADO: ', user_maria.status)
# DESBLOQUEAR USUÁRIO
user_maria.desbloquear_usuario()
print('USUÁRIO 01 STATUS DESBLOQUEADO', user_maria.status)
# VERIFICAR STATUS USUÁRIO
print('VERIFICAR STATUS USUÁRIO: ', user_maria.verificar_status())
# ALTERAÇÃO DE SENHA
print('ALTERAÇÃO DE SENHA: ', user_maria.alterar_senha('123@Orfeu', '123'))


print(100 * '*')

op_caixa_01 = NivelAcesso.query.get(1)
user_joao = Usuario('Joao', '1199992222', 'joao@email.com',
                    'joao.joao', '123', op_caixa_01.id)

db.session.add(user_joao)
db.session.commit()
user_joao = Usuario.query.get(2)
print('USUÁRIO 02 ID: ', user_joao)
print('USUÁRIO 02 NOME: ', user_joao.nome)
print('USUÁRIO 02 TELEFONE: ', user_joao.telefone)
print('USUÁRIO 02 EMAIL: ', user_joao.email)
print('USUÁRIO 02 LOGIN: ', user_joao.login)
print('USUÁRIO 02 SENHA: ', user_joao.senha)
print('USUÁRIO 02 STATUS: ', user_joao.status)
print('USUÁRIO 02 ID_NIVEL_ACESSO_ID: ', user_joao.id_nivel_acesso_id)

# BLOQUEAR USUÁRIO
user_joao.bloquear_usuario()
print('USUÁRIO 02 STATUS BLOQUEADO: ', user_joao.status)
# BLOQUEAR USUÁRIO
user_joao.bloquear_usuario()
print('USUÁRIO 02 STATUS BLOQUEADO', user_joao.status)
# VERIFICAR STATUS USUÁRIO
print('VERIFICAR STATUS USUÁRIO: ', user_joao.verificar_status())
user_joao.desbloquear_usuario()
print('USUÁRIO 02 STATUS BLOQUEADO', user_joao.status)

print(100 * '*')
print()
print()
print()

# ************************************************************************
# ************************************************************************
# ************************************************************************

print("# ********************** TESTES USUARIO 02********************** #")
user_maria = Usuario.query.get(1)
nivel_user = NivelAcesso.query.get(user_maria.id_nivel_acesso_id)
user_maria.nome_nivel_acesso = nivel_user.nivel_acesso
print('USUÁRIO 01 NOME ID_NIVEL_ACESSO_ID: ', user_maria.nome_nivel_acesso)

print(100 * '*')

user_joao = Usuario.query.get(2)
nivel_user = NivelAcesso.query.get(user_joao.id_nivel_acesso_id)
user_joao.nome_nivel_acesso = nivel_user.nivel_acesso
print('USUÁRIO 02 NOME ID_NIVEL_ACESSO_ID: ', user_joao.nome_nivel_acesso)
'''

'''
print("# ********************** TESTES CLIENTE ********************** #")

# Ajustar formato de data e hora

# nome, telefone, data_pagamento, cpf=None, observacao=None
# data_e_hora = datetime.strptime('20/04/2021 12:30', '%d/%m/%Y %H:%M')

cli_jose = Cliente('Jose 1', '1199995333', '20/04/2021',
                   '11111111111', 'observacao 01')
db.session.add(cli_jose)
db.session.commit()
# cli_jose = Cliente.query.get(1)


print('CLIENTE 01 ID: ', cli_jose)
print('CLIENTE 01 NOME: ', cli_jose.nome)
print('CLIENTE 01 TELEFONE: ', cli_jose.telefone)
print('CLIENTE 01 DATA_PAGAMENTO: ', cli_jose.data_pagamento)


print('CLIENTE 01 DATA_ULTIMA_COMPRA: ', cli_jose.data_ultima_compra)
print('CLIENTE 01 VALOR_DIVIDA: ', cli_jose.valor_divida)
print('CLIENTE 01 STATUS: ', cli_jose.status)
print('CLIENTE 01 CPF: ', cli_jose.cpf)
print('CLIENTE 01 OBSERVACAO: ', cli_jose.observacao)

print(100 * '*')


# data_e_hora = datetime.strptime('20/04/2021 12:30', '%d/%m/%Y %H:%M')
# cli_marta = Cliente('Marta', '1199994444', data_e_hora)

# db.session.add(cli_marta)
# db.session.commit()
cli_marta = Cliente.query.get(2)
print('CLIENTE 02 ID: ', cli_marta)
print('CLIENTE 02 NOME: ', cli_marta.nome)
print('CLIENTE 02 TELEFONE: ', cli_marta.telefone)
print('CLIENTE 02 DATA_PAGAMENTO: ', cli_marta.data_pagamento)
print('CLIENTE 02 DATA_ULTIMA_COMPRA: ', cli_marta.data_ultima_compra)
print('CLIENTE 02 VALOR_DIVIDA: ', cli_marta.valor_divida)
print('CLIENTE 02 STATUS: ', cli_marta.status)
print('CLIENTE 02 CPF: ', cli_marta.cpf)
print('CLIENTE 02 OBSERVACAO: ', cli_marta.observacao)

print(100 * '*')
print()
print()
print()

# TESTE PARA NÃO PERMIRTIR UM CLIENTE COM O MESMO TELEFONE
# data_e_hora = datetime.strptime('20/04/2021 12:30', '%d/%m/%Y %H:%M')
# cli_marta = Cliente('Paula', '1199994444', data_e_hora)
# db.session.add(cli_marta)
# db.session.commit()


print("# ********************** TESTES CATEGORIA ********************** #")
# nome_categoria
# categoria_01 = Categoria('GRÃOS')
# db.session.add(categoria_01)
# db.session.commit()
categoria_01 = Categoria.query.get(1)
print('CATEGORIA ID: ', categoria_01)
print('CATEGORIA NOME: ', categoria_01.nome_categoria)


print(100 * '*')
print()
print()
print()

print("# ********************** TESTES MARCA ********************** #")
# nome_marca
# marca_01 = Marca('CAMIL')
# db.session.add(marca_01)
# db.session.commit()
marca_01 = Marca.query.get(1)
print('MARCA ID: ', marca_01)
print('MARCA NOME: ', marca_01.nome_marca)

print(100 * '*')
print()
print()
print()

print("# ********************** TESTES MEDIDA ********************** #")
# nome_medida
# medida_01 = Medida('LITRO')
# db.session.add(medida_01)
# db.session.commit()
medida_01 = Medida.query.get(1)
print('MEDIDA ID: ', medida_01)
print('MEDIDA NOME: ', medida_01.nome_medida)


print(100 * '*')
print()
print()
print()


print("# ********************** TESTES PRODUTO ********************** #")
# codigo_barras, descricao_produto, quantidade_produto,
# quantidade_minima, preco_custo,
# preco_venda, quantidade_maxima = None, peso_liquido = None,
# peso_bruto = None, id_categoria_id = 1, id_marca_id = 1,
# id_medida_id = 1

# produto_01 = Produto('10', 'FEIJÃO', 200, 50, 5.00, 9.00, 300, 1, 1, 1, 1, 1)
# db.session.add(produto_01)
# db.session.commit()
produto_01 = Produto.query.get(1)

print('PRODUTO ID: ', produto_01)
print('PRODUTO CODIGO_BARRAS: ', produto_01.codigo_barras)
print('PRODUTO DESCRICAO_PRODUTO: ', produto_01.descricao_produto)
print('PRODUTO QUANTIDADE_PRODUTO: ', produto_01.quantidade_produto)
print('PRODUTO QUANTIDADE_MINIMA: ', produto_01.quantidade_minima)
print('PRODUTO PRECO_CUSTO: ', produto_01.preco_custo)
print('PRODUTO PRECO_VENDA: ', produto_01.preco_venda)
print('PRODUTO QUANTIDADE_MAXIMA: ', produto_01.quantidade_maxima)
print('PRODUTO PESO_LIQUIDO: ', produto_01.peso_liquido)
print('PRODUTO PESO_BRUTO: ', produto_01.peso_bruto)
print('PRODUTO ID_CATEGORIA_ID: ', produto_01.id_categoria_id)
print('PRODUTO ID_MARCA_ID: ', produto_01.id_marca_id)
print('PRODUTO ID_MEDIDA_ID: ', produto_01.id_medida_id)


print(100 * '*')

# codigo_barras, descricao_produto, quantidade_produto,
# quantidade_minima, preco_custo,
# preco_venda, quantidade_maxima = None, peso_liquido = None,
# peso_bruto = None, id_categoria_id = 1, id_marca_id = 1,
# id_medida_id = 1

# produto_02 = Produto('11', 'ARROZ', 300, 80, 3.50, 6.20)
# produto_02 = Produto('11', 'ARROZ', 300, 80, 3.50, 6.20, None, None, None)
# produto_02 = Produto('11', 'ARROZ', 300, 80, 3.50,
#                      6.20, None, None, None, 1, 1, 1)

# db.session.add(produto_02)
# db.session.commit()
produto_02 = Produto.query.get(2)

print('PRODUTO ID: ', produto_02)
print('PRODUTO CODIGO_BARRAS: ', produto_02.codigo_barras)
print('PRODUTO DESCRICAO_PRODUTO: ', produto_02.descricao_produto)
print('PRODUTO QUANTIDADE_PRODUTO: ', produto_02.quantidade_produto)
print('PRODUTO QUANTIDADE_MINIMA: ', produto_02.quantidade_minima)
print('PRODUTO PRECO_CUSTO: ', produto_02.preco_custo)
print('PRODUTO PRECO_VENDA: ', produto_02.preco_venda)
print('PRODUTO QUANTIDADE_MAXIMA: ', produto_02.quantidade_maxima)
print('PRODUTO PESO_LIQUIDO: ', produto_02.peso_liquido)
print('PRODUTO PESO_BRUTO: ', produto_02.peso_bruto)
print('PRODUTO ID_CATEGORIA_ID: ', produto_02.id_categoria_id)
print('PRODUTO ID_MARCA_ID: ', produto_02.id_marca_id)
print('PRODUTO ID_MEDIDA_ID: ', produto_02.id_medida_id)


print(100 * '*')

# produto_03 = Produto('12', 'ARROZ', 300, 80, 3.50, 6.20)

# db.session.add(produto_03)
# db.session.commit()
produto_03 = Produto.query.get(3)

print('PRODUTO ID: ', produto_03)
print('PRODUTO CODIGO_BARRAS: ', produto_03.codigo_barras)
print('PRODUTO DESCRICAO_PRODUTO: ', produto_03.descricao_produto)
print('PRODUTO QUANTIDADE_PRODUTO: ', produto_03.quantidade_produto)
print('PRODUTO QUANTIDADE_MINIMA: ', produto_03.quantidade_minima)
print('PRODUTO PRECO_CUSTO: ', produto_03.preco_custo)
print('PRODUTO PRECO_VENDA: ', produto_03.preco_venda)
print('PRODUTO QUANTIDADE_MAXIMA: ', produto_03.quantidade_maxima)
print('PRODUTO PESO_LIQUIDO: ', produto_03.peso_liquido)
print('PRODUTO PESO_BRUTO: ', produto_03.peso_bruto)
print('PRODUTO ID_CATEGORIA_ID: ', produto_03.id_categoria_id)
print('PRODUTO ID_MARCA_ID: ', produto_03.id_marca_id)
print('PRODUTO ID_MEDIDA_ID: ', produto_03.id_medida_id)


print(100 * '*')
print()
print()
print()


print("# ********************** TESTES VENDA ********************** #")
# data_venda
# valor_total
# id_usuario_id
# id_cliente_id

user_maria = Usuario.query.get(1)
cli_jose = Cliente.query.get(1)

venda_01 = Venda(user_maria.id, cli_jose.id)
db.session.add(venda_01)
db.session.commit()
venda_01 = Venda.query.get(1)

print('VENDA ID: ', venda_01)
print('VENDA DATA_VENDA: ', venda_01.data_venda)
print('VENDA VALOR_TOTAL: ', venda_01.valor_total)
print('VENDA ID_USUARIO_ID: ', venda_01.id_usuario_id)
print('VENDA ID_CLIENTE_ID: ', venda_01.id_cliente_id)


print(100 * '*')

# data_venda
# valor_total
# id_usuario_id
# id_cliente_id

# venda_02 = Venda(user_maria.id)
# db.session.add(venda_02)
# db.session.commit()
venda_02 = Venda.query.get(2)


print('VENDA ID: ', venda_02)
print('VENDA DATA_VENDA: ', venda_02.data_venda)
print('VENDA VALOR_TOTAL: ', venda_02.valor_total)
print('VENDA ID_USUARIO_ID: ', venda_02.id_usuario_id)
print('VENDA ID_CLIENTE_ID: ', venda_02.id_cliente_id)


print(100 * '*')
print()
print()
print()

'''
'''
print("# ********************** TESTES TIPO PAGAMENTO ********************** #")
# tipo_pagamento

tipo_pagamento_dinheiro = TipoPagamento('DINHEIRO')  # ID 1
db.session.add(tipo_pagamento_dinheiro)
db.session.commit()
# tipo_pagamento_dinheiro = TipoPagamento.query.get(1)

print('TIPO PAGAMENTO ID: ', tipo_pagamento_dinheiro)
print('TIPO PAGAMENTO NOME: ', tipo_pagamento_dinheiro.tipo_pagamento)

print(100 * '*')

tipo_pagamento_cartao_debito = TipoPagamento('CARTÃO DÉBITO')  # ID 2
db.session.add(tipo_pagamento_cartao_debito)
db.session.commit()
# tipo_pagamento_cartao_debito = TipoPagamento.query.get(2)

print('TIPO PAGAMENTO ID: ', tipo_pagamento_cartao_debito)
print('TIPO PAGAMENTO NOME: ', tipo_pagamento_cartao_debito.tipo_pagamento)

print(100 * '*')

tipo_pagamento_cartao_credito = TipoPagamento('CARTÃO CRÉDITO')  # ID 3
db.session.add(tipo_pagamento_cartao_credito)
db.session.commit()
# tipo_pagamento_cartao_credito = TipoPagamento.query.get(3)

print('TIPO PAGAMENTO ID: ', tipo_pagamento_cartao_credito)
print('TIPO PAGAMENTO NOME: ', tipo_pagamento_cartao_credito.tipo_pagamento)

print(100 * '*')

tipo_pagamento_fiado = TipoPagamento('FIADO')  # ID 4
db.session.add(tipo_pagamento_fiado)
db.session.commit()
# tipo_pagamento_fiado = TipoPagamento.query.get(4)

print('TIPO PAGAMENTO ID: ', tipo_pagamento_fiado)
print('TIPO PAGAMENTO NOME: ', tipo_pagamento_fiado.tipo_pagamento)


print(100 * '*')
print()
print()
print()
'''

'''
print("# ********************** TESTES DETALHES PAGAMENTO ********************** #")
# valor
# id_tipo_pagamento_id
# id_venda_id

# detalhes_pagamento_01 = DetalhesPagamento(
#     25.00, tipo_pagamento_dinheiro.id, venda_01.id)  # ID 1
# db.session.add(detalhes_pagamento_01)
# db.session.commit()
detalhes_pagamento_01 = DetalhesPagamento.query.get(1)

print('DETALHES PAGAMENTO ID: ', detalhes_pagamento_01)
print('DETALHES PAGAMENTO VALOR: ', detalhes_pagamento_01.valor)
print('DETALHES PAGAMENTO ID_TIPO_PAGAMENTO_ID: ',
      detalhes_pagamento_01.id_tipo_pagamento_id)
print('DETALHES PAGAMENTO ID_VENDA_ID: ', detalhes_pagamento_01.id_venda_id)

print(100 * '*')

# detalhes_pagamento_02 = DetalhesPagamento(
#     25.00, tipo_pagamento_cartao_debito.id, venda_01.id)  # ID 2
# db.session.add(detalhes_pagamento_02)
# db.session.commit()
detalhes_pagamento_02 = DetalhesPagamento.query.get(2)

print('DETALHES PAGAMENTO ID: ', detalhes_pagamento_02)
print('DETALHES PAGAMENTO VALOR: ', detalhes_pagamento_02.valor)
print('DETALHES PAGAMENTO ID_TIPO_PAGAMENTO_ID: ',
      detalhes_pagamento_02.id_tipo_pagamento_id)
print('DETALHES PAGAMENTO ID_VENDA_ID: ', detalhes_pagamento_02.id_venda_id)

print(100 * '*')

# detalhes_pagamento_03 = DetalhesPagamento(
#     25.00, tipo_pagamento_cartao_credito.id, venda_01.id)  # ID 3
# db.session.add(detalhes_pagamento_03)
# db.session.commit()
detalhes_pagamento_03 = DetalhesPagamento.query.get(3)

print('DETALHES PAGAMENTO ID: ', detalhes_pagamento_03)
print('DETALHES PAGAMENTO VALOR: ', detalhes_pagamento_03.valor)
print('DETALHES PAGAMENTO ID_TIPO_PAGAMENTO_ID: ',
      detalhes_pagamento_03.id_tipo_pagamento_id)
print('DETALHES PAGAMENTO ID_VENDA_ID: ', detalhes_pagamento_03.id_venda_id)

print(100 * '*')

# detalhes_pagamento_04 = DetalhesPagamento(
#     25.00, tipo_pagamento_fiado.id, venda_01.id)  # ID 4
# db.session.add(detalhes_pagamento_04)
# db.session.commit()
detalhes_pagamento_04 = DetalhesPagamento.query.get(4)

print('DETALHES PAGAMENTO ID: ', detalhes_pagamento_04)
print('DETALHES PAGAMENTO VALOR: ', detalhes_pagamento_04.valor)
print('DETALHES PAGAMENTO ID_TIPO_PAGAMENTO_ID: ',
      detalhes_pagamento_04.id_tipo_pagamento_id)
print('DETALHES PAGAMENTO ID_VENDA_ID: ', detalhes_pagamento_04.id_venda_id)


print(100 * '*')
print()
print()
print()


print("# ********************** TESTES DETALHES VENDA ********************** #")
# quantidade_produto, id_venda_id, id_produto_id

# detalhes_venda_01 = DetalhesVenda(1, venda_01.id, produto_01.id)  # ID 1
# db.session.add(detalhes_venda_01)
# db.session.commit()
detalhes_venda_01 = DetalhesVenda.query.get(1)

print('DETALHES VENDA ID: ', detalhes_venda_01)
print('DETALHES QUANTIDADE_PRODUTO: ', detalhes_venda_01.quantidade_produto)
print('DETALHES VALOR_PRODUTO: ', detalhes_venda_01.valor_produto)
print('DETALHES VALOR_DESCONTO: ', detalhes_venda_01.valor_desconto)
print('DETALHES TROCA: ', detalhes_venda_01.troca)
print('DETALHES DEVOLUCAO: ', detalhes_venda_01.devolucao)
print('DETALHES ID_VENDA_ID: ', detalhes_venda_01.id_venda_id)
print('DETALHES ID_PRODUTO_ID: ', detalhes_venda_01.id_produto_id)

print(100 * '*')

# detalhes_venda_02 = DetalhesVenda(1, venda_01.id, produto_02.id)  # ID 2
# db.session.add(detalhes_venda_02)
# db.session.commit()
detalhes_venda_02 = DetalhesVenda.query.get(2)

print('DETALHES VENDA ID: ', detalhes_venda_02)
print('DETALHES QUANTIDADE_PRODUTO: ', detalhes_venda_02.quantidade_produto)
print('DETALHES VALOR_PRODUTO: ', detalhes_venda_02.valor_produto)
print('DETALHES VALOR_DESCONTO: ', detalhes_venda_02.valor_desconto)
print('DETALHES TROCA: ', detalhes_venda_02.troca)
print('DETALHES DEVOLUCAO: ', detalhes_venda_02.devolucao)
print('DETALHES ID_VENDA_ID: ', detalhes_venda_02.id_venda_id)
print('DETALHES ID_PRODUTO_ID: ', detalhes_venda_02.id_produto_id)

print(100 * '*')

# detalhes_venda_03 = DetalhesVenda(1, venda_01.id, produto_03.id)  # ID 3
# db.session.add(detalhes_venda_03)
# db.session.commit()
detalhes_venda_03 = DetalhesVenda.query.get(3)

print('DETALHES VENDA ID: ', detalhes_venda_03)
print('DETALHES QUANTIDADE_PRODUTO: ', detalhes_venda_03.quantidade_produto)
print('DETALHES VALOR_PRODUTO: ', detalhes_venda_03.valor_produto)
print('DETALHES VALOR_DESCONTO: ', detalhes_venda_03.valor_desconto)
print('DETALHES TROCA: ', detalhes_venda_03.troca)
print('DETALHES DEVOLUCAO: ', detalhes_venda_03.devolucao)
print('DETALHES ID_VENDA_ID: ', detalhes_venda_03.id_venda_id)
print('DETALHES ID_PRODUTO_ID: ', detalhes_venda_03.id_produto_id)

print(100 * '*')

print()
print()
print()


print("# ********************** TESTES JUSTIFICATIVA ********************** #")


# justificativa_01 = Justificativa("01 - OUTROS")  # ID 01
# db.session.add(justificativa_01)
# db.session.commit()
justificativa_01 = Justificativa.query.get(1)

# justificativa_02 = Justificativa("02 - TROCO")  # ID 02
# db.session.add(justificativa_02)
# db.session.commit()
justificativa_02 = Justificativa.query.get(2)

# justificativa_03 = Justificativa("03 - PAGAMENTO DE DÉBITO")  # ID 03
# db.session.add(justificativa_03)
# db.session.commit()
justificativa_03 = Justificativa.query.get(3)

# justificativa_04 = Justificativa("04 - PAGAMENTO PARA FORNECEDOR")  # ID 04
# db.session.add(justificativa_04)
# db.session.commit()
justificativa_04 = Justificativa.query.get(4)

# justificativa_05 = Justificativa(
#     "05 - PAGAMENTO DE CONTA (ÁGUA, LUZ, TELEFONE)")  # ID 05
# db.session.add(justificativa_05)
# db.session.commit()
justificativa_05 = Justificativa.query.get(5)

# justificativa_06 = Justificativa("06 - VALE PARA FUNCIONÁRIO")  # ID 06
# db.session.add(justificativa_06)
# db.session.commit()
justificativa_06 = Justificativa.query.get(6)

# justificativa_07 = Justificativa("07 - VENDA")  # ID 07
# db.session.add(justificativa_07)
# db.session.commit()
justificativa_07 = Justificativa.query.get(7)


print('JUSTIFICATIVA ID: ', justificativa_01)
print('JUSTIFICATIVA NOME: ', justificativa_01.justificativa)
print(100 * '*')

print('JUSTIFICATIVA ID: ', justificativa_02)
print('JUSTIFICATIVA NOME: ', justificativa_02.justificativa)
print(100 * '*')

print('JUSTIFICATIVA ID: ', justificativa_03)
print('JUSTIFICATIVA NOME: ', justificativa_03.justificativa)
print(100 * '*')

print('JUSTIFICATIVA ID: ', justificativa_04)
print('JUSTIFICATIVA NOME: ', justificativa_04.justificativa)
print(100 * '*')

print('JUSTIFICATIVA ID: ', justificativa_05)
print('JUSTIFICATIVA NOME: ', justificativa_05.justificativa)
print(100 * '*')

print('JUSTIFICATIVA ID: ', justificativa_06)
print('JUSTIFICATIVA NOME: ', justificativa_06.justificativa)
print(100 * '*')

print('JUSTIFICATIVA ID: ', justificativa_07)
print('JUSTIFICATIVA NOME: ', justificativa_07.justificativa)
print(100 * '*')

print()
print()
print()


print("# ********************** TESTES MOVIMENTACAO CAIXA ********************** #")
# valor_movimentacao=0, observacao=None, id_venda_id=None, id_justificativa_id=1

# movimentacao_caixa_01 = MovimentacaoCaixa(
#     100.00, 'Vale para Maria Souza', None, justificativa_06.id)
# db.session.add(movimentacao_caixa_01)
# db.session.commit()
movimentacao_caixa_01 = MovimentacaoCaixa.query.get(1)

print('MOVIMENTACAO CAIXA ID: ', movimentacao_caixa_01)
print('MOVIMENTACAO CAIXA VALOR_MOVIMENTACAO: ',
      movimentacao_caixa_01.valor_movimentacao)
print('MOVIMENTACAO CAIXA DATA_MOVIMENTACAO: ',
      movimentacao_caixa_01.data_movimentacao)
print('MOVIMENTACAO CAIXA STATUS: ', movimentacao_caixa_01.status)
print('MOVIMENTACAO CAIXA OBSERVACAO: ', movimentacao_caixa_01.observacao)
print('MOVIMENTACAO CAIXA ID_VENDA_ID: ', movimentacao_caixa_01.id_venda_id)
print('MOVIMENTACAO CAIXA ID_JUSTIFICATIVA_ID: ',
      movimentacao_caixa_01.id_justificativa_id)

print(100 * '*')


# movimentacao_caixa_02 = MovimentacaoCaixa(
#     50.00, 'Pagamento para Italac', None, justificativa_04.id)
# db.session.add(movimentacao_caixa_02)
# db.session.commit()
movimentacao_caixa_02 = MovimentacaoCaixa.query.get(2)

print('MOVIMENTACAO CAIXA ID: ', movimentacao_caixa_02)
print('MOVIMENTACAO CAIXA VALOR_MOVIMENTACAO: ',
      movimentacao_caixa_02.valor_movimentacao)
print('MOVIMENTACAO CAIXA DATA_MOVIMENTACAO: ',
      movimentacao_caixa_02.data_movimentacao)
print('MOVIMENTACAO CAIXA STATUS: ', movimentacao_caixa_02.status)
print('MOVIMENTACAO CAIXA OBSERVACAO: ', movimentacao_caixa_02.observacao)
print('MOVIMENTACAO CAIXA ID_VENDA_ID: ', movimentacao_caixa_02.id_venda_id)
print('MOVIMENTACAO CAIXA ID_JUSTIFICATIVA_ID: ',
      movimentacao_caixa_02.id_justificativa_id)
print(100 * '*')


# movimentacao_caixa_03 = MovimentacaoCaixa(venda_01.valor_total, None, venda_01.id, 7)

# movimentacao_caixa_03 = MovimentacaoCaixa(venda_01.valor_total, None, venda_01.id, justificativa_07.id)
# db.session.add(movimentacao_caixa_03)
# db.session.commit()
movimentacao_caixa_03 = MovimentacaoCaixa.query.get(3)

print('MOVIMENTACAO CAIXA ID: ', movimentacao_caixa_03)
print('MOVIMENTACAO CAIXA VALOR_MOVIMENTACAO: ',
      movimentacao_caixa_03.valor_movimentacao)
print('MOVIMENTACAO CAIXA DATA_MOVIMENTACAO: ',
      movimentacao_caixa_03.data_movimentacao)
print('MOVIMENTACAO CAIXA STATUS: ', movimentacao_caixa_03.status)
print('MOVIMENTACAO CAIXA OBSERVACAO: ', movimentacao_caixa_03.observacao)
print('MOVIMENTACAO CAIXA ID_VENDA_ID: ', movimentacao_caixa_03.id_venda_id)
print('MOVIMENTACAO CAIXA ID_JUSTIFICATIVA_ID: ',
      movimentacao_caixa_03.id_justificativa_id)
print(100 * '*')


print(100 * '*')
print()
print()
print()

'''

'''******************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************'''

'''******************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************'''

'''******************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************'''


@app.route("/apoio")
def apoio():
    return render_template('apoio.html')


@app.route("/add_nivel_admin")
def add_nivel_admin():
    admin = NivelAcesso('ADMINISTRADOR')  # ID 1
    db.session.add(admin)
    db.session.commit()
    return "Nivel de Acesso ADMINISTRADOR adicionado com sucesso"


@app.route("/add_nivel_op_caixa")
def add_nivel_op_caixa():
    op_caixa = NivelAcesso('OPERADOR DE CAIXA')  # ID 2
    db.session.add(op_caixa)
    db.session.commit()
    return "Nivel de Acesso OPERADOR DE CAIXA adicionado com sucesso"


@app.route("/add_usuario_admin")
def add_usuario_admin():
    administrador = NivelAcesso.query.get(1)
    admin = Usuario('Admin', '11988881515',
                    'emprentime@gmail.com', 'admin', '123', administrador.id)
    db.session.add(admin)
    db.session.commit()
    return "Usuario ADMINISTRADOR adicionado com sucesso"


@app.route("/add_usuario_caixa")
def add_usuario_caixa():
    op_caixa = NivelAcesso.query.get(2)
    caixa = Usuario('Caixa', '11988881515',
                    'emprentime2@gmail.com', 'caixa', '123', op_caixa.id)
    db.session.add(caixa)
    db.session.commit()
    return "Usuario OPERADOR DE CAIXA adicionado com sucesso"


@app.route("/add_cliente_joao")
def add_cliente_joao():
    joao = Cliente('João', '1199995333', '10/03/2021',
                   '11111111111', 'Tem desconto de 5%')
    db.session.add(joao)
    db.session.commit()
    return "Cliente João adicionado com sucesso"


from random import choice
import string

from random import shuffle


@app.route("/add_varios_cliente")
def add_varios_cliente():
    j1 = ['Jose', 'Bruno', 'Lucas', 'Eduardo', 'Pedro', 'Luciano', 'Vitor', 'Diego', 'Rômulo', '*Pisca']
    j2 = ['Carlinhos', 'Carlos', 'Davi', 'Thiago', 'Paulo', 'Igor', 'Felipe', 'Marcelo', 'Matheus', 'Fabio']
    j3 = ['Artur', 'Anderson', 'Gustavo', 'Rogerio', 'Marcus', 'Nando', 'Jorge', 'Rodrigo', 'Caio', 'Jonas']

    shuffle(j1)
    shuffle(j2)
    shuffle(j3)

    fones = string.digits
    data = '10/06/2021'
    for n, (c1, c2, c3) in enumerate(zip(j1, j2, j3), start=1):
        nome = c1 + " " + c2 + " " + c3
        fone = "11" + choice(fones) + choice(fones) + choice(fones) + choice(fones) + choice(fones) + choice(fones) + choice(fones) + choice(fones)
        # print(nome)
        # print(fone)
        # print(data)
        nome = Cliente(nome, fone, data)
        db.session.add(nome)
        db.session.commit()
    return f"Cliente {nome} adicionado com sucesso"


@app.route("/adicionar_venda")
@login_required
def adicionar_venda():
    # ADICIONAR UMA VENDA:
    # admin = Usuario.query.get(app.id_usuario)
    venda = Venda(app.id_usuario)
    db.session.add(venda)
    db.session.commit()
    # EXIBIR UMA VENDA:
    exibir_venda(venda)
    return f"Venda adicionada {venda}"


def exibir_venda(venda):
    print('venda.id: ', venda.id)
    print('venda.data_venda: ', venda.data_venda)
    print("ANTES DO CÁLCULO: 'venda.valor_total' ", venda.valor_total)
    venda.calcular_valor_total()
    print("DEPOIS DO CÁLCULO: 'venda.valor_total' ", venda.valor_total)
    print('venda.valor_desconto: ', venda.valor_desconto)
    print('venda.cod_status_venda: ', venda.cod_status_venda)
    print('venda.observacao: ', venda.observacao)
    print('venda.id_usuario_id: ', venda.id_usuario_id)
    print('venda.id_cliente_id: ', venda.id_cliente_id)
    print('venda.id: ', venda.lista_itens)
    print(50 * "*")


def adicionar_detalhe_venda(quantidade_produto, id_venda, id_produto):
    detalhes_venda = DetalhesVenda(quantidade_produto, id_venda, id_produto)
    db.session.add(detalhes_venda)
    db.session.commit()
    print("Antes de calcular o valor total dos detalhes da venda")
    exibir_detalhes_venda(detalhes_venda)
    detalhes_venda.calcular_valor_itens()
    print("Depois de calcular o valor total dos detalhes da venda")
    exibir_detalhes_venda(detalhes_venda)


def exibir_detalhes_venda(detalhes_venda):
    print("detalhes_venda.id: ", detalhes_venda.id)
    print("detalhes_venda.quantidade_produto: ",
          detalhes_venda.quantidade_produto)
    print("detalhes_venda.valor_desconto_produto: ", detalhes_venda.valor_desconto_produto)
    print("detalhes_venda.valor_desconto_adicional: ",
          detalhes_venda.valor_desconto_adicional)
    # print("detalhes_venda.valor_total: ", detalhes_venda.valor_total)
    print("detalhes_venda.observacao: ", detalhes_venda.observacao)
    print("detalhes_venda.id_venda_id: ", detalhes_venda.id_venda_id)
    print("detalhes_venda.id_produto_id: ", detalhes_venda.id_produto_id)
    print(50 * "*")


def adicionar_tipo_pagamento(tipo_pagamento, cod_tipo_pagamento):
    tipo_pagamento_dinheiro = TipoPagamento(tipo_pagamento, cod_tipo_pagamento)
    db.session.add(tipo_pagamento_dinheiro)
    db.session.commit()
    print('TIPO PAGAMENTO ID: ', tipo_pagamento_dinheiro)
    print('TIPO PAGAMENTO NOME: ', tipo_pagamento_dinheiro.tipo_pagamento)


def adicionar_detalhe_pagamento(valor, id_tipo_pagamento_id, id_venda_id):
    detalhes_pagamento = DetalhesPagamento(valor, id_tipo_pagamento_id,
                                           id_venda_id)
    db.session.add(detalhes_pagamento)
    db.session.commit()


def deletar_detalhes_pagamento(id):
    detalhes_pagamento = DetalhesPagamento.query.get(id)
    db.session.delete(detalhes_pagamento)
    db.session.commit()


def deletar_detalhes_venda(id):
    detalhes_venda = DetalhesVenda.query.get(id)
    db.session.delete(detalhes_venda)
    db.session.commit()



@app.route("/deletar_venda/<int:id>")
@login_required
def deletar_venda(id):
    venda = Venda.query.get(id)
    if venda:
        # print("Achei venda")
        db.session.delete(venda)
        db.session.commit()
        return redirect(url_for('vendas_cadastradas'))
    # print("Não achei venda")
    return redirect(url_for('usuarios_cadastrados'))



# detalhes_venda = DetalhesVenda.query.get(1)
# detalhes_venda.valor_produto = 5.00
# # # # # detalhes_venda.valor_total = 0
# db.session.commit()
#*****************************************************************************************************************#
#*****************************************************************************************************************#
#*****************************************************************************************************************#


# TESTES NA CLASSE Venda
'''
# TESTES NO MÉTODO alterar_status_venda()
venda01 = Venda.query.get(1)
venda01.alterar_status_venda(100) # Aberta
print('venda01.cod_status_venda Aberta: ', venda01.cod_status_venda)
print(50 * "*")
venda01.alterar_status_venda(200)
print('venda01.cod_status_venda Fechada: ', venda01.cod_status_venda) # Fechada
print(50 * "*")
venda01.alterar_status_venda(300)
print('venda01.cod_status_venda Finalizada: ', venda01.cod_status_venda) # Finalizada
print(50 * "*")
venda01.alterar_status_venda(400) # Cancelada
print('venda01.cod_status_venda Cancelada: ', venda01.cod_status_venda)
print(50 * "*")
venda01.alterar_status_venda(100) # Aberta
print('venda01.cod_status_venda Aberta: ', venda01.cod_status_venda)
print(50 * "*")
'''


# TESTES NO MÉTODO alterar_valor_desconto() E calcular_valor_total()
# venda01 = Venda.query.get(1)
# venda01.alterar_valor_desconto(4.5)
# print('valor_total: ', venda01.valor_total)
# db.session.commit()

# venda01 = Venda.query.get(1)
# venda01.calcular_valor_total()
# print('valor_total: ', venda01.valor_total)
# db.session.commit()

# venda01 = Venda.query.get(1)
# venda01.calcular_valor_total()

# detalhes_venda_01 = DetalhesVenda.query.get(1)
# detalhes_venda_02 = DetalhesVenda.query.get(2)
# detalhes_venda_04 = DetalhesVenda.query.get(4)
# print(50 * "*")
# print(detalhes_venda_01.valor_produto)
# print(detalhes_venda_01.valor_desconto_produto)
# print(detalhes_venda_01.valor_desconto_adicional)
# print(50 * "*")
# print(detalhes_venda_02.valor_produto)
# print(detalhes_venda_02.valor_desconto_produto)
# print(detalhes_venda_02.valor_desconto_adicional)
# print(50 * "*")
# print(detalhes_venda_04.valor_produto)
# print(detalhes_venda_04.valor_desconto_produto)
# print(detalhes_venda_04.valor_desconto_adicional)

################################################# Calculando o total da venda sem desconto
# print('VALOR TOTAL DA VENDA SEM DESCONTO: ', venda01.calcular_valor_venda_sem_desconto())
# print('VALOR TOTAL DOS DESCONTOS: ', venda01.calcular_descontos())  # 36.599999999999994 ARREDONDAR
# print('VALOR TOTAL DA VENDA COM DESCONTO: ', venda01.calcular_valor_total())
# db.session.commit()




'''
print(50 * "*")
# Calculando o desconto dos detalhes e somando com o desconto da venda para obtermos o total da venda com desconto
desconto_detalhes_venda_01 = (detalhes_venda_01.quantidade_produto * detalhes_venda_01.valor_desconto_produto) + detalhes_venda_01.valor_desconto_adicional
desconto_detalhes_venda_02 = (detalhes_venda_02.quantidade_produto * detalhes_venda_02.valor_desconto_produto) + detalhes_venda_02.valor_desconto_adicional
desconto_detalhes_venda_04 = (detalhes_venda_04.quantidade_produto * detalhes_venda_04.valor_desconto_produto) + detalhes_venda_04.valor_desconto_adicional

valor_total_desconto = desconto_detalhes_venda_01 + desconto_detalhes_venda_02 + desconto_detalhes_venda_04
print(valor_total_desconto + venda01.valor_desconto)
'''


'''
venda01.alterar_valor_desconto(0)
venda01.calcular_valor_total()
print('valor_total: ', venda01.valor_total)
'''


# TESTES NO MÉTODO adicionar_cliente()
'''
venda01 = Venda.query.get(1)
venda01.adicionar_cliente(1)
print('venda01.id_cliente_id: ', venda01.id_cliente_id)
print(50 * "*")

venda01.adicionar_cliente(None)
print('venda01.id_cliente_id: ', venda01.id_cliente_id)
print(50 * "*")
'''


# TESTES NO MÉTODO alterar_observacao()
'''
venda01 = Venda.query.get(1)
venda01.alterar_observacao("Observação na venda geral!")
print('venda01.observacao: ', venda01.observacao)

venda01.alterar_observacao("")
print('venda01.observacao: ', venda01.observacao)
'''


#*****************************************************************************************************************#
#*****************************************************************************************************************#
#*****************************************************************************************************************#

# TESTES NA CLASSE DetalhesVenda

# venda01 = Venda.query.get(1)
# produto01 = Produto.query.get(1)
# print(produto01.descricao_produto)
# adicionar_detalhe_venda = adicionar_detalhe_venda(2, venda01.id, produto01.id)

# venda01 = Venda.query.get(1)
# produto02 = Produto.query.get(2)
# print(produto02.descricao_produto)
# adicionar_detalhe_venda = adicionar_detalhe_venda(3, venda01.id, produto02.id)

# venda01 = Venda.query.get(1)
# produto03 = Produto.query.get(3)
# print(produto03.descricao_produto)
# adicionar_detalhe_venda = adicionar_detalhe_venda(1, venda01.id, produto03.id)

# detalhes_venda = DetalhesVenda.query.get(3)
# print("Antes de calcular o valor total dos detalhes da venda")
# exibir_detalhes_venda(detalhes_venda)
# detalhes_venda.calcular_valor_itens()
# print("Depois de calcular o valor total dos detalhes da venda")
# exibir_detalhes_venda(detalhes_venda)
# db.session.commit()



# venda01 = Venda.query.get(1)
# produto04 = Produto.query.get(4)
# print(produto04.descricao_produto)
# adicionar_detalhe_venda = adicionar_detalhe_venda(4, venda01.id, produto04.id)
'''
detalhes_venda_01 = DetalhesVenda.query.get(3)
print("Antes de calcular o valor total dos detalhes da venda")
exibir_detalhes_venda(detalhes_venda_01)
print(50 * "*")
detalhes_venda_01.alterar_valor_desconto_adicional(2)
detalhes_venda_01.calcular_valor_itens()
print("Depois de calcular o valor total dos detalhes da venda")
exibir_detalhes_venda(detalhes_venda_01)

print(50 * "*")
print(50 * "*")
print(50 * "*")

detalhes_venda_02 = DetalhesVenda.query.get(4)
print("Antes de calcular o valor total dos detalhes da venda")
exibir_detalhes_venda(detalhes_venda_02)
print(50 * "*")
detalhes_venda_02.alterar_valor_desconto_adicional(4.5)
detalhes_venda_02.calcular_valor_itens()
print("Depois de calcular o valor total dos detalhes da venda")
exibir_detalhes_venda(detalhes_venda_02)
'''

# detalhes_venda_04 = DetalhesVenda.query.get(5)
# detalhes_venda_04.valor_desconto_produto = 0.3
# detalhes_venda_04.alterar_valor_desconto_adicional(0.2)
# db.session.commit()


'''
print(50 * "*")
print(50 * "*")
print(50 * "*")
venda01 = Venda.query.get(1)
print("venda01.valor_desconto' ", venda01.valor_desconto)
venda01.valor_desconto = 3
venda01.valor_desconto = 3
print("ANTES DO CÁLCULO: 'venda.valor_total' ", venda01.valor_total)

print(50 * "*")
venda01.calcular_valor_total()
print("venda01.valor_desconto' ", venda01.valor_desconto)
print("DEPOIS DO CÁLCULO: 'venda.valor_total' ", venda01.valor_total)
db.session.commit()

print('DESCONTO VENDA ', venda01.valor_desconto)

print('DESCONTO DETALHES 01: ', detalhes_venda_01.valor_desconto_produto)
print('DESCONTO DETALHES ADICIONAL 01: ', detalhes_venda_01.valor_desconto_adicional)

print('DESCONTO DETALHES 02', detalhes_venda_02.valor_desconto_produto)
print('DESCONTO DETALHES ADICIONAL 02', detalhes_venda_02.valor_desconto_adicional)

print('TOTAL DE DESCONTOS: ', venda01.valor_desconto +
      ((detalhes_venda_01.quantidade_produto * detalhes_venda_01.valor_desconto_produto) + detalhes_venda_01.valor_desconto_adicional + (detalhes_venda_02.quantidade_produto * detalhes_venda_02.valor_desconto_produto) + detalhes_venda_02.valor_desconto_adicional))
'''
# detalhes_venda = DetalhesVenda.query.get(3)
# print(detalhes_venda.alterar_quantidade_produto(5))
# exibir_detalhes_venda(detalhes_venda)
# detalhes_venda.calcular_valor_itens()
# print("Depois de calcular o valor total dos detalhes da venda")
# exibir_detalhes_venda(detalhes_venda)

# detalhes_venda = DetalhesVenda.query.get(3)
# print(detalhes_venda.alterar_quantidade_produto(2))
# exibir_detalhes_venda(detalhes_venda)

# detalhes_venda = DetalhesVenda.query.get(1)
# print(detalhes_venda.calcular_valor_itens())

'''
detalhes_venda = DetalhesVenda.query.get(4)
exibir_detalhes_venda(detalhes_venda)
print("detalhes_venda.alterar_valor_desconto_adicional(3): ", detalhes_venda.alterar_valor_desconto_adicional(3))
print("detalhes_venda.calcular_valor_itens(): ", detalhes_venda.calcular_valor_itens())
exibir_detalhes_venda(detalhes_venda)

venda01 = Venda.query.get(1)
venda01.valor_desconto = 3
exibir_venda(venda01)
'''


# detalhes_venda = DetalhesVenda.query.get(1)
# print(detalhes_venda.alterar_valor_desconto_adicional(1.5))
# db.session.commit()
# print(detalhes_venda.calcular_valor_itens())

# detalhes_venda = DetalhesVenda.query.get(4)
# print(detalhes_venda.alterar_valor_desconto_adicional(1))
# db.session.commit()


# detalhes_venda = DetalhesVenda.query.get(1)
# print(detalhes_venda.alterar_observacao("Promoção leva 2"))
# exibir_detalhes_venda(detalhes_venda)
# db.session.commit()

# detalhes_venda = DetalhesVenda.query.get(1)
# print(detalhes_venda.alterar_observacao(""))
# exibir_detalhes_venda(detalhes_venda)
# db.session.commit()

#*****************************************************************************************************************#
#*****************************************************************************************************************#
#*****************************************************************************************************************#


# TESTES NA CLASSE TipoPagamento

# adicionar_tipo_pagamento('DINHEIRO', 1)
# adicionar_tipo_pagamento('CARTÃO DÉBITO', 2)
# adicionar_tipo_pagamento('CARTÃO CRÉDITO', 3)
# adicionar_tipo_pagamento('FIADO', 4)
# tipo_pagamento_dinheiro = TipoPagamento.query.get(1)
# tipo_pagamento_cartao_debito = TipoPagamento.query.get(2)
# tipo_pagamento_cartao_credito = TipoPagamento.query.get(3)
# tipo_pagamento_fiado = TipoPagamento.query.get(4)

# tipo_pagamento_dinheiro = TipoPagamento.query.filter_by(cod_tipo_pagamento=1).first()
# print('Aqui estou tipo_pagamento_dinheiro.tipo_pagamento: ', tipo_pagamento_dinheiro.tipo_pagamento)

# tipo_pagamento_fiado = TipoPagamento.query.filter_by(cod_tipo_pagamento=4).first()
# print('Aqui estou tipo_pagamento_fiado.tipo_pagamento: ', tipo_pagamento_fiado.tipo_pagamento)

# tipo_pagamento_cartao_debito = TipoPagamento.query.filter_by(cod_tipo_pagamento=2).first()
# print('Aqui estou tipo_pagamento_cartao_debito.tipo_pagamento: ', tipo_pagamento_cartao_debito.tipo_pagamento)

#*****************************************************************************************************************#
#*****************************************************************************************************************#
#*****************************************************************************************************************#


# TESTES NA CLASSE DetalhesPagamento

# adicionar_detalhe_pagamento(20.00, tipo_pagamento_dinheiro.id, venda01.id)
# adicionar_detalhe_pagamento(16.60, tipo_pagamento_cartao_debito.id, venda01.id)

# tipo_pagamento_dinheiro = TipoPagamento.query.filter_by(cod_tipo_pagamento=1).first()
# print('Aqui estou', tipo_pagamento_dinheiro.tipo_pagamento)

# detalhes_pagamento_01 = DetalhesPagamento(50.00, tipo_pagamento_dinheiro.id, venda01.id)
# db.session.add(detalhes_pagamento_01)
# db.session.commit()

# tipo_pagamento_debito = TipoPagamento.query.filter_by(cod_tipo_pagamento=4).first()
# print('Aqui estou', tipo_pagamento_debito.tipo_pagamento)

# detalhes_pagamento_02 = DetalhesPagamento(49.50, tipo_pagamento_debito.id, venda01.id)
# db.session.add(detalhes_pagamento_02)
# db.session.commit()

# detalhes_pagamento_02 = DetalhesPagamento.query.get(2)
# detalhes_pagamento_02.alterar_id_tipo_pagamento_id(2)


#*****************************************************************************************************************#
#*****************************************************************************************************************#
#*****************************************************************************************************************#

# TESTES PARA DELETAR

# deletar_detalhes_pagamento(3)
# deletar_detalhes_venda(1)
# deletar_detalhes_venda(2)
# deletar_detalhes_venda(3)


# detalhes_venda = DetalhesVenda.query.get(4)
# detalhes_venda.id_produto_id = 2
# detalhes_venda.valor_produto = 2.5
# detalhes_venda.valor_desconto = 0
# detalhes_venda.quantidade_produto = 3
# db.session.commit()

'''
#*****************************************************************************************************************#
#*****************************************************************************************************************#
#*****************************************************************************************************************#
#*****************************************************************************************************************#
#*****************************************************************************************************************#
#*****************************************************************************************************************#
'''
'''
@app.route("/adicionar_nova_venda")
@login_required
def adicionar_nova_venda():
    return redirect(url_for('nova_venda_full'))


@app.route("/nova_venda_full")
@login_required
def nova_venda_full():
    venda = Venda(app.id_usuario)
    db.session.add(venda)
    db.session.commit()
    tipo_pagamentos = TipoPagamento.query.all()
    clientes = Cliente.query.all()
    return render_template('nova_venda.html', venda=venda, tipo_pagamentos=tipo_pagamentos, clientes=clientes)
'''

@app.route("/adicionar_nova_venda")
@login_required
def adicionar_nova_venda():
    venda = Venda(app.id_usuario)
    db.session.add(venda)
    db.session.commit()
    return redirect('/nova_venda_full/'+str(venda.id))

@app.route("/nova_venda_full/<int:id_venda>")
@login_required
def nova_venda_full(id_venda):
    venda = Venda.query.get(id_venda)
    tipo_pagamentos = TipoPagamento.query.all()
    clientes = Cliente.query.all()
    detalhes_vendas = DetalhesVenda.query.filter(DetalhesVenda.id_venda_id == venda.id).all()
    # print(detalhes_vendas)
    # numero_item = 0

    for dv in detalhes_vendas:
        dv.alterar_nome_produto()

    # if len(detalhes_vendas) > 0 :
    #     numero_item = detalhes_vendas[len(detalhes_vendas) - 1].numero_item
        
    return render_template('nova_venda.html', venda=venda, tipo_pagamentos=tipo_pagamentos, clientes=clientes, detalhes_vendas=detalhes_vendas)



# @app.route("/adicionar_cliente/<int:id>", methods=['GET', 'POST'])
# @login_required
# def adicionar_cliente(id):
#     cliente = Cliente.query.get(id)
#     if cliente:
#         print('Cheguei aqui ', id)
#         print(f'{cliente.nome} ', id)
#         return json.dumps({"teste": "Olá teste"})
#         print('Não existe esse usuario método GET!!!')
#     return redirect(url_for('usuarios_cadastrados'))
@app.route("/adicionar_cliente/<data>", methods=['GET', 'POST'])
@login_required
def adicionar_cliente(data):
    # print('Teste no data', data)
    obj = json.loads(data)
    # obter o nome
    # print(type(obj['id_venda']))
    # print(obj['id_cliente'])
    cliente = Cliente.query.get(obj['id_cliente'])
    venda = Venda.query.get(obj['id_venda'])
    # print(cliente.nome)
    # print(venda.data_venda)
    if cliente != None:
        # print("Entrei no adicionar")
        venda.adicionar_cliente(cliente.id)
        return json.dumps({"teste": 1})
    # print("Não Entrei no adicionar")
    return json.dumps({"teste": 0})


# obj = json.loads(texto)
# # obter o nome
# print(obj['nome'])
# venda01 = Venda.query.get(1)
# venda01.adicionar_cliente(1)
# print('venda01.id_cliente_id: ', venda01.id_cliente_id)


@app.route("/buscar_produto/<data>", methods=['GET', 'POST'])
@login_required
def buscar_produto(data):
    # print('Teste no data', data)
    obj = json.loads(data)
    # print(obj['codigo_barras'].upper(), " Aqui estou")
    nome_codigo_produto = obj['nome_codigo_produto'].upper()
    produto = Produto.query.filter(db.or_(Produto.codigo_barras == nome_codigo_produto, Produto.descricao_produto == nome_codigo_produto)).first()
    if produto != None:
        return json.dumps(produto.serialized())
    return json.dumps({"codigo_barras": 0})


# @app.route("/adicionar_detalhes_venda/<data>", methods=['GET', 'POST'])
# @login_required
# def adicionar_detalhes_venda(data):
#     obj = json.loads(data)
#     # print(obj['qtd_produto'], obj['id_venda'], obj['id_produto'])
#     detalhes_venda = DetalhesVenda(obj['qtd_produto'], obj['id_venda'], obj['id_produto'])
#     db.session.add(detalhes_venda)
#     db.session.commit()
#     return json.dumps({"codigo_barras": 1})
#     # detalhes_venda = DetalhesVenda(obj['nome_codigo_produto'], obj['nome_codigo_produto'], obj['nome_codigo_produto'])
#     # db.session.add(detalhes_venda)
#     # db.session.commit()
#     # print("Antes de calcular o valor total dos detalhes da venda")
#     # exibir_detalhes_venda(detalhes_venda)
#     # detalhes_venda.calcular_valor_itens()
#     # print("Depois de calcular o valor total dos detalhes da venda")
#     # exibir_detalhes_venda(detalhes_venda)


@app.route("/adicionar_detalhes_venda/<data>", methods=['GET', 'POST'])
@login_required
def adicionar_detalhes_venda(data):
    obj = json.loads(data)
    # print(obj['qtd_produto'], obj['id_venda'], obj['id_produto'])

    numero_item = 1
    detalhes_vendas = DetalhesVenda.query.filter(DetalhesVenda.id_venda_id == int(obj['id_venda'])).all()
    if len(detalhes_vendas) > 0:
        numero_item = (detalhes_vendas[len(detalhes_vendas) - 1].numero_item) + 1
    detalhes_venda = DetalhesVenda(numero_item, obj['qtd_produto'], obj['id_venda'], obj['id_produto'])
    db.session.add(detalhes_venda)
    db.session.commit()
    return json.dumps({"codigo_barras": 1})
    # detalhes_venda = DetalhesVenda(obj['nome_codigo_produto'], obj['nome_codigo_produto'], obj['nome_codigo_produto'])
    # db.session.add(detalhes_venda)
    # db.session.commit()
    # print("Antes de calcular o valor total dos detalhes da venda")
    # exibir_detalhes_venda(detalhes_venda)
    # detalhes_venda.calcular_valor_itens()
    # print("Depois de calcular o valor total dos detalhes da venda")
    # exibir_detalhes_venda(detalhes_venda)



@app.route("/editar_item/<id>", methods=['GET', 'POST'])
@login_required
def editar_item(id):
    print(id, " Peguei o id")
    detalhesVenda = DetalhesVenda.query.get(id)
    return json.dumps(detalhesVenda.serialized())
    # nome_codigo_produto = obj['nome_codigo_produto'].upper()
    # produto = Produto.query.filter(db.or_(Produto.codigo_barras == nome_codigo_produto, Produto.descricao_produto == nome_codigo_produto)).first()
    # if produto != None:
    #     return json.dumps(produto.serialized())
    # return json.dumps({"codigo_barras": 0})


@app.route("/deletar_item/<int:id>", methods=['GET', 'POST'])
@login_required
def deletar_item(id):
    print(id, " Cheguei")
    detalhesVenda = DetalhesVenda.query.get(id)
    if detalhesVenda:
        db.session.delete(detalhesVenda)
        db.session.commit()
        return json.dumps({"msg": "item deletado com sucesso!"})
    return json.dumps({"msg": 0})