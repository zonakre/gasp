"""
Code to be adapted
"""

# Calcula as frequencias absolutas e relativas para intervalos pre-definidos
def calculo_frequencias(xls_entrada, folha_entrada, coluna, xls_saida, intervalos):
    import xlwt, xlrd
    # ler ficheiro entrada
    excel = xlrd.open_workbook(xls_entrada)
    livro = excel.sheet_by_name(folha_entrada)
    lista_valores = []
    for contracto in range(1,livro.nrows):
        cell = livro.cell(contracto, coluna)
        cell_value = cell.value
        lista_valores.append(float(cell_value))
    frequencias = []
    logos = 0
    classes = len(intervalos) + 1
    for i in range(classes):
        freq_absoluta = 0
        if logos == 0:   
            for e in range(len(lista_valores)):
                if lista_valores[e] <= intervalos[i]:
                    freq_absoluta += 1
        else:
            if logos != len(intervalos):
                for e in range(len(lista_valores)):
                    o = i -1
                    if lista_valores[e] > intervalos[o] and lista_valores[e] <= intervalos[i]:
                        freq_absoluta +=1
            else:
                for e in range(len(lista_valores)):
                    if lista_valores[e] > intervalos[-1]:
                        freq_absoluta +=1
        frequencias.append(freq_absoluta)
        logos += 1
    #criar excel
    livro = xlwt.Workbook()
    add_livro = livro.add_sheet('frequencias')
    # Título das colunas
    titulos = ['classe', 'freq_abs', 'freq_abs_acu', 'freq_rel', 'freq_rel_acu']
    for i in range(len(titulos)):
        add_livro.write(0, i, titulos[i])
    # Escreve frequências
    contador = 0
    e = 1
    for i in range(len(frequencias)):
        # Frequencia absoluta
        add_livro.write(e, 1, frequencias[i])
        # Frequencia relativa
        freq_relativa = (frequencias[i] / float(len(lista_valores)))*100
        add_livro.write(e, 3, freq_relativa)
        if contador == 0:
            # Frequência absoluta acumulada
            add_livro.write(e, 2, frequencias[i])
            # Frequência relativa acumulada
            add_livro.write(e, 4, freq_relativa)
        else:
            temp = 0
            for freq in range(i+1):
                temp = temp + frequencias[freq]
            # Frequência absoluta acumulada
            add_livro.write(e, 2, temp)
            # Frequência relativa acumulada
            freq_relativa = (temp / float(len(lista_valores)))*100
            add_livro.write(e, 4, freq_relativa)
        e +=1
        contador += 1
    livro.save(xls_saida)

def que_respostas(folha, coluna_pergunta):
    lst = []
    for i in range(1, folha.nrows):
        resposta = folha.cell(i, coluna_pergunta).value
        lst.append(resposta)
    nova = numpy.unique(lst)
    return nova
def percentagem(tabela, folha, pergunta):
    tab = xlrd.open_workbook(tabela)
    l = tab.sheet_by_name(folha)
    nr_inqueritos = 0
    for i in range(1, l.nrows):
        nr_inqueritos += 1
    respostas = que_respostas(l, pergunta)
    nr_respostas = []
    for resposta in respostas:
        c = 0
        for i in range(1, l.nrows):
            valor = l.cell(i, pergunta).value
            if resposta == valor:
                c += 1
        nr_respostas.append(c)
    dic = {}
    for resposta in range(len(respostas)):
        dic.update({respostas[resposta]: [nr_respostas[resposta], nr_respostas[resposta]/ float(nr_inqueritos) * 100.0]})
    print dic

# Da tabela que contém toda a informação sobre os contractos extrai e regista os gastos tidos por cada um dos ógãos envolvidos 
def cria_tabela_orgaos(xls_entrada, folha_entrada, col_org, col_euros, xls_saida):
    import xlwt, xlrd, numpy
    excel = xlrd.open_workbook(xls_entrada)
    livro = excel.sheet_by_name(folha_entrada)
    orgaos = []
    for contrato in range(1, livro.nrows):
        cell = livro.cell(contrato, col_org)
        value = cell.value
        orgaos.append(value)
    id_orgaos = numpy.unique(orgaos)
    del orgaos
    dic = {}
    for orgao in id_orgaos:
        montante = 0
        for contrato in range(1, livro.nrows):
            cell = livro.cell(contrato, col_org)
            _orgao_ = cell.value
            if int(orgao) == int(_orgao_):
                _euros_ = livro.cell(contrato, col_euros)
                euros = float(_euros_.value)
                montante += euros
        dic.update({orgao:montante})
    excel = xlwt.Workbook()
    add = excel.add_sheet('orgaos')
    add.write(0, 0, 'orgao')
    add.write(0,1, 'euros')
    nr = 1
    for orgao in dic.keys():
        add.write(nr, 0, orgao)
        add.write(nr, 1, dic[orgao])
        nr += 1
    excel.save(xls_saida)
cria_tabela_orgaos(r"C:\Dropbox\MTIG_Cronicas2.0\Jangada2015\bd_DespS4OS.xls", "bd_sforos", 3, 9, r"C:\gis\XYZ\orgaos_s4os.xls")

