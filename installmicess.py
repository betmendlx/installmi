#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil
import platform
from typing import Dict, List
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.panel import Panel
from rich.table import Table

console = Console()

class InstallerAlatKeamanan:
    def __init__(self, daftar_alat: Dict[str, str]):
        """
        Inisialisasi Installer Tools nya cuy.
        
        :param daftar_alat: Kamus dengan nama alat sebagai kunci dan perintah instalasi sebagai nilai
        """
        self.daftar_alat = daftar_alat
        self.alat_berhasil: List[str] = []
        self.alat_gagal: List[str] = []
        self.jenis_os = self._deteksi_os()

    def _deteksi_os(self) -> str:
        """
        Mendeteksi jenis sistem operasi.
        
        :return: Jenis sistem operasi (linux, darwin, windows)
        """
        nama_os = platform.system().lower()
        console.print(f"[bold blue][INFO][/bold blue] Sistem Operasi Terdeteksi: {nama_os}")
        return nama_os

    def periksa_dependensi(self) -> bool:
        """
        Memeriksa apakah dependensi yang diperlukan telah terpasang.
        
        :return: Boolean yang menunjukkan keberadaan semua dependensi
        """
        dependensi = ["git", "go", "pip"]
        tidak_tersedia = []
        
        for dep in dependensi:
            if not shutil.which(dep):
                tidak_tersedia.append(dep)
        
        if tidak_tersedia:
            console.print(
                Panel.fit(
                    f"Dependensi tidak tersedia: {', '.join(tidak_tersedia)}",
                    title="[bold red]Kesalahan Dependensi[/bold red]",
                    border_style="red"
                )
            )
            return False
        return True

    def jalankan_perintah(self, perintah: str, alat: str) -> bool:
        """
        Menjalankan perintah shell untuk instalasi alat.
        
        :param perintah: Perintah instalasi untuk dijalankan
        :param alat: Nama alat yang sedang dipasang
        :return: Boolean yang menunjukkan keberhasilan atau kegagalan
        """
        try:
            # Tangani kasus khusus seperti perintah 'open' atau tautan web
            if perintah.startswith('open '):
                console.print(f"[yellow][MANUAL][/yellow] Silakan kunjungi: {perintah.split('open ')[1]}")
                return True
            
            result = subprocess.run(
                perintah, 
                shell=True, 
                check=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True
            )
            console.print(f"[green]✓[/green] {alat} berhasil dipasang")
            return True
        except subprocess.CalledProcessError as e:
            console.print(
                Panel.fit(
                    f"Instalasi gagal untuk {alat}\n"
                    f"Perintah: {perintah}\n"
                    f"Kesalahan: {e.stderr}",
                    title="[bold red]Kesalahan Instalasi[/bold red]",
                    border_style="red"
                )
            )
            return False

    def install_alat(self, alat_terpilih: List[str] = None) -> None:
        """
        Memasang alat yang dipilih atau semua alat jika tidak ada yang dispesifikasi.
        
        :param alat_terpilih: Daftar opsional alat spesifik untuk dipasang
        """
        if not self.periksa_dependensi():
            console.print("[bold red]Selesaikan dependensi sebelum melanjutkan.[/bold red]")
            return

        # Gunakan semua alat jika tidak ada pilihan
        alat_untuk_dipasang = alat_terpilih or list(self.daftar_alat.keys())
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("{task.completed}/{task.total} [bold green]alat[/bold green] dipasang"),
            console=console,
        ) as progress:
            task = progress.add_task("Memasang alat", total=len(alat_untuk_dipasang))

            for alat in alat_untuk_dipasang:
                if alat not in self.daftar_alat:
                    console.print(f"[yellow]Peringatan: Alat {alat} tidak ditemukan dalam daftar.[/yellow]")
                    progress.update(task, advance=1)
                    continue

                console.print(f"[bold cyan][INFO][/bold cyan] Memasang {alat}...")
                berhasil = self.jalankan_perintah(self.daftar_alat[alat], alat)
                
                if berhasil:
                    self.alat_berhasil.append(alat)
                else:
                    self.alat_gagal.append(alat)
                
                progress.update(task, advance=1)

        self._cetak_ringkasan()

    def _cetak_ringkasan(self) -> None:
        """
        Mencetak ringkasan hasil instalasi alat.
        """
        tabel = Table(title="Ringkasan Instalasi Alat")
        tabel.add_column("Status", style="cyan")
        tabel.add_column("Alat", style="magenta")
        
        if self.alat_berhasil:
            tabel.add_row("[green]Terpasang[/green]", ", ".join(self.alat_berhasil))
        if self.alat_gagal:
            tabel.add_row("[red]Gagal[/red]", ", ".join(self.alat_gagal))
        
        console.print(tabel)

def tampilkan_bantuan():
    """
    Menampilkan informasi bantuan penggunaan skrip.
    """
    console.print(Panel(
        "[bold yellow]Installer Alat Keamanan Siber[/bold yellow]\n\n"
        "[bold white]Penggunaan:[/bold white]\n"
        "  python installer_alat.py [pilihan] [nama_alat1] [nama_alat2] ...\n\n"
        "[bold white]Pilihan:[/bold white]\n"
        "  [cyan]Tanpa argumen[/cyan]: Memasang semua alat\n"
        "  [cyan]Dengan nama alat[/cyan]: Memasang alat spesifik\n"
        "  [cyan]--help[/cyan]: Menampilkan halaman bantuan ini\n\n"
        "[bold white]Contoh:[/bold white]\n"
        "  python installer_alat.py                 # Pasang semua alat\n"
        "  python installer_alat.py Amass Subfinder # Pasang Amass dan Subfinder\n"
        "  python installer_alat.py --help          # Tampilkan bantuan",
        title="[bold green]Bantuan[/bold green]",
        border_style="blue"
    ))

def main():
    """
    Titik masuk utama untuk installer alat.
    """
    # Daftar alat (contoh singkat, tambahkan daftar lengkap)
    daftar_alat = {
    	"Amass": "go install github.com/OWASP/Amass/v3/...@latest",
    	"Anew": "go install github.com/tomnomnom/anew@latest",
    	"Anti-burl": "git clone https://github.com/tomnomnom/hacks.git && cp hacks/anti-burl ~/go/bin/",
   	"Assetfinder": "go install github.com/tomnomnom/assetfinder@latest",
   	"Airixss": "git clone https://github.com/ferreiraklet/airixss.git && cd airixss && go build && mv airixss /usr/local/bin/",
    "Axiom": "git clone https://github.com/pry0cc/axiom.git && cd axiom && ./setup.sh",
    "Bhedak": "git clone https://github.com/R0X4R/bhedak.git && cd bhedak && pip install -r requirements.txt",
    "CF-check": "git clone https://github.com/dwisiswant0/cf-check.git && cd cf-check && go build && mv cf-check /usr/local/bin/",
    "Chaos": "go install github.com/projectdiscovery/chaos-client/cmd/chaos@latest",
    "Cariddi": "git clone https://github.com/edoardottt/cariddi.git && cd cariddi && make build && mv cariddi /usr/local/bin/",
    "Dalfox": "go install github.com/hahwul/dalfox/v2@latest",
    "DNSgen": "pip install dnsgen",
    "Filter-resolved": "git clone https://github.com/tomnomnom/hacks.git && cp hacks/filter-resolved ~/go/bin/",
    "Findomain": "wget https://github.com/Edu4rdSHL/findomain/releases/latest/download/findomain-linux.zip && unzip findomain-linux.zip && chmod +x findomain && mv findomain /usr/local/bin/",
    "Fuff": "go install github.com/ffuf/ffuf@latest",
    "Freq": "git clone https://github.com/takshal/freq.git && cd freq && pip install .",
    "Gargs": "go install github.com/brentp/gargs@latest",
    "Gau": "go install github.com/lc/gau/v2/cmd/gau@latest",
    "Gf": "go install github.com/tomnomnom/gf@latest && cp -r $(go env GOPATH)/src/github.com/tomnomnom/gf/examples ~/.gf",
    "Github-Search": "git clone https://github.com/gwen001/github-search.git && cd github-search && pip install -r requirements.txt",
    "Gospider": "go install github.com/jaeles-project/gospider@latest",
    "Gowitness": "go install github.com/sensepost/gowitness@latest",
    "Goop": "go install github.com/deletescape/goop@latest",
    "GetJS": "git clone https://github.com/003random/getJS.git && cd getJS && pip install -r requirements.txt",
    "Hakrawler": "go install github.com/hakluke/hakrawler@latest",
    "HakrevDNS": "go install github.com/hakluke/hakrevdns@latest",
    "Haktldextract": "go install github.com/hakluke/haktldextract@latest",
    "Haklistgen": "go install github.com/hakluke/haklistgen@latest",
    "Hudson Rock Free Cybercrime Intelligence Toolset": "open https://www.hudsonrock.com/threat-intelligence-cybercrime-tools",
    "Html-tool": "git clone https://github.com/tomnomnom/hacks.git && cp hacks/html-tool ~/go/bin/",
    "Httpx": "go install github.com/projectdiscovery/httpx/cmd/httpx@latest",
    "Jaeles": "go install github.com/jaeles-project/jaeles@latest",
    "Jsubfinder": "git clone https://github.com/ThreatUnkown/jsubfinder.git && cd jsubfinder && go build && mv jsubfinder /usr/local/bin/",
    "Kxss": "go install github.com/Emoe/kxss@latest",
    "Knoxss": "open https://knoxss.me/",
    "Katana": "go install github.com/projectdiscovery/katana/cmd/katana@latest",
    "LinkFinder": "git clone https://github.com/GerbenJavado/LinkFinder.git && cd LinkFinder && pip install -r requirements.txt",
    "log4j-scan": "git clone https://github.com/fullhunt/log4j-scan.git && cd log4j-scan && pip install -r requirements.txt",
    "Metabigor": "git clone https://github.com/j3ssie/metabigor.git && cd metabigor && pip install -r requirements.txt",
    "MassDNS": "git clone https://github.com/blechschmidt/massdns.git && cd massdns && make",
    "Naabu": "go install github.com/projectdiscovery/naabu/v2/cmd/naabu@latest",
    "Notify": "go install github.com/projectdiscovery/notify/cmd/notify@latest",
    "Paramspider": "git clone https://github.com/devanshbatham/ParamSpider.git && cd ParamSpider && pip install -r requirements.txt",
    "Qsreplace": "go install github.com/tomnomnom/qsreplace@latest",
    "Rush": "go install github.com/shenwei356/rush@latest",
    "SecretFinder": "git clone https://github.com/m4ll0k/SecretFinder.git && cd SecretFinder && pip install -r requirements.txt",
    "Shodan": "pip install shodan",
    "ShuffleDNS": "go install github.com/projectdiscovery/shuffledns/cmd/shuffledns@latest",
    "SQLMap": "git clone --depth 1 https://github.com/sqlmapproject/sqlmap.git sqlmap-dev",
    "Subfinder": "go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest",
    "SubJS": "go install github.com/lc/subjs@latest",
    "Unew": "git clone https://github.com/dwisiswant0/unew.git && cd unew && go build",
    "Unfurl": "go install github.com/tomnomnom/unfurl@latest",
    "Urldedupe": "git clone https://github.com/ameenmaali/urldedupe.git && cd urldedupe && go build",
    "WaybackURLs": "go install github.com/tomnomnom/waybackurls@latest",
    "Wingman": "open https://xsswingman.com/#faq",
    "Tojson": "git clone https://github.com/tomnomnom/hacks.git && cp hacks/tojson ~/go/bin/",
    "X8": "git clone https://github.com/Sh1Yo/x8.git && cd x8 && go build",
    "xray": "git clone https://github.com/chaitin/xray.git && cd xray && go build",
    "XSStrike": "git clone https://github.com/s0md3v/XSStrike.git && cd XSStrike && pip install -r requirements.txt",
    "Page-fetch": "git clone https://github.com/detectify/page-fetch.git && cd page-fetch && pip install -r requirements.txt",
    "HEDnsExtractor": "git clone https://github.com/HuntDownProject/HEDnsExtractor.git && cd HEDnsExtractor && pip install -r requirements.txt",
    }

    # Periksa argumen bantuan
    if len(sys.argv) > 1 and (sys.argv[1] in ['-h', '--help']):
        tampilkan_bantuan()
        return

    installer = InstallerAlatKeamanan(daftar_alat)

    # Pilih alat untuk dipasang berdasarkan argumen
    if len(sys.argv) > 1:
        alat_terpilih = sys.argv[1:]
        console.print(f"[bold blue]Memasang alat terpilih: {', '.join(alat_terpilih)}[/bold blue]")
        installer.install_alat(alat_terpilih)
    else:
        console.print("[bold blue]Memasang semua alat[/bold blue]")
        installer.install_alat()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Instalasi dihentikan oleh pengguna.[/bold yellow]")
    except Exception as e:
        console.print(
            Panel.fit(
                f"Terjadi kesalahan yang tidak terduga: {e}",
                title="[bold red]Kesalahan Fatal[/bold red]",
                border_style="red"
            )
        )
