import csv, os, pdfplumber
from datetime import datetime
from pathlib import Path

FOLDER_PATH = Path(__file__).resolve().parent
PDF_SUB_FOLDER_NAME = "PDF"
CSV_SUB_FOLDER_NAME = "CSV"
DATE_IN_CSV_ROWS_FORMAT = '%d/%m/%Y' 
# %d/%m/%Y <=> day/month/year ex: 25/12/2021

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
    value = value.replace(".","")
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

def format(raw_list):
    """
        return a formatted list :
        select valid rows and transform from raw to formatted
        valid rows have 5 fields and first is a date:
        label on one row
        row1 = [date, value_date, label uniq part, value neg, value pos]
        or label on two rows
        row1 = [date, value_date, label 1st part , value neg, value pos]
        row2 = [    ,           , label 2nd part ,          ,          ]
        ----------------------------------------------------------------
        formatted = [date, value_date, value, label]

        will return an empty list if something is wrong during the conversion
    """
    rows_list = []
    for index,row in enumerate(raw_list):
        if len(row) == 5 and string_is_date(row[0]):
            try:
                next_row = ["not empty"]*5
                if index < len(raw_list)-1:
                    next_row = raw_list[index+1]
                date = row[0]
                value_date = row[1]
                label = row[2]
                # if row[0] is a date and the row[0] in the next row is 
                # empty : the label is on TWO row   
                if string_is_date(row[0]) and not next_row[0]:
                    next_row_label = next_row[2]
                    label = f'{label} {next_row_label}' 
                value = value_in_raw_row(row)
                row_to_add = [date, value_date, value, label]
                # return an empty rows_list and stop conversion if not  
                # all field are present in the row to add
                if all(field for field in row_to_add):
                    rows_list.append(row_to_add)
                else:
                    print(
                        f'!!! problem with row {index} : {row}\n'
                        f'one or more field are missing'
                    )
                    rows_list = []
                    break                        
            except Exception as problem:
                print(f'!!! problem with row {index} : {row}\n{problem}')
                rows_list = []
                
    return rows_list

def tables_in_pdf(pdf_path):
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
    new_csv_file = file_path(CSV_SUB_FOLDER_NAME, "global_csv","csv")
    with open(new_csv_file, "w", newline="") as csv_file :
        new_file = csv.writer(csv_file, delimiter=";")
        for row in global_csv:
            new_file.writerow(row)
    if file_exist(new_csv_file):
        return True
    return False

def main():
    global_csv = []
    for file in sorted(pdf_filenames()):
        print(f'\n{file}')
        pdf_path = file_path(PDF_SUB_FOLDER_NAME, file, 'pdf')
        for table in tables_in_pdf(pdf_path):
            formatted_list = format(table)
            if formatted_list:
                global_csv += formatted_list
        print(f'--> DONE\n')
    if build_csv_file(global_csv):
        print(
            f'csv file created:\n\n'
            f'{file_path(CSV_SUB_FOLDER_NAME, "global_csv","csv")}\n'
        )
if __name__ == '__main__':
    main()