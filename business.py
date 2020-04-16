# Generation new Business Process
#
# /neteye/shared/icingaweb2/conf/modules/businessprocess/processes
#
# (C) 2020 Nicolae Caragia, Würth Phoenix GmbH


import os
import argparse
import sys
import logging
import linecache
import stat

parser = argparse.ArgumentParser(description='Bussiness Process Tutorial || For more info and examples type "python3 business.py"')
parser.add_argument('-b', '--business', dest='process', required=True, type=str, help='Choose Your Config Business Process Name')
parser.add_argument('-p', '--parent',  dest='parent', required=True, type=str, help='Choose your Node Master')
parser.add_argument('-m', '--min' , dest='min', required=True, type=str, help='Choose your Minimal Activity Service')
parser.add_argument('-t', '--template', dest='template', required=True, type=str, help='Choose your Host Template')
parser.add_argument('-f', '--host' , dest='host', required=True, type=str, help='Choose your Hosts File')
# parser.add_argument('--tutorial' , dest='tutorial', required=False, help='For more info and examples type "python3 business.py"', action='store_true')

args = parser.parse_args()

parent = args.parent
min = args.min
min = min.lower()
process = args.process + '.conf'
hosts_file = args.host
template_file = args.template

print('\n\nBusiness process= '+ process)
print('Parent Node= '+ parent)
print('Min= '+ min)
print('Template File= '+ template_file)
print('Hosts File= '+ hosts_file)
print('\n\n')

path_process =  '/neteye/shared/icingaweb2/conf/modules/businessprocess/processes'
# tutorial = args.tutorial

logging.debug("[i] Process Name: %s" %process)
logging.debug("[i] Parent Name: %s" %parent)
logging.debug("[i] Min Argument: %s" %min)
logging.debug("[i] Host File: %s" %hosts_file)
logging.debug("[i] Template File: %s" %template_file)


host_list = []
host_to_replace = []
header = '### Business Process Config File ###\n#\n# Title           : '+process.strip('.conf')+'\n# Owner           : root\n# AddToMenu       : yes\n# Statetype       : hard\n#\n###################################\n\n'

# def helpOption():

#     print("\nERROR  No arguments ERROR\n")
#     print("business.py [-h] [-b --business process] [-p --parent node_parent] [-m --min min] [-t --template template_file] [-f --host host_file]" )
#     print("-b | --business     Choose Your Config Business Process Name")
#     print("-p | --parent       Choose your Node Master")
#     print("-m | --min          Choose your Minimal Activity Service (INTEGER, AND, OR)")
#     print("-t | --template     Choose your Host Template")
#     print("-f | --host         Choose your Hosts File\n")

def permission(process):
    #change owner
    filename = path_process
    st = os.stat(filename)
    usr_own = st.st_uid
    grp_own = st.st_gid

    #usr_own = 48    #apache
    #grp_own = 999   #icingaweb2

    #change mode
    f_mode = stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP      #file mode

    os.chown(process, usr_own, grp_own)
    os.chmod(process, f_mode)


def generate_temp(hostname,template):
    host_t1 = linecache.getline(template,1)
    host_t2 = linecache.getline(template,2)

    host_1 = host_t1.replace('%HOSTNAME%', hostname)
    host_2 = host_t2.replace('%HOSTNAME%', hostname)

    return(host_1, host_2)

def parse_host(hosts_file, host_list):
    with open (hosts_file, 'r') as myfile:
        for line in myfile:
            host = line.strip('\n')
            host_list.append(host) 
    myfile.close
    return(host_list)

def create_parent(parent, min, host_list):
    if min is 'AND':
        parent_1 = parent + ' = ' + ' & '.join(host_list)
    if min is 'OR':
        parent_1 = parent + ' = ' + ' | '.join(host_list)
    parent_2 = 'display 1;'+parent+';'+parent
    if min is not 'and' and 'or' :
        parent_1 = parent + ' = ' + min + ' of: ' + ' + '.join(host_list)
    return(parent_1, parent_2)

def check_exists(file):
    if not os.path.exists(file):
        with open(file, 'w') as title:
            os.utime(file, None)
            # Write header
            title.write(header)
            title.close
            status = 'write'
            permission(process)
    elif os.path.exists(file):
            status = 'append'
    return(status)


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


# def update_parent(process, parent, parent_1):
#     with open(process, 'r') as f:
#         data = f.readlines()
#         for line in data:
#             parent = parent + ' ='
#             if parent in line:
#                 line = 'ciao'
#                 with open(process, 'a') as a:
#                     a.write(line.replace(line, parent_1))
#                     break


def add_parent(process, parent, host_list, parent_1, parent_2):
    with open(process) as f:
            file_read = f.read()
            parent = parent + ' ='
            if parent in file_read:    
                # update_parent(process, parent, parent_1)
                print(parent + ' exists')
            elif parent is not file_read:
                write_file(process,host_list,parent_1,parent_2)





        
#MAIN

# The list of command line arguments passed to a Python script. argv[0] is the script name. So:
# if tutorial is not None:
#     helpOption()
#     sys.exit(1)

host_list = parse_host(hosts_file, host_list)
parent_1, parent_2 = create_parent(parent, min, host_list)
os.chdir(path_process)

 
print('Hosts = ' + str(host_list)[1:-1])
print('Parent is = ' + parent)




status = check_exists(process)
if status == 'write':
    #Write Parent and Child
    write_file(process,host_list,parent_1,parent_2)
elif status == 'append':
    ##Add parent with hosts
    add_parent(process, parent, host_list, parent_1, parent_2)

print('\n\n\nSuccessfully')
