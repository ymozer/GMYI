from tabulate import tabulate
import os
import GPUtil
import psutil
import platform
from datetime import datetime
import subprocess
import pandas as pd
import numpy as np


def get_size(bytes, suffix="B"):
    """
    Scale bytes to its proper format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor


def os_info():
    uname = platform.uname()
    boot_time_timestamp = psutil.boot_time()
    bt = datetime.fromtimestamp(boot_time_timestamp)
    df = pd.DataFrame({
        'System': uname.system,
        'Node Name': uname.node,
        'Release': uname.release,
        'Version': uname.version,
        'Machine': uname.machine,
        'Processor': uname.processor,
        "Boot Time": datetime(bt.year, bt.month, bt.day, bt.hour, bt.minute, bt.second)
    }, index=[0])
    return df


def cpu_info():
    cpufreq = psutil.cpu_freq()
    max_freq=f"{cpufreq.max:.2f}Mhz"
    min_freq=f"{cpufreq.min:.2f}Mhz"
    current_freq=f"{cpufreq.current:.2f}Mhz"
    total_usage = f"{psutil.cpu_percent()}%"
    dizi=[]
    for i, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
        a = (f"Core {i}: {percentage}%")
        dizi.append(a)
    
    df = pd.DataFrame({
        "Physical cores": psutil.cpu_count(logical=False),
        "Total cores": psutil.cpu_count(logical=True),
        "Max Frequency": max_freq,
        "Min Frequency": min_freq,
        "Current Frequency": current_freq,
        "CPU Usage Per Core":{dizi},
        "Total CPU Usage": total_usage
    }, index=[0])
    print(df)

def mem_info():
    print("="*40, "Memory Information", "="*40)
    svmem = psutil.virtual_memory()
    print(f"Total: {get_size(svmem.total)}")
    print(f"Available: {get_size(svmem.available)}")
    print(f"Used: {get_size(svmem.used)}")
    print(f"Percentage: {svmem.percent}%")
    print("="*20, "SWAP", "="*20)
    # get the swap memory details (if exists)
    swap = psutil.swap_memory()
    print(f"Total: {get_size(swap.total)}")
    print(f"Free: {get_size(swap.free)}")
    print(f"Used: {get_size(swap.used)}")
    print(f"Percentage: {swap.percent}%")


def disk_info():
    # Disk Information
    print("="*40, "Disk Information", "="*40)
    print("Partitions and Usage:")
    # get all disk partitions
    partitions = psutil.disk_partitions()
    for partition in partitions:
        print(f"=== Device: {partition.device} ===")
        print(f"  Mountpoint: {partition.mountpoint}")
        print(f"  File system type: {partition.fstype}")
        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)
        except PermissionError:
            # this can be catched due to the disk that
            # isn't ready
            continue
        print(f"  Total Size: {get_size(partition_usage.total)}")
        print(f"  Used: {get_size(partition_usage.used)}")
        print(f"  Free: {get_size(partition_usage.free)}")
        print(f"  Percentage: {partition_usage.percent}%")
    # get IO statistics since boot
    disk_io = psutil.disk_io_counters()
    print(f"Total read: {get_size(disk_io.read_bytes)}")
    print(f"Total write: {get_size(disk_io.write_bytes)}")


def network_info():
    # Network information
    print("="*40, "Network Information", "="*40)
    # get all network interfaces (virtual and physical)
    if_addrs = psutil.net_if_addrs()
    for interface_name, interface_addresses in if_addrs.items():
        for address in interface_addresses:
            print(f"=== Interface: {interface_name} ===")
            if str(address.family) == 'AddressFamily.AF_INET':
                print(f"  IP Address: {address.address}")
                print(f"  Netmask: {address.netmask}")
                print(f"  Broadcast IP: {address.broadcast}")
            elif str(address.family) == 'AddressFamily.AF_PACKET':
                print(f"  MAC Address: {address.address}")
                print(f"  Netmask: {address.netmask}")
                print(f"  Broadcast MAC: {address.broadcast}")
    # get IO statistics since boot
    net_io = psutil.net_io_counters()
    print(f"Total Bytes Sent: {get_size(net_io.bytes_sent)}")
    print(f"Total Bytes Received: {get_size(net_io.bytes_recv)}")


def gpu_info():
    # GPU information
    print('\n', "="*40, "GPU Details", "="*40)
    gpus = GPUtil.getGPUs()
    list_gpus = []
    for gpu in gpus:
        # get the GPU id
        gpu_id = gpu.id
        # name of GPU
        gpu_name = gpu.name
        # get % percentage of GPU usage of that GPU
        gpu_load = f"{gpu.load*100}%"
        # get free memory in MB format
        gpu_free_memory = f"{gpu.memoryFree}MB"
        # get used memory
        gpu_used_memory = f"{gpu.memoryUsed}MB"
        # get total memory
        gpu_total_memory = f"{gpu.memoryTotal}MB"
        # get GPU temperature in Celsius
        gpu_temperature = f"{gpu.temperature} °C"
        gpu_uuid = gpu.uuid
        list_gpus.append((
            gpu_id, gpu_name, gpu_load, gpu_free_memory, gpu_used_memory,
            gpu_total_memory, gpu_temperature, gpu_uuid
        ))

    print(tabulate(list_gpus, headers=("id", "name", "load", "free memory", "used memory", "total memory",
                                       "temperature", "uuid")))
    print()


def installed_programs():
    # traverse the software list
    print('\n', "="*40, "Installed Programs", "="*40)
    Data = subprocess.check_output(['wmic', 'product', 'get', 'name'])
    a = str(Data)
    # try block
    try:
        # arrange the string
        for i in range(len(a)):
            print(a.split("\\r\\r\\n")[6:][i])
    except IndexError as e:
        print("All Done")


def update_status():
    # List of updates on system
    print('\n', "="*40, "List of Updates on System", "="*40)
    a = os.system('cmd /c wmic qfe list')
    print('\n', str(a)[1:-1])


def bios_info():
    print('\n', "="*40, "BIOS Info", "="*40)
    a = os.system('wmic bios get version')
    print('\n', str(a)[1:-1])





if __name__ == '__main__':
    os_info()
    cpu_info()
    #mem_info()
    #disk_info()
    #network_info()
    #gpu_info()
    #update_status()
    #bios_info()
    #installed_programs()
