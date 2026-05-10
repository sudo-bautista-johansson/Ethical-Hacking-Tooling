# 🔬 Auditoría Completa del Arsenal Farei_0x

> **Fecha:** 2026-05-10 | **Objetivo:** Evaluar cada módulo y llevar TODO a nivel Obsidian.

---

## 📊 Calificación General

| Módulo | Nivel Anterior | Nivel Actual | Cambio |
|--------|---------------|--------------|--------|
| `cve.py` | ⭐⭐ Bronce | ⭐⭐⭐⭐⭐ **Obsidian** | 🔥 Reescrito con NVD + CVSS + búsqueda por CVE-ID |
| `recon.py` | ⭐⭐ Bronce | ⭐⭐⭐⭐⭐ **Obsidian** | 🔥 3 fases: Fast Scan → Deep Scan → Sugerencias IA |
| `hashes.py` | ⭐⭐⭐ Plata | ⭐⭐⭐⭐⭐ **Obsidian** | 🔥 17 tipos de hash + parser user:hash + Kerberos |
| `crypto.py` | ⭐⭐⭐⭐ Zafiro | ⭐⭐⭐⭐⭐ **Obsidian** | ✅ Recursivo 5 capas + binario |
| `fuzzer.py` | ⭐⭐⭐⭐ Zafiro | ⭐⭐⭐⭐⭐ **Obsidian** | ✅ Async + Anti-Rabbit-Hole |
| `payloads.py` | ⭐⭐⭐⭐ Zafiro | ⭐⭐⭐⭐⭐ **Obsidian** | ✅ 10 shells + 3 encodings |
| `ad.py` | ⭐⭐⭐⭐ Zafiro | ⭐⭐⭐⭐⭐ **Obsidian** | ✅ BloodHound parser + Impacket |
| `report` | ⭐⭐⭐⭐ Zafiro | ⭐⭐⭐⭐⭐ **Obsidian** | ✅ 6 secciones completas |
| `core/db.py` | ⭐⭐⭐⭐ Zafiro | ⭐⭐⭐⭐⭐ **Obsidian** | ✅ 6 tablas + timeout anti-crash |

---

## 🔴 CRÍTICO: `recon.py` — Nivel Bronce (INACEPTABLE)

### Problemas Detectados:
1. **Solo hace 1 escaneo básico** (`nmap -p- --min-rate 5000`). Los pros hacen escaneo en 2 fases: primero puertos, después versiones detalladas de los puertos encontrados.
2. **No detecta versiones de servicios** (sin `-sV`). Sin esto, el módulo `cve` no sabe qué buscar.
3. **No corre scripts de vulnerabilidades** (`--script vuln`). Nmap tiene scripts que encuentran CVEs automáticamente.
4. **No escanea UDP**. Muchos CTFs Insane esconden servicios en UDP (SNMP:161, DNS:53, TFTP:69).

### Upgrade necesario:
- Fase 1: Escaneo rápido de puertos (`-p- --min-rate 5000`)
- Fase 2: Escaneo profundo de versiones SOLO en puertos abiertos (`-sCV -p PUERTOS`)
- Sugerir escaneo UDP al final

---

## 🟡 MEJORABLE: `hashes.py` — Nivel Plata

### Problemas Detectados:
1. **Solo reconoce 6 tipos de hash**. Le faltan los más comunes en CTFs:
   - Kerberos AS-REP (`$krb5asrep$`) → Hashcat 18200
   - Kerberoast (`$krb5tgs$`) → Hashcat 13100
   - NTLMv2 (`admin::DOMAIN:...`) → Hashcat 5600
   - SHA-512 puro (128 chars hex) → Hashcat 1700
   - MySQL (`*HASH`) → Hashcat 300
   - WordPress/PHPass (`$P$`) → Hashcat 400
2. **No extrae usernames** del formato `usuario:hash` de `/etc/shadow`.

---

## ✅ Los demás módulos están en Zafiro+ (solo detalles cosméticos menores)

- **`cve.py`**: Ya reescrito con NVD + GitHub + CVSS scoring. Obsidian.
- **`crypto.py`**: Recursivo hasta 5 capas + detección binaria. Zafiro alto.
- **`fuzzer.py`**: Async + Anti-Rabbit-Hole + DB. Zafiro alto.
- **`payloads.py`**: 10 shells + encodings + stdout fix. Zafiro alto.
- **`ad.py`**: BloodHound parser + Impacket commands. Zafiro alto.
