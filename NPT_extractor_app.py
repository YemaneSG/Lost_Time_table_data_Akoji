import pdfplumber
import os
import pandas as pd
from os import listdir
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
import pandas as pd 
from bs4 import BeautifulSoup
from lxml import etree
from os.path import isfile, join


#constants 
f_size = 10     # Default font size
curr_row = 0    # Use this variable to enter the row each widget will occupy in the grid.  This makes it so we don't have to hard-code each row for each widget
max_cols = 5    # Used when we want to have a widget span an entire row (i.e. the "Step #:" labels, and horizontal lines)
t_color = 'blue'       # text color
t_bg_color = 'white'    # text background color
w_bg_color = 'white'    # window background color
application_name = "Blue Majic NPT Extractor"

# create window object
app = Tk()
app['background'] = w_bg_color

######## this is to improve the application window ##################
#####################################################################
# w = 800 #width for the tk root/app
# h = 650 #height for the tk root/app

# #get screen width and height
# ws = app.winfo_screenmmwidth() #width of screen
# hs = app.winfo_screenheight() #height of screen

# #calculate x and y coordinates for Tk root/app window
# x = (ws/2) - (w/2)
# y = (hs/2) - (h/2)
# app.geometry('%dx%d+%d+%d' %(w,h,x,y))
# app.mainloop() #starts the main loop

# key down function for select folder button
def select_folder():
    global folder_path
    folder_path = filedialog.askdirectory()
    Label(app, bg=t_bg_color, text='Selected Folder: '+ folder_path, font=('arial', f_size)).place(x=25, y=178)

def select_file_path():
    global xlsx_file_path
    xlsx_file_path = filedialog.askopenfilename()
    Label(app, bg=t_bg_color, text='Selected file: '+ xlsx_file_path, font=('arial', f_size)).place(x=25, y=230)

#this is the extraction function 
df = pd.DataFrame()

def run_program(df):

    

    def extractdata(df, filename):
    #this is extraction function

    #opening the the html file
      with open(filename, 'r') as f:

        contents = f.read()
        #this is lxml method to read
        #soup = BeautifulSoup(contents, 'lxml')
        #this is beautiful soup html parser 
        soup = BeautifulSoup(contents, "html.parser")
        dom = etree.HTML(str(soup))

        try:
            title = soup.title.text
            print(title)
        except:
            pass

        #print("File: " + soup.title.text)

        #assign soup items in to table and rows rows is table body and table rows 
        table = soup.find("table", {"id": "AutoNumber2"})     
        #printing the table
        #print(table)
        rows = table.find("tbody").find_all("tr")
        #neg_length_rows = 0 - len(rows)
        #print("length of rows is:" ,neg_length_rows)


        for row in rows:
            columns = row.find_all("td")
            print("lenght of the column is" , len(columns))
        #for i in range(neg_length_rows,-1):
        #   columns = rows[i].find_all("td")
        #    columns[-1].get_text()
        #    if columns == "LT Summary":
        #        break

            if len(columns) == 16 or len(columns) == 18 or len(columns) == 23:
                continue
            else:
                #iterating over the rows from table
                #this will grab all the columns for each row 
                #the number of columns per each row is
                # 16 if there is no NPT
                # 18 for upper table
                # 11 for lost time table
                # there is an item with 23 elements it is in the middle
                
                #print(getTextFromTag(columns, 18))
                #print(getTextFromTag(columns, lastrow_index)
                try:
                    date = dom.xpath('//*[@id="AutoNumber1"]/thead/tr[1]/td/table/tbody/tr[1]/td[2]/table/tbody/tr[3]/td')[0].text
                    wellno = dom.xpath('//*[@id="AutoNumber1"]/thead/tr[1]/td/table/tbody/tr[1]/td[3]/table[1]/tbody/tr[2]/td')[0].text
                    rigname = dom.xpath('//*[@id="AutoNumber1"]/thead/tr[1]/td/table/tbody/tr[1]/td[4]/table/tbody/tr[2]/td')[0].text
                    Date_and_time = columns[-11].get_text()
                    Time_in_Hrs = columns[-10].get_text()
                    cum_Hrs = columns[-9].get_text()
                    LT_ID = columns[-8].get_text()
                    Parent_LT_ID = columns[-7].get_text()
                    LT_type = columns[-6].get_text()
                    cause = columns[-5].get_text()      
                    object = columns[-4].get_text()
                    company = columns[-3].get_text()
                    depth = columns[-2].get_text()
                    LT_summary = columns[-1].get_text()
                except:
                    date = ""
                    wellno = ""
                    rigname = ""
                    Date_and_time = ""
                    Time_in_Hrs = ""
                    cum_Hrs = ""
                    LT_ID = ""
                    Parent_LT_ID = ""
                    LT_type = ""
                    cause = ""      
                    object = ""
                    company = ""
                    depth = ""
                    LT_summary = ""
                #checking for extra line of information about the depth 
                #and company this will ignore that line. it is un necessary 
                # if company == "Depth":
                #     continue
                    #LT_depth == company
                data = {
                    #this is is to capture lost time
                    "Report Date": date,
                    "Rig Name": rigname,
                    "Well No": wellno, 
                    "Date and Time": Date_and_time,
                    "Time in Hrs": Time_in_Hrs,
                    "Cummulative Hrs" : cum_Hrs,
                    "LT ID": LT_ID,
                    "Parent LT ID":Parent_LT_ID,
                    "LT Type": LT_type,
                    "Cause" : cause,
                    "Object": object,
                    "Company Name": company, 
                    "Depth": depth,
                    "LT Summary": LT_summary,
                    }
                
                df_master = df.append(data, ignore_index = True)
                
        return df_master

    #this takes in df and morning reports folder
    #it goes through all files in the folder 
    #returns data frame 
    def readReportsPerDay(df, morningReportFolder):

        mypath = morningReportFolder + "/reports"
        #mypath += "/reports"
        onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

        count = 1

        for filename in onlyfiles:

            if "DS_Store" in filename:
                continue
            filename = mypath + "/" + filename
            print(str(count) + " " + filename)

            df = extractdata(df, filename)
            count += 1

        return df
    #this funtion will call the reports per day function 
    #this is to be used for running the program in folder
    #it goes thru the all morning report folders per day inside specific folder 
    def runInRunningFolder(df):

        for morningReportFolder in listdir(os.getcwd()):

            if ".ipynb" in morningReportFolder or ".git" in morningReportFolder or ".csv" in morningReportFolder or "DS_Store" in morningReportFolder or ".xlsx" in morningReportFolder or ".json" in morningReportFolder or ".pbix" in morningReportFolder or ".zip" in morningReportFolder:
                continue

            print(morningReportFolder + "\n")

            df = readReportsPerDay(df, morningReportFolder)

        return df
    #this is where we run the code for each item in directory 
    #this will list curent working directory and rung th code 

    print(os.getcwd())


    df = runInRunningFolder(df)

    print(df)

    return(df)



        
print(df)
print("UNTIL df IS GOOD.")
df.to_excel('NEW OUTPUT.xlsx') 

# #this reads the existing excle file from input
# old_df = pd.read_excel(xlsx_file_path,index_col=0)

# #this combines existing excel file to the new one
# new_df = pd.concat([old_df,df],ignore_index=True)

# #this outputs updated excel file
# new_df.to_excel(xlsx_file_path)

#show message when the program is done
messagebox.showinfo(title = application_name, message = 'Great Job! Your report is ready. Please open the the xlsx file.')

      ##print(df)
    ################################################################################
    ############### END OF EXTRACTOR ###############################################
    ################################################################################ 

# Header
Label(app, fg = t_color, bg = t_bg_color, text=application_name, font = ('bold', f_size*2)).place(x = 400, anchor = N)
Label(app, fg = t_color, bg = t_bg_color, text = 'Application owner Akoji Haruna', font = ('bold', f_size)).place(x = 300, y = 40)


# # Step 1 section - enter name, auto-populate date
# Label(app, fg = t_color, bg = t_bg_color, text = 'Step 1:  Enter your name.', font = ('arial italic', f_size)).place(x = 0, y = 72)

# # Name
# Label(app, fg = t_color, bg = t_bg_color, text = 'Name:', font = ('bold', f_size)).place(x = 0 , y = 110)
# username = Entry(app, textvariable = StringVar(), border = 2)
# username.place(x = 60, y = 110)

# Date
# Label(app, fg = t_color, bg = t_bg_color, text = 'Today\'s date:', font = ('bold', f_size)).place(x = 25, y = 100)
# date = Entry(app, textvariable = StringVar(), border = 2)
# date.insert(0, datetime.today())
# date.place(x = 400, y = 100)


## Step 2 section - select report folder, and output format
Label(app, fg = t_color, bg = t_bg_color, text = 'Select the working folder ', font = ('arial italic', f_size)).place(x = 25 , y = 150)
sf_button = Button(app,text='Select Folder...', font = ('arial', int(1 * f_size)), command = select_folder())
sf_button.place(x = 400 , y = 150)

##step Section - select the excel file 
Label(app, fg = t_color, bg = t_bg_color, text = 'Select the Master Excel file', font = ('arial italic', f_size)).place(x = 25 , y = 200)
sf_button = Button(app,text='Select File...', font = ('arial', int(1 * f_size)), command =  select_file_path())
sf_button.place(x = 400 , y = 200)



## Section 3:  Generate the report.
Label(app, fg = t_color, bg = t_bg_color, text = 'Run Program.', font = ('arial italic', f_size)).place( x = 25, y = 250)
gen_button = Button(app,text = 'Run\n Program', font = ('arial', int(1.5 * f_size)), command = lambda: run_program())
gen_button.place(x = 400, y = 250)

## Draw and run the GUI
app.title(application_name)
app.geometry('800x400')
app.mainloop()