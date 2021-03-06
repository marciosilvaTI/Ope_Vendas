"""empty message

Revision ID: dddf930c8371
Revises: 
Create Date: 2021-06-05 17:57:30.173747

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dddf930c8371'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('categoria',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('nome_categoria', sa.String(length=30), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('nome_categoria')
    )
    op.create_table('cliente',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('nome', sa.String(length=50), nullable=False),
    sa.Column('telefone', sa.String(length=11), nullable=False),
    sa.Column('data_pagamento', sa.DateTime(), nullable=False),
    sa.Column('data_ultima_compra', sa.DateTime(), nullable=True),
    sa.Column('valor_divida', sa.Float(precision=2), nullable=True),
    sa.Column('status', sa.Boolean(), nullable=True),
    sa.Column('cpf', sa.String(length=11), nullable=True),
    sa.Column('observacao', sa.String(length=50), nullable=True),
    sa.Column('inativado', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('telefone')
    )
    op.create_table('justificativa',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('justificativa', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('justificativa')
    )
    op.create_table('marca',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('nome_marca', sa.String(length=30), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('nome_marca')
    )
    op.create_table('medida',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('nome_medida', sa.String(length=30), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('nome_medida')
    )
    op.create_table('nivel_acesso',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('nivel_acesso', sa.String(length=20), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('nivel_acesso')
    )
    op.create_table('tipo_pagamento',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('tipo_pagamento', sa.String(length=15), nullable=False),
    sa.Column('cod_tipo_pagamento', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('cod_tipo_pagamento'),
    sa.UniqueConstraint('tipo_pagamento')
    )
    op.create_table('produto',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('codigo_barras', sa.String(length=50), nullable=False),
    sa.Column('descricao_produto', sa.String(length=40), nullable=False),
    sa.Column('quantidade_produto', sa.Integer(), nullable=False),
    sa.Column('quantidade_minima', sa.Integer(), nullable=False),
    sa.Column('preco_custo', sa.Float(precision=2), nullable=False),
    sa.Column('preco_venda', sa.Float(precision=2), nullable=False),
    sa.Column('valor_desconto', sa.Float(precision=2), nullable=True),
    sa.Column('quantidade_maxima', sa.Integer(), nullable=True),
    sa.Column('peso_liquido', sa.Float(), nullable=True),
    sa.Column('peso_bruto', sa.Float(), nullable=True),
    sa.Column('id_categoria_id', sa.Integer(), nullable=False),
    sa.Column('id_marca_id', sa.Integer(), nullable=False),
    sa.Column('id_medida_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['id_categoria_id'], ['categoria.id'], ),
    sa.ForeignKeyConstraint(['id_marca_id'], ['marca.id'], ),
    sa.ForeignKeyConstraint(['id_medida_id'], ['medida.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('codigo_barras')
    )
    op.create_table('usuario',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('nome', sa.String(length=50), nullable=False),
    sa.Column('telefone', sa.String(length=11), nullable=False),
    sa.Column('email', sa.String(length=50), nullable=False),
    sa.Column('login', sa.String(length=25), nullable=False),
    sa.Column('senha', sa.String(length=128), nullable=False),
    sa.Column('status', sa.Boolean(), nullable=True),
    sa.Column('recuperou_senha', sa.Boolean(), nullable=True),
    sa.Column('inativado', sa.Boolean(), nullable=True),
    sa.Column('id_nivel_acesso_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['id_nivel_acesso_id'], ['nivel_acesso.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('login')
    )
    op.create_table('venda',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('data_venda', sa.DateTime(), nullable=True),
    sa.Column('valor_total', sa.Float(precision=2), nullable=True),
    sa.Column('valor_desconto', sa.Float(precision=2), nullable=True),
    sa.Column('cod_status_venda', sa.Integer(), nullable=False),
    sa.Column('observacao', sa.String(length=100), nullable=True),
    sa.Column('id_usuario_id', sa.Integer(), nullable=False),
    sa.Column('id_cliente_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['id_cliente_id'], ['cliente.id'], ),
    sa.ForeignKeyConstraint(['id_usuario_id'], ['usuario.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('detalhes_pagamento',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('valor', sa.Float(precision=2), nullable=True),
    sa.Column('id_tipo_pagamento_id', sa.Integer(), nullable=False),
    sa.Column('id_venda_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['id_tipo_pagamento_id'], ['tipo_pagamento.id'], ),
    sa.ForeignKeyConstraint(['id_venda_id'], ['venda.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('detalhes_venda',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('numero_item', sa.Integer(), nullable=False),
    sa.Column('quantidade_produto', sa.Integer(), nullable=False),
    sa.Column('valor_produto', sa.Float(precision=2), nullable=True),
    sa.Column('valor_desconto_produto', sa.Float(precision=2), nullable=True),
    sa.Column('valor_desconto_adicional', sa.Float(precision=2), nullable=True),
    sa.Column('observacao', sa.String(length=100), nullable=True),
    sa.Column('id_venda_id', sa.Integer(), nullable=False),
    sa.Column('id_produto_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['id_produto_id'], ['produto.id'], ),
    sa.ForeignKeyConstraint(['id_venda_id'], ['venda.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('movimentacao_caixa',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('valor_movimentacao', sa.Float(precision=2), nullable=False),
    sa.Column('data_movimentacao', sa.DateTime(), nullable=True),
    sa.Column('status', sa.Boolean(), nullable=True),
    sa.Column('observacao', sa.String(length=50), nullable=True),
    sa.Column('id_venda_id', sa.Integer(), nullable=True),
    sa.Column('id_justificativa_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['id_justificativa_id'], ['justificativa.id'], ),
    sa.ForeignKeyConstraint(['id_venda_id'], ['venda.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('movimentacao_caixa')
    op.drop_table('detalhes_venda')
    op.drop_table('detalhes_pagamento')
    op.drop_table('venda')
    op.drop_table('usuario')
    op.drop_table('produto')
    op.drop_table('tipo_pagamento')
    op.drop_table('nivel_acesso')
    op.drop_table('medida')
    op.drop_table('marca')
    op.drop_table('justificativa')
    op.drop_table('cliente')
    op.drop_table('categoria')
    # ### end Alembic commands ###
