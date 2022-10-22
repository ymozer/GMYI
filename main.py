'''
GMYI (Give Me Your Info)
AUTHOR(s): Yusuf Metin ÖZER, Bayram SALMAN, Cihat ÇOBAN

This software collects Windows computer's data like 
Hardware, 3rd Party Software... 

For more information: https://github.com/ymozer/GMYI

NOTE(s):
!!! This part contains to-do's that needs to be done urgently !!!
* Convert all data collecting functions to dataframe output functions. 
* Change installed_programs func for getting all programs and outputs by alphabetic order.
* USB devices information function
* Need to convert this software to some kind an executable file.   
    After running software, it needs to output collected data file to current directory (or tmp).
* We can have a function that detects antivirus softwares and Windows Defender status.
* Browser data collection (especially Chrome)

THOUGHTS:
* We don't need 1 row for all the data. we can create seperate file outputs (json/csv)
* Windows Defender disabling ???
* Posting output files to webserver/Database (flask, sqllite)???
* Deobfuscation...
* Limit imports for performance (import only used functions from libraries)
* Screenshot/Recording ability as well as access to microphone & camera. 
    (pyautogui, mss, wx, openCV, PyAudio, SpeechRecognition)
* Keylogger ability (pynput)
'''

from tabulate import tabulate
import os
import GPUtil
import psutil
from cpuinfo import get_cpu_info
import platform
from datetime import datetime
import subprocess
import pandas as pd

# to get rid of print clipping to console and files 
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 200)


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


# Operating system and general information about machine 
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
        'Boot Time': datetime(bt.year, bt.month, bt.day, bt.hour, bt.minute, bt.second)
    }, index=[0])  # , columns=['System','Node Name','Release','Version','Machine','Processor','Boot Time']
    return df


def cpu_info():
    '''
    Can't get current CPU freq (win 11) Tried wmic and Get-WmiObject but its equals 
    to max freq. For the good part, we really dont need that data because cpu freq is
    constantly changing.  *Removed Per Core usage info.
    '''
    cpu_model = get_cpu_info()['brand_raw']
    cpufreq = psutil.cpu_freq()
    max_freq = f"{cpufreq.max:.2f}Mhz"
    min_freq = f"{cpufreq.min:.2f}Mhz"
    total_usage = f"{psutil.cpu_percent(interval=2)}%"

    #dizi = []
    # for i, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
    #     a = (f"Core {i}: {percentage}%")
    #     dizi.append(a)

    df = pd.DataFrame({
        "CPU model": cpu_model,
        "Physical cores": psutil.cpu_count(logical=False),
        "Total cores": psutil.cpu_count(logical=True),
        "Max Frequency": max_freq,
        "Min Frequency": min_freq,
        "Total CPU Usage": total_usage
    }, index=[0])
    return df


# Memory information converts to DataFrame
def mem_info():

    svmem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    df = pd.DataFrame({
        "Total": get_size(svmem.total),
        "Available": get_size(svmem.available),
        "Used": get_size(svmem.used),
        "Percentage": svmem.percent,
        "Total Swap": get_size(swap.total),
        "Free Swap": get_size(swap.free),
        "Used Swap": get_size(swap.used),
        "Percentage Swap": swap.percent,
    }, index=[0])
    return df


'''
This function's structure can change to switch-case. It may be better??
'''
def disk_info():
    partitions = psutil.disk_partitions()
    disk_io = psutil.disk_io_counters()
    df = pd.DataFrame(columns=["Device", "Mountpoint", "File system type",
                      "Total Size", "Used", "Free", "Percentage", "Total read", "Total write"], index=[0])
    # disk count on system (external or internal)
    count = 0
    for p in partitions:
        for i in range(len(df.columns)):
            try:
                partition_usage = psutil.disk_usage(p.mountpoint)
            except PermissionError:
                continue
            if i == 0:
                df.at[count, 'Device'] = p.device
            if i == 1:
                df.at[count, 'Mountpoint'] = p.mountpoint
            if i == 2:
                df.at[count, 'File system type'] = p.fstype
            if i == 3:
                df.at[count, 'Total Size'] = get_size(partition_usage.total)
            if i == 4:
                df.at[count, 'Used'] = get_size(partition_usage.used)
            if i == 5:
                df.at[count, 'Free'] = get_size(partition_usage.free)
            if i == 6:
                strr = get_size(partition_usage.percent)
                df.at[count, 'Percentage'] = f'{strr[:-1]}%'
            if i == 7:
                df.at[count, 'Total read'] = get_size(disk_io.read_bytes)
            if i == 8:
                df.at[count, 'Total write'] = get_size(disk_io.write_bytes)
                count = count+1
    return df

'''
Network info function printing kinda mess... 
For converting data to Dataframe, we can take only network connected interface.
So we don't need other interfaces that are not in use...
'''
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
    print() # new line 


'''
Can be improved... Some programs doesn't show up with wmic command.
'''
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


'''
main function for combining functions seperate data
currently it writes outputs to txt file. Soon it will output json files 
'''
if __name__ == '__main__':
    with open("test.txt", "w", encoding='utf-8') as f:
        f.writelines(f"{str(os_info())}\n")
        f.writelines(f"{str(cpu_info())}\n")
        f.writelines(f"{str(mem_info())}\n")
        f.writelines(f"{str(disk_info())}\n")

    # print(network_info())
    # gpu_info()
    # update_status()
    # bios_info()
    print(installed_programs())
