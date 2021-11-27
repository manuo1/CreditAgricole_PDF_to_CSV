import csv, os
from pathlib import Path
import pdfplumber

FOLDER_PATH = Path(__file__).resolve().parent
PDF_SUB_FOLDER_NAME = "PDF"
CSV_SUB_FOLDER_NAME = "CSV"

def file_path(sub_folder_name, file_name, extension):
    """
    returns the file path whatever the os 
    """
    return os.path.join(
        FOLDER_PATH, sub_folder_name, f'{file_name}.{extension}'
    )


def pdf_filenames():
    """
    return a list of pdf file names in the PDF folder
    """
    filenames = []
    for file in os.listdir(os.path.join(FOLDER_PATH, PDF_SUB_FOLDER_NAME)):
        filename, extension = os.path.splitext(file)
        if "pdf" in extension.lower():
            filenames.append(filename)
    return filenames

def main():
    pdf_doc = file_path(PDF_SUB_FOLDER_NAME, pdf_filenames()[0], 'pdf')
    
    
    with pdfplumber.open(pdf_doc) as pdf:
        first_page = pdf.pages[0]
        table = first_page.extract_tables()
    for index, sub_row in enumerate(table):
        print(f'{index} \n')
        for row in sub_row:
            print(f'{row} \n')


   
    print(pdf_filenames()[0])

if __name__ == '__main__':
    main()