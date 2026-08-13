import os
import subprocess
import shutil
import tempfile
import sys
import stat

RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[0;33m'
CYAN = '\033[36m'
RESET = '\033[0m'

# Use D: drive (has space) instead of C: (full). Falls back to temp if D: not available
if os.path.exists("D:\\"):
    RAM_BASE_DIR = os.path.join("D:\\", "dark_marijuana_tools")
else:
    RAM_BASE_DIR = os.path.join(tempfile.gettempdir(), "dark_marijuana_tools")

def clear_screen():
    if os.name == 'posix':
        os.system('clear')
    else:
        os.system('cls')

def ensure_ram_dir():
    try:
        if not os.path.exists(RAM_BASE_DIR):
            os.makedirs(RAM_BASE_DIR, exist_ok=True)
    except PermissionError:
        print(f"{RED}Error: Permission denied creating directory {RAM_BASE_DIR}{RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"{RED}Error creating directory: {str(e)}{RESET}")
        sys.exit(1)

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
        print(f"{CYAN}Cloning {tool_name} to temporary directory ({tool_path})...{RESET}")
        try:
            result = subprocess.run(
                ["git", "clone", repo_url, tool_path],
                timeout=300,  # 5 minute timeout
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(f"{GREEN}Download completed successfully!{RESET}\n")
                return tool_path
            else:
                print(f"{RED}Failed to clone {tool_name}: {result.stderr}{RESET}")
                return None
        except subprocess.TimeoutExpired:
            print(f"{RED}Clone timeout for {tool_name}. Repository too large or network issue.{RESET}")
            return None
        except FileNotFoundError:
            print(f"{RED}Error: git is not installed or not in PATH.{RESET}")
            return None
        except Exception as e:
            print(f"{RED}Error cloning {tool_name}: {str(e)}{RESET}")
            return None
    else:
        print(f"{YELLOW}{tool_name} already exists in temporary storage.{RESET}")
        return tool_path

def cleanup_tool_files(tool_path):
    """Remove temporary and signature files created by the tool"""
    if not os.path.exists(tool_path):
        return
    
    # Extensions and patterns to clean up
    temp_patterns = [
        '.tmp', '.temp', '.cache', '.sig', '.signature',
        '.lock', '.pid', '.log', '.bak', '.swp', '.swo',
        '__pycache__', '.pytest_cache', '.coverage'
    ]
    
    print(f"{YELLOW}Cleaning temporary files...{RESET}")
    cleaned_count = 0
    
    try:
        for root, dirs, files in os.walk(tool_path):
            # Remove directories matching patterns
            dirs_to_remove = []
            for dir_name in dirs:
                if dir_name in ['__pycache__', '.pytest_cache', '.cache', '.git']:
                    dirs_to_remove.append(dir_name)
            
            for dir_name in dirs_to_remove:
                dir_path = os.path.join(root, dir_name)
                try:
                    shutil.rmtree(dir_path, ignore_errors=True)
                    cleaned_count += 1
                except Exception:
                    pass
            
            # Remove files matching patterns
            for file_name in files:
                file_path = os.path.join(root, file_name)
                # Check if file matches any cleanup pattern
                should_delete = any(file_name.endswith(pattern) for pattern in temp_patterns)
                
                if should_delete:
                    try:
                        os.remove(file_path)
                        cleaned_count += 1
                    except Exception:
                        pass
        
        if cleaned_count > 0:
            print(f"{GREEN}Removed {cleaned_count} temporary file(s).{RESET}\n")
    except Exception as e:
        print(f"{YELLOW}Warning: Could not fully clean temporary files: {str(e)}{RESET}\n")

import stat

def find_executable(tool_path, tool_name):
    """Find executable file in tool directory with smart detection including Go projects"""
    candidates = []  # (priority, file_path, interpreter, tool_root)
    
    # Check for Go project (go.mod file)
    go_mod_path = os.path.join(tool_path, "go.mod")
    if os.path.exists(go_mod_path):
        # Look for main.go in cmd/{tool_name}/ directory
        cmd_path = os.path.join(tool_path, "cmd", tool_name)
        main_go = os.path.join(cmd_path, "main.go")
        if os.path.exists(main_go):
            candidates.append((0, main_go, "go", tool_path))  # Go projects highest priority
    
    for root, dirs, files in os.walk(tool_path):
        # Skip hidden and cache directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['.git', '__pycache__', 'node_modules', 'vendor']]
        
        for file in files:
            if file.startswith('.'):
                continue
            
            full_path = os.path.join(root, file)
            
            # Skip common non-executable files
            if file.endswith(('.md', '.txt', '.png', '.jpg', '.json', '.yml', '.yaml', '.toml', '.lock', '.log', '.tmp', '.mod', '.sum')):
                continue
            
            # Priority 2: Python scripts (main entry points)
            if file.endswith('.py'):
                if file in ['main.py', '__main__.py', f'{tool_name}.py']:
                    candidates.append((2, full_path, "python3", tool_path))
                elif 'test' not in file and 'setup' not in file and 'config' not in file:
                    candidates.append((3, full_path, "python3", tool_path))
            
            # Priority 3: Shell/Bash scripts
            elif file.endswith('.sh'):
                if file in ['main.sh', 'run.sh', f'{tool_name}.sh']:
                    candidates.append((4, full_path, "bash", tool_path))
                else:
                    candidates.append((5, full_path, "bash", tool_path))
    
    # Return best candidate
    if candidates:
        candidates.sort(key=lambda x: x[0])
        best = candidates[0]
        return best[1], best[2], best[3]
    
    return None, None, None

def launch_tool(tool_path):
    if not tool_path or not os.path.exists(tool_path):
        print(f"{RED}Error: Tool directory does not exist.{RESET}")
        return False

    # Extract tool name from path for Go project detection
    tool_name = os.path.basename(tool_path)
    
    # Find executable using smart detection
    executable_file, interpreter, tool_root = find_executable(tool_path, tool_name)

    if executable_file:
        print(f"{GREEN}[+] Found: {os.path.basename(executable_file)}{RESET}")
        print(f"{GREEN}[+] Launching via {interpreter.upper()}...{RESET}\n")
        
        current_dir = os.getcwd()
        
        try:
            if interpreter == "go":
                # Run Go program: go run <path_to_main.go>
                os.chdir(tool_root)  # Change to root of Go project
                subprocess.run(["go", "run", executable_file], timeout=3600, check=False)
            elif interpreter == "python3":
                os.chdir(os.path.dirname(executable_file))
                subprocess.run([sys.executable, executable_file], timeout=3600, check=False)
            elif interpreter == "bash":
                os.chdir(os.path.dirname(executable_file))
                subprocess.run(["bash", executable_file], timeout=3600, check=False)
            
            # Clean up temporary files after tool execution
            cleanup_tool_files(tool_path)
            return True
        except subprocess.TimeoutExpired:
            print(f"{RED}Tool execution timeout (1 hour limit exceeded).{RESET}")
            cleanup_tool_files(tool_path)  # Still cleanup even on timeout
            return False
        except FileNotFoundError as e:
            print(f"{RED}Error: Cannot find {interpreter}: {str(e)}{RESET}")
            if interpreter == "go":
                print(f"{YELLOW}Install Go from: https://golang.org/dl/{RESET}")
            return False
        except Exception as e:
            print(f"{RED}Error executing tool: {str(e)}{RESET}")
            return False
        finally:
            os.chdir(current_dir)
    else:
        print(f"{RED}No executable script or binary found in {tool_name}.{RESET}")
        print(f"{YELLOW}Contents of {tool_name}:{RESET}")
        try:
            for root, dirs, files in os.walk(tool_path):
                level = root.replace(tool_path, '').count(os.sep)
                indent = ' ' * 2 * level
                rel_path = os.path.relpath(root, tool_path)
                print(f'{indent}{rel_path}/')
                subindent = ' ' * 2 * (level + 1)
                for file in sorted(files)[:15]:
                    print(f'{subindent}{file}')
                if len(files) > 15:
                    print(f'{subindent}... and {len(files) - 15} more files')
                if level > 2:
                    break
        except Exception as e:
            print(f"{YELLOW}Error listing contents: {str(e)}{RESET}")
        return False

def cleanup_ram():
    """Clean up temporary directory with proper error handling"""
    if os.path.exists(RAM_BASE_DIR):
        try:
            print(f"\n{YELLOW}Cleaning up temporary directory...{RESET}")
            shutil.rmtree(RAM_BASE_DIR)
            print(f"{GREEN}Temporary directory cleaned successfully.{RESET}")
        except PermissionError:
            print(f"{YELLOW}Warning: Permission denied cleaning directory. Some files may remain.{RESET}")
        except Exception as e:
            print(f"{YELLOW}Warning: Error cleaning directory: {str(e)}{RESET}")

tools_dict = {
    "OSINT Tools": {
        "Sherlock": "sherlock",
        "Full-OSINT Ways": "OPSEC-OSINT-Tools",
        "theHarvester": "theHarvester",
        "Sploitego": "sploitego",
        "Recon-ng": "recon-ng",
        "FOCA": "FOCA",
        "Amass": "Amass",
        "TS-OSINT": "TS-OSINT",
        "SpiderFoot": "spiderfoot",
        "Photon": "Photon",
        "Cr3dOv3r": "Cr3dOv3r"
    },
    "Network Tools": {
        "Nmap": "nmap",
        "Netcat": "netcat",
        "Wireshark": "wireshark",
        "Aircrack-ng": "aircrack-ng",
        "Sublist3r": "Sublist3r",
        "SubnetWizard": "SubnetWizard",
        "Naabu": "naabu",
        "Masscan": "masscan",
        "RustScan": "RustScan",
        "NetworkManager": "NETworkManager"
    },
    "Web Hacking Tools": {
        "Nikto": "nikto",
        "Burpsuite": "Burpsuite-Professional",
        "Commix": "commix",
        "Katana": "katana",
        "BadMod": "BadMod",
        "SQLMap": "sqlmap",
        "XSStrike": "XSStrike",
        "XSSer": "xsser",
        "Pocsuite3": "pocsuite3",
        "Gobuster": "gobuster",
        "FFUF": "ffuf",
        "NucleiScanner": "nuclei",
        "Red-Hawk": "Red_Hawk",
        "AngryOxide": "AngryOxide",
        "Azemux": "Azemux"
    },
    "Social-Media Phishing Tools": {
        "Social-Engineer-Toolkit(SET)": "social-engineer-toolkit",
        "GoPhish": "gophish",
        "ZPhisher": "zphisher",
        "Black-Eye": "blackeye",
        "ADV-Phishing": "AdvPhishing",
        "Saintgram": "saintgram",
        "Hrack": "Hrack",
        "instaloader": "instaloader",
        "InstaHack": "instahack",
        "InstaScraper": "instascraper",
        "InstaBrute": "InstaBrute"
    },
    "Dark-Web Tools": {
        "Tor": "tor",
        "TorBot": "TorBot",
        "TorSearcher": "TorSearcher",
        "OnionShare": "onionshare",
        "Onion-Peeler": "onion-peeler",
        "DP-Search Engine": "Darkweb-search-engine",
        "Dark-Science": "darkweb",
        "Darkus": "Darkus",
        "FreshOnions": "FreshOnions-clone",
        "AHA-Mia": "ahamia"
    }
}
def show_categories():
    """Menu loop for category selection - avoid recursion for stability"""
    while True:
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
                return
            else:
                print(f"{YELLOW}Invalid choice! Please try again.{RESET}\n")
        else:
            print(f"{YELLOW}Invalid choice! Please try again.{RESET}\n")

def select_tool(category):
    """Menu loop for tool selection - avoid recursion for stability"""
    while True:
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
                
                tool_path = clone_tool(tool_name, repo_url)
                if tool_path:
                    launch_tool(tool_path)
            elif idx == 0:
                return
            else:
                print(f"{YELLOW}Invalid choice! Please try again.{RESET}\n")
        else:
            print(f"{YELLOW}Invalid choice! Please try again.{RESET}\n")

if __name__ == "__main__":
    try:
        clear_screen()
        display_logo()
        show_categories()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Interrupted by user.{RESET}")
        cleanup_ram()
        sys.exit(0)
    except Exception as e:
        print(f"{RED}Unexpected error: {str(e)}{RESET}")
        cleanup_ram()
        sys.exit(1)