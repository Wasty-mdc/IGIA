# IGIA - Generador de Imágenes con IA para Roguecat

**IGIA** (Intelligent Game Image Artificer) es una herramienta de generación de imágenes con Inteligencia Artificial local, diseñada específicamente para crear assets de videojuegos en estilo pixel art de manera coherente y en serie usando **Stable Diffusion 3.5 Large**.

## 🎯 Características Principales

- **✨ Generación con SD3.5 Large**: Usa el modelo más avanzado de Stability AI localmente
- **🎨 Pre-prompts Configurables**: Mantén consistencia visual con templates predefinidos
- **🎬 Generación en Serie**: Crea animaciones completas y múltiples variaciones
- **📁 Categorías Organizadas**: Personajes, mapas, items, enemigos, etc.
- **🌍 Sistema de Biomas**: Contexto adicional para coherencia temática
- **🖥️ Interfaz Gráfica Intuitiva**: No necesitas saber programar para usarla
- **⚙️ Parámetros Ajustables**: Control total sobre resolución, steps, guidance, seed

## 📋 Requisitos del Sistema

### Hardware Recomendado
- **GPU NVIDIA** con al menos **12GB de VRAM** (para SD3.5 Large)
  - RTX 4070 Ti o superior (ideal)
  - RTX 3080/3090 (recomendado)
  - RTX 3060 12GB (mínimo, puede ser lento)
- **RAM**: 16GB recomendado (32GB ideal)
- **Espacio en disco**: ~20GB para modelos + espacio para imágenes generadas

### Software
- **Windows 10/11** (64-bit)
- **Python 3.10 o 3.11** (Python 3.12 puede tener problemas de compatibilidad)
- **CUDA Toolkit 11.8 o 12.1** (para GPU NVIDIA)

> ⚠️ **Nota**: SD3.5 Large requiere significativamente más VRAM que modelos anteriores. No se recomienda usar CPU.

## 🚀 Instalación

### Paso 1: Instalar Python

1. Descarga Python 3.10 o 3.11 desde [python.org](https://www.python.org/downloads/)
2. Durante la instalación, **marca la casilla "Add Python to PATH"**
3. Verifica la instalación abriendo PowerShell y ejecutando:
   ```powershell
   python --version
   ```

### Paso 2: Instalar CUDA (Solo para GPUs NVIDIA)

1. Verifica tu versión de driver NVIDIA:
   ```powershell
   nvidia-smi
   ```
2. Descarga CUDA Toolkit desde [nvidia.com/cuda-downloads](https://developer.nvidia.com/cuda-downloads)
3. Instala siguiendo las instrucciones

### Paso 3: Descargar el Modelo SD3.5 Large

1. Ve a [Hugging Face - Stable Diffusion 3.5 Large](https://huggingface.co/stabilityai/stable-diffusion-3.5-large)
2. Acepta la licencia de uso
3. Descarga los siguientes archivos a la carpeta `ia/sd3.5-main/models/`:
   - `clip_g.safetensors` (OpenCLIP bigG)
   - `clip_l.safetensors` (OpenAI CLIP-L)
   - `t5xxl.safetensors` (Google T5-v1.1-XXL)
   - `sd3.5_large.safetensors` (Modelo principal, ~9.8GB)
   - `sd3_vae.safetensors` (Opcional, VAE separado)

La estructura debe quedar así:
```
IGIA/
├── ia/
│   └── sd3.5-main/
│       ├── models/
│       │   ├── clip_g.safetensors
│       │   ├── clip_l.safetensors
│       │   ├── t5xxl.safetensors
│       │   ├── sd3.5_large.safetensors
│       │   └── sd3_vae.safetensors (opcional)
│       └── sd3_infer.py
└── ...
```

### Paso 3: Clonar/Descargar el Proyecto

Si tienes Git:
```powershell
git clone <url-del-repositorio>
cd IGIA
```

O simplemente descarga el ZIP y descomprímelo.

### Paso 4: Instalar Dependencias

Abre PowerShell en la carpeta del proyecto y ejecuta:

```powershell
# Crear entorno virtual (recomendado)
python -m venv venv

# Activar entorno virtual
.\venv\Scripts\Activate.ps1

# Si da error de permisos, ejecuta esto primero:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Instalar PyTorch con CUDA (si tienes GPU NVIDIA)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# Instalar el resto de dependencias
pip install -r requirements.txt
```

> ⏱️ **Nota**: La instalación puede tardar 10-20 minutos dependiendo de tu conexión.

## 🎮 Uso Básico

### Iniciar la Aplicación

```powershell
# Asegúrate de tener el entorno virtual activado
.\venv\Scripts\Activate.ps1

# Ejecutar la aplicación
python main.py
```

### Flujo de Trabajo

1. **Cargar el Modelo**
   - Haz clic en "🔄 Cargar Modelo IA"
   - Espera a que se cargue el modelo SD3.5 Large (puede tardar 1-2 minutos)
   - Verás "✅ SD3.5 Large cargado" cuando esté listo

2. **Configurar el Asset**
   - Selecciona una **Categoría** (personajes, mapas, items, etc.)
   - Escribe la **Descripción Específica** (ej: "warrior with blue armor and magic sword")
   - (Opcional) Selecciona un **Bioma** para contexto adicional

3. **Ajustar Parámetros**
   - **Resolución**: 512x512, 768x768, 1024x1024 (SD3.5 funciona mejor con resoluciones altas)
   - **Steps**: 40 recomendado para SD3.5 Large (balance calidad/velocidad)
   - **Guidance**: 4.5 recomendado para SD3.5 (el modelo funciona mejor con CFG bajo)
   - **Seed**: -1 para aleatorio, o un número fijo para reproducibilidad
   - **Cantidad**: Número de variaciones a generar

4. **Generar**
   - Haz clic en "🎨 GENERAR IMÁGENES"
   - Observa el progreso en el log
   - Las imágenes se guardarán en `output/` con su metadata

### Generación de Animaciones

1. Marca ☑️ **"Generar animación completa"**
2. Selecciona el tipo de animación (walk, attack, jump, etc.)
3. Describe el personaje base
4. Genera → Se crearán todos los frames de la animación

## 📁 Estructura del Proyecto

```
IGIA/
├── main.py                          # Aplicación principal
├── requirements.txt                 # Dependencias de Python
├── README.md                        # Este archivo
├── src/
│   ├── image_generator.py          # Motor de generación IA
│   └── prompt_manager.py           # Gestión de prompts y config
├── config/
│   └── prompts_templates.json      # Pre-prompts configurables
├── output/                          # Imágenes generadas (se crea automáticamente)
└── models/                          # Caché de modelos (se crea automáticamente)
```

## ⚙️ Configuración Avanzada

### Editar Pre-prompts

Los pre-prompts garantizan consistencia en tus assets. Cada categoría tiene:
- **Base**: Descripción fundamental del tipo de asset
- **Estilo**: Directivas de estilo artístico
- **Calidad**: Parámetros de calidad y formato

Para editar:
1. En la app, haz clic en "📝 Editar Pre-prompts"
2. Selecciona la categoría
3. Modifica los campos
4. Guarda

O edita directamente `config/prompts_templates.json`.

### Añadir Nuevas Animaciones

Edita `config/prompts_templates.json` en la sección `"animaciones"`:

```json
"personaje_custom": [
  "character custom pose 1",
  "character custom pose 2",
  "character custom pose 3"
]
```

### Añadir Nuevos Biomas

En `config/prompts_templates.json`, sección `"biomas"`:

```json
"espacio": "space environment, stars, cosmic background, sci-fi"
```

### Usar un Modelo Diferente

Por defecto usa `runwayml/stable-diffusion-v1-5`. Para cambiarlo, edita `src/image_generator.py`:

```python
# En la clase ImageGenerator.__init__()
model_path="stabilityai/stable-diffusion-2-1"  # O ruta local
```

Modelos recomendados para pixel art:
- `runwayml/stable-diffusion-v1-5` (default, buen balance)
- `stabilityai/stable-diffusion-2-1` (mejor calidad general)
- Modelos fine-tuned para pixel art de HuggingFace

## 🐛 Solución de Problemas

### "Error al cargar modelo"
- Verifica tu conexión a internet (primera vez)
- Asegúrate de tener espacio en disco (~10GB)
- Verifica que PyTorch esté instalado correctamente

### "Out of memory" / Error de VRAM
- Reduce la resolución (prueba 256x256 o menos)
- Reduce el batch size a 1
- Cierra otras aplicaciones que usen la GPU
- Edita `src/image_generator.py` y descomenta `enable_attention_slicing()`

### Generación muy lenta
- Si no tienes GPU NVIDIA, es normal (usa CPU)
- Reduce `num_inference_steps` a 30-40
- Verifica que CUDA esté instalado correctamente

### Las imágenes no se ven pixel art
- Ajusta tus pre-prompts para enfatizar "pixel art", "8-bit", "retro"
- Añade "3D, realistic, smooth" al negative prompt
- Usa resoluciones bajas (16x16, 32x32, 64x64)
- Considera usar un modelo fine-tuned para pixel art

## 🎨 Tips para Mejores Resultados

### Para Pixel Art
1. Usa resoluciones bajas (16x16 a 128x128)
2. Sé específico: "16x16 pixel art sprite, simple colors, clear outline"
3. Evita en negative prompt: "blurry, gradient, anti-aliased, 3D, realistic"
4. Usa guidance_scale entre 7-9

### Para Consistencia
1. Usa siempre el mismo pre-prompt para una serie
2. Fija el seed para variaciones del mismo personaje
3. Describe características clave: "blue armor, red cape, sword"
4. Usa biomas para contexto coherente

### Para Animaciones
1. Describe el personaje base de forma clara
2. Usa el mismo seed para todos los frames
3. Revisa que las poses tengan sentido secuencialmente
4. Considera generar frames individuales primero para probar

## 📝 Workflow Recomendado para Roguecat

1. **Define tu Paleta/Estilo**
   - Edita pre-prompts de "personajes" con tu estilo específico
   - Genera un personaje de prueba
   - Itera hasta conseguir el look deseado

2. **Crea Personaje Base**
   - Describe tu héroe: "cat warrior, blue tunic, sword"
   - Genera idle pose
   - Si te gusta, anota el seed

3. **Genera Animaciones**
   - Usa el mismo seed y descripción
   - Genera walk, attack, jump, etc.
   - Revisa coherencia

4. **Expande a Otros Assets**
   - Enemigos con mismo estilo (usa pre-prompts)
   - Items coherentes con el bioma
   - Tiles de mapa del mismo bioma

5. **Post-procesamiento**
   - Abre las imágenes en tu editor favorito
   - Ajusta paleta de colores si es necesario
   - Recorta/escala según necesites

## 📄 Licencia

Este proyecto es de código abierto. Los modelos de Stable Diffusion tienen sus propias licencias (generalmente CreativeML OpenRAIL).

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Si encuentras bugs o tienes ideas de mejora, abre un issue o pull request.

## 📧 Contacto

Proyecto creado para **Roguecat** - Un juego roguelike pixel art.

---

**¡Disfruta creando assets con IA! 🎮✨**
