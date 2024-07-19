import platform
import psutil
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
import getpass

def get_system_info():
    info = {
        'System': platform.system(),
        'Node Name': platform.node(),
        'Release': platform.release(),
        'Version': platform.version(),
        'Machine': platform.machine(),
        'Processor': platform.processor(),
        'CPU Count': psutil.cpu_count(logical=False),
        'CPU Count (Logical)': psutil.cpu_count(logical=True),
        'Memory Total': f"{psutil.virtual_memory().total / (1024 ** 3):.2f} GB",
        'Memory Available': f"{psutil.virtual_memory().available / (1024 ** 3):.2f} GB",
    }
    return info

def create_pdf(info, username):
    file_name = 'system_info.pdf'
    pdf = canvas.Canvas(file_name, pagesize=letter)
    pdf.setFont("Helvetica", 12)
    pdf.drawString(100, 750, "Süsteemi info")
    pdf.drawString(100, 730, f"Genereeritud: {username}")
    pdf.drawString(100, 710, "-" * 60)
    
    y_position = 690
    for key, value in info.items():
        pdf.drawString(100, y_position, f"{key}: {value}")
        y_position -= 20
    
    pdf.save()
    return file_name

def send_email(email_from, email_to, password, subject, body, attachment):
    msg = MIMEMultipart()
    msg['From'] = email_from
    msg['To'] = email_to
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    # Lisa PDF fail manusena
    with open(attachment, 'rb') as attachment_file:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment_file.read())
    
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename= {attachment}')
    msg.attach(part)
    
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(email_from, password)
    server.sendmail(email_from, email_to, msg.as_string())
    server.quit()

    print('Meili saatmine õnnestus.')

def collect_and_send_info():
    email_from = entry_from.get()
    password = entry_password.get()
    email_to = entry_to.get()
    username = entry_name.get()

    # Kontrolli, et kõik väljad oleks täidetud
    if not email_from or not password or not email_to or not username:
        messagebox.showwarning('Hoiatus', 'Palun täitke kõik väljad.')
        return

    # Kogu süsteemi info
    system_info = get_system_info()

    # Koosta PDF
    pdf_file = create_pdf(system_info, username)

    # Koosta e-kirja sisu
    subject = 'Süsteemiteave PDF'
    body = f'Süsteemi teave on lisatud PDF-failina.\nGenereeritud: {username}'

    # Saada e-kiri
    send_email(email_from, email_to, password, subject, body, pdf_file)

    # Kustuta loodud PDF fail
    os.remove(pdf_file)

# Loo GUI
from tkinter import *
from tkinter import messagebox

root = Tk()
root.title('Süsteemiteave PDF-i e-posti saatja')

Label(root, text='Sinu email:').grid(row=0, column=0, padx=10, pady=5)
entry_from = Entry(root, width=50)
entry_from.grid(row=0, column=1, padx=10, pady=5)

Label(root, text='Teie parool:').grid(row=1, column=0, padx=10, pady=5)
entry_password = Entry(root, width=50, show='*')
entry_password.grid(row=1, column=1, padx=10, pady=5)

Label(root, text='Saaja e-post:').grid(row=2, column=0, padx=10, pady=5)
entry_to = Entry(root, width=50)
entry_to.grid(row=2, column=1, padx=10, pady=5)

Label(root, text='Sinu nimi:').grid(row=3, column=0, padx=10, pady=5)
entry_name = Entry(root, width=50)
entry_name.grid(row=3, column=1, padx=10, pady=5)

Button(root, text='Koguge ja saatke teavet', command=collect_and_send_info).grid(row=4, column=0, columnspan=2, pady=10)

root.mainloop()
