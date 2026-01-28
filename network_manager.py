import subprocess
import json
import re
import requests
import time
from utils import run_command

class NetworkManager:
    def __init__(self):
        pass

    def get_adapters(self):
        """
        Retrieves a list of network adapters using PowerShell.
        Returns a list of dicts: {'Name': str, 'Description': str, 'Status': str, 'MacAddress': str}
        """
        cmd = 'powershell -Command "Get-NetAdapter | Select-Object Name, InterfaceDescription, Status, MacAddress | ConvertTo-Json"'
        stdout, stderr, code = run_command(cmd)
        
        adapters = []
        if code == 0 and stdout:
            try:
                data = json.loads(stdout)
                if isinstance(data, dict):
                    data = [data]
                
                for item in data:
                    # Filter only Up or likely relevant adapters to reduce clutter? 
                    # Keeping all for now but user might want to see only 'Up'.
                    adapters.append({
                        'Name': item.get('Name', 'Unknown'),
                        'Description': item.get('InterfaceDescription', ''),
                        'Status': item.get('Status', 'Unknown'),
                        'MacAddress': item.get('MacAddress', '')
                    })
            except json.JSONDecodeError:
                pass
        return adapters

    def prioritize_adapter(self, target_name):
        """
        Sets the target adapter to Metric 1 (High Priority) and others to 100.
        """
        adapters = self.get_adapters()
        log = []
        
        # 1. Set Target to 1
        cmd_target = f'netsh interface ip set interface "{target_name}" metric=1'
        o, e, c = run_command(cmd_target)
        if c == 0:
            log.append(f"✓ {target_name} set to High Priority (Metric 1)")
        else:
            log.append(f"✗ Failed to prioritize {target_name}: {e or o}")

        # 2. Set others to 100 (Background)
        for adp in adapters:
            name = adp['Name']
            if name != target_name and adp['Status'].lower() == 'up':
                # Only touch active ones to avoid errors on disconnected NICs
                cmd_bg = f'netsh interface ip set interface "{name}" metric=100'
                run_command(cmd_bg) # Fire and forget for background ones
                
        return "\n".join(log)

    def set_dns(self, adapter_name, primary, secondary=None):
        cmd_primary = f'netsh interface ip set dns name="{adapter_name}" source=static addr={primary} register=primary'
        out, err, code = run_command(cmd_primary)
        
        if code != 0:
            return f"Error: {err or out}"

        if secondary:
            cmd_secondary = f'netsh interface ip add dns name="{adapter_name}" addr={secondary} index=2'
            run_command(cmd_secondary)
        
        return "DNS Updated"

    def clear_dns(self, adapter_name):
        cmd = f'netsh interface ip set dns name="{adapter_name}" source=dhcp'
        out, err, code = run_command(cmd)
        return "DNS Reset (DHCP)" if code == 0 else f"Error: {err or out}"

    def flush_dns(self):
        out, err, code = run_command("ipconfig /flushdns")
        return "DNS Cache Flushed" if code == 0 else "Failed"

    def release_ip(self, adapter_name=None):
        cmd = f'ipconfig /release "{adapter_name}"' if adapter_name else "ipconfig /release"
        out, err, code = run_command(cmd)
        return "IP Released" if code == 0 else "Error"

    def renew_ip(self, adapter_name=None):
        cmd = f'ipconfig /renew "{adapter_name}"' if adapter_name else "ipconfig /renew"
        out, err, code = run_command(cmd)
        return "IP Renewed" if code == 0 else "Error"

    def get_public_ip(self):
        try:
            response = requests.get("https://api.ipify.org?format=json", timeout=2)
            if response.status_code == 200:
                return response.json().get("ip", "Unknown")
        except:
            pass
        return "Unavailable"

    def get_connection_stats(self, target="8.8.8.8"):
        """Pings target 2 times. Returns (latency_str, loss_str)."""
        cmd = f"ping -n 2 -w 1000 {target}"
        out, err, code = run_command(cmd)
        
        latency = "N/A"
        loss = "N/A"

        if code == 0:
            # Latency (Average = Xms)
            match_lat = re.search(r"Average = (\d+)ms", out)
            if match_lat:
                latency = f"{match_lat.group(1)} ms"
            
            # Packet Loss (Loss = X% (Y loss))
            # Output format: "Packets: Sent = 4, Received = 4, Lost = 0 (0% loss),"
            match_loss = re.search(r"\((\d+)% loss\)", out)
            if match_loss:
                loss = f"{match_loss.group(1)}%"
        
        return latency, loss

    def get_location_info(self):
        """Fetches detailed location info from ip-api.com."""
        try:
            # ip-api.com/json/ returns {status, country, city, isp, query (ip), ...}
            r = requests.get("http://ip-api.com/json/?fields=status,message,country,regionName,city,isp,query", timeout=5)
            data = r.json()
            if data.get("status") == "success":
                return data
        except Exception as e:
            print(f"Loc Error: {e}")
        return None
