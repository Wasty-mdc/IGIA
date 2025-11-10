"""
Módulo para generación de imágenes con Stable Diffusion local
"""
import os
import json
import torch
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
from PIL import Image
import random
from datetime import datetime


class ImageGenerator:
    """Generador de imágenes con IA local usando Stable Diffusion"""
    
    def __init__(self, model_path="runwayml/stable-diffusion-v1-5", device="auto"):
        """
        Inicializa el generador de imágenes
        
        Args:
            model_path: Ruta al modelo (local o HuggingFace)
            device: 'cuda', 'cpu' o 'auto'
        """
        self.model_path = model_path
        self.device = self._get_device(device)
        self.pipe = None
        self.is_loaded = False
        
    def _get_device(self, device):
        """Determina el dispositivo a usar"""
        if device == "auto":
            return "cuda" if torch.cuda.is_available() else "cpu"
        return device
    
    def load_model(self, callback=None):
        """
        Carga el modelo de Stable Diffusion
        
        Args:
            callback: Función para reportar progreso
        """
        try:
            if callback:
                callback("Cargando modelo de Stable Diffusion...")
            
            # Configurar para usar menos VRAM si es CUDA
            torch_dtype = torch.float16 if self.device == "cuda" else torch.float32
            
            self.pipe = StableDiffusionPipeline.from_pretrained(
                self.model_path,
                torch_dtype=torch_dtype,
                safety_checker=None,  # Desactivar para velocidad
                requires_safety_checker=False
            )
            
            # Optimizar el scheduler para mejor calidad/velocidad
            self.pipe.scheduler = DPMSolverMultistepScheduler.from_config(
                self.pipe.scheduler.config
            )
            
            self.pipe = self.pipe.to(self.device)
            
            # Optimizaciones adicionales
            if self.device == "cuda":
                self.pipe.enable_attention_slicing()
                # self.pipe.enable_xformers_memory_efficient_attention()  # Descomentar si tienes xformers
            
            self.is_loaded = True
            
            if callback:
                callback(f"Modelo cargado correctamente en {self.device}")
            
            return True
            
        except Exception as e:
            if callback:
                callback(f"Error al cargar modelo: {str(e)}")
            return False
    
    def generate_image(self, prompt, negative_prompt="", width=512, height=512,
                      num_inference_steps=50, guidance_scale=7.5, seed=-1):
        """
        Genera una imagen usando el prompt proporcionado
        
        Args:
            prompt: Texto descriptivo de la imagen
            negative_prompt: Cosas a evitar en la imagen
            width: Ancho de la imagen
            height: Alto de la imagen
            num_inference_steps: Pasos de inferencia (más = mejor calidad pero más lento)
            guidance_scale: Qué tan estricto seguir el prompt (7-9 recomendado)
            seed: Semilla para reproducibilidad (-1 = aleatorio)
            
        Returns:
            PIL.Image: Imagen generada
        """
        if not self.is_loaded:
            raise Exception("El modelo no está cargado. Llama a load_model() primero.")
        
        # Configurar semilla
        generator = None
        if seed >= 0:
            generator = torch.Generator(device=self.device).manual_seed(seed)
        else:
            seed = random.randint(0, 2**32 - 1)
            generator = torch.Generator(device=self.device).manual_seed(seed)
        
        # Generar imagen
        with torch.no_grad():
            result = self.pipe(
                prompt=prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
                generator=generator
            )
        
        image = result.images[0]
        
        # Guardar metadata
        metadata = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "width": width,
            "height": height,
            "steps": num_inference_steps,
            "guidance_scale": guidance_scale,
            "seed": seed,
            "timestamp": datetime.now().isoformat()
        }
        
        return image, metadata
    
    def generate_batch(self, prompts_list, base_params, output_dir, 
                      name_prefix="sprite", callback=None):
        """
        Genera múltiples imágenes en serie
        
        Args:
            prompts_list: Lista de prompts a generar
            base_params: Parámetros base (negative_prompt, width, height, etc.)
            output_dir: Directorio donde guardar las imágenes
            name_prefix: Prefijo para los nombres de archivo
            callback: Función para reportar progreso (recibe: índice, total, mensaje)
            
        Returns:
            List[str]: Rutas a las imágenes generadas
        """
        os.makedirs(output_dir, exist_ok=True)
        generated_files = []
        
        total = len(prompts_list)
        
        for idx, prompt_data in enumerate(prompts_list):
            try:
                # Combinar prompt con parámetros
                if isinstance(prompt_data, dict):
                    full_prompt = prompt_data.get("prompt", "")
                    custom_params = {**base_params, **prompt_data.get("params", {})}
                else:
                    full_prompt = str(prompt_data)
                    custom_params = base_params
                
                if callback:
                    callback(idx + 1, total, f"Generando: {full_prompt[:50]}...")
                
                # Generar imagen
                image, metadata = self.generate_image(
                    prompt=full_prompt,
                    negative_prompt=custom_params.get("negative_prompt", ""),
                    width=custom_params.get("width", 512),
                    height=custom_params.get("height", 512),
                    num_inference_steps=custom_params.get("num_inference_steps", 50),
                    guidance_scale=custom_params.get("guidance_scale", 7.5),
                    seed=custom_params.get("seed", -1)
                )
                
                # Guardar imagen
                filename = f"{name_prefix}_{idx+1:03d}.png"
                filepath = os.path.join(output_dir, filename)
                image.save(filepath)
                
                # Guardar metadata
                metadata_path = os.path.join(output_dir, f"{name_prefix}_{idx+1:03d}_metadata.json")
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)
                
                generated_files.append(filepath)
                
                if callback:
                    callback(idx + 1, total, f"✓ Guardado: {filename}")
                
            except Exception as e:
                if callback:
                    callback(idx + 1, total, f"✗ Error: {str(e)}")
        
        return generated_files
    
    def unload_model(self):
        """Descarga el modelo de la memoria"""
        if self.pipe is not None:
            del self.pipe
            self.pipe = None
            torch.cuda.empty_cache() if torch.cuda.is_available() else None
            self.is_loaded = False
