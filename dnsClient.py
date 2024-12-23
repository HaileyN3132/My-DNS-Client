import sys
import random
import re

import binascii
import socket


#Part 1 start here
''' 
    Generate ID for Query message
    By generating random value for 16 bits binary
    Return a string of 16 bits as HEX without 0x
'''
def generate_id():
    id_binary = ""
    id_return = ""
    count = 0
    for i in range(16):
        bit = random.randint(0, 1)
        #print(f"Index {i} value {bit}")
        id_binary += str(bit)
        id_hex = hex(int(id_binary,2))[2:]

    #print(f"ID_b2 = {id_binary}")      #DB
    #print(f"ID_b16 = {id_hex}")            #DB

    if(len(id_hex) == 3):
        id_hex = "0" + id_hex
        #print(f"NEW id_hex = {id_hex}")    #DB

    # Create format hex value 
    for char in id_hex:
        id_return += char
        count += 1
        if(count == 2):
            id_return += " "
            count = 0
        

    return id_return 


'''
    Create Query Message
    Return a string query message in HEX at the end
'''
def createQueryMessage( header_sec,host_name):
    return header_sec + create_question_section(host_name)


'''
    Prepare header section for Query
    Return a string with 12 bytes in HEX form
'''
def create_header_section():
    id_field = generate_id()                # 16 bits in HEX 
    flag_field = "01 20 "                   # 16 bits in HEX
    qdcount_field = "00 01 "                # 16 bits, set to 1 means sending only 1 host name
    ancount_field = "00 00 "                # 16 bits, set to 0 for QUERY
    nscount_field = "00 00 "                # 16 bits, 
    arcount_field = "00 00 "                # 16 bits, the value for this field using dig is 00 01

    return id_field + flag_field + qdcount_field + ancount_field + nscount_field + arcount_field



'''
    Prepare question section base on user input
    Return a string of 3 fields in question section in string of HEX values 
'''
def create_question_section(user_input):
    qname_field = construct_qname_field(user_input)
    qtype_field = "00 01 "
    qclass_field = "00 01"

    return qname_field + qtype_field + qclass_field


    
'''
    Convert user input to QNAME format
    Return a string including HEX represent QNAME field 
'''
def construct_qname_field(user_input):
    qname_by_part = []
    listLabels = re.split(r'[.]', user_input)
    qname = ""      # Return

    # Loop through list of labels
    for str in listLabels:
        temp_part = ""

        #For each str, convert its length from decimal to hex
        if(len(str) <= 15):
            #print(f"length 0{hex(len(str))[2:]}")   # Add 0 prefix in case str's length < 16
            temp_part += f"0{hex(len(str))[2:]} "
        else:
            #print(f"length {hex(len(str))[2:]}")
            temp_part += f"{hex(len(str))[2:]} "

        #Convert each character in str into hex value
        for char in str:
            #print(hex(ord(char))[2:])       #Notice: syntax [2:0] help to eliminate the "0x" part in hex value
            temp_part += f"{hex(ord(char))[2:]} "
        
        #print(f"Current ={temp_part}")
        qname_by_part.append(temp_part)

    # Add "00" indicate end of qname
    qname_by_part.append("00 ")             # Notice empty space

    for str in qname_by_part:
        qname += str

    return qname





#Part 2 start here



def send_query_message(message, server, port):
    count = 0
    message = message.replace(" ", "").replace("\n", "")
    server_address = (server, port)


    while count < 3:
        try: 
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(5)
            sock.sendto(binascii.unhexlify(message), server_address)        # Send the message through socket

            #Receive response
            data, _ = sock.recvfrom(2048)
            sock.close()

            response = binascii.hexlify(data).decode("utf-8")
            return response
        
        except socket.timeout:
            count +=1

    # Print ERROR when attempt count = 3 reached
    print("Error! No Response from DNS server after 3 times attempts.")
            




#Part 3 start here
def display_response_message(answer_message):
    header = get_header_section(answer_message)
    question = get_question_section(answer_message)

    num_ans = 0

    # print header section
    for field, value in header:
        if(field == "header.ANCOUNT = "):
            num_ans = int(value,16)

        print(f"{field}{value}")

    print("\n")

    # print question section
    for field, value in question:
        print(f"{field}{value}")

    print("\n")


    # print answer section

    #calculate the start index for answer section
    count = 0
    str = ""
    for element in question:
        str += element[1].replace(" ", "").replace("\n", "")


    answer_start_index = 24+len(str)

    #print(f"ANCOUNT = {num_ans}")                                      #DB
    #print("Testing START index = ", answer_start_index)                #DB
    #print("Testing : ", answer_message[answer_start_index:])           #DB

    print_answer_section(num_ans,answer_start_index, answer_message)
    

    

def print_answer_section(num_answer, answer_start_index, message):
    
    start_index = answer_start_index
    dataLength = 0

    for i in range(0,num_answer):
        
        # For each message
        temp = ""
        

        name_bit_stop = start_index + 3
        type_bit_stop =  name_bit_stop + 4               #start_index + 7
        class_bit_stop = type_bit_stop + 4              #start_index + 11
        ttl_bit_stop = class_bit_stop + 8
        rdlength_bit_stop = ttl_bit_stop + 4
        rdata_bit_stop = rdlength_bit_stop


        for j in range(start_index, len(message)):
            temp += message[j]

            if(j == name_bit_stop):
                print("answer.NAME =  ", temp)
                temp = ""
                
            elif(j == type_bit_stop):
                print("answer.TYPE = ", temp)
                temp = ""

            elif(j == class_bit_stop):
                print("answer.CLASS = ", temp)
                temp = ""

            elif(j == ttl_bit_stop):
                print("answer.TTL = ", temp)
                temp = ""

            elif(j == rdlength_bit_stop):
                print("answer.RDLENGTH = ", temp)
                dataLength = int(temp, 16)
                temp = ""
            
            elif( j == rdata_bit_stop + (dataLength*2)):
                
                if(len(temp) < 10):
                    address = get_IP_address(temp)
                else:
                    address = temp

                print("answer.RDATA = ", address)
                print(" ")
                temp = ""
                #Reset start index for next RRs
                start_index = rdata_bit_stop + (dataLength*2) + 1
                break
        
# Convert string of hexadecimal into IP address
def get_IP_address(temp):
    address = ""
    hexStr = ""
     
    for c in temp:
        hexStr += c
        if(len(hexStr) == 2):
            num = int(hexStr, 16)
            address = address + str(num) + "."
            hexStr = ""

    return address[:len(address)-1]
        
    

# Return string array that each element represent a field in question section
def get_question_section(message):
    question_part = message[24:]    # end is unknown untill reached 00
    qtype_start_index = -1
    temp = ""  
    result = []


    #Obtain QNAME
    qname_field = ""
    for index, c in enumerate(question_part):
        
        temp += c

        if(len(temp) == 2):
            qname_field = qname_field + temp + " "
            if(temp == "00"):
                #print("End index of question = ", index)       #DB
                qtype_start_index = 24 + index + 1
                break

            temp = ""
    
    result.append(("question.QNAME = ", qname_field))

    #Obtain QTYPE
    qtype = message[qtype_start_index: qtype_start_index+4]
    result.append(("questionQTYPE = ", qtype))



    #Obtain QCLASS
    qclass = message[qtype_start_index+4: qtype_start_index + 8 ]
    result.append(("question.QCLASS = ", qclass))
    

    return result






# Return string array for each element represent a field in header section 
def get_header_section(message):
    header_part = message[0:24]
    result = []
    field = ""
    
    for index, c in enumerate(header_part):
        field += c

        if(index == 3):
            id = ("header.ID = ", field)
            result.append(id)
            field = ""

        elif(index == 7):
            #Convert hex to binary for flag field
            flags_binary =  bin(int(field, 16))[2:]
            temp = ""           

            # Loop through each part of flag field
            for bit_no, value in enumerate(flags_binary):
                temp += value

                if(bit_no == 0):
                    qr = ("header.QR = ", int(temp,2))
                    result.append(qr)
                    temp = ""

                elif(bit_no == 4):
                    opcode = ("header.OPCODE = ", int(temp,2))
                    result.append(opcode)
                    temp = ""

                elif(bit_no == 5):
                    aa = ("header.AA = ", int(temp,2))
                    result.append(aa)
                    temp = ""

                elif(bit_no == 6):
                    tc = ("header.TC = ", int(temp,2))     
                    result.append(tc)
                    temp = ""

                elif(bit_no == 7):
                    rd = ("header.RD = ", int(temp,2))
                    result.append(rd)
                    temp = "" 

                elif (bit_no == 8):
                    ra = ("header.RA = ", int(temp,2))   
                    result.append(ra)
                    temp = ""
                
                elif (bit_no == 11):
                    z = ("header.Z = ", int(temp,2))
                    result.append(z)
                    temp = ""
                elif (bit_no == 15):
                    rcode = ("header.RCODE = ", int(temp,2))
                    result.append(rcode)
                    temp = ""


            #flag = ("header.FLAGS = ", field)         #DB
            #result.append(flag)                       #DB

            field = ""

        elif(index == 11):
            qdcount = ("header.QDCOUNT = ", field)
            result.append(qdcount)
            field = ""

        elif(index == 15):
            ancount = ("header.ANCOUNT = ", field)
            result.append(ancount)
            field = ""
        
        elif(index == 19):
            nscount = ("header.NSCOUNT = ", field)
            result.append(nscount)
            field = ""
        
        elif(index == 23):
            arcount = ("header.ARCOUNT = ", field)
            result.append(arcount)
            field = ""

    return result    
    





'''MAIN''' 
#Part 1
header_section = create_header_section()
querry_message = createQueryMessage(header_section,sys.argv[1])
print("Preparing DNS query ...")
print(f"DNS query header = {header_section}" )
print(f"DNS query question section = {create_question_section(sys.argv[1])}")
print(f"Complete DNS query = {querry_message}")

#Part 2
response = send_query_message(querry_message, "8.8.8.8", 53)
print("----------------------------------------------------------------------------")

#Part 3

display_response_message(response)



