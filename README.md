# 🛡️ BioPass App - Suite de Acceso Biométrico Profesional

[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.x-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)](https://opencv.org/)
[![Safe Identity](https://img.shields.io/badge/Security-Liveness_Detection-red?style=for-the-badge)](https://github.com/danielzorita/biopass_dao)

**BioPass App** es un sistema de control de acceso biométrico de nivel empresarial diseñado para entornos que requieren una seguridad robusta y una gestión de datos flexible. Utilizando modelos avanzados de **Deep Learning**, BioPass ofrece una solución completa de reconocimiento facial con detección de vida integrada para prevenir ataques de suplantación.

---

## 💎 Características Principales

### 1. Inteligencia en Reconocimiento Facial
*   **Detección Ultrarrápida**: Implementación de `YuNet`, optimizado para detección facial en tiempo real con baja latencia.
*   **Identificación Precisa**: Motor de reconocimiento basado en `SFace` para una comparación de firmas biométricas de alta fidelidad.
*   **Detección de Vida (Anti-Spoofing)**: Algoritmos diseñados para diferenciar rostros reales de fotografías o vídeos, garantizando que el usuario esté presente físicamente.

### 2. Resiliencia de Hardware (Smart Camera)
El motor de BioPass incluye un gestor de cámaras inteligente que resuelve automáticamente conflictos de drivers comunes en sistemas Windows (`MSMF` vs `DSHOW`), asegurando compatibilidad con prácticamente cualquier cámara web del mercado.

### 3. Privacidad y Seguridad Local
*   **Procesamiento Edge**: Todo el análisis biométrico se realiza localmente. Las firmas faciales nunca se envían a la nube.
*   **Cifrado de Datos**: La información de los usuarios se almacena de forma segura bajo el control de la organización.

### 4. Arquitectura DAO (Data Access Object)
Diseñado para la escalabilidad, el sistema permite alternar entre diferentes motores de base de datos mediante una abstracción profesional:
*   **SQLite**: Ideal para despliegues ligeros o entornos de desarrollo.
*   **PostgreSQL**: Configuración recomendada para entornos de producción de alta concurrencia.

---

## 🛠️ Stack Tecnológico

*   **Lenguaje**: Python 3.9+
*   **Visión Artificial**: OpenCV (Modelos ONNX YuNet & SFace)
*   **Interfaz**: CustomTkinter (UI Moderna con soporte nativo para Modo Oscuro)
*   **Persistencia**: Abstracción DAO compatible con SQL (Postgres/SQLite)
*   **Entorno**: Gestión de secretos mediante `python-dotenv`

---

## 🚀 Guía de Instalación

### 1. Clonar el Repositorio
```bash
git clone https://github.com/danielzorita/biopass_dao.git
cd biopass_dao
```

### 2. Configurar Entorno Virtual
Se recomienda el uso de un entorno virtual para mantener las dependencias aisladas:
```bash
# Crear entorno
python -m venv venv

# Activar en Windows
venv\Scripts\activate

# Activar en Linux/macOS
source venv/bin/activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configuración de Variables de Entorno
Crea un archivo `.env` basado en el ejemplo proporcionado:
```bash
# En Windows
copy .env.example .env

# En Linux/macOS
cp .env.example .env
```
Edita el archivo `.env` para seleccionar el motor de base de datos deseado (`sqlite` o `postgres`).

---

## 🖥️ Modo de Uso

Para ejecutar la aplicación principal, utilice el siguiente comando desde la raíz del proyecto:

```bash
python -m src.main
```

### Flujo Operativo:
1.  **Registro de Usuario**: El sistema captura los puntos biométricos esenciales para crear un perfil único.
2.  **Verificación**: Al intentar acceder, el sistema realiza el escaneo facial y el desafío de liveness.
3.  **Gestión**: A través de la interfaz administrativa, se pueden auditar los registros de acceso y gestionar usuarios.

---

## 🗺️ Roadmap

- [x] Integración de YuNet para detección en milisegundos.
- [x] Soporte Multi-DB (SQLite y PostgreSQL).
- [x] Motor de Liveness Detection robusto.
- [ ] Implementación de Multi-Factor Authentication (MFA).
- [ ] Módulo de exportación de auditorías avanzado.
- [ ] API REST para integraciones externas.

---

## 🤝 Contacto y Colaboración

¿Interesado en mejorar la seguridad biométrica? ¡Las contribuciones son bienvenidas!

**Autor**: [Daniel Zorita](https://www.linkedin.com/in/daniel-zorita-alonso-020140231/)
**Email**: daniel.zorita.alonso@gmail.com

---
*BioPass: Seguridad Inteligente, Privacidad Garantizada.*
