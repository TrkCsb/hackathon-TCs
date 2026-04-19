import json
import re
import sys
from pathlib import Path
 
 
def cleanValue(v):
    if v is None:
        return ""
    v = v.strip()
    v = re.sub(r'\(\w+\)$', '', v).strip()
    return v
 
 
def contValue(line):
    m = re.match(r'^\s{10,}(\S.*)', line)
    return m.group(1).strip() if m else None
 
 
KNOWN_FIELDS = re.compile(
    r'description\s*\.|physical address\s*\.|dhcp enabled\s*\.|'
    r'ipv4 address\s*\.|autoconfiguration ipv4 address\s*\.|'
    r'subnet mask\s*\.|default gateway\s*\.|dns servers\s*\.',
    re.IGNORECASE
)
 
 
def parseIpconfig(text):
    adapters = []
    blocks = re.split(r'\n(?=\S.*adapter )', text)
 
    for block in blocks:
        lines = block.strip().splitlines()
        if not lines:
            continue
 
        header_match = re.match(r'^(.+adapter .+?):', lines[0])
        if not header_match:
            continue
 
        adapter = {
            "adapter_name": header_match.group(1).strip(),
            "description": "",
            "physical_address": "",
            "dhcp_enabled": "",
            "ipv4_address": "",
            "subnet_mask": "",
            "default_gateway": [],
            "dns_servers": []
        }
 
        collecting = None
 
        for line in lines[1:]:
            def val(pattern):
                m = re.search(pattern, line, re.IGNORECASE)
                return cleanValue(m.group(1)) if m else None
 
            is_labeled = bool(re.match(r'^\s+\S[^:]+:', line))
            is_known = bool(KNOWN_FIELDS.search(line))
 
            if re.search(r'description\s*\.', line, re.IGNORECASE):
                adapter["description"] = val(r':\s*(.*)') or ""
                collecting = None
            elif re.search(r'physical address\s*\.', line, re.IGNORECASE):
                adapter["physical_address"] = val(r':\s*(.*)') or ""
                collecting = None
            elif re.search(r'dhcp enabled\s*\.', line, re.IGNORECASE):
                adapter["dhcp_enabled"] = val(r':\s*(.*)') or ""
                collecting = None
            elif re.search(r'ipv4 address\s*\.', line, re.IGNORECASE):
                adapter["ipv4_address"] = val(r':\s*(.*)') or ""
                collecting = None
            elif re.search(r'autoconfiguration ipv4 address\s*\.', line, re.IGNORECASE):
                if not adapter["ipv4_address"]:
                    adapter["ipv4_address"] = val(r':\s*(.*)') or ""
                collecting = None
            elif re.search(r'subnet mask\s*\.', line, re.IGNORECASE):
                adapter["subnet_mask"] = val(r':\s*(.*)') or ""
                collecting = None
            elif re.search(r'default gateway\s*\.', line, re.IGNORECASE):
                collecting = "gateway"
                v = val(r':\s*(.*)')
                if v:
                    adapter["default_gateway"].append(v)
            elif re.search(r'dns servers\s*\.', line, re.IGNORECASE):
                collecting = "dns"
                v = val(r':\s*(.*)')
                if v:
                    adapter["dns_servers"].append(v)
            elif not is_labeled:
                cv = contValue(line)
                if cv and collecting == "gateway":
                    adapter["default_gateway"].append(cv)
                elif cv and collecting == "dns":
                    adapter["dns_servers"].append(cv)
            elif is_labeled and not is_known:
                pass
            else:
                collecting = None
 
        adapter["default_gateway"] = adapter["default_gateway"] if adapter["default_gateway"] else ""
        adapters.append(adapter)
 
    return adapters
 
 
def processFiles(file_paths):
    result = []
    for path in file_paths:
        p = Path(path)
        text = p.read_text(encoding='utf-8', errors='replace')
        result.append({
            "file_name": p.name,
            "adapters": parseIpconfig(text)
        })
    return result
 
 
if __name__ == "__main__":
    files = sys.argv[1:] if len(sys.argv) > 1 else list(Path('.').glob('*.log')) + list(Path('.').glob('*.txt'))
    if not files:
        print("Usage: python parse_ipconfig.py file1.txt file2.txt ...")
        sys.exit(1)
    output = processFiles(files)
    print(json.dumps(output, indent=2, ensure_ascii=False))