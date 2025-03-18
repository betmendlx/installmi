#!/usr/bin/env python3
# Security Tools Installer buat Pemalas seperti nakke cess :D
# by betmen0x0 

import os
import sys
import subprocess
import shutil
import platform
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.panel import Panel
from rich.table import Table

console = Console()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class InstallerAlatKeamanan:
    def __init__(self, daftar_alat: Dict[str, str]):
        self.daftar_alat = daftar_alat
        self.alat_berhasil: List[str] = []
        self.alat_gagal: List[str] = []
        self.jenis_os = self._deteksi_os()
        self.tmp_dir = Path("./tmp_installer")
        self.tmp_dir.mkdir(exist_ok=True)
        self.go_path = self._setup_go_path()
        self.bin_path = self._setup_bin_path()
        self.repo_cache = {}  # Cache for cloned repositories

    def _deteksi_os(self) -> str:
        nama_os = platform.system().lower()
        console.print(f"[bold blue][INFO][/bold blue] Detected OS: {nama_os}")
        return nama_os

    def _setup_go_path(self) -> str:
        """Set up GOPATH and ensure it exists in the PATH."""
        go_path = os.environ.get('GOPATH')
        if not go_path:
            go_path = str(Path.home() / 'go')
            os.environ['GOPATH'] = go_path
        
        # Create bin directory if it doesn't exist
        bin_path = os.path.join(go_path, 'bin')
        os.makedirs(bin_path, exist_ok=True)
        
        # Add bin directory to PATH if it's not already there
        if bin_path not in os.environ.get('PATH', ''):
            os.environ['PATH'] = f"{bin_path}{os.pathsep}{os.environ.get('PATH', '')}"
        
        console.print(f"[bold blue][INFO][/bold blue] GOPATH set to: {go_path}")
        return go_path

    def _setup_bin_path(self) -> str:
        """Set up a local bin directory for installed tools."""
        if self.jenis_os == 'linux' or self.jenis_os == 'darwin':
            bin_path = '/usr/local/bin'
            if not os.path.exists(bin_path) or not os.access(bin_path, os.W_OK):
                bin_path = str(Path.home() / '.local' / 'bin')
                os.makedirs(bin_path, exist_ok=True)
                if bin_path not in os.environ.get('PATH', ''):
                    os.environ['PATH'] = f"{bin_path}{os.pathsep}{os.environ.get('PATH', '')}"
        else:
            # Windows or other OS
            bin_path = str(Path.home() / '.local' / 'bin')
            os.makedirs(bin_path, exist_ok=True)
            if bin_path not in os.environ.get('PATH', ''):
                os.environ['PATH'] = f"{bin_path}{os.pathsep}{os.environ.get('PATH', '')}"
        
        console.print(f"[bold blue][INFO][/bold blue] Local bin directory: {bin_path}")
        return bin_path

    def _check_installed(self, tool: str) -> bool:
        """Check if a tool is already installed."""
        # Check common variations of the tool name
        tool_variations = [tool.lower(), tool]
        
        for variation in tool_variations:
            if shutil.which(variation):
                return True
        
        # Check if in go bin directory
        go_bin_path = os.path.join(self.go_path, 'bin')
        if os.path.exists(os.path.join(go_bin_path, tool.lower())) or os.path.exists(os.path.join(go_bin_path, tool)):
            return True
            
        # Check if in local bin directory
        if os.path.exists(os.path.join(self.bin_path, tool.lower())) or os.path.exists(os.path.join(self.bin_path, tool)):
            return True
            
        return False

    def _run_command(self, command: str, cwd: Optional[str] = None) -> Tuple[bool, str]:
        """Run a shell command and return success status and output."""
        current_dir = os.getcwd()
        try:
            if cwd:
                os.chdir(cwd)
            
            process = subprocess.run(
                command,
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            return True, process.stdout
        except subprocess.CalledProcessError as e:
            return False, e.stderr
        except Exception as e:
            return False, str(e)
        finally:
            if cwd:
                os.chdir(current_dir)

    def _clone_repo(self, repo_url: str, repo_name: str = None) -> Tuple[bool, str]:
        """Clone a git repository to a temporary directory."""
        if repo_name is None:
            repo_name = repo_url.split('/')[-1].replace('.git', '')
        
        # Check if already cloned
        if repo_name in self.repo_cache:
            return True, self.repo_cache[repo_name]
        
        clone_path = self.tmp_dir / repo_name
        if clone_path.exists():
            shutil.rmtree(clone_path)
        
        clone_cmd = f"git clone {repo_url} {clone_path}"
        success, output = self._run_command(clone_cmd)
        
        if success:
            self.repo_cache[repo_name] = str(clone_path)
            return True, str(clone_path)
        else:
            return False, output

    def periksa_dependensi(self) -> bool:
        """Check for required dependencies."""
        dependensi = ["git", "go", "pip"]
        tidak_tersedia = []
        
        for dep in dependensi:
            if not shutil.which(dep):
                tidak_tersedia.append(dep)
        
        if tidak_tersedia:
            install_cmd = ""
            if self.jenis_os == 'linux':
                install_cmd = f"sudo apt install {' '.join(tidak_tersedia)}"
            elif self.jenis_os == 'darwin':
                install_cmd = f"brew install {' '.join(tidak_tersedia)}"
            elif self.jenis_os == 'windows':
                install_cmd = "Please install the following dependencies manually: " + ", ".join(tidak_tersedia)
            
            console.print(
                Panel.fit(
                    f"Missing dependencies: {', '.join(tidak_tersedia)}\n"
                    f"Install dependencies with:\n"
                    f"{install_cmd}",
                    title="[bold red]Dependency Error[/bold red]",
                    border_style="red"
                )
            )
            return False

        # Additional dependency for Naabu: Install libpcap
        if self.jenis_os == 'linux':
            try:
                console.print("[bold blue][INFO][/bold blue] Checking for libpcap-dev...")
                result = subprocess.run("apt-get -qq list libpcap-dev", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if "installed" not in result.stdout.decode():
                    console.print("[bold blue][INFO][/bold blue] Installing libpcap-dev...")
                    subprocess.run("sudo apt-get install -y libpcap-dev", shell=True, check=True)
            except subprocess.CalledProcessError:
                console.print("[yellow]Warning: Failed to install libpcap-dev. Naabu may fail.[/yellow]")

        return True

    def install_go_tool(self, tool_name: str, go_package: str) -> bool:
        """Install a Go tool using 'go install'."""
        install_cmd = f"go install -v {go_package}"
        success, output = self._run_command(install_cmd)
        
        if not success:
            console.print(f"[yellow]Warning: Failed to install {tool_name} with standard go install. Trying with GO111MODULE=on...[/yellow]")
            install_cmd = f"GO111MODULE=on go install -v {go_package}"
            success, output = self._run_command(install_cmd)
        
        return success

    def process_special_tools(self, tool_name: str) -> bool:
        """Handle special cases for specific tools."""
        tool_name_lower = tool_name.lower()
        
        # Handle Gf special case
        if tool_name_lower == "gf":
            success, repo_path = self._clone_repo("https://github.com/tomnomnom/gf.git")
            if not success:
                return False
                
            # Build and install gf
            success, _ = self._run_command("go build && cp gf ~/go/bin/", repo_path)
            if not success:
                return False
                
            # Set up .gf directory
            gf_dir = Path.home() / ".gf"
            gf_dir.mkdir(exist_ok=True)
            
            # Copy patterns
            patterns_src = Path(repo_path) / "examples"
            if patterns_src.exists():
                for pattern_file in patterns_src.glob("*"):
                    shutil.copy(pattern_file, gf_dir)
                console.print(f"[green]✓[/green] Copied GF patterns to {gf_dir}")
            else:
                console.print(f"[yellow]Warning: GF patterns directory not found.[/yellow]")
            
            return True
            
        # Handle hacks repository tools
        if tool_name_lower in ["anti-burl", "filter-resolved", "html-tool", "tojson"]:
            success, repo_path = self._clone_repo("https://github.com/tomnomnom/hacks.git")
            if not success:
                return False
                
            tool_path = Path(repo_path) / tool_name_lower
            if not tool_path.exists():
                console.print(f"[red]Error: Tool directory {tool_name_lower} not found in hacks repository.[/red]")
                return False
                
            # Copy tool to go bin directory
            target_path = Path(self.go_path) / "bin" / tool_name_lower
            try:
                shutil.copy(tool_path / tool_name_lower, target_path)
                os.chmod(target_path, 0o755)  # Make executable
                return True
            except Exception as e:
                console.print(f"[red]Error copying {tool_name_lower}: {str(e)}[/red]")
                return False
                
        return False  # Not a special case

    def jalankan_perintah(self, perintah: str, alat: str) -> bool:
        """Run installation command for a tool."""
        try:
            if self._check_installed(alat):
                console.print(f"[yellow][SKIP][/yellow] {alat} is already installed")
                return True

            # Check if it's a "manual" tool that just needs to open a website
            if perintah.startswith('open '):
                url = perintah.split('open ')[1]
                console.print(f"[yellow][MANUAL][/yellow] Please visit: {url}")
                return True
                
            # Check if it's a special case tool
            if self.process_special_tools(alat):
                console.print(f"[green]✓[/green] {alat} successfully installed")
                return True

            # Handle Go install commands
            if perintah.startswith('go install'):
                package = perintah.split('go install -v ')[1]
                return self.install_go_tool(alat, package)

            # Handle Git clone commands
            if perintah.startswith('git clone'):
                # Parse the command into components
                components = perintah.split('&&')
                clone_cmd = components[0].strip()
                repo_url = clone_cmd.split('git clone ')[1].split()[0]
                
                # Clone the repository
                success, repo_path = self._clone_repo(repo_url)
                if not success:
                    console.print(f"[red]Failed to clone repository for {alat}: {repo_path}[/red]")
                    return False
                    
                # Process the remaining commands
                for cmd in components[1:]:
                    cmd = cmd.strip()
                    if not cmd:
                        continue
                        
                    # Handle directory changes
                    if cmd.startswith('cd '):
                        # Extract the directory name
                        cd_parts = cmd.split('&&')
                        dir_name = cd_parts[0].replace('cd ', '').strip()
                        
                        # Determine the actual directory path
                        if dir_name.startswith('/'):
                            dir_path = dir_name  # Absolute path
                        else:
                            # Relative to the repo
                            dir_path = os.path.join(repo_path, dir_name)
                            
                        # Execute the remaining commands in this directory
                        remaining_cmd = '&&'.join(cd_parts[1:]).strip()
                        if remaining_cmd:
                            success, output = self._run_command(remaining_cmd, dir_path)
                            if not success:
                                console.print(f"[red]Failed to execute command for {alat}: {output}[/red]")
                                return False
                    else:
                        # Execute the command in the repo directory
                        success, output = self._run_command(cmd, repo_path)
                        if not success:
                            console.print(f"[red]Failed to execute command for {alat}: {output}[/red]")
                            return False
                
                console.print(f"[green]✓[/green] {alat} successfully installed")
                return True
                
            # Handle pip install commands
            if perintah.startswith('pip install'):
                success, output = self._run_command(perintah)
                if success:
                    console.print(f"[green]✓[/green] {alat} successfully installed")
                    return True
                else:
                    console.print(f"[red]Failed to install {alat} via pip: {output}[/red]")
                    return False
                
            # Handle other commands
            success, output = self._run_command(perintah)
            if success:
                console.print(f"[green]✓[/green] {alat} successfully installed")
                return True
            else:
                console.print(f"[red]Failed to install {alat}: {output}[/red]")
                return False
                
        except Exception as e:
            console.print(
                Panel.fit(
                    f"Installation failed for {alat}\n"
                    f"Command: {perintah}\n"
                    f"Error: {str(e)}",
                    title="[bold red]Installation Error[/bold red]",
                    border_style="red"
                )
            )
            return False

    def install_alat(self, alat_terpilih: List[str] = None) -> None:
        """Install selected tools or all tools."""
        if not self.periksa_dependensi():
            console.print("[bold red]Please install dependencies before continuing.[/bold red]")
            return

        # Normalize tool names for case-insensitive matching
        tool_map = {k.lower(): k for k in self.daftar_alat.keys()}
        
        if alat_terpilih:
            # Convert selected tools to lowercase for matching
            alat_terpilih_lower = [tool.lower() for tool in alat_terpilih]
            
            # Map back to original case
            alat_untuk_dipasang = []
            for tool_lower in alat_terpilih_lower:
                if tool_lower in tool_map:
                    alat_untuk_dipasang.append(tool_map[tool_lower])
                else:
                    console.print(f"[yellow]Warning: Tool {tool_lower} not found in the list.[/yellow]")
        else:
            alat_untuk_dipasang = list(self.daftar_alat.keys())
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("{task.completed}/{task.total} [bold green]tools[/bold green] installed"),
            console=console,
        ) as progress:
            task = progress.add_task("Installing tools", total=len(alat_untuk_dipasang))

            for alat in alat_untuk_dipasang:
                console.print(f"[bold cyan][INFO][/bold cyan] Starting installation of {alat}")
                berhasil = self.jalankan_perintah(self.daftar_alat[alat], alat)
                
                if berhasil:
                    self.alat_berhasil.append(alat)
                else:
                    self.alat_gagal.append(alat)
                
                progress.update(task, advance=1)

        self._cetak_ringkasan()
        
        # Clean up temporary directory
        try:
            shutil.rmtree(self.tmp_dir)
        except Exception as e:
            console.print(f"[yellow]Warning: Failed to clean up temporary directory: {str(e)}[/yellow]")

    def _cetak_ringkasan(self) -> None:
        """Print installation summary."""
        tabel = Table(title="Installation Summary")
        tabel.add_column("Status", style="cyan")
        tabel.add_column("Count", style="yellow")
        tabel.add_column("Tools", style="magenta")
        
        if self.alat_berhasil:
            tabel.add_row("[green]Installed[/green]", str(len(self.alat_berhasil)), ", ".join(self.alat_berhasil))
        if self.alat_gagal:
            tabel.add_row("[red]Failed[/red]", str(len(self.alat_gagal)), ", ".join(self.alat_gagal))
        
        console.print(tabel)

def tampilkan_bantuan():
    """Display help information."""
    console.print(Panel(
        "[bold yellow]Cybersecurity Tools Installer[/bold yellow]\n\n"
        "[bold white]Usage:[/bold white]\n"
        "  python installer_alat.py [options] [tool_name1] [tool_name2] ...\n\n"
        "[bold white]Options:[/bold white]\n"
        "  [cyan]No arguments[/cyan]: Install all tools\n"
        "  [cyan]With tool names[/cyan]: Install specific tools\n"
        "  [cyan]-h/--help[/cyan]: Show this help page\n\n"
        "[bold white]Examples:[/bold white]\n"
        "  python installer_alat.py                 # Install all tools\n"
        "  python installer_alat.py amass subfinder # Install amass and subfinder\n"
        "  python installer_alat.py --help          # Show help",
        title="[bold green]Help[/bold green]",
        border_style="blue"
    ))

def main():
    """Main function."""
    daftar_alat = {
        "Amass": "go install -v github.com/owasp-amass/amass/v4/...@master",
        "Anew": "go install -v github.com/tomnomnom/anew@latest",
        "Anti-burl": "go get -u github.com/raverrr/dantiburl",
        "Assetfinder": "go install -v github.com/tomnomnom/assetfinder@latest",
        "Asnmap": "go install github.com/projectdiscovery/asnmap/cmd/asnmap@latest",
        "Airixss": "git clone https://github.com/ferreiraklet/airixss.git && cd airixss && go mod init github.com/ferreiraklet/airixss && go build && cp airixss ~/go/bin/",
#        "Axiom": "git clone https://github.com/pry0cc/axiom.git && cd axiom && chmod +x ./setup.sh && ./setup.sh",
        "Bhedak": "pip3 install bhedak",
        "CF-check": "git clone https://github.com/dwisiswant0/cf-check.git && cd cf-check && go mod init cf-check && go build && cp cf-check ~/go/bin/",
        "Chaos": "go install -v github.com/projectdiscovery/chaos-client/cmd/chaos@latest",
        "Cariddi": "git clone https://github.com/edoardottt/cariddi.git && cd cariddi && go mod init github.com/edoardottt/cariddi && go mod tidy && make build && cp cariddi ~/go/bin/",
        "Dalfox": "go install -v github.com/hahwul/dalfox/v2@latest",
        "Dnsbrute": "pip install git+https://github.com/RevoltSecurities/Dnsbruter",
        "DNSgen": "pip install dnsgen",
        "Filter-resolved": "git clone https://github.com/tomnomnom/hacks.git && cp hacks/filter-resolved/filter-resolved ~/go/bin/",
        "Findomain": "wget https://github.com/Edu4rdSHL/findomain/releases/latest/download/findomain-linux.zip && unzip findomain-linux.zip && chmod +x findomain && cp findomain ~/go/bin/",
        "Fuff": "go install -v github.com/ffuf/ffuf@latest",
        "Freq": "git clone https://github.com/takshal/freq.git && cd freq && pip install .",
        "Gargs": "go install -v github.com/brentp/gargs@latest",
        "Gau": "go install -v github.com/lc/gau@latest",
        "Ghauri": "git clone https://github.com/r0oth3x49/ghauri.git && cd ghauri && python3 -m pip install --upgrade -r requirements.txt && python3 -m pip install -e .",
        "Gf": "go install -v github.com/tomnomnom/gf@latest",  # Handled specially
        "Gxss": "go install github.com/KathanP19/Gxss@latest",
        "Github-Search": "git clone https://github.com/gwen001/github-search.git && cd github-search && pip install -r requirements3.txt",
        "Gospider": "go install -v github.com/jaeles-project/gospider@latest",
        "Gobuster": "go install github.com/OJ/gobuster/v3@latest",
        "Gowitness": "go install -v github.com/sensepost/gowitness@latest",
        "Goop": "go install -v github.com/deletescape/goop@latest",
        "GetJS": "go install -v github.com/003random/getJS/v2@latest",
        "Hakrawler": "go install -v github.com/hakluke/hakrawler@latest",
        "HakrevDNS": "go install -v github.com/hakluke/hakrevdns@latest",
        "Haktldextract": "go install -v github.com/hakluke/haktldextract@latest",
        "Haklistgen": "go install -v github.com/hakluke/haklistgen@latest",
        "Hudson Rock Free Cybercrime Intelligence Toolset": "open https://www.hudsonrock.com/threat-intelligence-cybercrime-tools",
        "Html-tool": "git clone https://github.com/tomnomnom/hacks.git && cp hacks/html-tool/html-tool ~/go/bin/",
        "Httpx": "go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest",
        "Jaeles": "go install -v github.com/jaeles-project/jaeles@latest",
        "Jsubfinder": "git clone https://github.com/ThreatUnkown/jsubfinder.git && cd jsubfinder && go mod init github.com/ThreatUnkown/jsubfinder && go build && cp jsubfinder ~/go/bin/",
        "Kxss": "go install -v github.com/Emoe/kxss@latest",
        "Katana": "go install -v github.com/projectdiscovery/katana/cmd/katana@latest",
        "Knoxss": "open https://knoxss.me/",
        "LinkFinder": "git clone https://github.com/GerbenJavado/LinkFinder.git && cd LinkFinder && pip install -r requirements.txt && python3 setup.py install",
        "log4j-scan": "git clone https://github.com/fullhunt/log4j-scan.git && cd log4j-scan && pip install -r requirements.txt",
        "Metabigor": "go install -v github.com/j3ssie/metabigor@latest",
        "MassDNS": "git clone https://github.com/blechschmidt/massdns.git && cd massdns && make && cp bin/massdns ~/go/bin/",
        "Naabu": "go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest",
        "Notify": "go install -v github.com/projectdiscovery/notify/cmd/notify@latest",
        "Paramspider": "git clone https://github.com/devanshbatham/ParamSpider.git && cd ParamSpider && pip install .",
        "Qsreplace": "go install -v github.com/tomnomnom/qsreplace@latest",
        "Rush": "go install -v github.com/shenwei356/rush@latest",
        "SecretFinder": "git clone https://github.com/m4ll0k/SecretFinder.git && cd SecretFinder && pip install -r requirements.txt",
        "Shodan": "pip install shodan",
        "Subprober": "pip install git+https://github.com/RevoltSecurities/Subprober",
        "ShuffleDNS": "go install -v github.com/projectdiscovery/shuffledns/cmd/shuffledns@latest",
        "SQLMap": "git clone --depth 1 https://github.com/sqlmapproject/sqlmap.git sqlmap-dev && cd sqlmap-dev && ln -sf $(pwd)/sqlmap.py ~/go/bin/sqlmap",
        "Subfinder": "go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest",
        "Subdominator": "pip install git+https://github.com/RevoltSecurities/Subdominator",
        "SubJS": "go install -v github.com/lc/subjs@latest",
        "Uncover": "go install -v github.com/projectdiscovery/uncover/cmd/uncover@latest",
        "Unew": "git clone https://github.com/dwisiswant0/unew.git && cd unew && go mod init github.com/dwisiswant0/unew && go mod tidy && go build && cp unew ~/go/bin/",
        "Unfurl": "go install -v github.com/tomnomnom/unfurl@latest",
        "Urlfinder": "go install -v github.com/projectdiscovery/urlfinder/cmd/urlfinder@latest",
        "Urldedupe": "git clone https://github.com/ameenmaali/urldedupe.git && cd urldedupe && go mod init github.com/ameenmaali/urldedupe && go mod tidy && go build && cp urldedupe ~/go/bin/",
        "WaybackURLs": "go install -v github.com/tomnomnom/waybackurls@latest",
        "Wingman": "open https://xsswingman.com/#faq",
        "Tojson": "git clone https://github.com/tomnomnom/hacks.git && cp hacks/tojson/tojson ~/go/bin/",
        "X8": "git clone https://github.com/Sh1Yo/x8.git && cd x8 && go mod init github.com/Sh1Yo/x8 && go mod tidy && go build && cp x8 ~/go/bin/",
        "xray": "git clone https://github.com/chaitin/xray.git && cd xray && go mod init github.com/chaitin/xray && go mod tidy && go build && cp xray ~/go/bin/",
        "XSStrike": "git clone https://github.com/s0md3v/XSStrike.git && cd XSStrike && pip install -r requirements.txt",
        "Page-fetch": "go install -v github.com/detectify/page-fetch@latest",
        "HEDnsExtractor": "go install -v github.com/HuntDownProject/hednsextractor/cmd/hednsextractor@latest",
        "PIP package": "pip install -U sublist3r uro arjun colorama aiodns aiohttp selenium aiofiles aiolimiter alive_progress ratelimit pipx structlog requests uvloop setuptools asynciolimiter aiojarm tldextract playwright",
    }

    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        tampilkan_bantuan()
        return

    installer = InstallerAlatKeamanan(daftar_alat)
    
    try:
        if len(sys.argv) > 1:
            alat_terpilih = sys.argv[1:]
            console.print(f"[bold blue]Installing selected tools: {', '.join(alat_terpilih)}[/bold blue]")
            installer.install_alat(alat_terpilih)
        else:
            console.print("[bold blue]Installing all tools[/bold blue]")
            installer.install_alat()
    except KeyboardInterrupt:
        console.print("\n[bold red]Installation aborted by user[/bold red]")
        # Clean up temporary directory
        try:
            shutil.rmtree(installer.tmp_dir)
        except Exception as e:
            console.print(f"[yellow]Warning: Failed to clean up temporary directory: {str(e)}[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(
            Panel.fit(
                f"An unexpected error occurred:\n{str(e)}",
                title="[bold red]Error[/bold red]",
                border_style="red"
            )
        )
        logging.error(f"Unexpected error: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    console.print(
        Panel.fit(
            "[bold cyan]Cybersecurity Tools Installer[/bold cyan]\n"
            "Created by betmen0x0 | Improved by Claude",
            title="[bold blue]Welcome[/bold blue]",
            border_style="blue"
        )
    )
    main()
