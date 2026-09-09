<div align="center">

<pre>
███╗   ██╗███████╗████████╗███████╗ ██████╗ █████╗ ███╗   ██╗
████╗  ██║██╔════╝╚══██╔══╝██╔════╝██╔════╝██╔══██╗████╗  ██║
██╔██╗ ██║█████╗     ██║   ███████╗██║     ███████║██╔██╗ ██║
██║╚██╗██║██╔══╝     ██║   ╚════██║██║     ██╔══██║██║╚██╗██║
██║ ╚████║███████╗   ██║   ███████║╚██████╗██║  ██║██║ ╚████║
╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═══╝
</pre>

### 🔍 Сетевой сканер прямо на твоём Android

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Termux%20%2F%20Linux-green?logo=linux&logoColor=white)](https://termux.dev)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0-magenta)](https://github.com/TBFPUMBA/netscanner/releases)

**Ping-sweep · Сканер портов · Определение ОС по TTL · Вендоры по MAC**

</div>

---

## ✨ Возможности

| Фича | Описание |
|------|----------|
| ⚡ **Ping-sweep** | Поиск живых хостов в сети на 128 потоках |
| 🚪 **Сканер портов** | Проверка 28 популярных портов с именами сервисов |
| 🖥 **OS Detection** | Угадывание ОС по TTL (`64` = Linux, `128` = Windows) |
| 🏷 **MAC-вендоры** | Xiaomi, Raspberry Pi, TP-Link, Samsung... |
| 🎨 **Хакерский UI** | Цветные карточки, ASCII-баннер, прогресс-бары |
| 📡 **Авто-сеть** | Сам находит твою подсеть |
| 🪶 **Zero deps** | Только стандартная библиотека Python |

## 🚀 Быстрый старт

### Termux (Android)
```bash
pkg update && pkg install python iproute2
git clone https://github.com/TBF-of/TBF-NETSCAN.git
cd netscanner.py
python netscanner.py
```

## ⚠️ Дисклеймер

Сканируй **только свои сети**. Инструмент создан в образовательных целях.

## 📄 Лицензия

Распространяется под лицензией [MIT](LICENSE).
