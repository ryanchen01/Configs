import re
import os
from netaddr import IPAddress, IPNetwork, iprange_to_cidrs
import sys
import platform

def merge_ips_to_cidr(ip_list, min_cidr=-1):
    ips = sorted([int(IPAddress(ip)) for ip in ip_list])
    cidrs = []
    if min_cidr > 0:
        min_cidr = 2**(32 - min_cidr) - 1
    i = 0
    while i < len(ips):
        ip_start = ips[i]
        ip_end = ip_start
        if min_cidr != -1:
            while i < len(ips) - 1 and ips[i + 1] - ip_start < min_cidr:
                ip_end = ips[i + 1]
                i += 1
            while ip_start <= ip_end:
                network = IPNetwork(str(IPAddress(ip_start)))
                while network.prefixlen > 0:
                    network.prefixlen -= 1
                    broadcast = int(network.broadcast) if network.broadcast else ip_start
                    if broadcast > ip_end:
                        network.prefixlen += 1
                        break
                cidrs.append(network)
                ip_start = broadcast + 1
        
        else:
            while i < len(ips) - 1 and ips[i + 1] - ips[i] < 65535:
                ip_end = ips[i + 1]
                i += 1
            ncidr = iprange_to_cidrs(str(IPAddress(ip_start)), str(IPAddress(ip_end)))
            for c in ncidr:
                cidrs.append(c)
        i += 1
    return cidrs

def findExeInDir(directory, exeList):
    if platform.system() == "Darwin":
        if directory.endswith(".app"):
            exeList.append(os.path.split(directory)[-1])
            return exeList
    for file in os.listdir(directory):
        if os.path.isdir(directory + '/' + file):
            exeList = findExeInDir(directory + '/' + file, exeList)
        else:
            exeList.append(file)

    return exeList

if __name__ == '__main__':
    logfile = sys.argv[1]
    programdir = sys.argv[2]
    if len(sys.argv) > 3:
        min_cidr = int(sys.argv[3])
    else:
        min_cidr = -1
    
    exeList = []
    exeList = findExeInDir(programdir, exeList)
    file = open(logfile, 'r', encoding='utf-8')
    reg = r'.+:\d+\((.+)\) -->.+'
    ipreg = r'.+--> (\d+\.\d+\.\d+\.\d+).*'
    domainreg = r'.+--> (.+):.*'
    lines = []
    ipList = []
    for line in file.readlines():
        if 'warning' not in line and len(re.findall(reg, line)) > 0:
            process = re.findall(reg, line)[0]
            if process in exeList or str(process + '.app') in exeList:
                ip = re.findall(ipreg, line)
                if len(ip) > 0:
                    ipList.append(ip[0])
                else:
                    lines.append('DOMAIN,' + re.findall(domainreg, line)[0] + '\n')
    file.close()

    lines = list(set(lines))

    cidrs = merge_ips_to_cidr(list(set(ipList)), min_cidr)

    cidrs = list(set(cidrs))
    for cidr in cidrs:
        lines.append('IP-CIDR,' + str(cidr) + ',no-resolve\n')
    outname = os.path.split(programdir)[-1] + '.list'
    file = open(outname, 'w', encoding='utf-8')
    for line in lines:
        file.write(line)
    file.close()

