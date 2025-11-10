# Guía de Configuración - IGIA con SD3.5

## ✅ Verificación de Instalación

Antes de empezar, verifica que todo esté correctamente instalado:

### 1. Verificar Python
```powershell
python --version
# Debe mostrar: Python 3.10.x o 3.11.x
```

### 2. Verificar CUDA (GPU NVIDIA)
```powershell
nvidia-smi
# Debe mostrar información de tu GPU y versión de CUDA
```

### 3. Verificar PyTorch con CUDA
```powershell
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA disponible: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else None}')"
```

Debe mostrar algo como:
```
PyTorch: 2.x.x+cu118
CUDA disponible: True
GPU: NVIDIA GeForce RTX 3080
```

## 📁 Estructura de Archivos del Modelo

Asegúrate de que la carpeta `ia/sd3.5-main/models/` contenga:

```
models/
├── clip_g.safetensors          (~1.4GB)
├── clip_l.safetensors          (~246MB)
├── t5xxl.safetensors           (~4.9GB)
├── sd3.5_large.safetensors     (~9.8GB)
└── sd3_vae.safetensors         (~335MB, opcional)
```

Total: ~16.6GB de modelos

## ⚙️ Configuración de Parámetros

### Parámetros Recomendados para SD3.5 Large

| Parámetro | Valor Recomendado | Rango | Notas |
|-----------|------------------|-------|-------|
| **Resolución** | 1024x1024 | 512-1536 | Múltiplos de 64 |
| **Steps** | 40 | 28-50 | Más steps = mejor calidad |
| **Guidance Scale** | 4.5 | 3.5-5.5 | SD3.5 funciona mejor con CFG bajo |
| **Sampler** | dpmpp_2m | - | Por defecto |

### Ajustes según GPU

#### GPU con 12GB VRAM (RTX 3060/4070)
- Resolución máxima: 1024x1024
- Si hay problemas de memoria: reduce a 768x768

#### GPU con 16GB+ VRAM (RTX 3080/4080/4090)
- Resolución máxima: 1536x1536
- Puedes usar las resoluciones que necesites

#### GPU con menos de 12GB
- SD3.5 Large probablemente no funcionará
- Considera usar SD1.5 o SD2.1 (cambiar código)

## 🎨 Optimización de Prompts para SD3.5

SD3.5 tiene mejor comprensión del lenguaje natural que modelos anteriores.

### ✅ Buenos Prompts
```
pixel art sprite of a brave knight with blue armor, holding a golden sword, transparent background, game asset
```

```
2D top-down dungeon tileset, stone walls with moss, torch lighting, fantasy roguelike game
```

```
pixel art potion bottle, glowing red liquid, corked glass container, game item icon
```

### ❌ Evitar
- Prompts muy cortos: "knight" (demasiado vago)
- Negative prompts excesivos (SD3.5 no los usa bien)
- Keywords spam: "8k, uhd, hd, 4k, best quality" (innecesario)

## 🔧 Solución de Problemas

### Error: "CUDA out of memory"
**Solución:**
1. Reduce la resolución (1024→768→512)
2. Cierra otras aplicaciones que usen GPU
3. Reinicia la aplicación

### Error: "Archivos del modelo no encontrados"
**Solución:**
1. Verifica que los archivos estén en `ia/sd3.5-main/models/`
2. Revisa que los nombres sean exactos (distingue mayúsculas/minúsculas)
3. Verifica que los archivos no estén corruptos (tamaños correctos)

### La generación es muy lenta
**Causas posibles:**
- Usando CPU en lugar de GPU
- GPU de bajo rendimiento
- Resolución muy alta

**Soluciones:**
- Verifica CUDA: `torch.cuda.is_available()` debe ser True
- Reduce steps (40→30→28)
- Reduce resolución

### Resultados de baja calidad
**Soluciones:**
- Aumenta steps (40→50)
- Mejora el prompt (más descriptivo)
- Prueba diferentes seeds
- Ajusta guidance scale (prueba 3.5-5.5)

## 📊 Tiempos de Generación Esperados

| GPU | Resolución | Steps | Tiempo Aprox. |
|-----|-----------|-------|---------------|
| RTX 4090 | 1024x1024 | 40 | 15-20s |
| RTX 4080 | 1024x1024 | 40 | 20-25s |
| RTX 3090 | 1024x1024 | 40 | 25-35s |
| RTX 3080 | 1024x1024 | 40 | 30-40s |
| RTX 4070 Ti | 1024x1024 | 40 | 25-30s |
| RTX 3060 12GB | 1024x1024 | 40 | 50-70s |
| RTX 3060 12GB | 768x768 | 30 | 30-40s |

## 🎯 Consejos para Mejores Resultados

1. **Sé específico en los prompts**: Describe colores, poses, detalles
2. **Usa el sistema de categorías**: Los pre-prompts ayudan a la consistencia
3. **Experimenta con seeds**: Encuentra seeds que den buenos resultados
4. **Genera en lotes**: Usa cantidad > 1 para obtener variaciones
5. **Guarda los metadata**: Te ayudarán a reproducir buenos resultados

## 📝 Personalización de Pre-prompts

Edita `config/prompts_templates.json` para ajustar los pre-prompts a tu estilo:

```json
{
  "preprompts": {
    "personajes": {
      "base": "Tu descripción base aquí",
      "estilo": "Tu estilo artístico",
      "calidad": "Términos de calidad"
    }
  }
}
```

Reinicia la aplicación después de editar.

## 🔄 Actualización del Modelo

Si Stability AI lanza una nueva versión de SD3.5:

1. Descarga los nuevos archivos
2. Reemplaza en `ia/sd3.5-main/models/`
3. Actualiza `config/model_config.json` si es necesario
4. Reinicia la aplicación

---

**¿Necesitas ayuda?** Revisa los logs en la aplicación o consulta la documentación de SD3.5 en Hugging Face.
