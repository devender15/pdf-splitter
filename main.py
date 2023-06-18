import itertools
from PyPDF2 import PdfWriter, PdfReader
import os
import shutil
from rich import print as rprint
from rich.tree import Tree
import fitz
from PIL import Image
import pandas as pd
import time
import string
import random


# specify the directory names
INPUT_DIR = 'inputs'
OUTPUT_DIR = 'output'

# main code

# creating output folder if not exists
if (not os.path.exists(OUTPUT_DIR)):
    os.mkdir(OUTPUT_DIR)
else:
    shutil.rmtree(OUTPUT_DIR)
    os.mkdir(OUTPUT_DIR)

# Specify the input PDF file path and the output directory path
pdf_path = None

# gettings the list of pdfs
pdfs = [pdf for pdf in os.listdir(INPUT_DIR + "/") if pdf.endswith(".pdf")]

# initializing the counter for the total number of PDFs generated in the output folder
PDF_COUNT = 0
FAILED_PDF_COUNT = 0
PDF_DATA = []
START_TIME = time.time()

# Define the page sizes
PAGE_SIZES = {
    "A3": {
        "width": 842,
        "height": 1191,
    },
    "A4": {
        "width": 595,
        "height": 842,
    },
    "A5": {
        "width": 420,
        "height": 595,
    },
}

# functions


def generateUniqueId():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))


def generateImages(pdf_name, output_folder, output_filename, main_id):

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    doc = fitz.open(pdf_name)

    for i, page in enumerate(doc):
        image_name = f"page_{i+1}.jpg"
        image_path = os.path.join(output_folder, image_name)
        pix = page.get_pixmap()
        pix._writeIMG(image_path, format=100)

        # Open the image file with PIL
        image = Image.open(image_path)

        # Resize the image to A3 size (297 x 420 mm)
        a3_size = (PAGE_SIZES["A3"]['width'], PAGE_SIZES["A3"]['height'])
        image_a3 = image.resize(a3_size)
        image_a3.save(os.path.join(output_folder, f"a3_{image_name}"))

        # Resize the image to A4 size (210 x 297 mm)
        a4_size = (PAGE_SIZES["A4"]['width'], PAGE_SIZES["A4"]['height'])
        image_a4 = image.resize(a4_size)
        image_a4.save(os.path.join(output_folder, f"a4_{image_name}"))

        separate_jpg_file_name = "a4_" + \
            image_name.split(".")[0] + f"_ID_{main_id}.jpg"

        # saving this a4 generated pdf to the outside of this folder by creating a folder with name of this folder
        image_a4.save(os.path.join(
            output_folder, f"../../../A4/{output_filename[:-4]}", separate_jpg_file_name))

        # Resize the image to A5 size (148 x 210 mm)
        a5_size = (PAGE_SIZES["A5"]['width'], PAGE_SIZES["A5"]['height'])
        image_a5 = image.resize(a5_size)
        image_a5.save(os.path.join(output_folder, f"a5_{image_name}"))

        # delete the original image
        os.remove(image_path)


def saveResizedPdfs(pdf_name, output_folder, main_file_name):

    for page_size in ["A3", "A4", "A5"]:

        input_pdf = PdfReader(pdf_name)
        output_pdf = PdfWriter()

        for pdf_page_num in range(len(input_pdf.pages)):
            input_page = input_pdf.pages[pdf_page_num]
            input_page.scale_to(
                width=PAGE_SIZES[page_size]['width'], height=PAGE_SIZES[page_size]['height'])
            output_pdf.add_page(input_page)

        # saving the pdf with the page size in the file name
        output_filename = f"{page_size}_{main_file_name}"
        output_pdf.write(os.path.join(output_folder, output_filename))


def savePDF(output_dir, output_filename, main_id=None):

    main_id = '' if main_id is None else main_id

    # creating a folder of this variant
    os.mkdir(os.path.join(
        output_dir, output_filename.split(".")[0]))

    # create a folder named 'jpeg' inside this new folder
    os.mkdir(os.path.join(
        output_dir, output_filename.split(".")[0], f"jpg_ID_{main_id}"))
    os.mkdir(os.path.join(
        output_dir, output_filename.split(".")[0], f"pdfs_ID_{main_id}"))

    # saving this variant in this new folder
    with open(os.path.join(output_dir, output_filename.split(".")[0], output_filename), 'wb') as output_file:
        pdf_writer.write(output_file)

    tree.add(f"---> Saving PDFs of different sizes for {output_filename}...")

    # read this pdf file and resize it to A3, A4 and A5 size and save it in the 'pdfs' folder
    saveResizedPdfs(os.path.join(output_dir, output_filename.split(".")[0], output_filename), os.path.join(
        output_dir, output_filename.split(".")[0], f"pdfs_ID_{main_id}"), output_filename)

    tree.add(f"---> Generating images for {output_filename}...")

    # generate images from this pdf
    generateImages(os.path.join(output_dir, output_filename.split(".")[0], output_filename),
                   os.path.join(output_dir, output_filename.split(".")[0], f"jpg_ID_{main_id}"), output_filename, main_id)

    # finally delete the main pdf file
    os.remove(os.path.join(
        output_dir, output_filename.split(".")[0], output_filename))

    tree.add(f"---> Creating a .zip file for {output_filename}...")
    # now create a .zip file of the parent folder and keep it in the same parent folder
    shutil.make_archive(os.path.join(output_dir, output_filename.split(".")[0]), 'zip', os.path.join(
        output_dir, output_filename.split(".")[0]))

    shutil.rmtree(os.path.join(
        output_dir, output_filename.split(".")[0]))

    # create a new folder outside of this folder named zipped file original name
    os.mkdir(os.path.join(
        output_dir, output_filename.split(".")[0]))

    # create a new folder inside this folder named 'images'
    os.mkdir(os.path.join(
        output_dir, output_filename.split(".")[0], "images"))

    # now move the zipped file to this new folder
    shutil.move(os.path.join(output_dir, output_filename.split(".")[0]+".zip"), os.path.join(
        output_dir, output_filename.split(".")[0] + "/"))


def generateExcelSheet():
    # rprint(PDF_DATA)
    if (len(pdfs) > 1):
        data = pd.DataFrame(data=PDF_DATA)
    else:
        data = pd.DataFrame(data=PDF_DATA)
    data.to_excel(os.path.join(OUTPUT_DIR, "pdf_names.xlsx"), index=False)


def formatTime(seconds):
    seconds = round(seconds)
    if seconds < 60:
        return f"{seconds} seconds"
    elif seconds < 3600:
        return f"{seconds//60} minutes {seconds%60} seconds"
    else:
        return f"{seconds//3600} hours {(seconds%3600)//60} minutes {seconds%60} seconds"


rprint("[bold violet]Script started...[/bold violet]")

for pdf in pdfs:
    pdf_path = os.path.join(INPUT_DIR, pdf)
    pdf_name = pdf.split(".")[0]
    original_name = pdf_name
    # reducing the pdf name
    if len(pdf_name) > 28:
        pdf_name = pdf_name[:28]

    # remove whitespace from the end if exists
    if pdf_name[-1] == " ":
        pdf_name = pdf_name[:-1]

    output_dir = os.path.join(OUTPUT_DIR, pdf_name)

    # creating A4 folder
    if (not os.path.exists(os.path.join(OUTPUT_DIR, 'A4'))):
        os.mkdir(os.path.join(OUTPUT_DIR, 'A4'))

    tree = Tree(f"🔰 [bold green]{original_name}[/bold green]")

    rprint(f"[bold red]Processing '{original_name}...[/bold red]'")

    # setting output directory for each type of pdf
    os.mkdir(output_dir)

    # Open the PDF file and get the number of pages
    pdf_file = open(pdf_path, 'rb')
    pdf_reader = PdfReader(pdf_file)
    num_pages = len(pdf_reader.pages)

    # putting the original file in the output folder
    try:
        # read this pdf and then save it
        pdf_writer = PdfWriter()
        for page in pdf_reader.pages:
            pdf_writer.add_page(page)

        file_id = generateUniqueId()
        output_filename = f"{pdf_name}_original_ID_{file_id}.pdf"

        # create a folder with name of pdf in A4 folder
        os.mkdir(os.path.join(OUTPUT_DIR, 'A4', output_filename[:-4]))
        # run same operation on the original file
        savePDF(output_dir, output_filename, file_id)
        PDF_DATA.append({'Original Name': original_name,
                        'Reduced Name': f"{pdf_name}_original_{file_id}", 'Id': file_id})
        tree.add(f"[sandy_brown]Original PDF ✅[/sandy_brown]")

    except:
        tree.add(f"[red]Original PDF ❌[/red]")

    PDF_COUNT += 1

    # Generate all possible combinations of page numbers in sets of 1 and 2
    page_combinations = []
    for i in range(1, 3):
        combinations = list(itertools.combinations(range(num_pages), i))
        page_combinations.extend(combinations)

    # Generate 2 PDF files with 1 page each for an input PDF file with 2 pages
    if num_pages == 2:
        # Split into combinations of 1
        for i, page_num in enumerate(range(num_pages)):
            try:
                pdf_writer = PdfWriter()
                file_id = generateUniqueId()
                page = pdf_reader.pages[page_num]
                page.compress_content_streams()
                pdf_writer.add_page(page)
                output_filename = f"{pdf_name}_set-1_variant-{i+1}_ID_{file_id}.pdf"
                reduced_name = f"{pdf_name}_set-1_variant-{i+1}.pdf"

                # create a folder with name of pdf in A4 folder
                os.mkdir(os.path.join(OUTPUT_DIR, 'A4', output_filename[:-4]))

                savePDF(output_dir, output_filename, file_id)
                # saving the original and new name of pdf in PDF_DATA
                PDF_DATA.append({'Original Name': original_name,
                                'Reduced Name': reduced_name, 'Id': file_id})

                PDF_COUNT += 1
                tree.add(f"Set of 1 variant - {page_num+1} ✅")

            except Exception as e:
                FAILED_PDF_COUNT += 1
                tree.add(f"Set of 1 variant - {page_num+1} ❌")
                rprint(e)

    # Generate 3 PDF files with 1 page each for an input PDF file with 3 pages
    if num_pages == 3:
        # Split into combinations of 2 and 1
        page_ranges = itertools.combinations(range(num_pages), 2)
        for i, page_range in enumerate(page_ranges):
            try:
                pdf_writer = PdfWriter()
                for page_num in page_range:
                    pdf_writer.add_page(pdf_reader.pages[page_num])
                file_id = generateUniqueId()
                output_filename = f"{pdf_name}_set-2_variant-{i+1}_ID_{file_id}.pdf"
                reduced_name = f"{pdf_name}_set-2_variant-{i+1}.pdf"

                # create a folder with name of pdf in A4 folder
                os.mkdir(os.path.join(OUTPUT_DIR, 'A4', output_filename[:-4]))

                savePDF(output_dir, output_filename, file_id)
                # saving the original and new name of pdf in PDF_DATA
                PDF_DATA.append({'Original Name': original_name,
                                'Reduced Name': reduced_name, 'Id': file_id})

                PDF_COUNT += 1
                tree.add(f"Set of 2 variant - {i+1} ✅")

            except Exception as e:
                rprint(e)
                FAILED_PDF_COUNT += 1
                tree.add(f"Set of 2 variant - {i+1} ❌")

        # Split into combinations of 1
        for i, page_num in enumerate(range(num_pages)):
            try:
                pdf_writer = PdfWriter()
                file_id = generateUniqueId()
                page = pdf_reader.pages[page_num]
                page.compress_content_streams()
                pdf_writer.add_page(page)
                output_filename = f"{pdf_name}_set-1_variant-{i+1}_ID_{file_id}.pdf"
                reduced_name = f"{pdf_name}_set-1_variant-{i+1}.pdf"

                # create a folder with name of pdf in A4 folder
                os.mkdir(os.path.join(OUTPUT_DIR, 'A4', output_filename[:-4]))

                savePDF(output_dir, output_filename, file_id)
                # saving the original and new name of pdf in PDF_DATA
                PDF_DATA.append({'Original Name': original_name,
                                'Reduced Name': reduced_name, 'Id': file_id})

                PDF_COUNT += 1
                tree.add(f"Set of 1 variant - {page_num+1} ✅")

            except:
                FAILED_PDF_COUNT += 1
                tree.add(f"Set of 1 variant - {page_num+1} ❌")

    # Generate all possible combinations of sets of 3 pages for an input PDF file with 6 pages
    if num_pages == 6:
        for page_set in [3, 2, 1]:

            page_ranges_set_six = itertools.combinations(
                range(num_pages), page_set)

            for i, page_range in enumerate(page_ranges_set_six):
                try:
                    pdf_writer = PdfWriter()
                    for page_num in page_range:
                        pdf_writer.add_page(pdf_reader.pages[page_num])
                    file_id = generateUniqueId()
                    output_filename = f"{pdf_name}_set-{page_set}_variant-{i+1}_ID_{file_id}.pdf"
                    reduced_name = f"{pdf_name}_set-{page_set}_variant-{i+1}.pdf"

                    # create a folder with name of pdf in A4 folder
                    os.mkdir(os.path.join(
                        OUTPUT_DIR, 'A4', output_filename[:-4]))

                    savePDF(output_dir, output_filename, file_id)
                    # saving the original and new name of pdf in PDF_DATA
                    PDF_DATA.append(
                        {'Original Name': original_name, 'Reduced Name': reduced_name, 'Id': file_id})

                    PDF_COUNT += 1
                    tree.add(f"Set of {page_set} variant - {i+1} ✅")

                except Exception as e:
                    rprint(e)
                    FAILED_PDF_COUNT += 1
                    tree.add(f"Set of {page_set} variant - {i+1} ❌")

    # showing the tree
    rprint(tree)

    # Close the input PDF file
    pdf_file.close()


# saving the PDF_DATA in a csv file
generateExcelSheet()

# calculating the time taken to process the PDFs
END_TIME = time.time()

# final pdf generated count
PDF_COUNT *= 3

# showing the summary of the output
rprint(
    "[bold blue]-------------------------Summary of the output-------------------------")
rprint(
    f"[dark_olive_green2]Time taken by script: {formatTime(END_TIME - START_TIME)}[/dark_olive_green2]")
rprint(f"[dark_olive_green2]Input directory: {INPUT_DIR}[/dark_olive_green2]")
rprint(
    f"[dark_olive_green2]Output directory: {OUTPUT_DIR}[/dark_olive_green2]")
rprint(f"[dark_olive_green2]Total input PDFs: {len(pdfs)}[/dark_olive_green2]")
rprint(
    f"[dark_olive_green2]Total PDFs in output: {len(os.listdir(OUTPUT_DIR)) - 2}[/dark_olive_green2]")
rprint(
    f"[dark_olive_green2]Total PDFs generated: {PDF_COUNT}[/dark_olive_green2]")
rprint(
    f"[dark_olive_green2]Total PDFs failed: {FAILED_PDF_COUNT}[/dark_olive_green2]")
