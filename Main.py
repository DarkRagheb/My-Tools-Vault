import os
import subprocess
import shutil

RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[0;33m'
CYAN = '\033[36m'
RESET = '\033[0m'

# المسار المخصص للعمل بالكامل داخل الذاكرة العشوائية RAM
RAM_BASE_DIR = "/dev/shm/tools_ram"

def clear_screen():
    if os.name == 'posix':
        os.system('clear')
    else:
        os.system('cls')

def ensure_ram_dir():
    if not os.path.exists(RAM_BASE_DIR):
        os.makedirs(RAM_BASE_DIR, exist_ok=True)

def display_logo():
    logo = f"""
    {GREEN}
                  |
                 |.|
                 |.|
                |\\./|
                |\\./|
.               |\\./|               .
 \\^.\\          |\\\\.//|          /.^/
  \\--.|\\       |\\\\.//|       /|.--/
    \\--.| \\    |\\\\.//|    / |.--/
     \\---.|\\    |\./|    /|.---/
        \\--.|\\  |\\./|  /|.--/
           \\ .\\  |.|  /. /   
 _ -_^_^_^_-  \\ \\ // /  -_^_^_^_- _                            Info about Repo:
   - -/_/_/- ^_^/| |\\^_^ -\\_\\_\\- -                                Released date: 8/11/26 - By: Mohamed Ragheb </>...
                  |                                                  Link:https://www.github.com/DarkRagheb

$$$$$$$\\                      $$\xa0               $$\xa0     $$\xa0                    $$\xa0                                            
$$  __$$\xa0                    $$ |              $$$\xa0   $$$ |                    \__|                                            
$$ |  $$ | $$$$$$\   $$$$$$\  $$ |  $$\         $$$$\  $$$$ | $$$$$$\   $$$$$$\  $$\ $$\ $$\   $$\  $$$$$$\  $$$$$$$\   $$$$$$\  
$$ |  $$ | \____$$\ $$  __$$\ $$ | $$  |$$$$$$\ $$\$$\$$ $$ | \____$$\ $$  __$$\ $$ |\__|$$ |  $$ | \____$$\ $$  __$$\  \____$$\ 
$$ |  $$ | $$$$$$$ |$$ |  \__|$$$$$$  / \______|$$ \$$$  $$ | $$$$$$$ |$$ |  \__|$$ |$$\ $$ |  $$ | $$$$$$$ |$$ |  $$ | $$$$$$$ |
$$ |  $$ |$$  __$$ |$$ |      $$  _$$<          $$ |\$  /$$ |$$  __$$ |$$ |      $$ |$$ |$$ |  $$ |$$  __$$ |$$ |  $$ |$$  __$$ |
$$$$$$$  |\$$$$$$$ |$$ |      $$ | \$$\         $$ | \_/ $$ |\$$$$$$$ |$$ |      $$ |$$ |\$$$$$$  |\$$$$$$$ |$$ |  $$ |\$$$$$$$ |
\_______/  \_______|\__|      \__|  \__|        \__|     \__| \_______|\__|      \__|$$ | \______/  \_______|\__|  \__| \_______|
                                                                               $$\   $$ |                                        
                                                                               \$$$$$$  |                                        
                                                                                \______/                                         
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>..............>
    {RESET}
    """
    print(logo)

def clone_tool(tool_name, repo_url):
    ensure_ram_dir()
    tool_path = os.path.join(RAM_BASE_DIR, tool_name)
    
    if not os.path.exists(tool_path):
        print(f"{CYAN}Cloning {tool_name} to RAM ({tool_path})...{RESET}")
        result = subprocess.run(["git", "clone", repo_url, tool_path])
        if result.returncode == 0:
            print(f"{GREEN}Download completed in RAM!{RESET}\n")
        else:
            print(f"{RED}Failed to clone {tool_name}.{RESET}")
    else:
        print(f"{YELLOW}{tool_name} already exists in RAM.{RESET}")
    return tool_path

def launch_tool(tool_name):
    """تشغيل الأداة المخزنة في الذاكرة العشوائية"""
    tool_path = os.path.join(RAM_BASE_DIR, tool_name)

    if not os.path.exists(tool_path):
        print(f"{RED}Error: The directory for {tool_name} does not exist in RAM.{RESET}")
        return

    files = os.listdir(tool_path)
    script_to_run = None

    for file in files:
        if file.endswith(".py") or file.endswith(".sh"):
            script_to_run = file
            break

    if script_to_run:
        script_path = os.path.join(tool_path, script_to_run)
        print(f"{GREEN}Executing {script_to_run} from RAM...{RESET}\n")
        if script_to_run.endswith(".py"):
            subprocess.run(["python3", script_path])
        elif script_to_run.endswith(".sh"):
            subprocess.run(["bash", script_path])
    else:
        print(f"{RED}No executable Python or Bash script found in {tool_path}.{RESET}")

def cleanup_ram():
    """حذف جميع الأدوات من الذاكرة العشوائية فور الخروج"""
    if os.path.exists(RAM_BASE_DIR):
        print(f"\n{YELLOW}Cleaning up RAM directory (/dev/shm)...{RESET}")
        shutil.rmtree(RAM_BASE_DIR, ignore_errors=True)
        print(f"{GREEN}RAM cleaned successfully.{RESET}")

tools_dict = {
    "OSINT Tools": {
        "Sherlock": "https://github.com/sherlock-project/sherlock.git",
        "Full-OSINT Ways": "https://github.com/airborne-commando/OPSEC-OSINT-Tools",
        "theHarvester": "https://github.com/laramies/theHarvester.git",
        "Sploitego": "https://github.com/allfro/sploitego",
        "Recon-ng": "https://github.com/lanmaster53/recon-ng.git",
        "FOCA": "https://github.com/ElevenPaths/FOCA",
        "Amass": "https://github.com/OWASP/Amass.git",
        "TS-OSINT": "https://github.com/trsi-sa/TS-OSINT",
        "SpiderFoot": "https://github.com/smicallef/spiderfoot.git",
        "Photon": "https://github.com/s0md3v/Photon.git",
        "Cr3dOv3r": "https://github.com/D4Vinci/Cr3dOv3r"
    },
    "Network Tools": {
        "Nmap": "https://github.com/nmap/nmap.git",
        "Netcat": "https://github.com/diegocr/netcat.git",
        "Wireshark": "https://github.com/wireshark/wireshark.git",
        "Aircrack-ng": "https://github.com/aircrack-ng/aircrack-ng.git",
        "Sublist3r": "https://github.com/aboul3la/Sublist3r",
        "SubnetWizard": "https://github.com/naemazam/SubnetWizard",
        "Naabu": "https://github.com/projectdiscovery/naabu.git",
        "Masscan": "https://github.com/robertdavidgraham/masscan.git",
        "RustScan": "https://github.com/RustScan/RustScan.git",
        "NetworkManager": "https://github.com/BornToBeRoot/NETworkManager"
    },
    "Web Hacking Tools": {
        "Nikto": "https://github.com/sullo/nikto.git",
        "Burpsuite": "https://github.com/xiv3r/Burpsuite-Professional.git",
        "Commix": "https://github.com/commixproject/commix.git",
        "Katana": "https://github.com/projectdiscovery/katana.git",
        "BadMod": "https://github.com/M4DM0e/BadMod",
        "SQLMap": "https://github.com/sqlmapproject/sqlmap.git",
        "XSStrike": "https://github.com/s0md3v/XSStrike.git",
        "XSSer": "https://github.com/epsylon/xsser",
        "Pocsuite3": "https://github.com/knownsec/pocsuite3.git",
        "Gobuster": "https://github.com/OJ/gobuster.git",
        "FFUF": "https://github.com/ffuf/ffuf.git", # تم تصحيح رابط FFUF
        "NucleiScanner": "https://github.com/projectdiscovery/nuclei.git",
        "Red-Hawk": "https://github.com/Tuhinshubhra/Red_Hawk.git",
        "AngryOxide": "https://github.com/Ragnt/AngryOxide",
        "Azemux": "https://github.com/ByFragment/Azemux"
    },
    "Social-Media Phishing Tools": {
        "Social-Engineer-Toolkit(SET)": "https://github.com/trustedsec/social-engineer-toolkit.git",
        "GoPhish": "https://github.com/gophish/gophish.git",
        "ZPhisher": "https://github.com/htr-tech/zphisher",
        "Black-Eye":"https://github.com/8L4NK/blackeye",
        "ADV-Phishing": "https://github.com/bhikandeshmukh/AdvPhishing",
        "Saintgram": "https://github.com/joe444-pnj/saintgram.git",
        "Hrack": "https://github.com/trsi-sa/Hrack",
        "instaloader": "https://github.com/instaloader/instaloader.git",
        "InstaHack": "https://github.com/mark0909099/instahack",
        "InstaScraper": "https://github.com/andrew/instascraper",
        "InstaBrute": "https://github.com/Ha3MrX/InstaBrute"
    },
    "Dark-Web Tools": {
        "Tor": "https://github.com/torproject/tor.git",
        "TorBot": "https://github.com/DedSecInside/TorBot",
        "TorSearcher": "https://github.com/some-man1/TorSearcher",
        "OnionShare": "https://github.com/onionshare/onionshare.git",
        "Onion-Peeler": "https://github.com/albertoscala/onion-peeler",
        "DP-Search Engine": "https://github.com/NexvisionLab/Darkweb-search-engine",
        "Dark-Science": "https://github.com/darkscience/darkweb",
        "Darkus": "https://github.com/Lucksi/Darkus",
        "FreshOnions": "https://github.com/CainP/FreshOnions-clone.git",
        "AHA-Mia": "https://github.com/ahamia/ahamia.git"
    }
}

def show_categories():
    print(f"{RED}Select a category:{RESET}")
    categories = list(tools_dict.keys())

    for idx, cat in enumerate(categories, start=1):
        print(f"{RED}{idx} - {cat}{RESET}")
    print(f"{YELLOW}0 - Exit and Clean RAM{RESET}")

    choice = input(f"{CYAN}DARK-MARIJUANA > {RESET}")

    if choice.isdigit():
        idx = int(choice)
        if 1 <= idx <= len(categories):
            selected_cat = categories[idx - 1]
            select_tool(selected_cat)
        elif idx == 0:
            cleanup_ram()
            print(f"{YELLOW}GoodBye! CAN'T WAIT TO SEE YOU AGAIN ;){RESET}")
            exit()
        else:
            print(f"{YELLOW}Invalid choice!{RESET}")
            show_categories()
    else:
        print(f"{YELLOW}Invalid choice!{RESET}")
        show_categories()

def select_tool(category):
    print(f"\n{GREEN}{category}:{RESET}\n")
    tools = tools_dict[category]
    tool_names = list(tools.keys())

    for idx, tool in enumerate(tool_names, start=1):
        print(f"{RED}{idx} - {tool}{RESET}")
    print(f"{YELLOW}0 - Return to Categories{RESET}\n")

    tool_choice = input(f"{CYAN}DARK-MARIJUANA > {RESET}")

    if tool_choice.isdigit():
        idx = int(tool_choice)
        if 1 <= idx <= len(tool_names):
            tool_name = tool_names[idx - 1]
            repo_url = tools[tool_name]
            
            clone_tool(tool_name, repo_url)
            launch_tool(tool_name)
            select_tool(category)
        elif idx == 0:
            show_categories()
        else:
            print(f"{GREEN}Invalid choice!{RESET}")
            select_tool(category)
    else:
        print(f"{GREEN}Invalid choice!{RESET}")
        select_tool(category)

if __name__ == "__main__":
    try:
        clear_screen()
        display_logo()
        show_categories()
    except KeyboardInterrupt:
        cleanup_ram()
        exit()