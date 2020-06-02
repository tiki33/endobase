# -*- coding: utf-8 -*-
"""
Data entry for endobase.
Also uploads data to an AWS bucket for use by docbill
program on anaesthetist's computers
"""

#import atexit
from collections import defaultdict
import csv
from datetime import datetime, timedelta
import io
import logging
import os
import os.path
import threading
from tkinter import Tk, N, S, E, W, StringVar, ttk, Menu, FALSE
import urllib.request
import webbrowser

import boto3
from PIL import Image

import pyautogui as pya


ANAESTHETISTS = ['Barrett',
                 'Bowring',
                 'Brown',
                 'Doherty',
                 'Heffernan',
                 'Lee',   
                 'Locum',
                 'Manasiev',
                 'MOYLE',
                 "O'Hare",
                 "O'Neill",
                 "O'Sullivan",
                 'Riley',
                 'Robertson',
                 'Steele',
                 'Stevens',
                 'Stone',
                 'Tester',
                 'Thompson',
                 'Tillett',
                 'Vuong',
                 'Wood']

ENDOSCOPISTS = ['Bariol',
                'Danta',
                'Feller',
                'GETT',
                'GHALY',
                'LORD',
                'Meagher',
                'Stoita',
                'Vickers',
                'Vivekanandarajah',
                'Wettstein',
                'Williams',
                'DE LUCA',
                'Owen',
                'Bye',
                'Kim',
                'Haifer',
                'Lockart',
                'Mill',
                'NGUYEN',
                'Sanagapalli',
                'Wu']

PROCEDURES = ['None',
              'Double',
              'Colonoscopy',
              'Gastroscopy',
              'Oesophageal Dilatation',
              'Flexible Sigmoidoscopy',
              'BRAVO',
              'HALO']

add = os.path.dirname(os.path.abspath(__file__))
base = os.path.dirname(add)
enobase_local_path = os.path.join(base, "endobase_local")

aws_file = os.path.join(enobase_local_path, 'patients.csv')
backup_pat_file = os.path.join(enobase_local_path, 'backup_patients.csv')
screenshot_for_ocr = os.path.join(enobase_local_path, 'final_screenshot.png')
logging_file = os.path.join(enobase_local_path, 'logging.txt')

today = datetime.today()

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.join(enobase_local_path, 'named-chariot-275007-760483f6424c.json')


def connect():
    try:
        urllib.request.urlopen('http://google.com')
        return True
    except:
        return False


#@atexit.register
#def upload_to_aws():
#    """
#    Downloads csv file from aws s3 bucket dec601
#    puts the entries in a list while deleting records older than 10 days
#    concatenates that with the csv file of patients added in this run 
#    - today_pat_file
#    uploads csv file to s3
#    """
#    s3 = boto3.resource('s3')  
#    
#    s3.Object('dec601', 'patients.csv').download_file(pat_file)
#
#    temp_list = []
#    with open(pat_file, encoding="utf-8") as h:
#        reader = csv.reader(h)
#        for p in reader:
#            pat_date = datetime.strptime(p[0][-10:], "%d/%m/%Y")
#            if pat_date + timedelta(days=5) >= today:
#                temp_list.append(p)
#
#    with  open(today_pat_file, 'a', encoding="utf-8") as h:
#        csv_writer = csv.writer(h, dialect="excel", lineterminator='\n')
#        for p in temp_list:
#            csv_writer.writerow(p)
#  
#    try:
#        with open(today_pat_file, 'rb') as data:
#            s3.Bucket('dec601').put_object(Key='patients.csv', Body=data)
#            print('upload worked!')
#            logging.info("upload worked!")
#    except Exception as e:
#        print(e)
#        logging.error("upload failed!")
#        logging.error(e)


def patient_to_backup_file(data):
    """
    input data is a tuple containing
    date, doctor, ,mrn, name, anaesthetist, procedure, timestamp
    adds this data to a csv file of patients from this run
    """

    with open(os.path.join(enobase_local_path, backup_pat_file), 'at', encoding="utf-8") as f:
        writer = csv.writer(f, dialect="excel", lineterminator="\n")
        writer.writerow(data)


def get_concat_h(im1, im2, im3):
    """
    input - three Pil image objects representing screenshots of
    date, surname and firstname fields in endobase add page
    puts them in a new image and saves it at screenshot_for_ocr.png file in
    the endobase_local directory
    """
    dst = Image.new('RGB', (im1.width + im2.width + im3.width, im1.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (im1.width, 0))
    dst.paste(im3, (im1.width + im2.width, 0))
    
    dst.save(screenshot_for_ocr)


			  
def detect_text(im1, im2, im3):
    """Detects text in the given image  files
    Concatentes them, runs them through google vision api
    texts is the name of the returned object by the api
    
    """
    logging.info("Getting ocr.")
    from google.cloud import vision
    client = vision.ImageAnnotatorClient()

    get_concat_h(im1, im2, im3)
	
    with io.open(screenshot_for_ocr, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations
        
#    The following is just terminal output
    print('Texts:')
    for text in texts:
#        ocr_value = text.description
        print('\n"{}"'.format(text.description))
#        vertices = (['({},{})'.format(vertex.x, vertex.y)
#                    for vertex in text.bounding_poly.vertices])
#        print('bounds: {}'.format(','.join(vertices)))

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))
   
#    iterate over returned object and get a newline separated string
    texts_as_string = ""
    for word in texts:
        word_as_string = word.description
        texts_as_string += word_as_string
        texts_as_string += "\n"
    texts_as_string = texts_as_string
#    logging.info(texts_as_string)
    texts_split = texts_as_string.split("\n")
    print(texts_split[0], texts_split[1], texts_split[2])
    ocr_date = texts_split[0]
    ocr_fullname = texts_split[1] + ", " + texts_split[2]

    return ocr_date, ocr_fullname
    

def get_date_image():
    """
    Use pyautogui to get a screenshot of the date box on endobase entry form
    Save it as this_date.png and return a Pil Image object
    """
    x, y = pya.locateCenterOnScreen(os.path.join(enobase_local_path, 'date.png'), region=(400, 200, 400, 200))
    print("[DATE] {}, {}".format(x, y))
    this_date = os.path.join(enobase_local_path, 'this_date.jpg')
    im_date = pya.screenshot(this_date, region=(x - 15, y + 7, 200, 25))
    return im_date


def get_names_images():
    """
    Use pyautogui to get a screenshot of the names boxes on endobase entry form
    Save them as 'this_surname.jpg' and 'this_firstname.jpg'  and return two Pil Image objects
    """
    x, y = pya.locateCenterOnScreen(os.path.join(enobase_local_path, 'names.png'), region=(0, 300, 200, 100))
    print("[NAME] {}, {}".format(x, y))
    
    this_surname = os.path.join(enobase_local_path, 'this_surname.jpg')
    im_surname = pya.screenshot(this_surname, region=(0, y + 20, 200, 25))
    
    this_firstname = os.path.join(enobase_local_path, 'this_firstname.jpg')
    im_firstname = pya.screenshot(this_firstname, region=(0, y + 65, 200, 25))
    
    return im_surname, im_firstname


def upload_aws(data):
    s3 = boto3.resource('s3')  
    s3.Object('dec601', 'patients.csv').download_file(aws_file)
    # put aws data into temp list & remove old data
    temp_list = []
    with open(aws_file, encoding="utf-8") as h:
        reader = csv.reader(h)
        for p in reader:
            pat_date = datetime.strptime(p[0][-10:], "%d/%m/%Y")
            if pat_date + timedelta(days=5) >= today:
                temp_list.append(p)
    temp_list.append(data)
    # write the temp list over the old aws file
    with  open(aws_file, 'w', encoding="utf-8") as h:
            csv_writer = csv.writer(h, dialect="excel", lineterminator='\n')
            for p in temp_list:
                csv_writer.writerow(p)
    # upload aws file
    try:
        with open(aws_file, 'rb') as data:
            s3.Bucket('dec601').put_object(Key='patients.csv', Body=data)
            print('upload worked!')
            logging.info("upload worked!")
    except Exception as e:
        print(e)
        logging.error("upload failed!")
        logging.exception()

    try:
        os.remove(aws_file)
    except Exception as e:
        print('Failed to remove aws_file')
        print(e)
        logging.exception()


def ocr(im_date, im_surname, im_firstname, endoscopist, record_number, anaesthetist, procedure, timestamp):
    """Wrapper function. For Thread call"""
    ocr_date, ocr_fullname = detect_text(im_date, im_surname, im_firstname)
    data = [ocr_date, endoscopist, record_number, ocr_fullname, anaesthetist, procedure, timestamp]
    patient_to_backup_file(data)
    upload_aws(data)

		  
def clicks(procedure, record_number, endoscopist, anaesthetist, double_flag):
    """
    Workhorse pyautogui function. Tabs through endobase add patient entry field and inputs data
    Then tries to ocr the date and name fields and write them to a csv file
    """
    pya.click(250, 50)
    pya.PAUSE = 0.5
    pya.hotkey('alt', 'a')
    pya.typewrite(['tab'] * 1)
    pya.typewrite(procedure)
    pya.press('enter')
    pya.typewrite(['tab'] * 5)
    pya.typewrite(record_number)
    pya.press('enter')
    pya.typewrite(['tab'] * 6)
    pya.typewrite(endoscopist)
    pya.press('enter')
    pya.press('tab')
    pya.typewrite(anaesthetist)
    pya.press('enter')

    print('[DOUBLE_FLAG] {}'.format(double_flag))

    if ((not double_flag) or (double_flag and procedure == 'Gastroscopy')) and connected:
        try:
            im_date = get_date_image()
            im_surname, im_firstname = get_names_images()
            timestamp = datetime.now().strftime("%H%M%S")
	
            t = threading.Thread(target=ocr, args=(im_date, im_surname,
                                 im_firstname, endoscopist, record_number,
                                 anaesthetist, procedure, timestamp))
            t.start()
        except Exception as e:
            print("OCR Failed!")
            print(e)
            logging.exception()
    
    pya.hotkey('alt', 'o')
    pya.click(1000, 230)

def open_roster():
    webbrowser.open('http://dec601.nfshost.com/deccal.html')


def runner(*args):
    """
    Main function that runs when button clicked
    gets data from gui, does a few checks,
    then fires off clicks() function
    """
    global type_of_procedures
    endoscopist = endo.get()
    anaesthetist = anaes.get()
    record_number = mrn.get()
    procedure = proc.get()


    no_doc = endoscopist not in ENDOSCOPISTS
    no_an = anaesthetist not in ANAESTHETISTS
    if procedure == 'None' or no_doc or no_an:
        pya.alert(text='Missing Data!',
                  title='',
                  button='OK')
        raise Exception

    if not record_number.isdigit() or int(record_number) > 300000:
        pya.alert(text='MRN looks wrong!',
                  title='',
                  button='OK')
        raise Exception

    ignore_number_flag = False
    if procedure in type_of_procedures[record_number]:
        reply = pya.confirm(
            text='You already made a {} for this patient.'.format(procedure),
            title='',
            buttons=['Continue', 'Cancel'])
        if reply == 'Cancel':
            raise Exception
        else:
            ignore_number_flag = True

    if procedure == 'Double':
        type_of_procedures[record_number].extend(
            ['Colonoscopy', 'Gastroscopy'])
    else:
        type_of_procedures[record_number].append(procedure)
    print(type_of_procedures[record_number])

    number_of_procedures = len(type_of_procedures[record_number])

    print(number_of_procedures)
    if number_of_procedures > 2 and not ignore_number_flag:
        reply = pya.confirm(
            text='Do you want {} procedures for this patient??'.format(
                number_of_procedures),
            title='',
            buttons=['Yes', 'No'])
        if reply == 'No':
            raise Exception

    print(endoscopist + '-' + anaesthetist +
          '-' + procedure + '-' + record_number)

    if procedure == 'Double':
        double_flag = True
        procedure = 'Gastroscopy'
    else:
        double_flag = False

    clicks(procedure, record_number, endoscopist, anaesthetist, double_flag)

    if double_flag:
        procedure = 'Colonoscopy'
        clicks(procedure, record_number, endoscopist, anaesthetist, double_flag)

    proc.set('None')
    mrn.set('')
    mr.focus()
# start of script
logging.basicConfig(filename=logging_file, level=logging.INFO, format="%(asctime)s %(message)s")

try:
    connected = connect()
    print('Connected to Internet' if connected else 'No Internet!')
    logging.info("Connected")
except Exception:
    logging.exception()


#try:
#	os.remove(pat_file)
#except Exception as e:
#	print('Failed to remove pat_file')
#	print(e)
#
#try:
#    os.remove(today_pat_file)
#except Exception as e:
#    print('Failed to remove today_pat_file')
#    print(e)

# set up gui
root = Tk()
root.title('Endobase Data Entry')
root.geometry('320x190+900+400')
root.option_add('*tearOff', FALSE)

mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)

menubar = Menu(root)
root.config(menu=menubar)
# win['menu'] = menubar
menu_extras = Menu(menubar)
# menu_edit = Menu(menubar)
menubar.add_cascade(menu=menu_extras, label='Extras')
menu_extras.add_command(label='Roster', command=open_roster)
# menu_extras.add_command(label='Web Page', command=open_today)


endo = StringVar()
anaes = StringVar()
mrn = StringVar()
proc = StringVar()

type_of_procedures = defaultdict(list)

ttk.Label(mainframe, text="Endoscopist").grid(column=1, row=1, sticky=W)
end = ttk.Combobox(mainframe, textvariable=endo)
end['values'] = ENDOSCOPISTS
end['state'] = 'readonly'
end.grid(column=2, row=1, sticky=W)

ttk.Label(mainframe, text="Anaesthetist").grid(column=1, row=2, sticky=W)
an = ttk.Combobox(mainframe, textvariable=anaes)
an['values'] = ANAESTHETISTS
an['state'] = 'readonly'
an.grid(column=2, row=2, sticky=W)

ttk.Label(mainframe, text="MRN").grid(column=1, row=3, sticky=W)
mr = ttk.Entry(mainframe, textvariable=mrn)
mr.grid(column=2, row=3, sticky=W)

ttk.Label(mainframe, text="Procedure").grid(column=1, row=4, sticky=W)
pr = ttk.Combobox(mainframe, textvariable=proc)
pr['values'] = PROCEDURES
pr['state'] = 'readonly'
pr.grid(column=2, row=4, sticky=W)

but = ttk.Button(mainframe, text='Send!', command=runner)
but.grid(column=2, row=5, sticky=E)
root.bind('<Return>', runner)

for child in mainframe.winfo_children():
    child.grid_configure(padx=5, pady=5)

end.focus()
proc.set('None')
root.attributes("-topmost", True)

root.mainloop()
