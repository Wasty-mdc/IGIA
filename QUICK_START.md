# 🚀 INICIO RÁPIDO - IGIA con SD3.5

## Pasos de Instalación (Primera Vez)

### 1️⃣ Descargar Modelos SD3.5 (⚠️ MUY IMPORTANTE)

**Antes de instalar cualquier cosa, descarga los modelos:**

1. Ve a: https://huggingface.co/stabilityai/stable-diffusion-3.5-large
2. Haz clic en "Files and versions"
3. Acepta la licencia si te lo pide
4. Descarga estos 5 archivos:
   - `clip_g.safetensors` (1.39 GB)
   - `clip_l.safetensors` (246 MB)
   - `t5xxl.safetensors` (4.89 GB)
   - `sd3.5_large.safetensors` (9.82 GB)
   - `sd3_vae.safetensors` (335 MB) - OPCIONAL

5. Crea la carpeta: `ia\sd3.5-main\models\`
6. Mueve los archivos descargados a esa carpeta

**Estructura final:**
```
IGIA\
└── ia\
    └── sd3.5-main\
        └── models\
            ├── clip_g.safetensors
            ├── clip_l.safetensors
            ├── t5xxl.safetensors
            ├── sd3.5_large.safetensors
            └── sd3_vae.safetensors
```

### 2️⃣ Instalar Python 3.10 o 3.11

- Descarga: https://www.python.org/downloads/
- ✅ **IMPORTANTE:** Marca "Add Python to PATH" durante la instalación

### 3️⃣ Abrir PowerShell en la Carpeta del Proyecto

1. Navega a la carpeta IGIA
2. Shift + Click derecho en espacio vacío
3. "Abrir ventana de PowerShell aquí" o "Abrir en Terminal"

### 4️⃣ Crear Entorno Virtual

```powershell
# Crear entorno virtual
python -m venv venv

# Activar (si da error de permisos, ve al paso 5)
.\venv\Scripts\Activate.ps1
```

### 5️⃣ Si da Error de Permisos

```powershell
# Ejecuta esto PRIMERO
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Luego activa el entorno
.\venv\Scripts\Activate.ps1
```

### 6️⃣ Instalar PyTorch con CUDA

**Si tienes GPU NVIDIA:**
```powershell
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

**Si NO tienes GPU NVIDIA (solo CPU, MUY lento):**
```powershell
pip install torch torchvision
```

### 7️⃣ Instalar Resto de Dependencias

```powershell
pip install -r requirements.txt
```

⏱️ Esto puede tardar 5-10 minutos.

### 8️⃣ Verificar Instalación

```powershell
python verify_setup.py
```

Debe mostrar todo ✓ en verde.

---

## ▶️ Ejecutar la Aplicación

### Cada vez que quieras usar IGIA:

```powershell
# 1. Activar entorno virtual
.\venv\Scripts\Activate.ps1

# 2. Ejecutar aplicación
python main.py
```

---

## 🎨 Primer Uso

1. **Cargar Modelo**
   - Clic en "🔄 Cargar Modelo IA"
   - Espera 1-2 minutos (carga todos los componentes)
   - Verás "✅ SD3.5 Large cargado"

2. **Generar Primera Imagen**
   - Categoría: `personajes`
   - Descripción: `brave knight with blue armor and golden sword`
   - Resolución: `1024x1024`
   - Steps: `40`
   - Guidance: `4.5`
   - Cantidad: `1`
   - Clic en "🎨 GENERAR IMÁGENES"

3. **Esperar Resultado**
   - Primera generación tarda más (inicialización)
   - GPU RTX 3080: ~30-40 segundos
   - Imágenes se guardan en carpeta `output/`

---

## 🆘 Solución Rápida de Problemas

### ❌ "python no se reconoce..."
**Solución:** Python no está en PATH. Reinstala Python marcando "Add to PATH".

### ❌ "torch no se puede importar"
**Solución:** 
```powershell
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### ❌ "Archivos del modelo no encontrados"
**Solución:** Descarga los modelos del paso 1️⃣ y colócalos en la carpeta correcta.

### ❌ "CUDA out of memory"
**Solución:** 
- Reduce resolución a 768x768
- Cierra otras aplicaciones
- Tu GPU tiene menos de 12GB VRAM

### ❌ "torch.cuda.is_available() = False"
**Solución:** CUDA no detectado. Reinstala PyTorch con CUDA:
```powershell
pip uninstall torch torchvision
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### ❌ Generación muy lenta
**Causa:** Está usando CPU en lugar de GPU.
**Verificar:**
```powershell
python -c "import torch; print(torch.cuda.is_available())"
```
Debe mostrar `True`.

---

## 📊 Requisitos Mínimos

✅ **Funciona:**
- GPU: RTX 3060 12GB o superior
- RAM: 16GB
- Disco: 25GB libre
- SO: Windows 10/11

⚠️ **Puede funcionar (lento):**
- GPU: RTX 3060 8GB (reduce resolución)
- RAM: 8GB (puede dar problemas)

❌ **NO funcionará bien:**
- Sin GPU NVIDIA (demasiado lento)
- Menos de 8GB VRAM
- Menos de 8GB RAM

---

## 🎯 Parámetros Recomendados

| Uso | Resolución | Steps | Guidance | Tiempo (RTX 3080) |
|-----|-----------|-------|----------|-------------------|
| **Prueba rápida** | 512x512 | 28 | 4.5 | ~15s |
| **Calidad normal** | 1024x1024 | 40 | 4.5 | ~35s |
| **Alta calidad** | 1024x1024 | 50 | 4.5 | ~45s |
| **Máxima calidad** | 1536x1536 | 50 | 4.5 | ~90s |

---

## 📁 Estructura de Carpetas

```
IGIA/
├── config/
│   ├── prompts_templates.json    # Pre-prompts editables
│   └── model_config.json         # Configuración modelo
├── ia/
│   └── sd3.5-main/
│       ├── models/               # ⚠️ DESCARGAR AQUÍ LOS MODELOS
│       └── sd3_infer.py          # Inferencia SD3.5
├── src/
│   ├── sd3_generator.py          # Generador SD3.5 (NUEVO)
│   ├── prompt_manager.py         # Gestión de prompts
│   └── image_generator.py        # Generador SD1.5 (antiguo, no usado)
├── output/                       # Imágenes generadas
├── main.py                       # ▶️ Ejecutar esto
├── verify_setup.py               # Verificar instalación
├── requirements.txt
├── README.md
├── SETUP_GUIDE.md               # Guía detallada
└── CHANGELOG.md                 # Cambios realizados
```

---

## 🔗 Enlaces Útiles

- **Modelo SD3.5:** https://huggingface.co/stabilityai/stable-diffusion-3.5-large
- **Python:** https://www.python.org/downloads/
- **CUDA Toolkit:** https://developer.nvidia.com/cuda-downloads
- **PyTorch:** https://pytorch.org/get-started/locally/

---

## ✅ Checklist de Instalación

- [ ] Python 3.10/3.11 instalado y en PATH
- [ ] Modelos SD3.5 descargados y en `ia/sd3.5-main/models/`
- [ ] Entorno virtual creado (`venv`)
- [ ] PyTorch con CUDA instalado
- [ ] Dependencias instaladas (`requirements.txt`)
- [ ] `verify_setup.py` muestra todo ✓
- [ ] GPU NVIDIA con 12GB+ VRAM (recomendado)

---

**¿Todo listo?** → Ejecuta: `python main.py` 🚀

**¿Problemas?** → Ejecuta: `python verify_setup.py` 🔍

**¿Necesitas ayuda?** → Lee: `SETUP_GUIDE.md` 📖
