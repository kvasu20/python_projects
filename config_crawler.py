import re
import os
import csv


big_info_list = []

pattern0 = "hostname"
pattern0_1 = "#hostname:"
pattern1_list = ["Chassis type:", "Catalyst Chassis type:", "Model:", "model:"]
pattern2_list = ["Processor ID:", "Serial Number:", "Serial number", "serial:", "Hardware: Processor Board ID", "!   S/N         : " ]
pattern3_list = ["Image: Software: ", "ASA Version", "Image:     Boot Image: ", "Software image version: ", "Software: system: version", "Software: NXOS: version", "sw-version:"]
csv_file_name = "crawler.csv"
fields = ['SW_Version', 'Model', 'Hostname', 'S/N']


for filename in os.listdir('/path/to/configs/directory/'):
    info_dic = {} 
    host_name = filename       
    info_dic.update({"Hostname": host_name})

    
      
    with open(os.path.join('/path/to/configs/directory/', filename)) as f:    
        full_string = f.read()  
        full_string_splitted = full_string.split("\n")  
             
    for item in full_string_splitted:
        for pattern1 in pattern1_list:
            if pattern1 in item:
                x1 = item.strip()
                y1 = x1.split(":")
                chassis = y1[-1].strip()
                info_dic.update({"Model": chassis})
        for pattern2 in pattern2_list:
            if pattern2 in item:
                x2 = item.strip()
                y2 = x2.split(":")
                serial_number = y2[-1].strip()
                info_dic.update({"S/N": serial_number})
        for pattern3 in pattern3_list:
            if pattern3 in item:
                x3 = item.strip()
                if ":" in x3: 
                    y3 = x3.split(":") 
                else:
                    y3 = x3.split()
                version = y3[-1].strip()
                info_dic.update({"SW_Version": version})
                
      
    info_dic_copy = info_dic.copy()        
    big_info_list.append(info_dic_copy)
   
    
print(big_info_list)    


with open(csv_file_name, 'w') as csvfile: 
    writer = csv.DictWriter(csvfile, fieldnames = fields)        
    writer.writeheader() 
    writer.writerows(big_info_list)         
             


