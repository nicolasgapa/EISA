# ------------------------------------------------------------------------------------------------------------------------------------------------- #
# ------------------------------------------------------------------------------------------------------------------------------------------------- #
# ------------------------------------------------------------------------------------------------------------------------------------------------- #
# ------------------------------------------------------------------------------------------------------------------------------------------------- #
# ------------------------------------------------------------------------------------------------------------------------------------------------- #
# ------------------------------------------------------------------------------------------------------------------------------------------------- #
# ------------------------------------------------------------------------------------------------------------------------------------------------- #
#                                                                                                                                                   #
#                           Graphingmain.py code for ionospheric scintillation and Total Electron Content. BETA VERSION.                            #
#                                                      GPStation-6 multi-constellation receiver.                                                    #
#                                                                                                                                                   #
# ------------------------------------------------------------------------------------------------------------------------------------------------- #
#                                                                                                                                                   #
#                                            JOSE NICOLAS GACHANCIPA - Embry-Riddle Aeronautical University                                         #
#                                                                                                                                                   #
# ------------------------------------------------------------------------------------------------------------------------------------------------- #
# ------------------------------------------------------------------------------------------------------------------------------------------------- #
# ------------------------------------------------------------------------------------------------------------------------------------------------- #
# ------------------------------------------------------------------------------------------------------------------------------------------------- #
# ------------------------------------------------------------------------------------------------------------------------------------------------- #
# ------------------------------------------------------------------------------------------------------------------------------------------------- #

# ------------------------------------------------------------------------------------------------------------------------------------------------- #
# ------------------------------------------------------------------------------------------------------------------------------------------------- #
#                                                                                                                                                   #
#                                                                   CREDITS                                                                         #
#                                                                                                                                                   #
# The Butterworth filter used for TEC detrending was based on a Matlab function written by Dr. Kshitija Deshpande, Assistant Professor of           #
# Engineering Physics at Embry-Riddle Aeronautical University.                                                                                      #
#                                                                                                                                                   #
# ------------------------------------------------------------------------------------------------------------------------------------------------- #
# ------------------------------------------------------------------------------------------------------------------------------------------------- #
#                                                                                                                                                   #
#                                                   DO NOT HARD CODE ANYTHING BELOW THIS POINT.                                                     #
#                                                                                                                                                   #
# ------------------------------------------------------------------------------------------------------------------------------------------------- #
# ------------------------------------------------------------------------------------------------------------------------------------------------- #
# ------------------------------------------------------------------------------------------------------------------------------------------------- #
                                                        # --------------------- SECTION 1: READING THE GRAPHSETTINGS.CSV FILE --------------------- #
import os, sys                                          
no_menu = 0
if len(sys.argv)>1:
    if sys.argv[1] == "no_menu":
        no_menu = 1
        user_selec = sys.argv[2]
    else:
        print("The purpose of this code is to plot and save ionospheric scintillation and TEC graphs.")
        print("The directories can be changed by modifying the paths.csv file.")
        print("The settings can be changed by modifying the graphsettings.csv file.")
                                                        # Set the file separator to work in both Linux and Windows.
filesep=os.sep                                          # Save the file separator into a variable. 
import csv                                              # Import the graphsettings.csv file.
#print("hello world")
with open("graphsettings.csv") as csvfile:              #        
    readCSV=csv.reader(csvfile, delimiter=',')          # Read the csv file.                
    count=1                                             # Start a count for every row in the excel file. 
    for row in readCSV:                                 # Start a FOR loop (FOR LOOP A) that will repeat n times, being n the amount of rows in the csv file.
        if count==2:                                    # For row 2, extract cell 1 and cell 2 and put them together. This is the file type selected by the user. 
            filetyperow=row                             #
            firstpart=filetyperow[0]                    #
            secondpart=filetyperow[1]                   #
            filetype=firstpart+secondpart               #
        elif count==4:                                  # For row 4, extract cell 1 and convert the character to a float. 
            thresholdrow=row                            #
            threshold=thresholdrow[0]                   #
            threshold=float(threshold)                  #
        elif count==6:                                  # For row 6, identify the constellation system selected by the user.
            constellation=row[0]                        #
            if constellation=="G":                      #
                constellationtype="GPS"                 #
            elif constellation=="R":                    #
                constellationtype="GLONASS"             #
            elif constellation=="E":                    #
                constellationtype="GALILEO"             #
        elif count==8:                                  # Row 8. Extract all PRN codes from the row and save them to a variable PRNstograph.
            PRNnumber=row[0]                            #
            savedPRNnumber=PRNnumber                    #
            PRNstographrow=row                          #
            PRNstograph=[]                              #
            for a in range(len(PRNstographrow)):        #
                toappendPRNs=PRNstographrow[a]          #
                if len(toappendPRNs)!=0:                #
                    PRNstograph.append(toappendPRNs)    #
        elif count==10:                                 # Initial date.       
            monthi=str(row[0])                          #
            dayi=str(row[1])                            #
            if len(str(monthi))==1:                     #
                monthi='0'+str(monthi)                  #
            if len(str(dayi))==1:                       #
                dayi='0'+str(dayi)                      #
        elif count==12:                                 # Final Date.
            monthf=str(row[0])                          #
            dayf=str(row[1])                            #
            if len(str(monthf))==1:                     #
                monthf='0'+str(monthf)                  #
            if len(str(dayf))==1:                       #
                dayf='0'+str(dayf)                      #
        elif count==14:                                 # Extract the year from row 14. 
            year=row[0]                                 #
            yeari=year                                  #
        elif count==16:                                 # Extract the values from column 1 and 2. Column 1 is the summary plot option. Column 2 is the shift value.     
            independentgraph=int(row[0])                #        
            shiftvalue=float(row[1])                    #
        elif count==18:                                 # Normalize the data (Night-subtraction). 
            normalizedata=int(row[0])                   #
        elif count==20:                                 # Set limits for the x-axis.
            setxaxisrange=int(row[0])                   #
            xaxisstartvalue=float(row[1])               # X-axis start value.
            xaxisfinalvalue=float(row[2])               # X-axis final value. 
        elif count==21:                                 #
            setyaxisrange=int(row[0])                   # Set limits for the y-axis.
            yaxisstartvalue=float(row[1])               # Y-axis star value.
            yaxisfinalvalue=float(row[2])               # Y-axis final value. 
        elif count==23:                                 #
            TECdetrending=int(row[0])                   # TEC detrending for High-Rate TEC.
        elif count==25:                                 #
            PRNlabeling=int(row[0])                     # Labeling the PRN's next to the lines on the graph. 
        elif count==27:                                 #
            legend=int(row[0])                          # Include a legend next to the graph showing the differnt lines being plotted (for summary plots). 
        elif count==29:                                 #
            verticalline=int(row[0])                    # Vertical line across the graph. 
            verticallinexpoint=float(row[1])            # 
        elif count==31:                                 #
            verticaltec=int(row[0])                     # Convert Slant to Vertical TEC
        elif count==33:                                 #
            onlyonesignal=int(row[0])                   # Get rid of the duplicates - Only plot ONE signal combination per PRN.
        elif count==35:                                 #
            formattype=row[0]                           # Plot format (.png, .pdf, etc).
        elif count==37:                                 # Title and Subtitle font Size.
            titlefontsize=float(row[0])                 # 
            subtitlefontsize=float(row[1])              # 
        elif count==39:                                 # 
            location=row[0]                             #
        count=count+1                                   # Add 1 to the count and END FOR LOOP A.
                                                        # ----------------------------------------- SECTION 1B: DATES ----------------------------------------------- #
daymatrix=[]                                                                # Create two matrices: One for the months and the other one for the days.                                                               
monthmatrix=[]                                                              # 
numberofmonths=int(monthf)-int(monthi)                                      # How many months will be plotted?
monthcount=0                                                                # 
rangea=numberofmonths+1                                                     #
if numberofmonths!=0:                                                       # If there is more than one month:
    for month in range(rangea):                                             # Start a for loop for each month.
        if monthcount<=numberofmonths:                                      # 
            if monthcount==0:                                               # 
                month=int(monthi)                                           # 
            else:                                                           # 
                month=int(monthi)+monthcount                                # Determine the number of days for each specific month.
            if month==1 or month==3 or month==5 or month==7 or month==8 or month==10 or month==12:
                numofdays=31;                                               # 
            elif month==4 or month==6 or month==9 or month==11:             # 
                numofdays=30;                                               # 
            elif month==2:                                                  # 
                remainder=int(yeari)%4                                      # 
                if remainder==0:                                            # 
                    numofdays=29                                            # 
                elif remainder!=0:                                          # 
                    numofdays=28                                            # 
            if monthcount==0:                                               # Determine all the days inside the range given by the user.
                numofdays1=numofdays-int(dayi)                              #
            elif monthcount!=0 and month!=int(monthf):                      #
                numofdays1=numofdays                                        #
            elif month==int(monthf):                                        # 
                numofdays1=int(dayf)                                        #
            for day in range(numofdays1+1):                                 #
                if monthcount==0:                                           # 
                    daytoadd=int(dayi)+day                                  #
                    daymatrix.append(daytoadd)                              #
                elif monthcount!=0 and month!=int(monthf):                  #
                    if day!=0:                                              #
                        daytoadd=day                                        # 
                        daymatrix.append(daytoadd)                          # 
                elif month==int(monthf) and monthcount==numberofmonths:     # 
                    if day<=int(dayf) and day!=0:                           # 
                        daytoadd=day                                        # 
                        daymatrix.append(daytoadd)                          # 
                monthmatrix.append(month)                                   # 
            monthcount=monthcount+1                                         #
elif numberofmonths==0:                                                     # Elseif the range includes only one month:
    month=monthi                                                            # 
    numberofdays=int(dayf)-int(dayi)                                        # Add each day of the month to the matrix.
    for day in range(numberofdays+1):                                       # 
        daytoadd=day+int(dayi)                                              # 
        monthmatrix.append(int(month))                                      # 
        daymatrix.append(daytoadd)                                          #
# --------------------------------------------------------------------------------------------------------------------------------------------------------- #
# --------------------------------------------------------------------------------------------------------------------------------------------------------- #
                                                                                # ----------------- SECTION 2: READING THE PATHS.CSV FILE ----------------- #
import platform                                                                 # Identify the operating system. 
osname=platform.system()                                                        #                                                                                                                       
import csv                                                                      # Open the paths .csv file.
with open("PATHS.csv") as csvfile:                                              #
    readCSV=csv.reader(csvfile, delimiter=',')                                  #
    count=1                                                                     #
    for row in readCSV:                                                         # Identify the path to the CSV folder and save it to a variable.
        if count==2:                                                            # This folder is where all CSV files are located.
            outputfolderpath=row                                                #
            lengthoutput=len(outputfolderpath)                                  #
            outputfolderdirectory=""                                            #
            for a in range(lengthoutput):                                       #
                toappendoutput=outputfolderpath[a]                              #
                toappendoutput=toappendoutput+filesep                           #
                outputfolderdirectory=outputfolderdirectory+toappendoutput      #
        elif count==4:                                                          # Identify the path to the Graphs folder.
            graphsfolderpath=row                                                # This folder is where the graphs will be saved.
            lengthgraphs=len(graphsfolderpath)                                  # 
            graphsfolderdirectory=""                                            # 
            for b in range(lengthgraphs):                                       #  
                toappendgraphs=graphsfolderpath[b]                              # 
                if len(toappendgraphs)!=0:                                      # 
                    toappendgraphs=toappendgraphs+filesep                       # 
                graphsfolderdirectory=graphsfolderdirectory+toappendgraphs      # 
        count=count+1                                                           #
dcount=0                                                                        #   
validdates=[]                                                                   #
import os                                                                       #
for element in daymatrix:                                                       #
    monthint=monthmatrix[(dcount)]                                              #
    dayint=element                                                              #
    if len(str(monthint))==1:                                                   #
        monthint='0'+str(monthint)                                              #
    if len(str(dayint))==1:                                                     #
        dayint='0'+str(dayint)                                                  #
    readdirectorya=outputfolderdirectory+str(yeari)+str(monthint)+str(dayint)   # Identify the csv files present within the selected folder.                                                    
    if os.path.exists(readdirectorya):                                          #
        validfolder=str(yeari)+str(monthint)+str(dayint)                        #
        validdates.append(validfolder)                                          #
    dcount=dcount+1                                                             #                                                                 
# --------------------------------------------------------------------------------------------------------------------------------------------------------- #
# --------------------------------------------------------------------------------------------------------------------------------------------------------- #
# --------------------------------------------------------------------------------------------------------------------------------------------------------- #
                                                                            # --------------------- SECTION 3: PRINTING THE MENU -------------------------- #
y=filetype                                                                  # Set y=filetype. The filetype is selected by the user in the graphsettings.csv file.
if y=='REDTEC':                                                             # IF THE FILE TYPE IS REDTEC, PRINT THE OPTIONS FOR LOW-RATE TEC.
    ans=True                                                                # EACH OF THESE OPTIONS IS EXPLAINED IN DETAIL IN THE GPSTATION-6 USER MANUAL.
    while ans:                                                              # SEE THE "INSTRUCTIONS" WORD DOCUMENT TO ACCESS AND DOWNLOAD THIS MANUAL.                                                                
        if no_menu == 1:
            ans = user_selec
        else:
            print ("""                                                      
            1. Azimuth                                                          
            2. Elevation                                                          
            3. SecSig Lock                                                          
            4. SecSig CNo                                                          
            5. TEC15                                                          
            6. TECRate15                                                          
            7. TEC30                                                          
            8. TECRate30
            9. TEC45
            10. TECRate45
            11. TECTOW
            12. TECRateTOW
            """) 
            ans=input("What would you like to plot? ")                      # Ask the user for an input.
        if ans=="1":                                                        # 
          graphtype="Azymuth"                                               # Determine the graph type selected by the user. 
          units="(Degrees)"                                                 # Set the units for each graph type. 
        elif ans=="2":                                                      # DO THE SAME WITH ALL THE POSSIBLE SELECTIONS...
          graphtype="Elevation"                                             # 
          units="(Degrees)"                                                 #                             
        elif ans=="3":                                                      # 
          graphtype="SecSigLock"                                            # 
          units="(seconds)"                                                 #                             
        elif ans=="4":                                                      # 
          graphtype="SecSig_CNo"                                            # 
          units="(dB-Hz)"                                                   #                               
        elif ans=="5":                                                      # 
          graphtype="TEC15"                                                 #        
          units="(TECU)"                                                    #                                 
        elif ans=="6":                                                      # 
          graphtype="TECRate15"                                             # 
          units="(TECU)"                                                    #                              
        elif ans=="7":                                                      # 
          graphtype="TEC30"                                                 # 
          units="(TECU)"                                                    #                                   
        elif ans=="8":                                                      # 
          graphtype="TECRate30"                                             # 
          units="(TECU)"                                                    #                                 
        elif ans=="9":                                                      # 
          graphtype="TEC45"                                                 # 
          units="(TECU)"                                                    #                                 
        elif ans=="10":                                                     # 
          graphtype="TECRate45"                                             # 
          units="(TECU)"                                                    #                              
        elif ans=="11":                                                     # 
          graphtype="TECTOW"                                                # 
          units="(TECU)"                                                    #                                 
        elif ans=="12":                                                     #
          graphtype="TECRateTow"                                            # 
          units="(TECU)"                                                    #                              
        else:                                                               # 
          print("\nThis is an incorrect number")                            # 
        break                                                               # 
    columna=int(ans)+4                                                      # The column in the csvfile corresponding to the user selection. e.g. user selects "7" for
                                                                            # "TEC30" - column 7 in the csvfile corresponds to the TEC30 values. 
if y=='REDOBS':                                                             # IF THE FILE TYPE IS REDOBS, PRINT THE OPTIONS FOR LOW-RATE SCINTILLATION.                                            
    ans=True                                                                # EACH OF THESE OPTIONS IS EXPLAINED IN DETAIL IN THE GPSTATION-6 USER MANUAL.
    while ans:                                                              # SEE THE "INSTRUCTIONS" WORD DOCUMENT TO ACCESS AND DOWNLOAD THIS MANUAL.
        if no_menu == 1:
            ans = user_selec
        else:
            print ("""                                               
            1. Azimuth
            2. Elevation
            3. CNo
            4. Lock Time
            5. CMC avg
            6. CMC std
            7. S4
            8. S4 Cor
            9. 1secsigma
            10. 3secsigma
            11. 10secsigma
            12. 30secsigma
            13. 60secsigma
            """)
            ans=input("What would you like to plot? ")                      # Ask the user for an input.
        if ans=="1":                                                        # Determine the graph type selected by the user. 
          graphtype="Azymuth"                                               # Set the units for each graph type. 
          units="(Degrees)"                                                 # Print the type of plot that will be generated by the code in the command window.
                                                                            # DO THE SAME WITH ALL THE POSSIBLE SELECTIONS...
        elif ans=="2":                                                      #
          graphtype="Elevation"                                             #
          units="(Degrees)"                                                 #                         
        elif ans=="3":                                                      #
          graphtype="CNo"                                                   #
          units="(dB-Hz)"                                                   #                                   
        elif ans=="4":                                                      #
          graphtype="Lock_Time"                                             #
          units='(seconds)'                                                 #                                    
        elif ans=="5":                                                      #
          graphtype="CMC_avg"                                               #
          units="(m)"                                                       #                                
        elif ans=="6":                                                      #
          graphtype="CMC_std"                                               #
          units="(m)"                                                       #                                 
        elif ans=="7":                                                      #
          graphtype="S4"                                                    #
          units=" "                                                         #                                    
        elif ans=="8":                                                      #
          graphtype="S4_Cor"                                                #
          units=" "                                                         #                                  
        elif ans=="9":                                                      #
          graphtype="1secsigma"                                             #
          units="(radians)"                                                 #                              
        elif ans=="10":                                                     #
          graphtype="3secsigma"                                             #
          units="(radians)"                                                 #                              
        elif ans=="11":                                                     #
          graphtype="10secsigma"                                            #
          units="(radians)"                                                 #                           
        elif ans=="12":                                                     #
          graphtype="30secsigma"                                            #
          units="(radians)"                                                 #                          
        elif ans=="13":                                                     #
          graphtype="60secsigma"                                            #
          units="(radians)"                                                 #                           
        else:                                                               #
          print("\nThis is an incorrect number")                            #
        break                                                               #
    columna=int(ans)+3                                                      # The column in the csvfile corresponding to the user selection. e.g. user selects "8" for
                                                                            # "S4_Cor" - column 11 (8+3) in the csvfile corresponds to the S4_Cor values. 
elif y=='ismRawTEC' or y=='ismRawTec':                                      # IF THE FILE TYPE IS ISMRAWTEC, PRINT THE OPTIONS FOR HIGH-RATE TEC.
    ans=True                                                                # EACH OF THESE OPTIONS IS EXPLAINED IN DETAIL IN THE GPSTATION-6 USER MANUAL.
    while ans:                                                              # SEE THE "INSTRUCTIONS" WORD DOCUMENT TO ACCESS AND DOWNLOAD THIS MANUAL.                   
        if no_menu == 1:
            ans = user_selec
        else:
            print ("""
            1. TEC
            2. TECdot
            """)  
            ans=input("What would you like to plot? ")                      # Ask the user for an input.
        if ans=="1":                                                        # Determine the graph type selected by the user. 
          graphtype="TEC"                                                   # Set the units for each graph type. 
          units="(TECU)"                                                    # Print the type of plot that will be generated by the code in the command window.
                                                                            # DO THE SAME WITH ALL THE POSSIBLE SELECTIONS...
        elif ans=="2":                                                      #
          graphtype="TECdot"                                                #
          units="(TECU)"                                                    #
        else:                                                               #
          print("\nThis is an incorrect number")                            #
        break                                                               #
    columna=int(ans)+4                                                      # The column in the csvfile corresponding to the user selection. e.g. user selects "1" for
                                                                            # "TEC" - column 5 (1+4) in the csvfile corresponds to the TEC values. 
elif y=='ismRawObs' or y=='ismRawOBS' or y=='ismDetObs' or y=='ismDetOBS':  # IF THE FILE TYPE IS ISMRAWOBS OR ISMDETOBS, PRINT THE OPTIONS FOR HIGH-RATE SCINTILLATION.  
    ans=True                                                                # EACH OF THESE OPTIONS IS EXPLAINED IN DETAIL IN THE GPSTATION-6 USER MANUAL.
    while ans:                                                              # SEE THE "INSTRUCTIONS" WORD DOCUMENT TO ACCESS AND DOWNLOAD THIS MANUAL.
        if no_menu == 1:
            ans = user_selec
        else:
            print ("""                         
            1. ADR
            2. Power
            """)
            ans=input("What would you like to plot? ")                      # Ask the user for an input.
        if ans=="1":                                                        # Determine the graph type selected by the user. 
          graphtype="(ADR)"                                                 # Set the units for each graph type.
          units=" "                                                         # Print the type of plot that will be generated by the code in the command window.
                                                                            # DO THE SAME WITH ALL THE POSSIBLE SELECTIONS...
        elif ans=="2":                                                      #
          graphtype="(Power)"                                               #
          units=" "                                                         #
        else:                                                               #
          print("\nThis is an incorrect number")                            #
        break                                                               #
    columna=int(ans)+2                                                      #
                                                                            #
                                             
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- #
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- #
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- #
for eachdate in validdates:                             # FOR EVERY VALID DATE (EXISTENT CSVFILE FOLDERS), RUN THE CODE.
    year=eachdate[0:4]                                  #
    monthnumber=eachdate[4:6]                           #
    daynumber=eachdate[6:8]                             #
    readdirectory=outputfolderdirectory+str(year)+str(monthnumber)+str(daynumber)
    if monthnumber=="01":                               # MONTH NAME
        monthname="January"                             #
    elif monthnumber=="02":                             #
        monthname="February"                            #
    elif monthnumber=="03":                             #
        monthname="March"                               #
    elif monthnumber=="04":                             #
        monthname="April"                               #
    elif monthnumber=="05":                             #
        monthname="May"                                 #
    elif monthnumber=="06":                             #
        monthname="June"                                #
    elif monthnumber=="07":                             #
        monthname="July"                                #
    elif monthnumber=="08":                             #
        monthname="August"                              #
    elif monthnumber=="09":                             #
        monthname="September"                           #
    elif monthnumber=="10":                             #
        monthname="October"                             #
    elif monthnumber=="11":                             # 
        monthname="November"                            #
    elif monthnumber=="12":                             #
        monthname="December"                            #
                                                            # ------------------------------------------- SECTION 4: PLOTTING ----------------------------------------------- #
                                                            # ---------------------------------------- SECTION 4A: NUMBER OF PRNs ------------------------------------------- #
    minimum=1000                                            # Set minimum=big number (like 1000) - FOR FURTHER USE IN SECTION 4M. 
    if PRNstograph[0]!="T" and PRNstograph[0]!="t":         # First, identify how many PRNs the user wants to plot from their selection in the graphsettings.csv file. 
        limit=len(PRNstograph)                              # If the user DID NOT insert "T" ("T" means plot all satellites), determine how many PRNs are to be plotted 
    elif PRNstograph[0]=="T" or PRNstograph[0]=="t":        # calcuating the length of the row (i.e. if len(PRNstograph)=6, 6 PRNs will be plotted). 
        if constellation=="G":                              # If the user inserts "T", it means they want to plot all satellites within a constellation. 
            limit=32                                        # Each satellite constellation has a different amount of working satellites.
        elif constellation=="R":                            # GPS has a total of 32 satellites.     
            limit=24                                        # GLONASS has a total of 24 satellites.
        elif constellation=="E":                            # GALILEO has a total of 30 satellites. 
            limit=30                                        #
                                                            # -------------------------------- SECTION 4B: FOR LOOP B FOR NIGHT SUBTRACTION --------------------------------- #     
    import matplotlib.pyplot as plt                         # Import matplotlib: MATPLOTLIB is a Python 2d Plotting Library.
    if normalizedata==1:                                    # If the user selectes to do night subtraction for TEC (normalizedata==1), run the code twice using a for loop:
        torepeat=3                                          # One time for regular data (normalizedcount==1), and the second time for the normalized data (normalizedcount==2).
    else:                                                   # This will generate two plots: One for regular data, and one with night-subtraction. 
        torepeat=2                                          # 
    for normalizedcount in range(1,torepeat):               # START FOR LOOP B.   
        count=1                                             # Start a count. 
        if normalizedcount==2:                              # If normalizedata==1 the code will run twice. After running once for regular data, clear the plot and create a 
            plt.clf()                                       # new one with normalized data.
                                                            # ---------------------------------- SECTION 4C: FOR LOOP C FOR NUMBER OF PRNs ---------------------------------- #
        for i in range(limit):                              # START FOR LOOP C - It will repeat N times, where N is the number of PRNs selected by the user (Section 4A).   
            if PRNstograph[0]=="T" or PRNstograph[0]=="t":  # Save the count into a variable calles savedPRNnumber. This variable will be used later to show the PRN number
                savedPRNnumber=count                        # in the title of the plot, to include the PRN# in the legends, among other uses. If the user selects to plot all satellites
            elif len(PRNstograph)>1:                        # this number is equal to the count started in Section 4B. If the user inputs specific PRN numbers in the graphsettings.csv
                savedPRNnumber=PRNstograph[count-1]         # file, select the value from the PRNstograph vector from Section 1.
                                                            # Set the directory to the csv file.
            csvtograph=filetype+"_"+constellation+str(savedPRNnumber)+"_"+str(year)+str(monthnumber)+str(daynumber)+".csv" ##################YOU CHANGED THIS
            csvtographdirectory=readdirectory+filesep+csvtograph                                                               
                                                                            # ------------------------------ SECTION 4D: ELEVATION THRESHOLD FOR RAW DATA FILES ----------------------------- #
                                                                            # For raw data files, extract the elevation column for the REDTEC file and determine a range of times that are above
                                                                            # the elevation threshold. Save the directory to the REDTEC into a variable called readreducedfile. 
            if y=="ismRawObs" or y=="ismRawOBS" or y=="ismDetObs" or y=="ismDetOBS" or y=="ismRawTEC" or y=="ismRawTec":
                readreducedfile=readdirectory+filesep+"REDTEC"+"_"+constellation+str(savedPRNnumber)+"_"+str(year)+"_"+str(monthnumber)+"_"+str(daynumber)+".csv" #####################YOU ALSO CHANGED THIS
               #  readreducedfile=readdirectory+filesep+"REDTEC"+"_"+constellation+str(savedPRNnumber)+"_"+str(year)+str(monthnumber)+str(daynumber)+".csv" #####################YOU ALSO CHANGED THIS
                if not os.path.isfile(readreducedfile):
                    continue
                import csv                                                  # Open the REDTEC file using import csv. 
                with open(readreducedfile) as csvfilethree:                 #
                    readCSVthree = csv.reader(csvfilethree, delimiter=',')  #
                    counttwo=1                                              # Cut the header off the csvfile cutting the first 20 rows and select the elevation's column.
                    validcolumns=[]                                         #
                    timescolumn=[]                                          #
                    for row in readCSVthree:                                #
                        if len(row)==0:                                     #
                            timescolumnitem="0"                             #
                        else:                                               #
                            timescolumnitem=row[0]                          #
                        timescolumn.append(timescolumnitem)                 #
                        if counttwo>=20:                                    #
                            elevationforthresholdb=row[6]                   #
                            if float(elevationforthresholdb)>=threshold:    # Determine which rows of the elevation column have a value that exceeds the threshold set by the user.
                                validcolumns.append(counttwo)               #
                        counttwo=counttwo+1                                 #
                                                                            #
                    subtractthisvalue=0                                     # Sometimes, satellites cross the elevation threshold multiple times within a day. E.G. PRN 2 is above
                    rangestartrows=[]                                       # the elevation threshold between 1PM and 3PM, and then later between 7PM and 9PM. 
                    for itema in validcolumns:                              # Identify the times at which satellites cross the elevation threshold and save those values into variables.
                        if (itema-subtractthisvalue)!=1:                    # e.g. in the previous example: rangestartrows:[1PM, 7PM] and rangefinalrows=[3PM, 9PM]. 
                            rangestartrow=itema                             #
                            rangestartrows.append(rangestartrow)            #
                        subtractthisvalue=itema                             #
                    if len(rangestartrows)>1:                               #
                        rangefinalrows=[]                                   #
                        for j in range(len(rangestartrows)-1):              #
                            rangefinalrow=rangestartrows[1]                 #
                            rangefinalrows.append(rangefinalrow)            #
                        rangefinalrows=(rangefinalrows,validcolumns[-1])    #
                    elif len(rangestartrows)==1:                            #
                        rangefinalrows=[validcolumns[-1]]                   #
                    countfour=0                                             # Determine the times (in seconds) for both start and final rows in the range variables.
                    starttimes=[]                                           # 
                    finaltimes=[]                                           # 
                    if len(rangestartrows)>1:                               # 
                        for itemb in len(rangestartrows):                   # 
                            startselection=rangestartrows[countfour]        # 
                            finalselection=rangefinalrows[countfour]        # 
                            starttime=timescolumn[startselection]           # 
                            finaltime=timescolumn[finalselection-1]         # 
                            starttimes.append(str(starttime))               # 
                            finaltimes.append(str(finaltime))               # 
                            countfour=countfour+1                           # 
                    elif len(rangestartrows)==1:                            # 
                        startselection=rangestartrows[0]                    # 
                        finalselection=rangefinalrows[0]                    # 
                        starttimes=[timescolumn[startselection]]            # 
                        finaltimes=[timescolumn[finalselection-1]]          # 
                    starttimesflt=[]                                        # Convert the times to float values.
                    finaltimesflt=[]                                        #  
                    for t in starttimes:                                    # 
                        starttimesflt.append(float(t))                      # 
                    for u in finaltimes:                                    # 
                        finaltimesflt.append(float(u))                      # 
                                                                                                # ----------------------- SECTION 4E: EXTRACTING THE COLUMNS FROM THE CSV FILE ----------------------- # 
            import os                                                                           # Import and read the csv (if it exists) If not, jump to SECTION 5.
            if os.path.isfile(csvtographdirectory):                                             #
                print("Plotting Time vs.",graphtype)
                import csv                                                                      #
                with open(csvtographdirectory) as csvfiletwo:                                   #
                    readCSVtwo = csv.reader(csvfiletwo, delimiter=',')                          #
                    print(y)                                                                    # Print the file type in the command window. 
                    if y=="REDTEC" or y=="ismRawTEC" or y=="ismRawTec":                         # Set the variable numbers - These nunmbers will be used later for multiple purposes and vary 
                              variablesignal=4                                                  # between file types. 
                              variable=20                                                       #
                              elevationvar=6                                                    #
                    elif y=="REDOBS":                                                           #   
                              variablesignal=3                                                  #
                              variable=20                                                       #
                              elevationvar=5                                                    #
                    elif y=="ismRawObs" or y=="ismRawOBS" or y=="ismDetObs" or y=="ismDetOBS":  #
                              variablesignal=2                                                  #
                              variable=9                                                        #
                    rawyaxiscolumn=[]                                                           # Select the column within the csv file based on the user selection in part 3.  
                    varsignaltypecolumn=[]                                                      # Cut off the header using the variable from 11ac. Do the same with the "times" column.
                    elevationcolumn=[]                                                          #
                    times=[]                                                                    #
                    countone=1                                                                  #
                    for row in readCSVtwo:                                                      #
                        if countone>=variable:                                                  #
                            selectedrowitem=row[columna]                                        #
                            signaltypeitem=row[variablesignal]                                  #
                            if y=="REDTEC" or y=="REDOBS":                                      #
                                elevationforthreshold=row[elevationvar]                         #
                                elevationcolumn.append(elevationforthreshold)                   #
                            time=row[0]                                                         #
                            rawyaxiscolumn.append(selectedrowitem)                              # Save the column to a variable called "rawyaxiscolumn".
                            varsignaltypecolumn.append(signaltypeitem)                          # Read the signal type column. This variable will be used later to determine the signal types for the selected PRN. 
                            times.append(time)                                                  #
                        countone=countone+1                                                     #
                    types=[1,2,3,4,5,6,7]                                                       # There are 7 types of signals (1 through 7).
                    saves=[]                                                                    # Determine how many types of signals (and which ones) are present in the selected file.
                    varsignaltypecolumn = list(map(int, varsignaltypecolumn))                   # Save the present signal types into a variable calles saves. 
                    for item in types:                                                          #                                   
                        if item in varsignaltypecolumn:                                         #
                            item=int(item)                                                      #
                            saves.append(item)                                                  #
                    if onlyonesignal==1:                                                        #
                        saves=[saves[0]]                                                        #
                                                                                                # ----------------------- SECTION 4F: FOR LOOP D FOR SIGNAL TYPE ----------------------- #                                      
                    for selection in saves:                                                     # START FOR LOOP D that will repeat for each signal type (selection) for the selected PRN. 
                        countthree=variable                                                     # First, determine which rows correspond to the selected signal type.
                        selectionint=int(selection)                                             # Save the row numbers to a variable called listofrows.
                        listofrows=[]                                                           #
                        for signaltoeval in varsignaltypecolumn:                                #
                            signaltoevalint=int(signaltoeval)                                   #
                            if signaltoevalint==selectionint:                                   #
                                listofrows.append(countthree)                                   #
                                if selection==1:                                                #
                                    rowlistone=listofrows                                       #
                                elif selection==2:                                              #
                                    rowlisttwo=listofrows                                       #
                                elif selection==3:                                              #
                                    rowlistthree=listofrows                                     #
                                elif selection==4:                                              #
                                    rowlistfour=listofrows                                      #
                                elif selection==5:                                              #
                                    rowlistfive=listofrows                                      #
                                elif selection==6:                                              #
                                    rowlistsix=listofrows                                       #
                                elif selection==7:                                              #
                                    rowlistseven=listofrows                                     #
                            countthree=countthree+1                                             #
                                                                                                # ---------------------------- SECTION 4G: TIME PERIODS ---------------------------- # 
                        redyaxiscolumn=[]                                                       # Use the listofrows variable from section 4f and cut the rawyaxiscolumn from section 4e with the respective rows. 
                        newelevations=[]                                                        #
                        newtimes=[]
                        for rowitem in listofrows:                                              #
                            rowitemint=int(rowitem)                                             #
                            rowitemint=rowitemint-variable                                      #
                            newtime=times[rowitemint]                                           # Cut the times column with the respective rows. 
                            redyaxisitem=rawyaxiscolumn[rowitemint]                             #
                            if y=="REDTEC" or y=="REDOBS":                                      #
                                newelevation=elevationcolumn[rowitemint]                        #
                                newelevations.append(newelevation)                              #
                            newtimes.append(newtime)                                            #
                            redyaxiscolumn.append(redyaxisitem)                                 # Save the new column as "redyaxiscolumn". Save the new times column as "newtimes".
                        countsix=1                                                              # Sometimes, satellites cross the elevation threshold multiple times within a day. E.G. PRN 2 is above
                        biggerdiference=1                                                       # the elevation threshold between 1PM and 3PM, and then later between 7PM and 9PM. Ecah of these times is called a TIME PERIOD. 
                        listofpositions=[]                                                      # Identify the times at which satellites cross the elevation threshold and save those values into a variable.
                        firstselection=0                                                        # 
                        for timeinsec in newtimes:                                              #
                            difference=float(timeinsec)-firstselection                          # Determine the difference between each data value and the next one in the newtimes vector.
                            if difference>1200:                                                 # If the difference is bigger than 1200 (i.e 1200 seconds), save the position into a variable called
                                biggerdifference=1                                              # listofpositions. 
                            elif difference<=1200:                                              # 
                                biggerdifference=0                                              #
                            if countsix==1 or biggerdifference==1:                              #
                                listofpositions.append(countsix)                                #
                            firstselection=float(timeinsec)                                     #
                            countsix=countsix+1                                                 #
                                                                                                # ---------------------------- SECTION 4H: FOR LOOP E FOR TIME PERIOD ------------------------------- # 
                        lengthofthelist=len(listofpositions)                                    # Determine the amount of time periods by finding the length of the listofpositions variable.
                        countseven=1                                                            # 
                        countfifteen=1                                                          # 
                        if y=="ismRawObs" or y=="ismDetObs" or y=="ismDetOBS" or y=="ismRawTEC" or y=="ismRawTec":
                            listofpositions=starttimesflt                                       # If the selected file is a raw data file, set listofpositions equal to the starttimesflt variable from Section 4D. 
                        if onlyonesignal==1 and independentgraph==0:                            # If the plot to be created is NOT a summary plot and onlyonesignal=1 from section 1,
                            listofpositions=[listofpositions[0]]                                # listofpositions=first value in listofpositions (listofpositions[0])
                            lengthofthelist=len(listofpositions)                                #                            
                        for timestartposition in listofpositions:                               # START FOR LOOP E THAT WILL REPEAT FOR EVERY TIME PERIOD.             
                            if y=="REDTEC" or y=="REDOBS":                                      # Start this section ONLY if the user selected a reduced file, either REDOBS or REDTEC.
                                if countseven<lengthofthelist:                                  # Each time period has a different start time and end time. The start time will change automatically
                                    timefinalposition=listofpositions[countseven]               # every time FOR LOOP E restarts, while the final time must be extracted from the "listofpositions" variable.
                                    timefinalposition=timefinalposition-1                       # 
                                elif countseven==lengthofthelist:                               #         
                                    timefinalposition=len(newtimes)                             # 
                                counteight=1                                                    # 
                                finaltimes=[]                                                   # 
                                finalyaxis=[]                                                   #
                                finalelevationcolumn=[]                                         # Start another for loop to create the new x and y axes.
                                for itemd in newtimes:                                          # Cut the newtimes and redyaxiscolumn from section 4G.
                                    if counteight>=timestartposition and counteight<=timefinalposition:
                                        finaltimes.append(itemd)                                # Create new variables that include ONLY data within the selected time period.
                                    counteight=counteight+1                                     # New variables: finaltimes (x axis) and finalyaxis (y axis). 
                                countnine=1                                                     #
                                for iteme in redyaxiscolumn:                                    #
                                    if countnine>=timestartposition and countnine<=timefinalposition:
                                        finalyaxis.append(iteme)                                #
                                    countnine=countnine+1                                       #
                                counteleven=1                                                   #
                                for itemf in newelevations:                                     # Cut off the rows that have an elevation under the threshold.
                                    if counteleven>=timestartposition and counteleven<=timefinalposition:
                                        finalelevationcolumn.append(itemf)                      # 
                                    counteleven=counteleven+1                                   # 
                                addvariablestart=timestartposition+variable-1                   # 
                                addvariablefinal=timefinalposition+variable-1                   # 
                                counttwelve=1                                                   # 
                                validelevpositions=[]                                           # 
                                correctedelevation=[]                                           # 
                                finalelevationcolumn = list(map(float, finalelevationcolumn))   # 
                                for itemg in finalelevationcolumn:                              # 
                                    if itemg>=threshold:                                        # 
                                        validelevpositions.append(counttwelve)                  # 
                                        correctedelevation.append(itemg)                        # Create a new variable (vector) containing all elevations above the threshold. 
                                    counttwelve=counttwelve+1                                   # 
                                countthirteen=1                                                 # 
                                validelevpositionsint=list(map(int,validelevpositions))         # 
                                finaltimescorrected=[]                                          # 
                                finalyaxiscorrected=[]                                          # 
                                for itemh in finaltimes:                                        # Cut the finaltimes vector to include only the times at which the eleveation
                                    if countthirteen in validelevpositionsint:                  # is above the threshold. Save it to finaltimescorrected.  
                                        finaltimescorrected.append(itemh)                       # 
                                    countthirteen=countthirteen+1                               # 
                                countforteen=1                                                  # 
                                for itemi in finalyaxis:                                        # Cut the finalyaxis vector to include only the values corresponding to elevations
                                    if countforteen in validelevpositionsint:                   # above the threshold. Save it to finalyaxiscorrected. 
                                        finalyaxiscorrected.append(itemi)                       # 
                                    countforteen=countforteen+1                                 #
                                                                                                # --------------------------------- SECTION 4J: MODIFY RAW DATA ---------------------------------- #
                            elif y=="ismRawObs" or y=="ismRawOBS"  or y=="ismDetObs" or y=="ismDetOBS" or y=="ismRawTEC" or y=="ismRawTec":
                                                                                                # Start this section if the user selects a raw data file type.
                                starttimetocompare=starttimesflt[countseven-1]                  # Extract the start time from the starttimesflt from Section 4D.
                                finaltimetocompare=finaltimesflt[countseven-1]                  # Extract the final time from the starttimesflt from Section 4D.
                                countfive=0                                                     # 
                                validpositions=[]                                               # 
                                for itemc in newtimes:                                          # Determine which rows have time values within the specified range.
                                    itemc=float(itemc)                                          #
                                    if itemc>=starttimetocompare and itemc<=finaltimetocompare: #
                                        validpositions.append(countfive)                        #
                                    countfive=countfive+1                                       # 
                                finaltimescorrected=[]                                          #
                                finalyaxiscorrected=[]                                          #
                                for itemj in validpositions:                                    # Correct the x and y axes to include only values within the specified range.
                                    timetoappend=newtimes[itemj]                                #
                                    yaxistoappend=redyaxiscolumn[itemj]                         #
                                    finaltimescorrected.append(timetoappend)                    #
                                    finalyaxiscorrected.append(yaxistoappend)                   #
                                                                                                # If TEC detrending is activated, from Section 1, run Section 4K:
        # --------------------------------------------------------------------------------------------------------------------------------------------------------- #
        # --------------------------------------------------------------------------------------------------------------------------------------------------------- #
        # --------------------------------------------------------- SECTION 4K: TEC DETRENDING -------------------------------------------------------------------- #    
                                if TECdetrending==1:                                            # For TEC: If TECdetrending=1 in the GRAPHSETTINGS csv file, detrend the TEC data.
                                    bftimes=[]                                                  # Convert the elements of finaltimescorrected and finalyaxiscorrected into float values 
                                    bfTEC=[]                                                    # before applying the butterworth filter.
                                    for itemk in finaltimescorrected:                           # 
                                        bftimes.append(float(itemk))                            # 
                                    for iteml in finalyaxiscorrected:                           # 
                                        bfTEC.append(float(iteml))                              # 
                                    matrixtoprint=[]                                            # Print the times and TEC vectors into two columns in a new csv file. 
                                    counteighteen=0                                             # This file can be later called from MATLAB for a better TEC detrending.
                                    for itemm in range(len(bftimes)):                           # This CSV file is saved in the same folder as the graphingmain.py code.
                                        row=[bftimes[counteighteen],bfTEC[counteighteen]]       #
                                        matrixtoprint.append(row)                               #
                                        counteighteen=counteighteen+1                           #
                                    import csv                                                  #
                                    namedetrending = "TECdetrending"+constellation+str(savedPRNnumber)+str(selection)+"-"+str(year)+str(monthnumber)+str(daynumber)+".csv"
                                    with open(namedetrending, "w", newline='') as csvfile:      #
                                        writer = csv.writer(csvfile)                            #
                                        writer.writerows(matrixtoprint)                         #
                                    import numpy as np                                          # TEC: Polyfit subtraction and then a type of Butterworth filtering/ Sliding Avg
                                    poly_degree=3                                               # filtering on TEC time series (TEC_ts values).
                                    poly_coef=np.polyfit(bftimes,bfTEC,poly_degree)             # Degree of the polynomial.
                                    poly=np.polyval(poly_coef,bftimes)                          # In this case, finalyaxiscorrected is the TEC vector.
                                    poly_sub_tec=bfTEC-poly                                     # 
                                    from scipy import signal                                    # 
                                    polyfit_tec=signal.detrend(poly_sub_tec)                    # 
                                    Tdata=bftimes[-2]-bftimes[0]                                # 
                                    dfreq=1/Tdata                                               # 
                                    LP=len(polyfit_tec)                                         # 
                                    tec_fft=np.fft.fftshift(np.fft.fft(np.fft.ifftshift(polyfit_tec)))
                                    if Tdata<=60:                                               # Desired cut off frequency [Hz]
                                        cutoff=0.1                                              # Higher cut off for shorter lengths
                                    else:                                                       #
                                        cutoff=0.1                                              #
                                    order=6                                                     # Order of the butterworth filter
                                                                                                # ------------------- Butterworth filter -------------------------- #
                                                                                                            # This extract creates a kernel for low pass butterworth filter.
                                    freq=np.arange(-LP/2*dfreq+dfreq,(LP/2*dfreq)+dfreq,dfreq)              # Create frequency array
                                    butterlow=np.divide(1,np.sqrt(1+(np.power((freq/cutoff),(2*order)))))   # Size(freq)
                                    butterhi=1.0-butterlow
                                                                                                # ----------------------------------------------------------------- #
                                    tec_filt=np.fft.fftshift(np.fft.ifft(np.fft.ifftshift(np.multiply(tec_fft,butterhi))))
                                    Detrended_TEC=(np.real(tec_filt))                           #
                                    finalyaxiscorrected=Detrended_TEC                           # Set the Detrended TEC as the new finalyaxiscorrected.
        # --------------------------------------------------------------- END OF TEC DETRENDING ------------------------------------------------------------------- #
        # --------------------------------------------------------------------------------------------------------------------------------------------------------- #
        # --------------------------------------------------------------------------------------------------------------------------------------------------------- #
                                                                                                    # --------------------------------- SECTION 4L: FINAL FIXES ---------------------------------- #
                            lengtha=len(finaltimescorrected)                                        # Calculate the length of the finaltimescorrected vector.
                            lengthb=len(finalyaxiscorrected)                                        # Calculate the length of the finalyaxiscorrected vector.
                            if countfifteen==1:                                                     # Select a letter. This letter will be printed in the title of the plot.
                                lettername='A'                                                      # The letter represents the time period. e.g. if there are two time periods for one PRN,
                            elif countfifteen==2:                                                   # the plot showing time period 1 will have "A" in the title. Time period 2 will have "B".
                                lettername='B'                                                      # Refer to Section 4G to see the definition of a time period. 
                            elif countfifteen==3:                                                
                                lettername='C'                                                   
                            elif countfifteen==4:                                                
                                lettername='D'                                                   
                            elif countfifteen==5:                                                
                                lettername='E'                                                   
                            countfifteen=countfifteen+1                                              
                            listtoreferto=finaltimescorrected                                       # Rename the x-axis values to "listtoreferto".
                            listforyaxis=finalyaxiscorrected                                        # Rename the y-axis values to "listforyaxis". 
                            newtimesUTC=[]                                                          # 
                            for numbertoconvert in listtoreferto:                                   # Convert the times to UTC.
                                numbertoconvert=float(numbertoconvert)                              # 86400 sec = 1 day.
                                if numbertoconvert>=86400:
                                    remainder=numbertoconvert%86400
                                    if remainder == 0:
                                        remainder = 86400
                                elif numbertoconvert<86400:                                         
                                    remainder=numbertoconvert                                       # 
                                howmanyhoursflt=remainder/3600                                      # Determine the amount of hours. 
                                newtimesUTC.append(howmanyhoursflt)                                 # 
                            if independentgraph==1:                                                 # Determine the name of the graph.
                                csvtograph=filetype+"_SummaryPlot_"+str(year)+str(monthnumber)+str(daynumber)+".csv"
                            else:                                                                   # 
                                csvtograph=filetype+"_"+constellation+str(savedPRNnumber)+"_"+str(year)+str(monthnumber)+str(daynumber)+".csv"
                            lengthtocutname=len(csvtograph)-4                                       # 
                            graphname=csvtograph[:lengthtocutname]                                  # 
                            if independentgraph==1:                                                 #
                                graphname=graphname+"_"+graphtype+"_"+constellationtype                                   #
                            else:                                                                   #
                                graphname=graphname+"_"+graphtype+"_"+"Signal"+str(selection)+"_"+lettername
                            if normalizedcount==2:                                                  #
                                graphname=graphname+"_Normalized"                                   #
                            if verticaltec==1 and normalizedcount==2:                               #
                                graphname=graphname+"_verticalTEC"                                  #
                            graphname=graphname+str(formattype)                                     #
                            savinggraphs=graphsfolderdirectory+str(year)+str(monthnumber)+str(daynumber)
                            print(graphname)                                                        # Print the graph name in the command window. 
                            listforyaxisflt=[]                                                      #
                            for element in listforyaxis:                                            # Convert all the elements within listforyaxis into float values.
                                elementtoadd=float(element)                                         #
                                listforyaxisflt.append(elementtoadd)                                #
                                                                                                    # --------------------------------- SECTION 4M: NIGHT SUBTRACTION AND VERTICAL TEC ---------------------------------- #
                            if len(listforyaxisflt)!=0:                                             # Run this part of the code ONLY if listforyaxisflt is not an empty vector.
                                if y=="REDTEC" or y=="REDOBS":                                      # Run this part of the code ONLY for low-rate TEC data. 
                                    if normalizedata==1:                                            # Run this part of the code ONLY if nigh-subtraction is selected (normalizedata==1).
                                        if normalizedcount==1:                                      # When normalizedcount==1 (regular data), select the minimum value. Refer to section 4B.
                                            minimumvalueyaxis = min(float(s) for s in listforyaxisflt)
                                            if minimumvalueyaxis<minimum:                           # 
                                                minimum=minimumvalueyaxis                           # After FOR LOOP B (SECTION 4B) runs completely for the first time, it will calculate the minimum TEC value from ALL PRNs.
                                        elif normalizedcount==2:                                    # When normalizedcount==2 (i.e. when FOR LOOP B runs for the second time):
                                            normalizedaxis=[]                                       #
                                            countthirty=0                                           #
                                            for elementa in listforyaxisflt:                        # For every element in listforyaxisflt, convert to vertical TEC (if vertical TEC==1) and do the night-subtraction. 
                                                                                                    # ----------------------------------------------- SLANT  TO VERTICAL TEC --------------------------------------------- #
                                                if verticaltec==1:                                  # This section uses geometry to get rid of the effects due to the variable thickness of the atmosphere. 
                                                    import math                                     #
                                                    minimumvaluetouse = min(float(s) for s in listforyaxisflt)
                                                    elementa=elementa-minimumvaluetouse             #
                                                    elevationtouse=correctedelevation[countthirty]*0.0174533
                                                    coselev=math.cos(elevationtouse)                #
                                                    obliquity=1/(math.sqrt(1-(0.947979*(coselev)))) #
                                                    newelement=elementa/obliquity                   #
                                                    newelement=newelement+minimumvaluetouse         #
                                                    countthirty=countthirty+1                       #
                                                                                                    # --------------------------------------------------------------------------------------------------------------------- #
                                                else:                                               #
                                                    newelement=elementa                             #
                                                elementtoappend=newelement-minimum                  # Subtract the minimum value (computed at the beginning of section 4M) from each element.
                                                normalizedaxis.append(elementtoappend)              # Append the element to a new vector called normalized axis. 
                                            listforyaxisflt=normalizedaxis                          # Set listforyaxisflt==normalizedaxis. 
                            if independentgraph==1:                                                 # If the user is doing a summary plot add the shift value to every element in the listforyaxisflt vector. See Section 1.
                                summaryplotaxis=[]                                                  #
                                for elementa in listforyaxisflt:                                    #
                                    elementtoappend=elementa+(count*shiftvalue)                     #
                                    summaryplotaxis.append(elementtoappend)                         #
                                listforyaxisflt=summaryplotaxis                                     #
                                                                                                    # ------------------------------------- SECTION 4N: PLOTTING ------------------------------------- #
                            signaltypetoprint=str(selection)                                        # Signal Mapping for Satellite Systems.
                            if constellation=="G":                                                  # From the selection from FOR LOOP D, determine the signal type (L1, L2, ETC). 
                                if signaltypetoprint=="1":                                          # This signal type will be printed in the plot's title. 
                                    sttp="L1CA"                                                     #
                                elif signaltypetoprint=="4":                                        #
                                    sttp="L2Y"                                                      #
                                elif signaltypetoprint=="5":                                        #
                                    sttp="L2C"                                                      #
                                elif signaltypetoprint=="6":                                        #
                                    sttp="L2P"                                                      # 
                                elif signaltypetoprint=="7":                                        #
                                    sttp="L5Q"                                                      #
                            elif constellation=="R":                                                #
                                if signaltypetoprint=="1":                                          #
                                    sttp="L1CA"                                                     #
                                elif signaltypetoprint=="3":                                        #
                                    sttp="L2CA"                                                     #
                                elif signaltypetoprint=="4":                                        #
                                    sttp="L2P"                                                      #
                            elif constellation=="E":                                                #
                                if signaltypetoprint=="1":                                          #
                                    sttp="E1"                                                       #
                                elif signaltypetoprint=="2":                                        #
                                    sttp="E5A"                                                      #
                                elif signaltypetoprint=="3":                                        #
                                    sttp="E5B"                                                      #
                                elif signaltypetoprint=="4":                                        #
                                    sttp="AltBOC"                                                   #
                                                                                                    # Only generate the plots if the vectors are not empty.
                            if len(listforyaxisflt) != 0:                                                                     
                                if legend==1:                                                           # If the user wants a legend, put it on the right next to the graph. Then, PLOT.
                                    legendtoprint=str(savedPRNnumber)                                   # 
                                    plt.plot(newtimesUTC,listforyaxisflt, label=legendtoprint)          # 
                                else:                                                                   #
                                    plt.plot(newtimesUTC,listforyaxisflt)                               #

                                # For sigma only: compute the rate of chagne.
                                if y == "REDOBS":
                                    if "secsigma" in graphtype:
                                        # Determine the maximum value in the y-axis, and set the max value as the axis limit.
                                        yaxis_max = max(listforyaxisflt)
                                        yaxis_min = min(listforyaxisflt)
                                        # If the maximum secsigma value > 100, set the y axis max to 3.
                                        if yaxis_max>100:
                                            setyaxisrange = 1
                                            yaxisfinalvalue = 2


                                plt.ylabel(str(graphtype)+" - "+str(units))                             # Y-axis label.
                                plt.xlabel('Time (UTC)')                                                # X-axis label.
                                itoprint=i+1                                                            #
                                if graphtype=='TECdot':                                                 # If graphtype==TECDOT, change the name to 'High Rate TEC Rate of change'.
                                    graphtype='High Rate TEC Rate of change'                            # 
                                if independentgraph==1:                                                 # Set the title  and subtitle of the plot. 
                                    titletoprint=monthname+" "+str(daynumber)+" - "+"Time (UTC) vs. "+graphtype+" - Summary Plot - "+constellationtype
                                else:                                                                   # 
                                    titletoprint=monthname+" "+str(daynumber)+" - "+"Time (UTC) vs. "+graphtype+" - "+constellationtype+" "+str(savedPRNnumber)+" ("+lettername+")"
                                subtitletoprint="Elevation threshold: "+str(threshold)+"° - Signal type: "+str(sttp)+" - Loc: "+location
                                if independentgraph==1:                                                 #  
                                    subtitletoprint="Elevation threshold: "+str(threshold) +" - Loc: "+location
                                if verticaltec==1 and normalizedcount==2:                               # 
                                    subtitletoprint=subtitletoprint+" - Vertical TEC"                   # 
                                if setxaxisrange==1:                                                    # Change the limits of the axes based on line 20 and 21 of the GRAPHSETTINGS.csv file. 
                                    plt.xlim([xaxisstartvalue,xaxisfinalvalue])                         #
                                if setyaxisrange==1:
                                    plt.ylim([yaxisstartvalue,yaxisfinalvalue])
                                if verticalline==1:                                                     # If the user wants to print a vertical line, use the axvline function - Line 29 of the GRAPHSETTINGS.csv file.
                                    plt.axvline(x=verticallinexpoint, color='K', linewidth=0.5)         #
                                if len(newtimesUTC)!=0:                                                 # Label the plot lines (in-plot legends) - Line 25 of the GRAPHSETTINGS.csv file.
                                    if PRNlabeling==1:                                                  # 
                                        xdatapoint=newtimesUTC[int((len(newtimesUTC))/2)]               # 
                                        ydatapoint=listforyaxisflt[int((len(listforyaxisflt))/2)]       # 
                                        plt.text(xdatapoint, ydatapoint,savedPRNnumber)                 # 
                                plt.suptitle(titletoprint, fontsize=titlefontsize)                      # Print the title and subtitle in the plot. 
                                plt.title(subtitletoprint, fontsize=subtitlefontsize)                   #
                                                                                                        # ------------------------------------- SECTION 4O: SAVING THE PLOT ------------------------------------- #
                                import os                                                               # Create the folder directory if it does not exist.
                                if independentgraph == 1:
                                    savinggraphs = savinggraphs + filesep + "Summary_Plots"
                                    if y == "REDTEC":
                                        savinggraphs = savinggraphs + filesep + "TEC"
                                    else:
                                        savinggraphs = savinggraphs + filesep + "OBS"
                                else:
                                    savinggraphs = savinggraphs + filesep + graphtype
                                if not os.path.exists(savinggraphs):                                    #
                                    os.makedirs(savinggraphs)                                           #
                                savinggraphs=savinggraphs+filesep+graphname
                                print(savinggraphs)                                                     # Print the directory in the command window. 
                                if legend==1:                                                           # 
                                    plt.legend()                                                        # Print the legend on the plot if legend==1.
                                    plt.savefig(savinggraphs)                                           # Save the figure.
                                else:                                                                   # 
                                    plt.savefig(savinggraphs)                                           # Save the figure.
                                if independentgraph==0:                                                 # If the summary plot option is not active, clear the graph.
                                    plt.clf()                                                           # 
                                countseven=countseven+1                                                 # END OF FOR LOOP D.
                                                                                                    #------------------------------------ SECTION 5: THE DIRECTORY DOES NOT EXIST ------------------------------------- #
            elif not os.path.isfile(csvtographdirectory):                                           # If the directory does NOT exist (from section 4E), print "THE DIRECTORY DOES NOT EXIST"
                toprint="The following directory does not exist: "+csvtographdirectory              # in the command window. 
                print(toprint)                                                                      # 
            count=count+1                                                                           #
                                                                                                    # END OF FOR LOOP B - END OF FOR LOOP C.
    TOBEPRINTED="The following day has been processed: "+monthname+" "+str(daynumber)               # Print a final message.
    print(TOBEPRINTED)                                                                              #
    print(" ")                                                                                      #
#print(" ")                                                                                      #  
#print("Done.")                                                                                  # END OF THE CODE.
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #                     

