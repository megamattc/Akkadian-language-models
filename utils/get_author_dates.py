import os
import re
import sys
import json
import csv

def process_name(name: str) -> str:
    if name == "":
        return ""

    name = re.sub("\[","",name)
    name = re.sub("\]", "", name)
    name = re.sub("^[(]", "", name)
    name = re.sub("[)]$", "", name)


    return name

#Function to process the various date formats in the SAA letter volumes
def process_date(date: str) -> str:
    if date == "":
        return ""

    print("old date: " + date)
    #Take out a number of characters from the date
    date = re.sub("ca[.] ","",date)
    date = re.sub("[(]","",date)
    date = re.sub("[)]", "", date)
    date = re.sub("[?]","",date)

    #match = re.search("r^[(]{1}(.+)[)]{1}$",date)
    #if match:
    #    print("match")
    #    date = match.group()
    #print("new date: " + date)
    #If date is a negative year
    if re.search(r"^-",date):
        date_num = int(date)
        date_num_new = -1*(date_num+1)
        return str(date_num_new)
    #If we have date formula
    if re.search(r"^\d+/\d+/\d+$",date):
        year = re.search(r"^[0]{0,1}(\d+)",date).group()
        return year

    #If we have compound year range yyy+1 or yyy-www, combine them:
    match = re.search("r^(\d{3}) or (\d{3})-(\d{3})$",date)
    if match:
        year1 = match.group(1)
        year2 = match.group(2)
        year3 = match.group(3)

        if int(year1)-1 == int(year2):
            print("Year1-Year2 = 1")
            year = year1+"-"+year3
            return year
        else:
            return date
    #ddd/dd/dd or ddd/dd/dd -> take only first year
    match = re.search(r"^(\d{3})/\d{2}/\d{2} or \d{3}/\d{2}/\d{2}$",date)
    if match:
        year1 = match.group(1)
        return year1

    # ddd/dd/dd or ddd/dd/dd -> take only first year
    match = re.search(r"^(\d{3})/\d{2}/\d{2}\s{0,1}-\s{0,1}\d{3}/\d{2}/\d{2}$", date)
    if match:
        year1 = match.group(1)
        return year1

    # ddd/dd/dd-dd -> take only first year
    match = re.search(r"^(\d{3})/\d{2}/\d{2}\s{0,1}-\s{0,1}\d{1,2}$", date)
    if match:
        year1 = match.group(1)
        return year1

    #ddd or ddd -> first year
    match = re.search(r"^(\d{3}) or \d{3}$", date)
    if match:
        year1 = match.group(1)
        return year1

    # ddd/dd-d/dd -> first year
    match = re.search(r"^(\d{3})/\d{2}\s{0,1}-\s{0,1}\d{1,2}/\d{2}$", date)
    if match:
        year1 = match.group(1)
        return year1

    #If we just get ranges for Es and Asb, combine them
    if date == "680-669 or 668-631":
        return "680-631"

    else:
        return date




#Concatenates all the files in input directory and adds a comment line before each one of the pnumber

input_dir = "catalogue_data"
cwd = os.getcwd()
input_path = os.path.join(cwd,input_dir)

output_file_name = "letter_metadata.csv"
output_file = open(output_file_name,'w',newline='',encoding="utf-8")

header_row = ["url","designation","ancient_author","ancient_recipient","date","provenience","ruler","genre","dialect","script","sender_loc"]

writer = csv.DictWriter(output_file,fieldnames=header_row)


#Write header row of output file
writer.writeheader()

#print(input_path)
oracc_str = "http://oracc.org/" #Base url string

#Dictionary for kings and ruling spans
ruler_dict = {"Sargon II":"721-705","Sennacherib":"705-681","Esarhaddon":"681-669","Ashurbanipal":"669-631","Esarhaddon or Ashurbanipal":"681-631",
              "Sargon II or Sennacherib":"721-681"}

for path, dirs, filenames in os.walk(input_path):
    #print("path")
    #print(path)
    for filename in filenames:
        print("Processing catalogue: " + filename)

        file_with_path = os.path.join(path, filename)
        print(file_with_path)
        file = open(file_with_path, 'r', encoding="utf-8")

        file_dict = json.load(file)


        project_name = file_dict["project"]

        members = file_dict["members"]

        for file in members.keys():

            print("Processing " + file)

            ancient_author = ""
            date = ""
            provenience = ""
            ruler = ""
            genre = ""
            dialect = ""
            script = ""
            sender_loc = ""
            ancient_recipient = ""
            designation = ""

            url = oracc_str + project_name + "/" + file #URL for Pnum

            member_info = members[file]

            #Try to get all values from the above keys

            if "ancient_author" in member_info.keys():
                ancient_author = process_name(member_info["ancient_author"])

            if "date" in member_info.keys():
                date = process_date(member_info["date"])

            if "provenience" in member_info.keys():
                provenience = member_info["provenience"]

            if "ruler" in member_info.keys():
                ruler = member_info["ruler"]

            if "genre" in member_info.keys():
                genre = member_info["genre"]

            if "dialect" in member_info.keys():
                dialect = member_info["dialect"]

            if "script" in member_info.keys():
                script = member_info["script"]

            if "sender_loc" in member_info.keys():
                sender_loc = member_info["sender_loc"]

            if "ancient_recipient" in member_info.keys():
                ancient_recipient= process_name(member_info["ancient_recipient"])

            if "designation" in member_info.keys():
                designation= member_info["designation"]

            #Put in a range of years equal to span of reigning years of given ruler or rulers, if date field is empty
            if date == "":
                if ruler in ruler_dict.keys():
                    date = ruler_dict[ruler]


            writer.writerow({"url":url,"designation":designation,"ancient_author":ancient_author,"date":date,"provenience":provenience,"ruler":ruler,"genre":genre,"sender_loc":sender_loc,"dialect":dialect,"script":script,"ancient_recipient":ancient_recipient})



