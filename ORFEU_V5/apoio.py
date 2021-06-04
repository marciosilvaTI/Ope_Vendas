'''
a=13.946
print(a)
# 13.946
print("%.2f" % a)
# 13.95
round(a, 2)
13.949999999999999
print("%.2f" % round(a,2))
# 13.95
print("{0:.2f}".format(a))
# 13.95
print("{0:.2f}".format(round(a,2)))
# 13.95
print("{0:.15f}".format(round(a,2)))
# 13.949999999999999
'''

'''
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from random import choice
import string

from random import shuffle

j1 = ['Jose', 'Bruno', 'Lucas', 'Eduardo', 'Pedro', 'Luciano', 'Vitor', 'Diego', 'Rômulo', '*Pisca']
j2 = ['Carlinhos', 'Carlos', 'Davi', 'Thiago', 'Paulo', 'Igor', 'Felipe', 'Marcelo', 'Matheus', 'Fabio']
j3 = ['Artur', 'Anderson', 'Gustavo', 'Rogerio', 'Marcus', 'Nando', 'Jorge', 'Rodrigo', 'Caio', 'Jonas']

shuffle(j1)
shuffle(j2)
shuffle(j3)

fones = string.digits
nome = ""
fone = ""
data = '10/06/2021'
for n, (c1, c2, c3) in enumerate(zip(j1, j2, j3), start=1):
    nome = c1 + " " + c2 + " " + c3
    fone = "11" + choice(fones) + choice(fones) + choice(fones) + choice(fones) + choice(fones) + choice(fones) + choice(fones) + choice(fones)
    print(nome)
    print(fone)
    print(data)
'''
