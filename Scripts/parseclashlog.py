import re
import os
from netaddr import IPNetwork, cidr_merge

def findExeInDir(directory, exeList):
    for file in os.listdir(directory):
        if os.path.isdir(directory + '/' + file):
            exeList = findExeInDir(directory + '/' + file, exeList)
        elif file.endswith('.exe'):
            exeList.append(file)

    return exeList

logfile = '2023-10-10-0828.log'
programdir = 'C:\Program Files (x86)\Tencent'
exeList = []
exeList = findExeInDir(programdir, exeList)
print(exeList)
file = open(logfile, 'r', encoding='utf-8')
reg = r'.+\((.+\.exe)\).+'
ipreg = r'.+--> (\d+\.\d+\.\d+\.\d+).*'
domainreg = r'.+--> (.+):.*'
lines = []
ipList = []
for line in file.readlines():
    if '.exe' in line and 'warning' not in line:
        process = re.findall(reg, line)[0]
        if process in exeList:
            ip = re.findall(ipreg, line)
            if len(ip) > 0:
                #lines.append(ip[0] + '\n')
                ipList.append(ip[0]+'/32')
            else:
                lines.append(re.findall(domainreg, line)[0] + '\n')
file.close()

networks = [IPNetwork(ip) for ip in ipList]
networks.sort()
cidrs = cidr_merge(networks)

for cidr in cidrs:
    lines.append(str(cidr) + '\n')

file = open('exe.txt', 'w', encoding='utf-8')
for line in lines:
    file.write(line)
file.close()

