#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TBFPUMBA NET SCANNER v1.0
Сетевой сканер для Termux: ping-sweep + порт-сканер + угадывание ОС по TTL
"""

import re, sys, socket, argparse, ipaddress, subprocess
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# ===================== ЦВЕТА =====================
class C:
    END = '\033[0m'; BOLD = '\033[1m'; DIM = '\033[2m'
    RED = '\033[91m'; GREEN = '\033[92m'; YELLOW = '\033[93m'
    BLUE = '\033[94m'; MAGENTA = '\033[95m'; CYAN = '\033[96m'; WHITE = '\033[97m'

def paint(t, *styles):
    return ''.join(styles) + str(t) + C.END

ANSI = re.compile(r'\033\[[0-9;]*m')
def visible(s):
    return ANSI.sub('', str(s))

BANNER = [
    '███╗   ██╗███████╗████████╗███████╗ ██████╗ █████╗ ███╗   ██╗',
    '████╗  ██║██╔════╝╚══██╔══╝██╔════╝██╔════╝██╔══██╗████╗  ██║',
    '██╔██╗ ██║█████╗     ██║   ███████╗██║     ███████║██╔██╗ ██║',
    '██║╚██╗██║██╔══╝     ██║   ╚════██║██║     ██╔══██║██║╚██╗██║',
    '██║ ╚████║███████╗   ██║   ███████║╚██████╗██║  ██║██║ ╚████║',
    '╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═══╝',
]

def show_banner():
    colors = [C.CYAN, C.CYAN, C.BLUE, C.BLUE, C.MAGENTA, C.MAGENTA]
    print()
    for line, col in zip(BANNER, colors):
        print(paint(line, col, C.BOLD))
    print(paint('          T B F P U M B A   //   network scanner v1.0', C.DIM))
    print()

# ===================== СЕТЬ =====================
def local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        return s.getsockname()[0]
    except OSError:
        return '127.0.0.1'
    finally:
        s.close()

def ping(ip, wait=1):
    try:
        out = subprocess.run(['ping', '-c', '1', '-W', str(wait), str(ip)],
                             capture_output=True, text=True, timeout=wait + 3)
        if out.returncode == 0:
            m = re.search(r'ttl[= :](\d+)', out.stdout, re.IGNORECASE)
            return True, (int(m.group(1)) if m else None)
        return False, None
    except Exception:
        return False, None

def hostname(ip):
    try:
        return socket.gethostbyaddr(str(ip))[0]
    except Exception:
        return '—'

def arp_table():
    table = {}
    try:
        out = subprocess.run(['ip', 'neigh'], capture_output=True, text=True)
        for line in out.stdout.splitlines():
            m = re.match(r'(\S+)\s+.*?lladdr\s+([0-9a-fA-F:]{17})', line)
            if m:
                table[m.group(1)] = m.group(2).upper()
    except Exception:
        pass
    if not table:
        try:
            with open('/proc/net/arp') as f:
                next(f)
                for line in f:
                    p = line.split()
                    if len(p) >= 4 and p[3] != '00:00:00:00:00:00':
                        table[p[0]] = p[3].upper()
        except Exception:
            pass
    return table

# ===================== ПОРТЫ =====================
PORTS = [21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445,
         554, 631, 1900, 3306, 3389, 4444, 5000, 5555, 5900, 6379,
         8000, 8080, 8888, 9100, 10000]

def port_open(ip, port, timeout=0.4):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        return s.connect_ex((str(ip), port)) == 0
    except OSError:
        return False
    finally:
        s.close()

def svc(port):
    try:
        return socket.getservbyport(port)
    except OSError:
        return '?'

# ===================== ВЕНДОРЫ / ОС =====================
VENDORS = {
    'B8:27:EB': 'Raspberry Pi', 'DC:A6:32': 'Raspberry Pi',
    'E4:5F:01': 'Raspberry Pi', 'D8:3A:DD': 'Raspberry Pi',
    '00:0C:29': 'VMware', '08:00:27': 'VirtualBox', '52:54:00': 'QEMU/KVM',
    '5C:CF:7F': 'Espressif IoT', '84:F3:EB': 'Espressif IoT', 'A4:CF:12': 'Espressif IoT',
    '78:02:F8': 'Xiaomi', '64:CC:2E': 'Xiaomi', 'AC:C1:EE': 'Xiaomi',
    '3C:5A:B4': 'Google', 'F4:F5:D8': 'Google', '00:1A:11': 'Google',
    'DC:56:E7': 'Apple', 'F0:18:98': 'Apple',
    '30:FD:38': 'LG', '34:13:E8': 'Samsung', 'D0:59:82': 'Samsung',
    '10:2E:AF': 'TP-Link', '50:C7:BF': 'TP-Link', 'C4:6E:1F': 'TP-Link',
    '20:F4:1B': 'D-Link', '00:22:B0': 'D-Link', '00:E0:4C': 'Realtek',
}

def guess_os(ttl):
    if ttl is None:
        return paint('???', C.DIM)
    if ttl <= 64:
        return paint('Linux/Android', C.GREEN)
    if ttl <= 128:
        return paint('Windows', C.BLUE)
    return paint('Router/устройство', C.YELLOW)

# ===================== ВЫВОД =====================
def progress(done, total, width=42):
    pct = done / total if total else 1
    n = int(width * pct)
    bar = '█' * n + '░' * (width - n)
    sys.stdout.write(f'\r  {paint("[" + bar + "]", C.CYAN)} {done}/{total} · {pct*100:5.1f}%')
    sys.stdout.flush()

def show_host(ip, ttl, host, mac, vendor, ports, w=52):
    top = paint('╭' + '─' * (w - 2) + '╮', C.BLUE)
    bot = paint('╰' + '─' * (w - 2) + '╯', C.BLUE)
    def row(t):
        return (paint('│', C.BLUE) + ' ' + t + ' ' * max(0, w - 4 - len(visible(t)))
                + ' ' + paint('│', C.BLUE))
    head = f'{paint(str(ip), C.GREEN, C.BOLD)}  {guess_os(ttl)}'
    if ttl:
        head += paint(f'  ttl={ttl}', C.DIM)
    print(top)
    print(row(head))
    print(row(f'{paint("Host:", C.DIM)} {paint(host, C.CYAN)}'))
    macline = paint('MAC:', C.DIM) + ' ' + (paint(mac, C.YELLOW) if mac else paint('—', C.DIM))
    if vendor:
        macline += paint('  ·  ', C.DIM) + paint(vendor, C.MAGENTA, C.BOLD)
    print(row(macline))
    if ports:
        plist = ' '.join(f'{p}({svc(p)})' for p in ports)
        print(row(paint('Порты:', C.DIM) + ' ' + paint(plist, C.WHITE)))
    else:
        print(row(paint('Порты: все закрыты', C.DIM)))
    print(bot)

# ===================== MAIN =====================
def main():
    ap = argparse.ArgumentParser(description='TBFPUMBA Net Scanner')
    ap.add_argument('cidr', nargs='?', help='подсеть, напр. 192.168.1.0/24')
    args = ap.parse_args()

    show_banner()
    me = local_ip()
    net = ipaddress.ip_network(args.cidr, strict=False) if args.cidr \
        else ipaddress.ip_network(me + '/24', strict=False)

    print(paint('  ▸ Твой IP:    ', C.DIM) + paint(me, C.GREEN, C.BOLD))
    print(paint('  ▸ Сканирую:   ', C.DIM) + paint(str(net), C.CYAN, C.BOLD))
    print(paint('  ▸ Портов:     ', C.DIM) + paint(str(len(PORTS)), C.YELLOW))
    print()

    hosts = list(net.hosts())
    total = len(hosts)
    if total > 1024:
        print(paint(f'  ⚠ Сеть большая: {total} хостов. Enter — продолжить, Ctrl+C — выйти', C.RED, C.BOLD))
        input()

    t0 = datetime.now()
    arps = arp_table()

    print(paint('  [1/2] Ping-sweep — ищу живые хосты...', C.YELLOW, C.BOLD))
    alive = []
    done = 0
    with ThreadPoolExecutor(max_workers=128) as ex:
        futs = {ex.submit(ping, h): h for h in hosts}
        for f in as_completed(futs):
            ok, ttl = f.result()
            if ok:
                alive.append((futs[f], ttl))
            done += 1
            progress(done, total)
    print()
    if not alive:
        print(paint('  ✖ Живых хостов не найдено.', C.RED, C.BOLD))
        sys.exit(0)
    print(paint(f'  ✔ Живых хостов: {len(alive)}', C.GREEN, C.BOLD))
    print()

    print(paint('  [2/2] Сканирую порты...', C.YELLOW, C.BOLD))
    found = {h: [] for h, _ in alive}
    pairs = [(h, p) for h, _ in alive for p in PORTS]
    done = 0

    def check(pair):
        h, p = pair
        if port_open(h, p):
            found[h].append(p)

    with ThreadPoolExecutor(max_workers=256) as ex:
        futs = [ex.submit(check, pair) for pair in pairs]
        for f in as_completed(futs):
            done += 1
            progress(done, len(pairs))
    print('\n')

    results = []
    for h, ttl in alive:
        mac = arps.get(str(h), '')
        results.append((h, ttl, hostname(h), mac,
                        VENDORS.get(mac[:8], '') if mac else '', sorted(found[h])))
    results.sort(key=lambda r: int(r[0]))

    for r in results:
        show_host(*r)
        print()

    dt = datetime.now() - t0
    op = sum(len(r[5]) for r in results)
    print(paint(f'  ✔ За {dt.total_seconds():.1f}с | хостов: {len(results)} | открытых портов: {op}', C.GREEN, C.BOLD))
    print(paint('  Сканируй только свои сети. Удачи, Макс!', C.DIM))

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(paint('\n\n  ✖ Остановлено пользователем', C.RED, C.BOLD))
        sys.exit(0)
  
