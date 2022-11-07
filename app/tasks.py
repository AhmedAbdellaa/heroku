#multi threding 

import fitz
from PIL import Image
from pyzbar.pyzbar import decode
import re
import pytesseract
import time

import os
import glob
import sys
import shutil
import concurrent.futures
import logging

def decode_(image):
    deco = decode(image)
    
    # print(deco)
    if len(deco) == 0 :
        text = pytesseract.image_to_string(image)
        text = re.sub(',','9',text)
        text = re.sub('\n\n','\n',text)
        tt = " "
        numberslist = [t for t in text.split('\n') if t.isnumeric()]
        tt = tt.join(numberslist)
        # print(tt)
        return tt
    else:
        for d in deco:
            barcode = d.data.decode('utf-8')
            # if barcode not in numberslist :
            #     tt = tt + " " + barcode
            return  barcode 

def get_barcode(page):
    mat = fitz.Matrix(5,5)
    clip = fitz.Rect(20,20,220,220)  # the area we want
    pix = page.get_pixmap(matrix=mat, clip=clip)
    # data = pix.getImageData()
    image = Image.frombytes('RGB', [pix.width, pix.height], pix.samples)
    return image

def process_page(page):
    # print("inside page")
    #helper method to run in pallar
    #get left up conrner from pdf page(image)
    image = get_barcode(page)
    #decode it  to text of number
    code = decode_(image)
    #clean content from page before add text
    page.clean_contents()
    
    page.insert_text(fitz.Point(350,35), code, fontsize=6, fontname="Times-Roman",color=(0, 0, 0))

def read_pdf(doc_pdf,save_path,MAX_WORKERS):
    start_time = time.time()
    #as i have multi page and each one can run indpendent i will use multiprocessing to make it fast
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor :
        executor.map(process_page,doc_pdf)
    # for page in doc_pdf:
    #     process_page(page)
    #save doc_pdf to the given path
    doc_pdf.save(save_path)
    #close fitz after finish
    doc_pdf.close()

    end_time = time.time()
    logging.info(f"time elabsed = {end_time - start_time}")
    return 1 #done succefully


def join_read(dir_path,save_path,MAX_WORKERS):
    """
    dir_path : input folder conting file want to read its number 
    save_path : dir to save output pdf file
    output 
        0 if function faild
        1 if it done successfully
    """
    start = time.time()
    #list all pdf in dir
    pdfs =[os.path.join(dir_path,pdf_name) for pdf_name in glob.glob(os.path.join(dir_path,'*.pdf')) ]
    #check if there is pdf in dir
    if len(pdfs) != 0 :
        #initalize fitz opject to read pdf
        doc = fitz.open()
        # loop over each pdf file and insert it to doc
        for fil in pdfs :
            try :
                #with for open file temporary
                with fitz.open(fil) as mydoc :
                    #join pdf
                    doc.insert_pdf(mydoc)
            except :
                return 0
        result =read_pdf(doc,save_path,MAX_WORKERS) 
        end = time.time()
        shutil.rmtree(dir_path)
        logging.info(end-start)
        return result

def windows_join_read(dir_path,save_path):
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract"
    MAX_WORKERS =15
    return join_read(dir_path,save_path,MAX_WORKERS)

def linux_join_read(dir_path,save_path):
    print("*******************************************joinread*****************************")
    print(os.getcwd())
    print(os.path.isdir(dir_path))
    print(os.listdir(dir_path))
    MAX_WORKERS =2 
    return join_read(dir_path,save_path,MAX_WORKERS)
    
if __name__ =="__main__":
    print(os.path.join(sys.argv[2]))
    print(join_read(os.path.join(sys.argv[1]),os.path.join(sys.argv[2])))

