'''
GMYI (Give Me Your Info)
AUTHOR(s): Yusuf Metin ÖZER, Bayram SALMAN, Cihat ÇOBAN

This software collects Windows computer's data like 
Hardware, 3rd Party Software... 

For more information: https://github.com/ymozer/GMYI

NOTE(s):
!!! This part contains to-do's that needs to be done urgently !!!
* Convert all data collecting functions to dataframe output functions. 
* Change installed_programs func for getting all programs and outputs by alphabetic order. --> DONE
* USB devices information function --> DONE
* Need to convert this software to some kind an executable file.   --> DONE
    After running software, it needs to output collected data file to current directory (or tmp).
* We can have a function that detects antivirus softwares and Windows Defender status.
* Browser data collection (especially Chrome)

THOUGHTS:
* We don't need 1 row for all the data. we can create seperate file outputs (json/csv)
* Windows Defender disabling ???
* Posting output files to webserver/Database (flask, sqllite) or mail???
* Deobfuscation...
* Limit imports for performance (import only used functions from libraries)
* Screenshot/Recording ability as well as access to microphone & camera. 
    (pyautogui, mss, wx, openCV, PyAudio, SpeechRecognition)
* Keylogger ability (pynput)
* check with intrrupt which proccess started 
'''

import pandas as pd
import numpy as np
import os
import GPUtil
import psutil
from cpuinfo import get_cpu_info
import platform
from datetime import datetime
import subprocess
import sys
import getopt
import sched


# to get rid of print clipping to console and files
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 200)

PS_PATH = "%SystemRoot%\system32\WindowsPowerShell\\v1.0\powershell.exe"

count_loop = 0


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

    # dizi = []
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
    '''
    Powershell: Get-WmiObject -Class Win32_PhysicalMemory
    '''
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





def disk_info():
    '''
    This function's structure can change to switch-case. It may be better??
    '''
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


def network_info():
    output = (f"{'='*40}Network Information{'='*40}\n")
    # get all network interfaces (virtual and physical)
    if_addrs = psutil.net_if_addrs()
    # get network stats
    net_stat = psutil.net_if_stats()
    for interface_name, interface_addresses in if_addrs.items():
        isup = net_stat[f'{interface_name}'].isup  # is up & running?
        output = output + interface_name + "\n"
        output = output + f"isup: {isup}\n"
        for address in interface_addresses:
            # flags=net_stat[f'{interface_name}'].flags
            if int(address.family) == 2:  # IPv4
                output = output + f"IPv4 Address: {address.address}\n"
            if int(address.family) == 23:  # IPv6
                output = output + f"IPv6 Address: {address.address}\n"
            if int(address.family) == -1:  # link
                output = output + f"link: {address.address}\n"
        output = output + ("="*20) + "\n"
    # get IO statistics since boot
    net_io = psutil.net_io_counters()
    output = output + f"Total Bytes Sent: {get_size(net_io.bytes_sent)}\n"
    output = output + f"Total Bytes Received: {get_size(net_io.bytes_recv)}\n"
    return output


def gpu_info():
    # GPU information
    df = pd.DataFrame(columns=("id", "name", "load", "memoryFree", "memoryUsed", "memoryTotal",
                               "temperature", "uuid"), index=[0])
    gpus = GPUtil.getGPUs()
    list_gpus = []
    count = 0
    for gpu in gpus:
        # get the GPU id
        df.at[count, 'id'] = gpu.id
        gpu_id = gpu.id
        # name of GPU
        gpu_name = gpu.name
        df.at[count, 'name'] = gpu.name
        # get % percentage of GPU usage of that GPU
        gpu_load = f"{gpu.load*100}%"
        df.at[count, 'load'] = f"{gpu.load*100}%"
        # get free memory in MB format
        gpu_free_memory = f"{gpu.memoryFree}MB"
        df.at[count, 'memoryFree'] = f"{gpu.memoryFree}MB"
        # get used memory
        gpu_used_memory = f"{gpu.memoryUsed}MB"
        df.at[count, 'memoryUsed'] = gpu.memoryUsed
        # get total memory
        gpu_total_memory = f"{gpu.memoryTotal}MB"
        df.at[count, 'memoryTotal'] = gpu.memoryTotal
        # get GPU temperature in Celsius
        gpu_temperature = f"{gpu.temperature} °C"
        df.at[count, 'temperature'] = gpu.temperature
        gpu_uuid = gpu.uuid
        df.at[count, 'uuid'] = gpu.uuid
        list_gpus.append((
            gpu_id, gpu_name, gpu_load, gpu_free_memory, gpu_used_memory,
            gpu_total_memory, gpu_temperature, gpu_uuid
        ))
        count = count+1

    return df


def run(cmd):
    completed = subprocess.run(["powershell", "-Command", cmd], capture_output=True)
    return completed


def get_language():
    cmd = "(Get-UICulture).Name"
    output = run(cmd)
    lines = output.stdout.decode('utf-8')
    lan_name = lines.split()[0][0:2]
    return lan_name


def cpu_usage():
    cmd = ''' # Source: https://xkln.net/blog/analyzing-cpu-usage-with-powershell-wmi-and-excel/
        (Get-Date).ToString("yyyy-MM-dd HH:mm:ss.ms"), ((Get-CimInstance -Query "select Name, PercentProcessorTime from Win32_PerfFormattedData_PerfOS_Processor" | Sort-Object -Property Name).PercentProcessorTime -join ",") -join ","
    '''
    # the first value is the timestamp, followed by the total usage, followed by each core.
    output = run(cmd)
    lines = output.stdout.decode('utf-8')
    return lines


def all_usb_devices(*args):  # Status, Class, FriendlyName, InstanceId
    # Python codecs for Turkish: iso8859_9 = latin5 = L5/ macturkish /ibm1026/IBM857=857
    cmd = f"Get-PnpDevice -PresentOnly | Where-Object {{ $_.InstanceId -match '^USB' }} | Select-Object {args} | Format-Table -AutoSize"
    output = run(cmd)

    if get_language() == "tr":  # check if system is Turkish then decode accordingly
        lines = output.stdout.decode('857')
        return lines
    if get_language() == "en":
        lines = output.stdout.decode('utf-8')
        return lines
    else:
        print("System is neither Turkish nor English.\nDecoding as UTF-8")
        lines = output.stdout.decode('utf-8')
        return lines


def disk_usb_devices():
    cmd = "Get-CimInstance -ClassName Win32_DiskDrive | where{$_.InterfaceType -eq 'USB'} | Format-List -property 'DeviceID', 'Caption', 'Partitions', 'Size', 'Model'"
    # cmd = "Get-CimInstance -ClassName Win32_DiskDrive | where{$_.InterfaceType -eq 'USB'} |  Format-Table -HideTableHeaders -Property DeviceID ,aaaa, Caption, asdasdasd, Partitions, asdasdasdasd,Size ,asdasdasd,Model "
    output = run(cmd)
    lines = output.stdout.decode('857').replace("\r", "").splitlines()
    stripped = []
    count = 0
    for l in lines:
        stripped.append(l.strip().split(':'))
        stripped[count][len(stripped[count])-1] = stripped[count][len(stripped[count])-1].strip()
        stripped[count][len(stripped[count])-2] = stripped[count][len(stripped[count])-2].strip()
        count = count+1
    if not stripped: # if list empty
        print("There is no flash drives on the system!")
        return 1
    else:
        del stripped[0], stripped[0], stripped[len(stripped)-1], stripped[len(stripped)-1], stripped[len(stripped)-1]
        stripped = list(filter(None, stripped))
        df = pd.DataFrame(columns=['Property', 'Value'])
        for value in stripped:
            if value[0] == '':
                continue
            for i in range(len(df.columns)):
                match i:
                    case 0:
                        df.at[count, 'Property'] = value[i]
                    case 1:
                        df.at[count, 'Value'] = value[i]
            count = count+1
        return df


def installed_programs():
    cmd = ''' # Source: https://bobcares.com/blog/powershell-list-installed-software/
        $list=@()
        $InstalledSoftwareKey="SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall"
        $InstalledSoftware=[microsoft.win32.registrykey]::OpenRemoteBaseKey('LocalMachine',$pcname)
        $RegistryKey=$InstalledSoftware.OpenSubKey($InstalledSoftwareKey)
        $SubKeys=$RegistryKey.GetSubKeyNames()
        Foreach ($key in $SubKeys){
        $thisKey=$InstalledSoftwareKey+"\\"+$key
        $thisSubKey=$InstalledSoftware.OpenSubKey($thisKey)
        $obj = New-Object PSObject
        $obj | Add-Member -MemberType NoteProperty -Name "DisplayName" -Value $($thisSubKey.GetValue("DisplayName"))
        $obj | Add-Member -MemberType NoteProperty -Name "DisplayVersion" -Value $($thisSubKey.GetValue("DisplayVersion"))
        $list += $obj
        }
        $list | where { $_.DisplayName } | select  DisplayName, DisplayVersion | FT
    '''
    output = run(cmd)
    lines = output.stdout.decode('857').replace("\r", "").splitlines()
    strip_list = []
    count = 0
    for l in lines:
        strip_list.append(l.strip().split("    ", 1))
        strip_list[count][len(strip_list[count])-1] = strip_list[count][len(strip_list[count])-1].lstrip()
        if len(strip_list[count]) == 1:
            strip_list[count].insert(count, "null")
        count = count+1
    del strip_list[0], strip_list[0], strip_list[0], strip_list[len(strip_list)-1], strip_list[len(strip_list)-1]

    df = pd.DataFrame(columns=['DisplayName', 'DisplayVersion'], index=[0])
    for value in strip_list:
        for i in range(len(df.columns)):
            match i:
                case 0:
                    df.at[count, 'DisplayName'] = value[i]
                case 1:
                    df.at[count, 'DisplayVersion'] = value[i]
        count = count+1
    return df


def update_status():
    # List of updates on system
    print('\n', "="*40, "List of Updates on System", "="*40)
    a = os.system('cmd /c wmic qfe list')
    return ('\n', str(a)[1:-1])


def bios_info():
    cmd = "Get-WmiObject -Class Win32_Bios | Format-List -Property *"
    output = run(cmd)
    lines = output.stdout.decode("utf-8").replace("\r", "").splitlines()
    striped = []
    for line in lines:
        temp = line.split(':', 1)
        if temp[0] == '':
            continue
        count = 0
        for element in temp:
            element = element.strip()
            if element == '':
                element = 'null'
            temp[count] = element
            count = count+1
        if len(temp) < 2:
            continue
        striped.append(temp)
    df = pd.DataFrame(columns=['Header', 'Value'], index=[0])
    for value in striped:
        for i in range(len(df.columns)):
            match i:
                case 0:
                    # the number of handles that the process has opened
                    df.at[count, 'Header'] = value[i]
                case 1:
                    # The amount of non-paged memory that the process is using, in kilobytes
                    df.at[count, 'Value'] = value[i]
        count = count+1
    return df


def get_process():
    cmd = "Get-Process | Where-Object {$_.WorkingSet -gt 20000000}"  # Get processes that have working set greater than 20 MB
    df = pd.DataFrame(columns=['Handles', 'NPM(K)', 'PM(K)', 'WS(K)', 'CPU(s)', 'Id', 'SI', 'ProcessName'], index=[0])
    output = run(cmd)
    lines = output.stdout.decode("utf-8").replace("\r", "").splitlines()
    striped = []
    for l in lines:
        striped.append(l.rstrip().replace("             ", "  null ").split())
    count = 0
    del striped[0], striped[0], striped[0], striped[len(striped)-1], striped[len(striped)-1]  # why not pop
    for value in striped:
        for i in range(len(df.columns)):
            match i:
                case 0:
                    # the number of handles that the process has opened
                    df.at[count, 'Handles'] = value[i]
                case 1:
                    # The amount of non-paged memory that the process is using, in kilobytes
                    df.at[count, 'NPM(K)'] = value[i]
                case 2:
                    # The amount of pageable memory that the process is using, in kilobytes.
                    df.at[count, 'PM(K)'] = value[i]
                case 3:
                    # The size of the working set of the process, in kilobytes. The working set consists of the pages of memory that were recently referenced by the process.
                    df.at[count, 'WS(K)'] = value[i]
                case 4:
                    # The amount of processor time that the process has used on all processors, i
                    df.at[count, 'CPU(s)'] = value[i]
                case 5:
                    # The process ID (PID) of the process.
                    df.at[count, 'Id'] = value[i]
                case 6:
                    # Session ID ??
                    df.at[count, 'SI'] = value[i]
                case 7:
                    # The name of the process.
                    df.at[count, 'ProcessName'] = value[i]
        count = count+1
    return df


def all_data_collection_write(filename, format):
    '''
    Write all data collection function outputs to file.
    NOTE: Currently not fully working!!
    '''
    results_path = "Results"
    processes_path = "Processes"
    global count_loop
    count_loop

    # Check if directories exist in current dir.
    isExist = os.path.exists(results_path)
    if not isExist:
        os.makedirs(results_path)
        print(f"{results_path} dir created.")
    isExist = os.path.exists(processes_path)
    if not isExist:
        os.makedirs(processes_path)
        print(f"{processes_path} dir created.")

    match format:
        case "json":
            '''
            Writes all data collection functions return (DataFrame) to Json file.
            Not all functions supported yet.
            '''
            if count_loop < 1:
                get_process().to_json(f'./{processes_path}/processes{count_loop}.{format}', orient="table")
                # cpu_usage().to_json(f'./{results_path}/cpu_usage{count_loop}.{format}', orient="table")
                os_info().to_json(f'./{results_path}/os_info{count_loop}.{format}', orient="table")
                cpu_info().to_json(f'./{results_path}/cpu_info{count_loop}.{format}', orient="table")
                mem_info().to_json(f'./{results_path}/mem_info{count_loop}.{format}', orient="table")
                disk_info().to_json(f'./{results_path}/disk_info{count_loop}.{format}', orient="table")
                gpu_info().to_json(f'./{results_path}/gpu_info{count_loop}.{format}', orient="table")
                if disk_usb_devices() == 1:
                    pass
                else:
                    disk_usb_devices().to_json(f'./{results_path}/flash_drives{count_loop}.{format}', orient="table")  # bad format
                installed_programs().to_json(f'./{results_path}/installed_programs{count_loop}.{format}', orient="table")
                # all_usb_devices().to_json(f'./{results_path}/all_usb_devices{count_loop}.{format}', orient="table")
                bios_info().to_json(f'./{results_path}/bios_info{count_loop}.{format}', orient="table")
                # update_status().to_json(f'./{results_path}/update_status{count_loop}.{format}', orient="table")
                # get_language().to_json(f'./{results_path}/get_language{count_loop}.{format}', orient="table")
            else:
                get_process().to_json(f'./{processes_path}/processes{count_loop}.{format}', orient="table")
                # cpu_usage().to_json(f'./{results_path}/cpu_usage{count_loop}.{format}', orient="table")

        case "csv":
            '''
            Currently only creates csv file for momentary CPU usage AND Processes
            NOTE: Add rest of the functions.
            '''
            with open(f"./{results_path}/cpu_usage.{format}", "a+", encoding='utf-8') as f:
                f.write(cpu_usage()[:-1])
            get_process().to_csv(f'./{processes_path}/processes{count_loop}.{format}')

        case "txt":
            '''
            Save all data collection functions to Text files.
            Some functions not supported yet.
            '''
            if count_loop < 1:
                with open(f"./{results_path}/os_info.{format}", "a+", encoding='utf-8') as f:
                    f.write("\n")
                    np.savetxt(f, os_info().values, header=str(os_info().columns.values), fmt='%s')
                    print(f"file os_info.{format} saved in 'Results' directory.")
                with open(f"./{results_path}/cpu_info.{format}", "a+", encoding='utf-8') as f:
                    f.write("\n")
                    np.savetxt(f, cpu_info().values, header=str(cpu_info().columns.values), fmt='%s')
                    print(f"file cpu_info.{format} saved in 'Results' directory.")
                with open(f"./{results_path}/mem_info.{format}", "a+", encoding='utf-8') as f:
                    f.write("\n")
                    np.savetxt(f, mem_info().values, header=str(mem_info().columns.values), fmt='%s')
                    print(f"file mem_info.{format} saved in 'Results' directory.")
                with open(f"./{results_path}/disk_info.{format}", "a+", encoding='utf-8') as f:
                    f.write("\n")
                    np.savetxt(f, disk_info().values, header=str(disk_info().columns.values), fmt='%s')
                    print(f"file disk_info.{format} saved in 'Results' directory.")
                # with open(f"./{results_path}/network_info.{format}", "a+", encoding='utf-8') as f:
                #    f.write("\n")
                #    np.savetxt(f, network_info().values, header=str(network_info().columns.values), fmt='%s')
                with open(f"./{results_path}/gpu_info.{format}", "a+", encoding='utf-8') as f:
                    f.write("\n")
                    np.savetxt(f, gpu_info().values, header=str(gpu_info().columns.values), fmt='%s')
                    print(f"file gpu_info.{format} saved in 'Results' directory.")
                with open(f"./{results_path}/all_usb_devices.{format}", "a+", encoding='utf-8') as f:
                   f.write("\n")
                   np.savetxt(f, [str(all_usb_devices("Status", "Class", "FriendlyName", "InstanceId"))], fmt='%s')
                   print(f"file all_usb_devices.{format} saved in 'Results' directory.")
                with open(f"./{results_path}/disk_usb_devices.{format}", "a+", encoding='utf-8') as f:
                    f.write("\n")
                    np.savetxt(f, disk_usb_devices().values, header=str(disk_usb_devices().columns.values), fmt='%s')
                    print(f"file disk_usb_devices.{format} saved in 'Results' directory.")
                # with open(f"./{results_path}/update_status.{format}", "a+", encoding='utf-8') as f:
                #    f.write("\n")
                #    np.savetxt(f, update_status().values, header=str(update_status().columns.values), fmt='%s')
                with open(f"./{results_path}/bios_info.{format}", "a+", encoding='utf-8') as f:
                   f.write("\n")
                   np.savetxt(f, bios_info().values, header=str(bios_info().columns.values), fmt='%s')
                with open(f"./{results_path}/installed_programs.{format}", "a+", encoding='utf-8') as f:
                    f.write("\n")
                    np.savetxt(f, installed_programs().values, header=str(installed_programs().columns.values), fmt='%s')
                    print(f"file installed_programs.{format} saved in 'Results' directory.")
                # with open(f"./{results_path}/get_language.{format}", "a+", encoding='utf-8') as f:
                #    f.write("\n")
                #    np.savetxt(f, get_language().values, header=str(get_language().columns.values), fmt='%s')
            else:
                with open(f"./{results_path}/{filename}_cpu_usage.{format}", "a+", encoding='utf-8') as f:
                    f.write(cpu_usage()[:-1])
                get_process().to_csv(f'./{processes_path}/processes{count_loop}.{format}')
        case _:
            sys.exit(f"Wrong file format supplied: {format}\nIt should be json, csv or txt")


def manual_page():
    '''                                                    
     $$$$$$\  $$\      $$\ $$\     $$\ $$$$$$\ 
    $$  __$$\ $$$\    $$$ |\$$\   $$  |\_$$  _|
    $$ /  \__|$$$$\  $$$$ | \$$\ $$  /   $$ |  
    $$ |$$$$\ $$\$$\$$ $$ |  \$$$$  /    $$ |  
    $$ |\_$$ |$$ \$$$  $$ |   \$$  /     $$ |  
    $$ |  $$ |$$ |\$  /$$ |    $$ |      $$ |  
    \$$$$$$  |$$ | \_/ $$ |    $$ |    $$$$$$\ 
     \______/ \__|     \__|    \__|    \______|

    GMYI - Give Me Your Info v0.1

    ==================================== USAGE ===================================================================
    -h or --help                           : Prints this page to terminal.
    -l or --loop <file_format> <delay_sec> : Writes to files in continous loop.
        -l flag in first loop executes all functions, after loop one completes,
        It only executes cpu usage and get processes functions.
        Look for files in 'Results' and 'Processes' Directories.
    -w or --all_write <file_format>        : Writes all data collection function outputs to specified file format.
    ==================================SIDE FUNCTIONS =============================================================
    -i or --programs                       : Prints installed programs with verisons to terminal. 
    -p or --process                        : Returns processess.
    -u or --usb                            : Prints all active USB devices connected or in the system to terminal. 
    -f or --flash_drives                   : Prints all active USB disk drives connected to the system. 
    -b or --bios                           : Prints bios info.
    -n or --network                        : Prints network info.
    -g or --language                       : System Language.
    -o or --os                             : Operating System information.
    -c or --cpu                            : CPU information.
    -e or --gpu                            : GPU information.
    -m or --mem                            : Memory information.
    -d or --disk                           : Disk information.
    -s or --cpu_usage                      : CPU usage.
    '''


'''
main function for combining functions seperate data
currently it writes outputs to txt file. Soon it will output json files 
'''
if __name__ == '__main__':
    arg_list = sys.argv[1:]
    opts = "hwl:bipuengocmedsf"
    long_opts = ["help", "all_write", "external_usb_disk",
                 "loop", "usb", "flash_drives", "programs", "boot", "network"]
    arguments = len(sys.argv) - 1
    print("Arg Count: "+str(arguments))
    if len(sys.argv) == 1:
        print("Showing Manual Page.")
        print(manual_page.__doc__)
        sys.exit()
    try:
        arg, val = getopt.getopt(arg_list, opts, long_opts)
        for current_arg, current_val in arg:
            if current_arg in ("-h", "--help"):
                print(manual_page.__doc__)
                sys.exit()
            if current_arg in ("-w", "--all_write"):  # write
                file_format = current_val if current_val != "" else val[0]
                all_data_collection_write("GMYI_output", file_format)
                print(f"Files saved in './Results' directory.")
            if current_arg in ("-p", "--process"):
                with pd.option_context('display.max_rows', None, 'display.max_columns', None):
                    print(get_process())
            if current_arg in ("-u", "--usb"):
                with pd.option_context('display.max_rows', None, 'display.max_columns', None):
                    print(all_usb_devices("Status", "Class", "FriendlyName", "InstanceId"))
            if current_arg in ("-f", "--flash_drives"):
                with pd.option_context('display.max_rows', None, 'display.max_columns', None):
                    print(disk_usb_devices())
            if current_arg in ("-i", "--programs"):
                with pd.option_context('display.max_rows', None, 'display.max_columns', None):
                    print(installed_programs())
            if current_arg in ("-b", "--bios"):
                with pd.option_context('display.max_rows', None, 'display.max_columns', None):
                    print(bios_info())
            if current_arg in ("-n", "--network"):
                with pd.option_context('display.max_rows', None, 'display.max_columns', None):
                    print(network_info())
            if current_arg in ("-g", "--language"):
                with pd.option_context('display.max_rows', None, 'display.max_columns', None):
                    print(get_language())
            if current_arg in ("-o", "--os"):
                with pd.option_context('display.max_rows', None, 'display.max_columns', None):
                    print(os_info())
            if current_arg in ("-c", "--cpu"):
                with pd.option_context('display.max_rows', None, 'display.max_columns', None):
                    print(cpu_info())
            if current_arg in ("-e", "--gpu"):
                with pd.option_context('display.max_rows', None, 'display.max_columns', None):
                    print(gpu_info())
            if current_arg in ("-m", "--mem"):
                with pd.option_context('display.max_rows', None, 'display.max_columns', None):
                    print(mem_info())
            if current_arg in ("-d", "--disk"):
                with pd.option_context('display.max_rows', None, 'display.max_columns', None):
                    print(disk_info())
            if current_arg in ("-s", "--cpu_usage"):
                with pd.option_context('display.max_rows', None, 'display.max_columns', None):
                    print(cpu_usage())
            if current_arg in ("-l", "--loop"):                
                count_loop = 0
                s = sched.scheduler()
                # Checks if correct file format supplied.
                file_format = current_val if current_val != "" else val[0]
                accepted_formats = ['json', 'csv', 'txt']
                if file_format in accepted_formats:
                    print(f"Correct file format supplied: {file_format}")
                else:
                    raise Exception(f"Wrong file format supplied: {file_format}")
                # Checks if delay seconds supplied.
                if val == []:
                    raise Exception("Please enter seconds to be delayed after specifing file format!")
                print("Delay Seconds: " + str(val[0]) + " seconds")
                # Software loop
                while True:
                    print("Start Time : ", datetime.now(), "\n")
                    # Triggers 'all_data_collection_write' function for specified periods.
                    # Keep in mind, these periods not accurate %100.
                    event1 = s.enter(int(val[0]), 1, all_data_collection_write, argument=("loop", file_format))
                    print("Event Created : \n", event1)
                    s.run()
                    print("End Time : ", datetime.now())
                    count_loop = count_loop+1
    # wrong parameter supplied.
    except getopt.error as err:
        print(str(err))
        print("Please refer to help page (-h)!")
