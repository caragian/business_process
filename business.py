# Generation / Update Business Process
#
# /neteye/shared/icingaweb2/conf/modules/businessprocess/processes
#
# (C) 2020 Nicolae Caragia, Würth Phoenix GmbH


import os
import argparse
import sys
import logging
import stat
import re
import in_place
import linecache

logging.basicConfig(level=logging.DEBUG)

# Declare Arguments
parser = argparse.ArgumentParser(description='Bussiness Process Tutorial')
parser = argparse.ArgumentParser(description='Example: python3 business.py -b Windows -p Windows_ESX -a AND -t template_esx.txt -f hosts_esx.txt')
parser.add_argument('-b', '--business', dest='process', required=True, type=str, help='Choose Your Config Business Process File (Without *.conf)')
parser.add_argument('-p', '--parent',  dest='parent', required=True, type=str, help='Choose your Node Parent')
parser.add_argument('-a', '--aggregator' , dest='aggregator', required=True, type=str, help='Choose your aggregator Activity Service (AND, OR, MIN[1-9])')
parser.add_argument('-t', '--template', dest='template', required=True, type=str, help='Choose your Host Template')
parser.add_argument('-f', '--host' , dest='host', required=True, type=str, help='Choose your Hosts File')


args = parser.parse_args()

parent = args.parent
aggregator = args.aggregator
aggregator = aggregator.lower()

process = args.process + '.conf'
hosts_file = args.host
template_file = args.template

path_process =  '/neteye/shared/icingaweb2/conf/modules/businessprocess/processes'
# tutorial = args.tutorial

print('\n')
logging.debug("[i] Process Name: %s" %process)
logging.debug("[i] Parent Name: %s" %parent)
logging.debug("[i] Aggregator : %s" %aggregator)
logging.debug("[i] Host File: %s" %hosts_file)
logging.debug("[i] Template File: %s\n" %template_file)


host_list = []
host_to_replace = []
header = '### Business Process Config File ###\n#\n# Title           : '+process.strip('.conf')+'\n# Owner           : root\n# AddToMenu       : yes\n# Statetype       : hard\n#\n###################################\n\n'

# def helpOption():

#     print("\nERROR  No arguments ERROR\n")
#     print("business.py [-h] [-b --business process] [-p --parent node_parent] [-m --aggregator aggregator] [-t --template template_file] [-f --host host_file]" )
#     print("-b | --business     Choose Your Config Business Process Name")
#     print("-p | --parent       Choose your Node Master")
#     print("-m | --aggregator          Choose your aggregatorimal Activity Service (INTEGER, AND, OR)")
#     print("-t | --template     Choose your Host Template")
#     print("-f | --host         Choose your Hosts File\n")


# Change Permission to Conf File
def permission(process):
    # change owner
    filename = path_process
    st = os.stat(filename)
    usr_own = st.st_uid
    grp_own = st.st_gid
    # file mode
    f_mode = stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP      

    os.chown(process, usr_own, grp_own)
    os.chmod(process, f_mode)

# Generate template for Hosts List
def generate_temp(hostname,template):
    host_t1 = linecache.getline(template,1)
    host_t2 = linecache.getline(template,2)

    host_1 = host_t1.replace('%HOSTNAME%', hostname)
    host_2 = host_t2.replace('%HOSTNAME%', hostname)

    return(host_1, host_2)

# Parse Hosts in TXT File to List (host_list)
def parse_host(hosts_file, host_list):
    with open (hosts_file, 'r') as myfile:
        for line in myfile:
            if line != '\n':
                host = line.strip('\n')
                host_list.append(host)
    myfile.close
    return(host_list)

# Generate Parent with Host List and choose Aggregator
def create_parent(parent, aggregator, host_list):
    if aggregator == 'and':
        parent_1 = parent + ' = ' + ' & '.join(host_list)
    # if aggregator == 'not':
    #    xxxxx
    if aggregator == 'or':
        parent_1 = parent + ' = ' + ' | '.join(host_list)
    parent_2 = 'display 1;'+parent+';'+parent

    match = re.match(r'min(\d+)', aggregator)

    if match:
        parent_1 = parent + ' = ' + match.group(1) + ' of: ' + ' + '.join(host_list)
    return(parent_1, parent_2)

# Check if File Conf exists
def check_exists(file):
    # Creation File and Write Header
    if not os.path.exists(file):
        with open(file, 'w') as title:
            os.utime(file, None)
            # Write header
            title.write(header)
            title.close
            status = 'write'
            permission(process)
    #Open File in Append Mode
    elif os.path.exists(file):
            status = 'append'
    return(status)

# Write Parent and Host List if not exists
def write_file(process,host_list, parent_1, parent_2):
    process = open(process, 'a')
    process.write(parent_1)
    process.write('\n')
    process.write(parent_2)
    process.write('\n\n')
    
    
    for host in host_list:
        host_1, host_2 = generate_temp(host,template_file)
        process.write(host_1)
        process.write(host_2)
        process.write('\n')

    process.close()

# Adding new Hosts in Append Mode
def write_host(process,host_1, host_2):
        print("Host1 is {n} || Host2 is {s}".format(n=host_1, s=host_2))
        process = open(process, 'a')

        process.write(host_1)
        process.write(host_2)
        process.write('\n')

        process.close()

# Update Parent Line or Write New Parent with Hosts
def add_parent(process, parent, host_list, parent_1, parent_2):
    with open(process) as f:
            file_read = f.read()
            parent = parent + ' ='
            f.close()
            if parent in file_read:    
                print(file_read)
                # update_parent(process, parent, parent_1)
                with in_place.InPlace(process) as fp:
                    for line in fp:
                        # If parent it's in this Line: Replace Line with New Line (containt also new Hosts)
                        if parent in line:
                            line = line.replace(line, parent_1)
                            fp.write(line)
                            fp.write('\n')
                        # If parent it's now in this Line: copy Line to New File
                        elif parent not in line:
                            fp.write(line)
            # If parent not exists in File: Create New Parent
            elif parent is not file_read:
                process = open(process, 'a')
                process.write(parent_1)
                process.write('\n')
                process.write(parent_2)
                process.write('\n\n')
                process.close()

# Update Hosts with new Template or Write New Hosts
def add_host(process, host_list, template_file):      
    print(host_list)
    with open(process) as f:
        file_read = f.read()
        for host in host_list:
            host_1, host_2 = generate_temp(host,template_file)
            # Check if Host is in the File
            if host in file_read:     
                print(host + ' is in File')
                # Replace Line with New Template
                with in_place.InPlace(process) as fp:
                    for line in fp:
                        match = re.match(r"{}\s+\=".format(host), line)
                        # If it' s in this Line : Replace with new Line
                        if bool(match) is True:
                            line = line.replace(line, host_1)
                            fp.write(line)
                        # It it's not in this Line : copy Line to new File
                        elif bool(match) is False:
                            fp.write(line)
            # Add New Host
            elif host is not file_read:
                write_host(process,host_1, host_2)
          
          

#MAIN

# Reading Input
host_list = parse_host(hosts_file, host_list)
parent_1, parent_2 = create_parent(parent, aggregator, host_list)

os.chdir(path_process)

# Host List
print('Hosts = ' + str(host_list)[1:-1])

status = check_exists(process)
if status == 'write':
    #Write Parent and Child
    write_file(process,host_list,parent_1,parent_2)
elif status == 'append':
    ##Add parent with hosts
    add_host(process, host_list, template_file)
    add_parent(process, parent, host_list, parent_1, parent_2)
 

print('\n\n\nSuccessfully')
