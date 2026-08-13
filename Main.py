import os
import subprocess
import shutil
import tempfile
import sys

# Import Rich components for professional terminal UI. If unavailable, provide plain fallbacks.
try:
    import rich
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich.prompt import Prompt
    from rich.columns import Columns
    from rich import print as rprint
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    print("\033[1;31m[!] Missing required library 'rich'. Falling back to plain output. Install it using: pip install rich\033[0m")
    RICH_AVAILABLE = False

    class SimpleConsole:
        def print(self, *args, **kwargs):
            end = kwargs.get('end', '\n')
            sep = kwargs.get('sep', ' ')
            to_print = sep.join(str(a) for a in args)
            built = to_print + end
            # Strip Rich-style markup if present
            built = built.replace('[bold ', '').replace('[/bold]', '')
            print(built, end='')

    class SimplePrompt:
        @staticmethod
        def ask(prompt, choices=None, default=None):
            if choices:
                choices_list = list(choices)
                while True:
                    opts = '/'.join(choices_list)
                    raw = input(f"{prompt} ({opts}) [{default}]: ").strip()
                    if raw == '' and default is not None:
                        return default
                    if raw in choices_list:
                        return raw
                    # allow numeric selection as free input
                    if raw.isdigit():
                        return raw
                    print(f"Choose one of: {', '.join(choices_list)}")
            else:
                raw = input(f"{prompt}: ")
                if raw == '' and default is not None:
                    return default
                return raw

    # lightweight placeholders for Rich classes used elsewhere
    Panel = None
    Table = None
    Text = None
    Columns = None
    Prompt = SimplePrompt
    rprint = print
    console = SimpleConsole()

# Base Directory Setup
if os.path.exists("D:\\"):
    RAM_BASE_DIR = os.path.join("D:\\", "dark_marijuana_tools")
else:
    RAM_BASE_DIR = os.path.join(tempfile.gettempdir(), "dark_marijuana_tools")

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def ensure_ram_dir():
    try:
        os.makedirs(RAM_BASE_DIR, exist_ok=True)
    except Exception as e:
        console.print(f"[bold red][!] Error creating directory: {str(e)}[/bold red]")
        sys.exit(1)

def display_logo():
    logo_text = r"""
                  |
                 |.|
                 |.|
                |\\./|
                |\\./|
.               |\\./|               .
 \\^.\\          |\\\\.//|          /.^/
  \\--.|\\       |\\\\.//|       |.--/
    \\--.| \\    |\\\\.//|    / |.--/
     \\---.|\\    |\\./|    /|.---/
        \\--.|\\  |\\./|  /|.--/
           \\ .\\  |.|  /. /   
_ -_^_^_^_-  \\ \\ // /  -_^_^_^_- _
   - -/_/_/- ^_^/| |\\^_^ -\\_\\_\\- -
                  |

$$$$$$$\                                                      $$$                    $$
 $$  __$$\                                         $$\    $$$\   $$$$ |                   \__|
 $$ |  $$ | $$$$$$\   $$$$$$\   $$ |  $$\         $$$$\  $$$ | $$$$$$\   $$$$$$\   $$\ $$\ $$\   $$\  $$$$$$\   $$$$$$$\   $$$$$$\  
 $$ |  $$ | \____$$\ $$  __$$\ $$ | $$  |$$$$$$\ $$\$$\$$ $$ | \____$$\ $$  __$$\ $$ |\__|$$ |  $$ | \____$$\ $$  __$$\  \____$$\ 
 $$ |  $$ | $$$$$$$ |$$ |  \__|$$$$$$  / \______|$$ \$$$  $$ | $$$$$$$ |$$ |  \__|$$ |$$\ $$ |  $$ | $$$$$$$ |$$ |  $$ | $$$$$$$ |
 $$ |  $$ |$$  __$$ |$$ |      $$  _$$<          $$ |\$  /$$ |$$  __$$ |$$ |      $$ |$$ |$$ |  $$ |$$  __$$ |$$ |  $$ |$$  __$$ |
 $$$$$$$  |\$$$$$$$ |$$ |      $$ | \$$\         $$ | \_/ $$ |\$$$$$$$ |$$ |      $$ |$$ |\$$$$$$  |\$$$$$$$ |$$ |  $$ |\$$$$$$$ |
 \_______/  \_______|\__|      \__|  \__|        \__|     \__| \_______|\__|      \__|$$ | \______/  \_______|\__|  \__| \_______|
                                                                                      $$\   $$ |                                      
                                                                                      \$$$$$$  |                                      
                                                                                       \______/                                                     
    """
    if RICH_AVAILABLE:
        console.print(Panel(logo_text, style="bold green", subtitle="[bold yellow]Released by: Mohamed Ragheb | GitHub: DarkRagheb[/bold yellow]"))
    else:
        print(logo_text)
        print("Released by: Mohamed Ragheb | GitHub: DarkRagheb")

def draw_menu(title, options, style="table", exit_text="Exit"):
    """Render a menu either as a Rich Table (style='table') or framed Panels (style='frames')."""
    if not RICH_AVAILABLE:
        # Plain text fallback
        print(f"=== {title} ===")
        for idx, opt in enumerate(options, start=1):
            print(f"[{idx:02d}] {opt}")
        print(f"[00] {exit_text}")
        return
    if style == "frames":
        panels = []
        for idx, opt in enumerate(options, start=1):
            panels.append(Panel(f"[{idx:02d}] {opt}", style="bold cyan"))
        # Add exit panel
        panels.append(Panel(f"[00] {exit_text}", style="bold red"))
        console.print(Panel(title, style="bold yellow"))
        console.print(Columns(panels, expand=True))
        return

    # default: table style
    table = Table(title=title, title_style="bold yellow", border_style="bold cyan", expand=True)
    table.add_column("Option", justify="center", style="bold green", no_wrap=True, width=10)
    table.add_column("Name / Action", justify="left", style="bold white")

    for idx, opt in enumerate(options, start=1):
        table.add_row(f"[{idx:02d}]", opt)

    table.add_section()
    table.add_row("[00]", f"[bold red]{exit_text}[/bold red]")

    console.print(table)


def get_user_choice(prompt_text, choices=None, default=None):
    """Safe wrapper around Prompt.ask or SimplePrompt.ask that returns default on EOF/interrupt."""
    try:
        if RICH_AVAILABLE:
            # Prompt.ask can raise EOFError on non-interactive terminals
            return Prompt.ask(f"[bold cyan]{prompt_text}[/bold cyan]", choices=choices, default=default)
        else:
            return Prompt.ask(f"{prompt_text}", choices=choices, default=default)
    except (EOFError, KeyboardInterrupt):
        return default if default is not None else "0"

def build_github_url(repo_identifier):
    if repo_identifier.startswith("http://") or repo_identifier.startswith("https://"):
        return repo_identifier
    if "/" in repo_identifier:
        return f"https://github.com/{repo_identifier}.git"
    return f"https://github.com/DarkRagheb/{repo_identifier}.git"

def clone_tool(tool_name, repo_identifier):
    ensure_ram_dir()
    tool_path = os.path.join(RAM_BASE_DIR, tool_name)
    repo_url = build_github_url(repo_identifier)
    
    if not os.path.exists(tool_path):
        console.print(f"[bold cyan][*] Cloning {tool_name}...[/bold cyan]")
        try:
            result = subprocess.run(["git", "clone", repo_url, tool_path], timeout=300, capture_output=True, text=True)
            if result.returncode == 0:
                console.print(f"[bold green][+] Download completed successfully![/bold green]\n")
                return tool_path
            else:
                console.print(f"[bold red][!] Failed to clone: {result.stderr.strip()}[/bold red]")
                return None
        except Exception as e:
            console.print(f"[bold red][!] Error: {str(e)}[/bold red]")
            return None
    else:
        console.print(f"[bold yellow][!] {tool_name} already exists in temporary storage.[/bold yellow]")
        return tool_path

def cleanup_tool_files(tool_path):
    if not os.path.exists(tool_path):
        return
    console.print("[bold yellow][*] Cleaning temporary files...[/bold yellow]")
    try:
        shutil.rmtree(tool_path, ignore_errors=True)
        console.print("[bold green][+] Temporary tool files cleaned.[/bold green]\n")
    except Exception as e:
        console.print(f"[bold yellow][!] Warning during cleanup: {str(e)}[/bold yellow]")

def find_executable(tool_path, tool_name):
    candidates = []
    for root, dirs, files in os.walk(tool_path):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['.git', '__pycache__']]
        for file in files:
            full_path = os.path.join(root, file)
            if file.endswith('.py'):
                candidates.append((1 if file in ['main.py', f'{tool_name}.py'] else 2, full_path, "python3"))
            elif file.endswith('.sh'):
                candidates.append((3, full_path, "bash"))
    if candidates:
        candidates.sort(key=lambda x: x[0])
        return candidates[0][1], candidates[0][2]
    return None, None

def launch_tool(tool_path):
    if not tool_path or not os.path.exists(tool_path):
        return False
    tool_name = os.path.basename(tool_path)
    executable_file, interpreter = find_executable(tool_path, tool_name)

    if executable_file:
        console.print(f"[bold green][+] Executing via {interpreter.upper()}...[/bold green]\n")
        current_dir = os.getcwd()
        try:
            os.chdir(os.path.dirname(executable_file))
            cmd = [sys.executable, executable_file] if interpreter == "python3" else ["bash", executable_file]
            subprocess.run(cmd, check=False)
            cleanup_tool_files(tool_path)
            return True
        except Exception as e:
            console.print(f"[bold red][!] Execution error: {str(e)}[/bold red]")
            return False
        finally:
            os.chdir(current_dir)
    else:
        console.print(f"[bold red][!] No executable script found in {tool_name}.[/bold red]")
        return False

def cleanup_ram():
    if os.path.exists(RAM_BASE_DIR):
        try:
            shutil.rmtree(RAM_BASE_DIR)
            console.print("[bold green][+] RAM directory cleaned.[/bold green]")
        except Exception:
            pass

tools_dict = {
    "OSINT Tools": {
        "Sherlock": "sherlock-project/sherlock",
        "Full-OSINT Ways": "OPSEC-OSINT-Tools",
        "theHarvester": "laramies/theHarvester",
        "Sploitego": "sploitego",
        "Recon-ng": "lanmaster53/recon-ng",
        "SpiderFoot": "smicallef/spiderfoot",
        "Photon": "s0md3v/Photon"
    },
    "Network Tools": {
        "Nmap": "nmap/nmap",
        "Wireshark": "wireshark",
        "Aircrack-ng": "aircrack-ng/aircrack-ng",
        "Masscan": "robertdavidgraham/masscan",
        "RustScan": "RustScan/RustScan"
    },
    "Web Hacking Tools": {
        "Nikto": "sullo/nikto",
        "Commix": "commixproject/commix",
        "SQLMap": "sqlmapproject/sqlmap",
        "XSStrike": "s0md3v/XSStrike",
        "Gobuster": "OJ/gobuster",
        "FFUF": "ffuf/ffuf"
    },
    "Social-Media Phishing Tools": {
        "Social-Engineer-Toolkit(SET)": "trustedsec/social-engineer-toolkit",
        "GoPhish": "gophish/gophish",
        "ZPhisher": "htr-tech/zphisher",
        "instaloader": "instaloader/instaloader"
    },
    "Dark-Web Tools": {
        "TorBot": "DedSecInside/TorBot",
        "OnionShare": "onionshare/onionshare"
    }
}

def show_categories():
    while True:
        categories = list(tools_dict.keys())
        draw_menu("MAIN MENU / CATEGORIES", categories, style=MENU_STYLE, exit_text="Exit & Clean RAM")

        choice = get_user_choice("DARK-MARIJUANA", choices=None, default="0")
        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(categories):
                select_tool(categories[idx - 1])
            elif idx == 0:
                cleanup_ram()
                console.print("[bold green]GoodBye![/bold green]")
                return

def select_tool(category):
    while True:
        tools = tools_dict[category]
        tool_names = list(tools.keys())
        draw_menu(f"CATEGORY: {category.upper()}", tool_names, style=MENU_STYLE, exit_text="Return to Main Menu")

        choice = get_user_choice(f"DARK-MARIJUANA [{category}]", choices=None, default="0")
        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(tool_names):
                tool_name = tool_names[idx - 1]
                tool_path = clone_tool(tool_name, tools[tool_name])
                if tool_path:
                    launch_tool(tool_path)
            elif idx == 0:
                return

if __name__ == "__main__":
    try:
        clear_screen()
        display_logo()
        # Ask user which menu style they prefer: table or frames
        # use safe getter to avoid EOF/interrupts in non-interactive environments
        MENU_STYLE = get_user_choice("Choose menu style", choices=["table", "frames"], default="table")
        show_categories()
    except KeyboardInterrupt:
        cleanup_ram()
        sys.exit(0)
