# ----- CONFIGURE YOUR EDITOR TO USE 4 SPACES PER TAB ----- #
import settings
import sys,os
sys.path.append(os.path.join(os.path.split(os.path.abspath(__file__))[0], 'lib'))
import pymysql as db

def connection():
    ''' User this function to create your connections '''
    con = db.connect(
        localhost,
        root,
        ert%64bgr0,
        vaxdbEx3)

    
    return con



def ngrams(text , num):
    import re
    stops  = set( ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 
    'you', "you're", "you've", "you'll", "you'd", 
    'your', 'yours', 'yourself', 'yourselves', 'he',
    'him', 'his', 'himself', 'she', "she's", 'her', 
    'hers', 'herself', 'it', "it's", 'its', 'itself', 
    'they', 'them', 'their', 'theirs', 'themselves', 
    'what', 'which', 'who', 'whom', 'this', 
    'that', "that'll", 'these', 'those', 'am', 'is',
    'are', 'was', 'were', 'be', 'been', 'being', 'have', 
    'has', 'had', 'having', 'do', 'does', 'did', 'doing', 
    'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 
    'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with',
    'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after',
    'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off',
    'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 
    'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most',
    'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 
    'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 
    'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 
    'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', 
    "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't",
     "days" , "day" , "around" , "went"   , "left" , "morning" , "night"  , "hours" , "minutes", "also" , "cannot"])
    tokens = [y for y in re.findall(r"[\w]+" , text.lower()) if y not in stops and not y[0].isdigit()]
    return [' '.join(tokens[i:i+num]) for i in range(len(tokens)-num+1)]

def mostcommonsymptoms(vax_name):
    
    from collections import Counter
    con=connection()
    cur=con.cursor()
    cur.execute("select symptoms from vaccination where vaccines_vax_name = '%s'" % vax_name)
    grams = []
    for x in cur.fetchall():
        grams +=  ngrams(x[0] , 1)
    return [(vax_name ,)] + [(x, ) for x , times in Counter(grams).most_common(20)]


def buildnewblock(blockfloor):
    
    import random
    from random import randint
    con=connection()
    cur=con.cursor()
    floor = int(blockfloor)
    cur.execute("select blockcode from block where blockfloor = %d" % floor)
    blocks = set([x[0] for x in cur.fetchall()])
    if len(blocks) < 9 :
        rooms = randint(0 , 4)
        for new_block in range(1,10):
            if new_block not in blocks:
                break
        try :
            cur.execute("""INSERT INTO BLOCK(BLOCKFLOOR , BLOCKCODE) VALUES(%d , %d )  """ %(floor , new_block))
            rand_room_type = ["single" , "double" , "triple" , "quadruple"]
            for j in range(0 , rooms+1):
                roomnumber = floor * 1000 + new_block * 100 + j
                cur.execute("""INSERT INTO ROOM(ROOMNUMBER , ROOMTYPE , BLOCKFLOOR , BLOCKCODE , UNAVAILABLE) 
                VALUES( %d , '%s' , %d , %d , %d) """ %(roomnumber , random.choice(rand_room_type) , floor , new_block , 0))
            con.commit()
            return [("ok" ,)]
        except :
            con.rollback()
            return [("error" ,)]
    else :
        return [("error" , )]
    
 

def findnurse(x,y):
    
    con=connection()
    cur=con.cursor()
    cur.execute(""" select  EmployeeID, Name , count(distinct patient_SSN) as patients_vaccinations_attended 
    from nurse, vaccination where EmployeeID = nurse_EmployeeID and EmployeeID in
    (select EmployeeID from  nurse n where not exists (select * from 
    block b where b.BlockFloor= %d and not exists(select * from on_call on2 where n.EmployeeID  = on2.Nurse and 
    b.BlockFloor = on2.BlockFloor and b.BlockCode =on2.BlockCode)))   
    and EmployeeID in(select PrepNurse from appointment group by PrepNurse having count(*) >= %d)
    group by EmployeeID , Name """ % (int(x) , int(y))) 
    return [tuple(z[0] for z in cur.description)] + list(cur.fetchall())

def empty(value, num):
    if value is None:
        return tuple( ["Nan" for i in range(num)])
    return value

# we assumed that bases might have missing values anywhere
def patientreport(patientName):
    con=connection()
    cur=con.cursor()
    cur.execute("select ssn from patient where name = '%s'" % patientName)  
    results = [("Patient_SSN" , "Patient_name" , "Doctors_name" , "Nurse_name" ,"Treatment_name" , 
        "Treatment_cost" , "Stay_end" , "Room_number" , "Block_floor" , "Block_code" , )]      
    for x in cur.fetchall():
        cur.execute("select stay , Physician , AssistingNurse , Treatment from undergoes where patient = %d" % x[0])
        undergoes = cur.fetchall()
        listed_undergoes = [z[0] for z in undergoes]
        cur.execute("select stayid from stay where patient = %d " % x[0])
        unique_stays =[z[0] for z in cur.fetchall() if z[0] not in listed_undergoes]
        for y in undergoes:
            temp = (x[0] , patientName , )
            cur.execute("select Name from physician where EmployeeID = %d" % y[1] ) 
            temp += empty(cur.fetchone() , 1)
            cur.execute("select name from nurse where EmployeeID  = %d" % y[2])
            temp += empty(cur.fetchone() , 1)
            cur.execute("select name , cost from treatment where code = %d" % y[3] )
            temp += empty(cur.fetchone() , 2)
            cur.execute("select stayend , room from stay where stayid = %d" % y[0])
            temp+=empty(cur.fetchone() ,2)
            cur.execute("select blockfloor , blockcode from room where roomnumber = %d" % temp[7])
            results.append( temp + empty(cur.fetchone() , 2)  )
        for i in range(len(unique_stays)):
            temp = (x[0] , patientName , ) + empty(None , 4)
            cur.execute("select stayend , room from stay where stayid = %d " % unique_stays[i])
            temp += cur.fetchone()
            cur.execute("select  blockfloor , blockcode from room where roomnumber = %d" % temp[7])
            temp += empty( cur.fetchone() , 2)
            results.append(temp)
    return results

