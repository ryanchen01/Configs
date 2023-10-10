from netaddr import IPAddress, IPNetwork

def merge_ips_to_cidr(ip_list):
    # Convert IPs to integer representation and sort
    ips = sorted([int(IPAddress(ip)) for ip in ip_list])
    merged_ranges = []
    
    i = 0
    while i < len(ips):
        start_ip = ips[i]
        end_ip = start_ip
        i += 1
        while i < len(ips) and end_ip + 1 == ips[i]:
            end_ip = ips[i]
            i += 1
        merged_ranges.append((start_ip, end_ip))
    
    # Convert ranges to CIDRs
    cidrs = []
    for start_ip, end_ip in merged_ranges:
        while start_ip <= end_ip:
            largest_possible_cidr = 32
            while largest_possible_cidr > 0:
                network = IPNetwork(f"{IPAddress(start_ip)}/{largest_possible_cidr}")
                broadcast = int(network.broadcast) if network.broadcast else start_ip
                if network.ip == IPAddress(start_ip) and broadcast <= end_ip:
                    break
                largest_possible_cidr -= 1
            cidrs.append(network)
            start_ip = broadcast + 1
    return cidrs

# List of IPs
ip_list = ['192.168.1.1', '192.168.1.2', '192.168.1.3', '192.168.1.4', '10.0.0.1', '10.0.0.2', '172.16.0.5']
cidrs = merge_ips_to_cidr(ip_list)

for cidr in cidrs:
    print(cidr)
