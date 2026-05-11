# 🏴‍☠️ Reporte de Inteligencia CTF - Farei_0x
**Generado el:** 2026-05-10 21:22:10
---

## 1. 🖥️ Superficie de Ataque (Hosts)
- 🟢 **IP:** `10.10.10.15` (Fecha: 2026-05-10 20:53:26)
- 🟢 **IP:** `127.0.0.1` (Fecha: 2026-05-11 00:18:46)

## 2. 🚪 Vectores de Red (Puertos)
| IP | Puerto | Servicio | Estado |
|---|---|---|---|
| `10.10.10.15` | **80** | http Apache 2.4.49 | open |
| `10.10.10.15` | **445** | smb | open |
| `127.0.0.1` | **135** | msrpc | open |
| `127.0.0.1` | **445** | microsoft-ds | open |
| `127.0.0.1` | **1234** | hotline | open |
| `127.0.0.1` | **1433** | ms-sql-s | open |
| `127.0.0.1` | **1434** | ms-sql-m | open |
| `127.0.0.1` | **1714** | sesi-lm | open |
| `127.0.0.1` | **1715** | houdini-lm | open |
| `127.0.0.1` | **2020** | xinupageserver | open |
| `127.0.0.1` | **2021** | servexec | open |
| `127.0.0.1` | **2022** | down | open |
| `127.0.0.1` | **3306** | mysql | open |
| `127.0.0.1` | **5040** | unknown | open |
| `127.0.0.1` | **6463** | unknown | open |
| `127.0.0.1` | **7680** | pando-pub | open |
| `127.0.0.1` | **8000** | http | open |
| `127.0.0.1` | **9180** | unknown | open |
| `127.0.0.1` | **31100** | unknown | open |
| `127.0.0.1` | **31104** | unknown | open |
| `127.0.0.1` | **31105** | unknown | open |
| `127.0.0.1` | **41343** | unknown | open |
| `127.0.0.1` | **47213** | unknown | open |
| `127.0.0.1` | **49664** | unknown | open |
| `127.0.0.1` | **49665** | unknown | open |
| `127.0.0.1` | **49666** | unknown | open |
| `127.0.0.1` | **49667** | unknown | open |
| `127.0.0.1` | **49671** | unknown | open |
| `127.0.0.1` | **49727** | unknown | open |
| `127.0.0.1` | **50051** | unknown | open |
| `127.0.0.1` | **50052** | unknown | open |
| `127.0.0.1` | **50071** | unknown | open |
| `127.0.0.1` | **53490** | unknown | open |
| `127.0.0.1` | **53491** | unknown | open |
| `127.0.0.1` | **53496** | unknown | open |
| `127.0.0.1` | **53497** | unknown | open |
| `127.0.0.1` | **53553** | unknown | open |
| `127.0.0.1` | **53554** | unknown | open |
| `127.0.0.1` | **53555** | unknown | open |
| `127.0.0.1` | **53563** | unknown | open |
| `127.0.0.1` | **53720** | unknown | open |
| `127.0.0.1` | **54228** | unknown | open |

## 3. 🌐 Mapeo Web (Fuzzing)
> No se registró fuzzing exitoso.

## 4. ☢️ Arsenal y Exploits (CVEs)
| Servicio Vulnerable | Link del Exploit (GitHub) | Detalles |
|---|---|---|
| **Apache 2.4.49** | [Link](https://github.com/Soliux/CVE-2021-41773) | CVE-2021-41773 | ⭐2 | Python |
| **Apache 2.4.49** | [Link](https://github.com/vinhjaxt/CVE-2021-41773-exploit) | CVE-2021-41773 | ⭐1 | JavaScript |
| **Apache 2.4.49** | [Link](https://github.com/K3ysTr0K3R/CVE-2021-42013-EXPLOIT) | CVE-2021-42013 | ⭐5 | Python |
| **Apache 2.4.49** | [Link](https://github.com/Makavellik/POC-CVE-2021-42013-EXPLOIT) | CVE-2021-42013 | ⭐0 | Python |

## 5. 🗝️ Credenciales y Hashes
> No se extrajeron credenciales.

## 6. 🏰 Infraestructura Active Directory
| Objetivo | Vulnerabilidad | Cuenta Afectada |
|---|---|---|
| `DOMINIO.LOCAL` | **AS-REP Roasting** | `j.smith` |

---
> Reporte de Inteligencia Total generado automáticamente por Farei_0x Core.
