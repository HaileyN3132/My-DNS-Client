import re
import sys

input = sys.argv[1]
listStr = re.split(r'[.]', input)

for i, str in enumerate(listStr):       # Loop through list of strings
    #Convert length of str from decimal to hex
    if(len(str) <= 15):
        print(f"length 0{hex(len(str))[2:]}")
    else:
        print(f"length {hex(len(str))[2:]}")

    #Represent each character as string of hex value
    for j , char in enumerate(str):
        #print(f"Index {j}, value = {char}")
        print(hex(ord(char))[2:])       #[2:0] help to eliminate the 0x in hex value
    
    print("")

    #print(f"Index {i}, value = {str}, length {len(str)}")

print("List string = ", listStr)

