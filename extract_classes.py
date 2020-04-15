import PyPDF2
import re
import os
import pandas as pd

ra_regex = re.compile(r"^\d{11}$|^\d{8}$")
turma_regex = re.compile(r".*-\d\d(SA|SB)$")

def extract_text_from_pdf(input_pdf, output_txt):
    pdf_file = open(input_pdf, 'rb')
    read_pdf = PyPDF2.PdfFileReader(pdf_file)
    number_of_pages = read_pdf.getNumPages()
    
    pdf_content = []
    for i in range(number_of_pages):
        print(f'appending page {i} of {number_of_pages}')
        page = read_pdf.getPage(i)
        page_content = page.extractText()
        pdf_content.append(page_content)

    pdf_file.close()

    with open(output_txt, 'w', encoding='utf-8') as deferidas:   
        c = 1
        for page in pdf_content:
            print(f'page {c} of {number_of_pages}')
            deferidas.write(page)
            c+=1

def create_classes_dataframe_from_xlsx(xlsx_file):
    labels = ['Código', 'Disicplina - turma', 'teoria', 'prática', 'docente teoria', 'docente prática']
    df = pd.read_excel(xlsx_file)

    df.drop(df[(df[labels[0]] == labels[0]) & (df[labels[1]] == labels[1]) & (df[labels[5]] == labels[5])].index, inplace=True)
    df.reset_index(inplace=True)
    df = df.drop('index', 1)

    df.loc[df[labels[2]] == 0, labels[2]] = ''
    df.loc[df[labels[3]] == 0, labels[3]] = ''
    df.loc[df[labels[4]] == 0, labels[4]] = ''
    df.loc[df[labels[5]] == 0, labels[5]] = ''

    df = df.fillna('')
    df.drop(df.columns.difference(labels), 1, inplace=True)

    return df

def get_classes(deferidas_file, ra):
    # ! comentar sobre uso de replace para nomear o arquivo de output txt
    if not os.path.isfile(deferidas_file.replace('.pdf', '.txt')):
        extract_text_from_pdf(deferidas_file, deferidas_file.replace('.pdf', '.txt'))

    cod_turmas_aluno = {
        'SA': [],
        'SB': []
    }
    
    cod_turmas_lista = []
    ra_lista = []
    
    with open(deferidas_file.replace('.pdf', '.txt'), 'r', encoding='utf-8') as file:
        all_lines = file.readlines()
        
        for line in all_lines:
            if ra_regex.match(line):
                ra_lista.append(line)
        
            if turma_regex.match(line):
                cod_turmas_lista.append(line)

    for i in range (len(ra_lista)):
        if ra in ra_lista[i]:
            # !comentar sobre remover \n do final
            cod_turma = cod_turmas_lista[i].strip()
            if cod_turma[-2:] == "SA":
                cod_turmas_aluno['SA'].append(cod_turma)
            elif cod_turma[-2:] == "SB":
                cod_turmas_aluno['SB'].append(cod_turma)
    
    if cod_turmas_aluno['SA']:
        df_sa = create_classes_dataframe_from_xlsx('turmas_sa.xlsx')
        df_sa.rename(columns={
            'Código':'codigo', 'Disicplina - turma':'disciplina',
            'prática':'pratica', 'docente teoria':'docente_teoria',
            'docente prática':'docente_pratica'    

        }, inplace=True)

        df_sa.set_index("codigo", inplace=True)

    if cod_turmas_aluno['SB']:
        df_sb = create_classes_dataframe_from_xlsx('turmas_sb.xlsx')
        df_sb.rename(columns={
            'Código':'codigo', 'Disicplina - turma':'disciplina',
            'prática':'pratica', 'docente teoria':'docente_teoria',
            'docente prática':'docente_pratica'    

        }, inplace=True) 
        df_sb.set_index("codigo", inplace=True)
    
    aulas = []
    for turma in cod_turmas_aluno['SA']:
        try:
            disc = df_sa.loc[turma].to_dict()
            disc.update({'campus': 'Santo André'})
            disc['disciplina'] = disc['disciplina'].replace('(Santo André)', '').strip()
            aulas.append(disc)
        except:
            pass
    
    for turma in cod_turmas_aluno['SB']:
        try:
            disc = df_sb.loc[turma].to_dict()
            disc.update({'campus': 'São Bernardo do Campo'})
            disc['disciplina'] = disc['disciplina'].replace('(São Bernardo do Campo)', '').strip()
            aulas.append(disc)
        except:
            pass

    return aulas

print(get_classes('deferidas.pdf', '11002112'))