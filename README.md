# 🔒 Security Pipeline Demo

Pipeline de seguridad que demuestra el uso de **SAST (Bandit)** y **DAST (OWASP ZAP)** para análisis de seguridad de aplicaciones.

## 📋 Contenido

- **SAST (Static Application Security Testing)**: Análisis estático del código usando Bandit
- **DAST (Dynamic Application Security Testing)**: Análisis dinámico usando OWASP ZAP
- **Aplicación Vulnerable**: Flask app con vulnerabilidades intencionales para demostración

## 🚀 Inicio Rápido

### 1. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 2. Ejecutar Solo SAST (Bandit)

```bash
# Opción 1: Usar el script SAST directamente
python run_sast.py

# Opción 2: Usar el pipeline con flag
python security_pipeline.py --sast-only
```

### 3. Ejecutar Pipeline Completo (SAST + DAST)

**Requisitos**: Docker Desktop debe estar corriendo

```bash
python security_pipeline.py --full
```

## 📁 Estructura del Proyecto

```
security-pipeline-demo/
├── app.py                    # Aplicación Flask vulnerable
├── requirements.txt          # Dependencias Python
├── .bandit                   # Configuración Bandit
├── docker-compose.yml        # Docker Compose para ZAP
├── Dockerfile                # Dockerfile para la app
├── run_sast.py              # Script SAST (Bandit)
├── run_dast.py              # Script DAST (OWASP ZAP)
├── security_pipeline.py      # Pipeline principal
├── README.md                 # Esta documentación
└── reports/                  # Directorio de reportes generados
    ├── bandit_report.html
    ├── bandit_report.json
    ├── zap_report.html
    └── security_pipeline_report.html
```

## 🔍 Vulnerabilidades Incluidas

La aplicación `app.py` incluye vulnerabilidades intencionales:

| Vulnerabilidad | Endpoint | Bandit ID |
|----------------|----------|-----------|
| SQL Injection | `/user?id=` | B608 |
| Command Injection | `/ping?host=` | B602, B605 |
| XSS | `/search?q=` | - |
| Hardcoded Passwords | - | B105, B106 |
| Weak Crypto (MD5) | `/hash` | B303, B324 |
| Debug Mode | - | B201 |

## 📊 Reportes

Después de ejecutar el pipeline, los reportes se generan en `/reports`:

- **bandit_report.html**: Reporte visual de SAST
- **bandit_report.json**: Datos estructurados de SAST
- **zap_report.html**: Reporte de DAST
- **security_pipeline_report.html**: Reporte consolidado

## ⚠️ Advertencia

Esta aplicación contiene vulnerabilidades **INTENCIONALES** para propósitos educativos.

**¡NO USAR EN PRODUCCIÓN!**

## 🛠️ Comandos Útiles

```bash
# Solo análisis SAST
python run_sast.py

# Solo análisis DAST (requiere app corriendo)
python app.py &
python run_dast.py

# Pipeline completo
python security_pipeline.py --full

# Usando Docker Compose
docker-compose up -d
python run_dast.py
docker-compose down
```

## 📚 Referencias

- [Bandit Documentation](https://bandit.readthedocs.io/)
- [OWASP ZAP](https://www.zaproxy.org/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
