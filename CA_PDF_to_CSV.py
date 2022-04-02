import csv
import os
import pdfplumber
from datetime import datetime
from pathlib import Path

FOLDER_PATH = Path(__file__).resolve().parent
PDF_SUB_FOLDER_NAME = "PDF"
CSV_SUB_FOLDER_NAME = "CSV"
DATE_IN_CSV_ROWS_FORMAT = '%d.%m'
# %d.%m <=> day/month ex: 25/12
CA_HEADER_ROW_INDICATOR = 'þ'
USELESS_LINES_CONTAIN = [
    'Total des opérations',
    'Nouveau solde',
    'Ancien solde'
]

def value_in_raw_row(row):
    """
    return value in debit or credit column
    row format = [date, value_date, label, value neg, value pos]
    """
    value = ""
    # get credit or debit value
    if row[3] and not row[4]:
        value = f'-{row[3]}'
    if row[4] and not row[3]:
        value = row[4]
    # replace numeric decimal value separator
    value = value.replace(".", "")
    return value


def string_is_date(str_date):
    """
    return a datetime object if strptime succeeded in converting 
    the string to a date
    """
    try:
        date = datetime. strptime(str_date, DATE_IN_CSV_ROWS_FORMAT)
        return date
    except:
        return None


def file_path(sub_folder_name, file_name, extension):
    """
    returns the file path whatever the os 
    """
    return os.path.join(
        FOLDER_PATH, sub_folder_name, f'{file_name}.{extension}'
    )


def clean_label(label):
    while "  " in label:
        label = label.replace("  ", " ")
    return label


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


def group_multi_line_descriptions(raw_list):
    """
    group descriptions on one line if they are on several lines
    """
    #work in progress
    rows_list = raw_list
    return rows_list


def tables_in_pdf(pdf_path):
    """
    extract the tables contained in the pdf
    """
    tables = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            for table in page.extract_tables():
                tables.append(table)
    return tables


def file_exist(path_checked):
    """ 
    return True if file exist
    """
    return os.path.isfile(path_checked)


def build_csv_file(global_csv):
    """
    buil the csv file
    """
    new_csv_file = file_path(CSV_SUB_FOLDER_NAME, "global_csv", "csv")
    with open(new_csv_file, "w", newline="") as csv_file:
        new_file = csv.writer(csv_file, delimiter=";")
        for row in global_csv:
            new_file.writerow(row)
    if file_exist(new_csv_file):
        return True
    return False

def row_is_useful(row):
    """
    check if a row is useful
    """
    if row[-1] == CA_HEADER_ROW_INDICATOR:
        return False
    for word in USELESS_LINES_CONTAIN:
        if word in row[2] :
            return False
    return True

def main():
    global_csv = []
    extracted_pdf_done = 0
    filenames_list = sorted(pdf_filenames())
    for file in filenames_list:
        pdf_path = file_path(PDF_SUB_FOLDER_NAME, file, 'pdf')
        page_rows = []
        for table in tables_in_pdf(pdf_path):
            for row in table:
                if row_is_useful(row):
                    page_rows.append(row)
        formatted_list = group_multi_line_descriptions(page_rows)
        if formatted_list:
            global_csv += formatted_list
            extracted_pdf_done += 1
        print(f'--> DONE  ({extracted_pdf_done}/{len(filenames_list)})\n')
    if build_csv_file(global_csv):
        print(
            f'csv file created: \"'
            f'{file_path(CSV_SUB_FOLDER_NAME, "global_csv","csv")}\"\n'
        )


if __name__ == '__main__':
    main()
