#!/usr/bin/env python3
# made for you gaess yang gak suka ribet" ;)
# betmen0x0
import os
import sys
import subprocess
import shutil
import platform
from typing import Dict, List
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.panel import Panel
from rich.table import Table

console = Console()

class InstallerAlatKeamanan:
    def __init__(self, daftar_alat: Dict[str, str]):
        self.daftar_alat = daftar_alat
        # Create a lowercase version of tool names for case-insensitive matching
        self.daftar_alat_lowercase = {k.lower(): k for k in daftar_alat.keys()}
        self.alat_berhasil: List[str] = []
        self.alat_gagal: List[str] = []
        self.jenis_os = self._deteksi_os()
        self.go_path = self._setup_go_path()
        self.hacks_cloned = False  # Untuk melacak apakah repositori hacks sudah di-clone

    def _deteksi_os(self) -> str:
        nama_os = platform.system().lower()
        console.print(f"[bold blue][INFO][/bold blue] Sistem Operasi Terdeteksi: {nama_os}")
        return nama_os

    def _setup_go_path(self) -> str:
        go_path = os.environ.get('GOPATH', str(Path.home() / 'go'))
        bin_path = os.path.join(go_path, 'bin')
        os.makedirs(bin_path, exist_ok=True)
        
        # OS-specific PATH separator
        path_separator = ';' if self.jenis_os == 'windows' else ':'
        os.environ['PATH'] = f"{bin_path}{path_separator}{os.environ.get('PATH', '')}"
        
        return go_path

    def _check_installed(self, tool: str) -> bool:
        return bool(shutil.which(tool.lower()) or shutil.which(tool))

    def periksa_dependensi(self) -> bool:
        dependensi = ["git", "go", "pip"]
        tidak_tersedia = []
        
        for dep in dependensi:
            if not shutil.which(dep):
                tidak_tersedia.append(dep)
        
        if tidak_tersedia:
            console.print(
                Panel.fit(
                    f"Dependensi tidak tersedia: {', '.join(tidak_tersedia)}\n"
                    f"Instal dependensi dengan:\n"
                    f"- Linux: sudo apt install {' '.join(tidak_tersedia)} libpcap-dev\n"
                    f"- MacOS: brew install {' '.join(tidak_tersedia)} libpcap\n"
                    f"- Windows: Gunakan Chocolatey atau instalasi manual",
                    title="[bold red]Kesalahan Dependensi[/bold red]",
                    border_style="red"
                )
            )
            return False
        return True

    def jalankan_perintah(self, perintah: str, alat: str) -> bool:
        try:
            if self._check_installed(alat):
                console.print(f"[yellow][SKIP][/yellow] {alat} sudah terinstall")
                return True

            # Handle URLs directly
            if perintah.startswith('open '):
                console.print(f"[yellow][MANUAL][/yellow] Silakan kunjungi: {perintah.split('open ')[1]}")
                return True

            commands = perintah.split('&&')
            current_dir = os.getcwd()

            for cmd in commands:
                cmd = cmd.strip()
                if not cmd:
                    continue

                # Tangani cloning repositori hacks sekali saja
                if 'git clone https://github.com/tomnomnom/hacks.git' in cmd and not self.hacks_cloned:
                    if os.path.exists('hacks'):
                        try:
                            shutil.rmtree('hacks')
                        except PermissionError:
                            console.print(f"[yellow][WARNING][/yellow] Tidak dapat menghapus direktori hacks yang ada. Pastikan tidak sedang digunakan.")
                    subprocess.run('git clone https://github.com/tomnomnom/hacks.git', shell=True, check=True)
                    self.hacks_cloned = True
                    continue
                elif 'git clone https://github.com/tomnomnom/hacks.git' in cmd:
                    # Skip if already cloned
                    continue

                # Tambahan untuk Go module
                if 'go build' in cmd and alat in ['Cariddi', 'Unew', 'Urldedupe', 'x8', 'xray', 'CF-check', 'Jsubfinder']:
                    try:
                        module_dir = cmd.split('cd ')[-1].split(' &&')[0].strip() if 'cd ' in cmd else '.'
                        init_cmd = f"cd {module_dir} && go mod init {alat.lower()} && go mod tidy"
                        subprocess.run(init_cmd, shell=True, check=True)
                    except subprocess.CalledProcessError:
                        console.print(f"[yellow][WARNING][/yellow] Gagal inisialisasi Go module untuk {alat}, mencoba melanjutkan...")

                # Tangani GF secara khusus
                if alat == 'Gf':
                    try:
                        # Remove existing installation if needed
                        if os.path.exists('gf'):
                            shutil.rmtree('gf')
                        
                        subprocess.run('git clone https://github.com/tomnomnom/gf.git', shell=True, check=True)
                        subprocess.run(f'cd gf && go build && cp gf {os.path.join(self.go_path, "bin")}', shell=True, check=True)
                        
                        # Create ~/.gf directory if it doesn't exist
                        gf_dir = os.path.expanduser('~/.gf')
                        os.makedirs(gf_dir, exist_ok=True)
                        
                        # Copy pattern files
                        subprocess.run(f'cp -r gf/examples/* {gf_dir}/', shell=True, check=True)
                        console.print(f"[green]✓[/green] {alat} berhasil dipasang")
                        return True
                    except Exception as e:
                        console.print(f"[red]Error saat menginstal Gf: {str(e)}[/red]")
                        return False

                # Pengecekan file requirements.txt sebelum pip install
                if 'pip install -r requirements.txt' in cmd:
                    try:
                        # Extract directory from command
                        req_dir = cmd.split('cd ')[-1].split(' &&')[0].strip() if 'cd ' in cmd else '.'
                        req_path = os.path.join(req_dir, 'requirements.txt')
                        
                        if not os.path.exists(req_path):
                            console.print(f"[yellow]Peringatan: File requirements.txt tidak ditemukan di {req_path} untuk {alat}, melewati langkah ini.[/yellow]")
                            continue
                    except Exception:
                        console.print(f"[yellow]Peringatan: Gagal memeriksa file requirements.txt untuk {alat}.[/yellow]")

                with console.status(f"[bold cyan]Menginstall {alat}..."):
                    try:
                        result = subprocess.run(
                            cmd,
                            shell=True,
                            check=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True
                        )
                    except subprocess.CalledProcessError as e:
                        console.print(f"[red]Error saat menjalankan: {cmd}\nDetail: {e.stderr or e.stdout or str(e)}[/red]")
                        if 'permission denied' in str(e.stderr).lower():
                            console.print("[yellow]Hint: Coba jalankan dengan sudo atau dengan hak administrator[/yellow]")
                        raise

            try:
                os.chdir(current_dir)
            except Exception as e:
                console.print(f"[yellow]Peringatan: Gagal kembali ke direktori awal: {str(e)}[/yellow]")
                
            console.print(f"[green]✓[/green] {alat} berhasil dipasang")
            return True
        except subprocess.CalledProcessError as e:
            console.print(
                Panel.fit(
                    f"Instalasi gagal untuk {alat}\n"
                    f"Perintah: {perintah}\n"
                    f"Kesalahan: {e.stderr[-1000:] if hasattr(e, 'stderr') and e.stderr else str(e)}",
                    title="[bold red]Kesalahan Instalasi[/bold red]",
                    border_style="red"
                )
            )
            return False
        except Exception as e:
            console.print(f"[red]Error tidak terduga pada {alat}: {str(e)}[/red]")
            return False

    def install_alat(self, alat_terpilih: List[str] = None) -> None:
        if not self.periksa_dependensi():
            console.print("[bold red]Selesaikan dependensi sebelum melanjutkan.[/bold red]")
            return

        if alat_terpilih:
            # Process lowercase tool names and map to original case
            normalized_tools = []
            for tool_name in alat_terpilih:
                lower_name = tool_name.lower()
                if lower_name in self.daftar_alat_lowercase:
                    # Get original case version
                    normalized_tools.append(self.daftar_alat_lowercase[lower_name])
                else:
                    console.print(f"[yellow]Peringatan: Alat '{tool_name}' tidak ditemukan dalam daftar.[/yellow]")
            
            alat_untuk_dipasang = normalized_tools
        else:
            alat_untuk_dipasang = list(self.daftar_alat.keys())
        
        if not alat_untuk_dipasang:
            console.print("[bold red]Tidak ada alat valid untuk diinstal.[/bold red]")
            return
            
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("{task.completed}/{task.total} [bold green]alat[/bold green] dipasang"),
            console=console,
        ) as progress:
            task = progress.add_task("Memasang alat", total=len(alat_untuk_dipasang))

            for alat in alat_untuk_dipasang:
                console.print(f"[bold cyan][INFO][/bold cyan] Memulai instalasi {alat}")
                berhasil = self.jalankan_perintah(self.daftar_alat[alat], alat)
                
                if berhasil:
                    self.alat_berhasil.append(alat)
                else:
                    self.alat_gagal.append(alat)
                
                progress.update(task, advance=1)

        self._cetak_ringkasan()

    def _cetak_ringkasan(self) -> None:
        tabel = Table(title="Ringkasan Instalasi Alat")
        tabel.add_column("Status", style="cyan")
        tabel.add_column("Jumlah", style="yellow")
        tabel.add_column("Alat", style="magenta")
        
        if self.alat_berhasil:
            tabel.add_row("[green]Terpasang[/green]", str(len(self.alat_berhasil)), ", ".join(self.alat_berhasil))
        if self.alat_gagal:
            tabel.add_row("[red]Gagal[/red]", str(len(self.alat_gagal)), ", ".join(self.alat_gagal))
        
        console.print(tabel)

def tampilkan_bantuan():
    console.print(Panel(
        "[bold yellow]Installer Alat Keamanan Siber[/bold yellow]\n\n"
        "[bold white]Penggunaan:[/bold white]\n"
        "  python installer_alat.py [pilihan] [nama_alat1] [nama_alat2] ...\n\n"
        "[bold white]Pilihan:[/bold white]\n"
        "  [cyan]Tanpa argumen[/cyan]: Memasang semua alat\n"
        "  [cyan]Dengan nama alat[/cyan]: Memasang alat spesifik\n"
        "  [cyan]-h/--help[/cyan]: Menampilkan halaman bantuan ini\n"
        "  [cyan]-u/--update[/cyan]: Memperbarui alat yang sudah terinstal\n"
        "  [cyan]-l/--list[/cyan]: Menampilkan daftar semua alat yang tersedia\n\n"
        "[bold white]Contoh:[/bold white]\n"
        "  python installer_alat.py                 # Pasang semua alat\n"
        "  python installer_alat.py amass subfinder # Pasang amass dan subfinder\n"
        "  python installer_alat.py --help          # Tampilkan bantuan\n"
        "  python installer_alat.py --list          # Tampilkan daftar alat\n"
        "  python installer_alat.py --update        # Perbarui alat terinstal",
        title="[bold green]Bantuan[/bold green]",
        border_style="blue"
    ))

def tampilkan_daftar_alat(daftar_alat):
    tabel = Table(title="Daftar Alat Tersedia")
    tabel.add_column("Nama Alat", style="cyan")
    
    for alat in sorted(daftar_alat.keys()):
        tabel.add_row(alat)
    
    console.print(tabel)

def main():
    daftar_alat = {
        "Amass": "go install -v github.com/OWASP/Amass/v3/...@latest",
        "Anew": "go install -v github.com/tomnomnom/anew@latest",
        "Anti-burl": "git clone https://github.com/tomnomnom/hacks.git && mkdir -p ~/go/bin/ && cp hacks/anti-burl/anti-burl ~/go/bin/",
        "Assetfinder": "go install -v github.com/tomnomnom/assetfinder@latest",
        "Asnmap":"go install github.com/projectdiscovery/asnmap/cmd/asnmap@latest",
        "Airixss": "git clone https://github.com/ferreiraklet/airixss.git && cd airixss && go mod init github.com/ferreiraklet/airixss && go build && sudo mv airixss /usr/local/bin/",
        "Axiom": "git clone https://github.com/pry0cc/axiom.git && cd axiom && chmod +x setup.sh && ./setup.sh",
        "Bhedak": "git clone https://github.com/R0X4R/bhedak.git && cd bhedak && pip install .",
        "CF-check": "git clone https://github.com/dwisiswant0/cf-check.git && cd cf-check && go mod init cf-check && go build && sudo mv cf-check /usr/local/bin/",
        "Chaos": "go install -v github.com/projectdiscovery/chaos-client/cmd/chaos@latest",
        "Cariddi": "git clone https://github.com/edoardottt/cariddi.git && cd cariddi && go mod init cariddi && make build && sudo mv cariddi /usr/local/bin/",
        "Dalfox": "go install -v github.com/hahwul/dalfox/v2@latest",
        "Dnsbrute": "pip install git+https://github.com/RevoltSecurities/Dnsbruter",
        "DNSgen": "pip install dnsgen",
        "Filter-resolved": "git clone https://github.com/tomnomnom/hacks.git && cp hacks/filter-resolved/filter-resolved ~/go/bin/",
        "Findomain": "wget https://github.com/Edu4rdSHL/findomain/releases/latest/download/findomain-linux.zip && unzip findomain-linux.zip && chmod +x findomain && sudo mv findomain /usr/local/bin/",
        "Fuff": "go install -v github.com/ffuf/ffuf@latest",
        "Freq": "git clone https://github.com/takshal/freq.git && cd freq && pip install .",
        "Gargs": "go install -v github.com/brentp/gargs@latest",
        "Gau": "go install -v github.com/lc/gau@latest",
        "Gf": "go install -v github.com/tomnomnom/gf@latest",  # Ditangani khusus
        "Gxss": "go install github.com/KathanP19/Gxss@latest",
        "Github-Search": "git clone https://github.com/gwen001/github-search.git && cd github-search && pip install -r requirements3.txt",
        "Gospider": "go install -v github.com/jaeles-project/gospider@latest",
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
        "Jsubfinder": "git clone https://github.com/ThreatUnkown/jsubfinder.git && cd jsubfinder && go mod init jsubfinder && go build && sudo mv jsubfinder /usr/local/bin/",
        "Kxss": "go install -v github.com/Emoe/kxss@latest",
        "Katana":"CGO_ENABLED=1 go install github.com/projectdiscovery/katana/cmd/katana@latest",
        "Knoxss": "open https://knoxss.me/",
        "Katana": "go install -v github.com/projectdiscovery/katana/cmd/katana@latest",
        "LinkFinder": "git clone https://github.com/GerbenJavado/LinkFinder.git && cd LinkFinder && pip install -r requirements.txt && python3 setup.py install",
        "log4j-scan": "git clone https://github.com/fullhunt/log4j-scan.git && cd log4j-scan && pip install -r requirements.txt",
        "Metabigor": "git clone https://github.com/j3ssie/metabigor.git && cd metabigor && go install .",
        "MassDNS": "git clone https://github.com/blechschmidt/massdns.git && cd massdns && make -j$(nproc) && sudo cp bin/massdns /usr/local/bin/",
        "Naabu": "go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest",
        "Notify": "go install -v github.com/projectdiscovery/notify/cmd/notify@latest",
        "Paramspider": "git clone https://github.com/devanshbatham/ParamSpider.git && cd ParamSpider && pip install .",
        "Qsreplace": "go install -v github.com/tomnomnom/qsreplace@latest",
        "Rush": "go install -v github.com/shenwei356/rush@latest",
        "SecretFinder": "git clone https://github.com/m4ll0k/SecretFinder.git && cd SecretFinder && pip install -r requirements.txt",
        "Shodan": "pip install shodan",
        "Subprober": "pip install git+https://github.com/RevoltSecurities/Subprober",
        "ShuffleDNS": "go install -v github.com/projectdiscovery/shuffledns/cmd/shuffledns@latest",
        "SQLMap": "git clone --depth 1 https://github.com/sqlmapproject/sqlmap.git sqlmap-dev",
        "Subfinder": "go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest",
        "Subdominator": "pip install git+https://github.com/RevoltSecurities/Subdominator",
        "SubJS": "go install -v github.com/lc/subjs@latest",
        "Uncover":"go install -v github.com/projectdiscovery/uncover/cmd/uncover@latest",
        "Unew": "git clone https://github.com/dwisiswant0/unew.git && cd unew && go mod init unew && go build && sudo mv unew /usr/local/bin/",
        "Unfurl": "go install -v github.com/tomnomnom/unfurl@latest",
        "Urlfinder": "go install -v github.com/projectdiscovery/urlfinder/cmd/urlfinder@latest",
        "Urldedupe": "git clone https://github.com/ameenmaali/urldedupe.git && cd urldedupe && go mod init urldedupe && go build && sudo mv urldedupe /usr/local/bin/",
        "WaybackURLs": "go install -v github.com/tomnomnom/waybackurls@latest",
        "Wingman": "open https://xsswingman.com/#faq",
        "Tojson": "git clone https://github.com/tomnomnom/hacks.git && cp hacks/tojson/tojson ~/go/bin/",
        "X8": "git clone https://github.com/Sh1Yo/x8.git && cd x8 && go mod init x8 && go build && sudo mv x8 /usr/local/bin/",
        "xray": "git clone https://github.com/chaitin/xray.git && cd xray && go mod init xray && go build && sudo mv xray /usr/local/bin/",
        "XSStrike": "git clone https://github.com/s0md3v/XSStrike.git && cd XSStrike && pip install -r requirements.txt",
        "Page-fetch": "go install -v github.com/detectify/page-fetch@latest",
        "HEDnsExtractor": "go install -v github.com/HuntDownProject/hednsextractor/cmd/hednsextractor@latest",
        "PIP package": "pip install -U sublist3r uro arjun colorama aiodns aiohttp selenium aiofiles aiolimiter alive_progress ratelimit pipx structlog requests uvloop setuptools asynciolimiter aiojarm tldextract playwright",
    }

    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h', '--help']:
            tampilkan_bantuan()
            sys.exit(0)
        elif sys.argv[1] in ['-l', '--list']:
            tampilkan_daftar_alat(daftar_alat)
            sys.exit(0)
        elif sys.argv[1] in ['-u', '--update']:
            console.print("[bold blue]Memperbarui semua alat yang sudah terinstal...[/bold blue]")
            installer = InstallerAlatKeamanan(daftar_alat)
            installer.install_alat(list(daftar_alat.keys()))  # Instal ulang semua
            sys.exit(0)

    installer = InstallerAlatKeamanan(daftar_alat)
    
    try:
        if len(sys.argv) > 1:
            alat_terpilih = sys.argv[1:]
            console.print(f"[bold blue]Memasang alat terpilih: {', '.join(alat_terpilih)}[/bold blue]")
            installer.install_alat(alat_terpilih)
        else:
            console.print("[bold blue]Memasang semua alat[/bold blue]")
            installer.install_alat()
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Instalasi dihentikan oleh pengguna.[/bold yellow]")
        sys.exit(1)

if __name__ == "__main__":
    main()
