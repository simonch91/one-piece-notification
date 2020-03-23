import smtplib, ssl, requests, shelve, csv, os, sys
from email.message import EmailMessage
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path

# set working directory
os.chdir('C:\\Users\\chens\\PycharmProjects\\onepiece')

# scrape manganelo for one piece
URL = 'https://chap.manganelo.com/manga-aa88620'
html = requests.get(URL)
soup = BeautifulSoup(html.content, 'html.parser')

## current chapter
chapter = soup.find('li', class_ = 'a-h')
chapter_link = chapter.find('a')['href']
current_chapter = chapter.text.split()[0:2]

#### store chapter number for reference
shelf_File = shelve.open('chapter')

# check for repetition
if shelf_File['chapter'] == current_chapter:
    shelf_File.close()
    sys.exit()

shelf_File['chapter'] = current_chapter
shelf_File.close()

## find date that the site was updated
date_updated = soup.find('span', class_ = 'stre-value')
date_updated_month = date_updated.text[0:3]
date_updated_day = date_updated.text[4:6]
date_updated_year = date_updated.text[7:11]
day1 = date_updated_day + date_updated_month + date_updated_year

## today's date
current_day = datetime.now().strftime('%d')
current_month = datetime.now().strftime('%b')
current_year = datetime.now().strftime('%Y')
day2 = current_day + current_month + current_year

## if update date is equal to today, then send notification email
if day1 >= day2:

    # store email credentials
    credentials = open('credentials.txt', 'r').readlines()
    credentials_list = list(credentials)
    from_email = credentials_list[0].strip()
    password = credentials_list[1].strip()
    open('credentials.txt', 'r').close()

    # begin loop to send email to subscribers
    with open('emails.csv', 'r') as file:
        email_file = csv.reader(file)
        next(email_file)

        for name, to_email in email_file:
            msg = EmailMessage()
            msg['Subject'] = 'NEW ONE PIECE CHAPTER IS OUT! [Chapter ' + current_chapter[1].replace(':', '') + ']'
            msg['From'] = from_email
            msg['To'] = to_email
            msg.set_content("Hi " + name + ",\n\nGo here for the new chapter: " + chapter_link)

            ### create a secure SSL context
            context = ssl.create_default_context()

            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
                server.login(from_email, password)
                server.sendmail(from_email, to_email, msg.as_string())

