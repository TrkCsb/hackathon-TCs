import json
import re
import sys
from pathlib import Path 

LIST_KEYS = ('default_gateway', 'dns_servers')

_LABEL_TO_KEY = {
    lbl.lower(): jkey
    for jkey, labels in {
        'description':     ['Description'],
        'physical_address':['Physical Address'],
        'dhcp_enabled':    ['DHCP Enabled'],
        'ipv4_address':    ['IPv4 Address', 'Autoconfiguration IPv4 Address'],
        'subnet_mask':     ['Subnet Mask'],
        'default_gateway': ['Default Gateway'],
        'dns_servers':     ['DNS Servers'],
        'ipv6_address':    ['IPv6 Address'],
        'link_local_ipv6': ['Link-local IPv6 Address'],
        'temp_ipv6':       ['Temporary IPv6 Address'],
        'media_state':     ['Media State'],
    }.items()
    for lbl in labels
}
 
def clean(v):
    return re.sub(r'\s*\((Preferred|Deferred)\)\s*$', '', v).strip()
 
def emptyAdapter(name):
    return {k: ([] if k in LIST_KEYS else '') for k in
            ['adapter_name','description','physical_address','dhcp_enabled',
             'ipv4_address','subnet_mask','default_gateway','dns_servers',
             'ipv6_address','link_local_ipv6','temp_ipv6','media_state']} | {'adapter_name': name}
 
def parseIpconfig(text):
    adapters, current, lastKey = [], None, None
    for raw in text.splitlines():
        line = raw.rstrip()
        h = re.match(r'^([A-Za-z][\w\s\*\#]+):\s*$', line)
        if h:
            if current is not None:
                adapters.append(current)
            current, lastKey = emptyAdapter(h.group(1).strip()), None
            continue
        if current is None:
            continue
        stripped = line.strip()
        indent = len(line) - len(line.lstrip())
        if indent >= 30 and stripped and re.match(r'^[\w:.%]+$', stripped) and lastKey in LIST_KEYS:
            current[lastKey].append(clean(stripped))
            continue
        m = re.match(r'^\s{2,}(.+?)\s*[.:]+\s*:\s*(.*?)\s*$', line)
        if not m:
            continue
        jkey = _LABEL_TO_KEY.get(re.sub(r'[\s.]+$', '', m.group(1)).lower())
        if not jkey:
            continue
        val, lastKey = clean(m.group(2)), jkey
        current[jkey] = [val] if (jkey in LIST_KEYS and val) else ([] if jkey in LIST_KEYS else val)
    if current is not None:
        adapters.append(current)
    return adapters

def main(filePaths):
    if not filePaths:
        print('Usage: python ipconfig_parser.py file1.txt file2.txt ...')
        sys.exit(1)
    results = []
    for fp in filePaths:
        p = Path(fp)
        if not p.exists():
            print(f'[WARN] File not found, skipping: {fp}', file=sys.stderr)
            continue
        results.append({'file_name': p.name, 'adapters': parseIpconfig(p.read_text(encoding='utf-8', errors='replace'))})
    out = Path('ipconfig_output.json')
    out.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f'Done. Results written to {out}')
    print(json.dumps(results, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main(sys.argv[1:])