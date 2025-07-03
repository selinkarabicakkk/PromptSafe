"""Sistem seviyesinde proxy yapılandırması için yardımcı sınıf."""
import os
import platform
import subprocess
import logging
from typing import Optional, Dict, List, Tuple

logger = logging.getLogger(__name__)


class SystemProxy:
    """Sistem seviyesinde proxy yapılandırması için yardımcı sınıf."""
    
    def __init__(self, proxy_host: str = "localhost", proxy_port: int = 8000):
        """
        Initialize system proxy helper.
        
        Args:
            proxy_host: Proxy sunucu host adresi
            proxy_port: Proxy sunucu port numarası
        """
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.proxy_url = f"http://{proxy_host}:{proxy_port}"
        self.system = platform.system()  # Windows, Darwin (macOS), Linux
    
    def enable(self) -> bool:
        """
        Sistem proxy ayarlarını etkinleştir.
        
        Returns:
            bool: Başarılı ise True
        """
        try:
            if self.system == "Windows":
                return self._enable_windows()
            elif self.system == "Darwin":  # macOS
                return self._enable_macos()
            elif self.system == "Linux":
                return self._enable_linux()
            else:
                logger.error(f"Desteklenmeyen işletim sistemi: {self.system}")
                return False
        except Exception as e:
            logger.error(f"Proxy etkinleştirilirken hata: {str(e)}")
            return False
    
    def disable(self) -> bool:
        """
        Sistem proxy ayarlarını devre dışı bırak.
        
        Returns:
            bool: Başarılı ise True
        """
        try:
            if self.system == "Windows":
                return self._disable_windows()
            elif self.system == "Darwin":  # macOS
                return self._disable_macos()
            elif self.system == "Linux":
                return self._disable_linux()
            else:
                logger.error(f"Desteklenmeyen işletim sistemi: {self.system}")
                return False
        except Exception as e:
            logger.error(f"Proxy devre dışı bırakılırken hata: {str(e)}")
            return False
    
    def _enable_windows(self) -> bool:
        """Windows'ta proxy ayarlarını etkinleştir."""
        try:
            # Windows Registry üzerinden proxy ayarlarını güncelle
            reg_command = (
                f'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" '
                f'/v ProxyEnable /t REG_DWORD /d 1 /f'
            )
            subprocess.run(reg_command, shell=True, check=True)
            
            # Proxy sunucu adresini ayarla
            reg_command = (
                f'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" '
                f'/v ProxyServer /t REG_SZ /d "{self.proxy_host}:{self.proxy_port}" /f'
            )
            subprocess.run(reg_command, shell=True, check=True)
            
            # Bypass listesini ayarla (localhost ve 127.0.0.1 hariç)
            reg_command = (
                f'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" '
                f'/v ProxyOverride /t REG_SZ /d "localhost;127.0.0.1;*.local" /f'
            )
            subprocess.run(reg_command, shell=True, check=True)
            
            logger.info("Windows proxy ayarları etkinleştirildi")
            return True
        except Exception as e:
            logger.error(f"Windows proxy ayarları etkinleştirilirken hata: {str(e)}")
            return False
    
    def _disable_windows(self) -> bool:
        """Windows'ta proxy ayarlarını devre dışı bırak."""
        try:
            # Windows Registry üzerinden proxy'yi devre dışı bırak
            reg_command = (
                f'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" '
                f'/v ProxyEnable /t REG_DWORD /d 0 /f'
            )
            subprocess.run(reg_command, shell=True, check=True)
            
            logger.info("Windows proxy ayarları devre dışı bırakıldı")
            return True
        except Exception as e:
            logger.error(f"Windows proxy ayarları devre dışı bırakılırken hata: {str(e)}")
            return False
    
    def _enable_macos(self) -> bool:
        """macOS'ta proxy ayarlarını etkinleştir."""
        try:
            # Aktif ağ servisini bul
            result = subprocess.run(
                "networksetup -listallnetworkservices",
                shell=True, capture_output=True, text=True, check=True
            )
            
            # İlk satır açıklama olduğu için atla
            services = result.stdout.strip().split("\n")[1:]
            
            # Her bir ağ servisi için proxy ayarlarını güncelle
            for service in services:
                if service.startswith("*"):
                    continue  # Devre dışı servisler
                
                # HTTP proxy ayarla
                subprocess.run(
                    f'networksetup -setwebproxy "{service}" {self.proxy_host} {self.proxy_port}',
                    shell=True, check=True
                )
                
                # HTTPS proxy ayarla
                subprocess.run(
                    f'networksetup -setsecurewebproxy "{service}" {self.proxy_host} {self.proxy_port}',
                    shell=True, check=True
                )
                
                # Bypass listesini ayarla
                subprocess.run(
                    f'networksetup -setproxybypassdomains "{service}" localhost 127.0.0.1 *.local',
                    shell=True, check=True
                )
            
            logger.info("macOS proxy ayarları etkinleştirildi")
            return True
        except Exception as e:
            logger.error(f"macOS proxy ayarları etkinleştirilirken hata: {str(e)}")
            return False
    
    def _disable_macos(self) -> bool:
        """macOS'ta proxy ayarlarını devre dışı bırak."""
        try:
            # Aktif ağ servisini bul
            result = subprocess.run(
                "networksetup -listallnetworkservices",
                shell=True, capture_output=True, text=True, check=True
            )
            
            # İlk satır açıklama olduğu için atla
            services = result.stdout.strip().split("\n")[1:]
            
            # Her bir ağ servisi için proxy ayarlarını kapat
            for service in services:
                if service.startswith("*"):
                    continue  # Devre dışı servisler
                
                # HTTP proxy kapat
                subprocess.run(
                    f'networksetup -setwebproxystate "{service}" off',
                    shell=True, check=True
                )
                
                # HTTPS proxy kapat
                subprocess.run(
                    f'networksetup -setsecurewebproxystate "{service}" off',
                    shell=True, check=True
                )
            
            logger.info("macOS proxy ayarları devre dışı bırakıldı")
            return True
        except Exception as e:
            logger.error(f"macOS proxy ayarları devre dışı bırakılırken hata: {str(e)}")
            return False
    
    def _enable_linux(self) -> bool:
        """Linux'ta proxy ayarlarını etkinleştir."""
        try:
            # GNOME masaüstü ortamı için proxy ayarları
            if os.environ.get("DESKTOP_SESSION") in ["gnome", "ubuntu", "gnome-classic"]:
                # HTTP proxy
                subprocess.run(
                    f"gsettings set org.gnome.system.proxy.http host '{self.proxy_host}'",
                    shell=True, check=True
                )
                subprocess.run(
                    f"gsettings set org.gnome.system.proxy.http port {self.proxy_port}",
                    shell=True, check=True
                )
                
                # HTTPS proxy
                subprocess.run(
                    f"gsettings set org.gnome.system.proxy.https host '{self.proxy_host}'",
                    shell=True, check=True
                )
                subprocess.run(
                    f"gsettings set org.gnome.system.proxy.https port {self.proxy_port}",
                    shell=True, check=True
                )
                
                # Proxy modunu 'manual' olarak ayarla
                subprocess.run(
                    "gsettings set org.gnome.system.proxy mode 'manual'",
                    shell=True, check=True
                )
                
                logger.info("GNOME proxy ayarları etkinleştirildi")
                return True
            else:
                # Diğer masaüstü ortamları için çevre değişkenleri ayarla
                with open(os.path.expanduser("~/.bashrc"), "a") as f:
                    f.write(f"\n# PromptSafe proxy ayarları\n")
                    f.write(f"export http_proxy={self.proxy_url}\n")
                    f.write(f"export https_proxy={self.proxy_url}\n")
                    f.write(f"export no_proxy=localhost,127.0.0.1\n")
                
                logger.info("Linux çevre değişkenleri ile proxy ayarları etkinleştirildi")
                return True
        except Exception as e:
            logger.error(f"Linux proxy ayarları etkinleştirilirken hata: {str(e)}")
            return False
    
    def _disable_linux(self) -> bool:
        """Linux'ta proxy ayarlarını devre dışı bırak."""
        try:
            # GNOME masaüstü ortamı için proxy ayarları
            if os.environ.get("DESKTOP_SESSION") in ["gnome", "ubuntu", "gnome-classic"]:
                # Proxy modunu 'none' olarak ayarla
                subprocess.run(
                    "gsettings set org.gnome.system.proxy mode 'none'",
                    shell=True, check=True
                )
                
                logger.info("GNOME proxy ayarları devre dışı bırakıldı")
                return True
            else:
                # Diğer masaüstü ortamları için çevre değişkenlerini kaldır
                # .bashrc dosyasından proxy satırlarını kaldır
                with open(os.path.expanduser("~/.bashrc"), "r") as f:
                    lines = f.readlines()
                
                with open(os.path.expanduser("~/.bashrc"), "w") as f:
                    for line in lines:
                        if not (
                            "PromptSafe proxy" in line or
                            "http_proxy=" in line or
                            "https_proxy=" in line or
                            "no_proxy=" in line
                        ):
                            f.write(line)
                
                logger.info("Linux çevre değişkenleri ile proxy ayarları devre dışı bırakıldı")
                return True
        except Exception as e:
            logger.error(f"Linux proxy ayarları devre dışı bırakılırken hata: {str(e)}")
            return False


# Singleton instance
system_proxy = SystemProxy() 