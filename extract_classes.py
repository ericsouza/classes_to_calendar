import PyPDF2
import re

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


def get_classes(deferidas_file, ra):
    
    # ! comentar sobre uso de replace para nomear o arquivo de output txt
    #extract_text_from_pdf(deferidas_file, deferidas_file.replace('.pdf', '.txt'))

    cod_turmas_aluno = []
    
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
            cod_turmas_aluno.append(cod_turmas_lista[i].strip())
    
    has_sa = False
    has_sbc = False

    for turma in cod_turmas_aluno:
        if turma[-2:] == "SA":
            has_sa = True
        elif turma[-2:] == "SB":
            has_sbc = True

    print(cod_turmas_aluno)
    print('Santo andré? ', has_sa, '| São Bernardo?', has_sbc)


get_classes('deferidas.pdf', '11201720512')