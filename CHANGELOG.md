# 🔄 CAMBIOS REALIZADOS EN IGIA

## Resumen de Modificaciones

Se ha actualizado completamente IGIA para usar **Stable Diffusion 3.5 Large** en lugar de Stable Diffusion 1.5.

---

## 📝 Archivos Modificados

### 1. **src/sd3_generator.py** (NUEVO)
- Nueva clase `SD3ImageGenerator` que integra el modelo SD3.5
- Usa la implementación de `ia/sd3.5-main/sd3_infer.py`
- Mantiene la misma interfaz que el generador anterior para compatibilidad con la GUI
- Métodos principales:
  - `load_model()`: Carga SD3.5 Large con todos sus componentes
  - `generate_image()`: Genera una imagen individual
  - `generate_batch()`: Genera múltiples imágenes en serie

### 2. **main.py** (MODIFICADO)
- Cambiado import de `ImageGenerator` a `SD3ImageGenerator`
- Actualizada función `load_model()` para cargar SD3.5
- Ajustados valores por defecto de parámetros:
  - Resolución: 512x512 → **1024x1024**
  - Steps: 50 → **40**
  - Guidance Scale: 7.5 → **4.5**
  - Opciones de resolución adaptadas a SD3.5

### 3. **requirements.txt** (MODIFICADO)
- Eliminado: `diffusers`, `accelerate` (no necesarios para SD3.5)
- Agregado: `fire`, `tqdm` (requeridos por sd3_infer.py)
- Mantenido: `torch`, `safetensors`, `transformers`, `Pillow`, `numpy`

### 4. **config/prompts_templates.json** (MODIFICADO)
- Optimizados pre-prompts para SD3.5
- Lenguaje más natural (SD3.5 entiende mejor el lenguaje natural)
- Removidos keywords spam innecesarios
- Mejoradas descripciones para pixel art y assets de juego

### 5. **config/model_config.json** (NUEVO)
- Configuración de rutas de modelos SD3.5
- Parámetros por defecto optimizados
- Instrucciones de descarga y setup
- Configuraciones de resolución recomendadas

### 6. **README.md** (MODIFICADO)
- Actualizado para SD3.5 Large
- Requisitos de hardware actualizados (12GB VRAM mínimo)
- Instrucciones de descarga del modelo desde Hugging Face
- Guía de instalación de PyTorch con CUDA
- Parámetros recomendados para SD3.5

### 7. **SETUP_GUIDE.md** (NUEVO)
- Guía completa de configuración paso a paso
- Verificación de instalación
- Solución de problemas comunes
- Optimización de parámetros según GPU
- Consejos para mejores resultados
- Tiempos de generación esperados por GPU

### 8. **verify_setup.py** (NUEVO)
- Script de verificación automática
- Chequea Python, PyTorch, CUDA
- Verifica archivos del modelo
- Valida estructura del proyecto
- Reporta estado completo del sistema

---

## 🔑 Cambios Clave en la Lógica

### Antes (SD1.5 con Diffusers)
```python
from diffusers import StableDiffusionPipeline
pipe = StableDiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5")
image = pipe(prompt=prompt, negative_prompt=neg, ...)
```

### Ahora (SD3.5 con implementación nativa)
```python
from sd3_infer import SD3Inferencer
inferencer = SD3Inferencer()
inferencer.load(model, vae, shift, ...)
latent = inferencer.get_empty_latent(...)
conditioning = inferencer.get_cond(prompt)
sampled = inferencer.do_sampling(...)
image = inferencer.vae_decode(sampled)
```

---

## ⚙️ Diferencias Técnicas Importantes

| Aspecto | SD1.5 (Anterior) | SD3.5 (Actual) |
|---------|------------------|----------------|
| **Modelo** | Stable Diffusion 1.5 | Stable Diffusion 3.5 Large |
| **Tamaño** | ~4GB | ~17GB (todos los componentes) |
| **VRAM Mínimo** | 6GB | 12GB |
| **Encoders de texto** | CLIP-L | CLIP-L + CLIP-G + T5-XXL |
| **Resolución nativa** | 512x512 | 1024x1024 |
| **CFG Scale óptimo** | 7-8 | 4-5 |
| **Steps recomendados** | 50 | 40 |
| **Negative prompts** | Efectivos | Menos efectivos (usa prompt vacío) |
| **Comprensión** | Keywords | Lenguaje natural |

---

## 📦 Estructura de Archivos del Modelo

Necesitas descargar y colocar en `ia/sd3.5-main/models/`:

```
models/
├── clip_g.safetensors          # 1.4GB - OpenCLIP bigG
├── clip_l.safetensors          # 246MB - OpenAI CLIP-L  
├── t5xxl.safetensors           # 4.9GB - Google T5-v1.1-XXL
├── sd3.5_large.safetensors     # 9.8GB - Modelo principal MMDiT
└── sd3_vae.safetensors         # 335MB - VAE (opcional)
```

**Descargar desde:** https://huggingface.co/stabilityai/stable-diffusion-3.5-large

---

## 🚀 Próximos Pasos

1. **Descargar archivos del modelo** desde Hugging Face
2. **Instalar dependencias:**
   ```powershell
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
   pip install -r requirements.txt
   ```
3. **Verificar instalación:**
   ```powershell
   python verify_setup.py
   ```
4. **Ejecutar aplicación:**
   ```powershell
   python main.py
   ```

---

## ⚠️ Notas Importantes

### Compatibilidad hacia atrás
- El archivo `src/image_generator.py` (SD1.5) se mantiene pero ya no se usa
- Puedes volver a usarlo cambiando el import en `main.py` si es necesario

### Rendimiento
- SD3.5 es más lento que SD1.5 pero genera imágenes de mucho mayor calidad
- Tiempo típico en RTX 3080: ~30-40s por imagen 1024x1024
- Requiere significativamente más VRAM

### Calidad
- SD3.5 entiende mucho mejor los prompts naturales
- Mejor coherencia en pixel art y assets de juego
- Menos necesidad de keywords spam
- Mejor composición y detalles

---

## 🐛 Problemas Conocidos y Soluciones

### "CUDA out of memory"
- Reduce resolución (1024→768)
- Cierra otras aplicaciones
- Verifica que no haya múltiples procesos Python

### Carga lenta del modelo
- Normal, tarda 1-2 minutos la primera vez
- Los encoders de texto (T5-XXL) son grandes

### Resultados no esperados
- Ajusta guidance scale (prueba 3.5-5.5)
- Usa prompts más descriptivos
- Prueba diferentes seeds

---

**Fecha de actualización:** 2025-11-10  
**Versión:** 2.0 (SD3.5)
