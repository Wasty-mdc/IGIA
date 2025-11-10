"""
Generador de imágenes usando Stable Diffusion 3.5
Adaptador para usar el modelo SD3.5 con la interfaz de IGIA
"""
import os
import sys
import json
import torch
from datetime import datetime
from PIL import Image

# Agregar el directorio del modelo SD3.5 al path
SD3_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ia", "sd3.5-main")
sys.path.insert(0, SD3_PATH)

from sd3_infer import SD3Inferencer


class SD3ImageGenerator:
    """Generador de imágenes con Stable Diffusion 3.5"""
    
    def __init__(self, model_folder="models", device="auto"):
        """
        Inicializa el generador SD3.5
        
        Args:
            model_folder: Carpeta donde están los archivos del modelo
                         Debe contener: clip_g.safetensors, clip_l.safetensors, 
                         t5xxl.safetensors, sd3.5_large.safetensors
            device: 'cuda', 'cpu' o 'auto'
        """
        self.model_folder = model_folder
        self.device = self._get_device(device)
        self.inferencer = None
        self.is_loaded = False
        
        # Configuración por defecto para SD3.5 Large
        self.default_config = {
            "shift": 3.0,
            "steps": 40,
            "cfg": 4.5,
            "sampler": "dpmpp_2m",
            "width": 1024,
            "height": 1024
        }
        
    def _get_device(self, device):
        """Determina el dispositivo a usar"""
        if device == "auto":
            return "cuda" if torch.cuda.is_available() else "cpu"
        return device
    
    def load_model(self, callback=None):
        """
        Carga el modelo SD3.5
        
        Args:
            callback: Función para reportar progreso
        
        Returns:
            bool: True si se cargó correctamente
        """
        try:
            if callback:
                callback("Cargando Stable Diffusion 3.5...")
            
            # Verificar que existan los archivos necesarios
            required_files = [
                "clip_g.safetensors",
                "clip_l.safetensors", 
                "t5xxl.safetensors",
                "sd3.5_large.safetensors"
            ]
            
            missing_files = []
            for file in required_files:
                if not os.path.exists(os.path.join(self.model_folder, file)):
                    missing_files.append(file)
            
            if missing_files:
                error_msg = f"Archivos faltantes en {self.model_folder}:\n" + "\n".join(missing_files)
                if callback:
                    callback(error_msg)
                return False
            
            # Crear instancia del inferencer
            self.inferencer = SD3Inferencer()
            
            if callback:
                callback("Cargando encoders de texto...")
            
            # Cargar el modelo
            model_path = os.path.join(self.model_folder, "sd3.5_large.safetensors")
            vae_path = os.path.join(self.model_folder, "sd3_vae.safetensors")
            
            # Si no existe VAE separado, usar el mismo archivo del modelo
            if not os.path.exists(vae_path):
                vae_path = None
            
            # Determinar dispositivo para encoders de texto
            text_encoder_device = self.device if self.device == "cuda" else "cpu"
            
            self.inferencer.load(
                model=model_path,
                vae=vae_path,
                shift=self.default_config["shift"],
                controlnet_ckpt=None,
                model_folder=self.model_folder,
                text_encoder_device=text_encoder_device,
                verbose=False,
                load_tokenizers=True
            )
            
            self.is_loaded = True
            
            if callback:
                callback(f"✓ Modelo SD3.5 Large cargado en {self.device}")
            
            return True
            
        except Exception as e:
            if callback:
                callback(f"✗ Error al cargar modelo: {str(e)}")
            return False
    
    def generate_image(self, prompt, negative_prompt="", width=1024, height=1024,
                      num_inference_steps=40, guidance_scale=4.5, seed=-1):
        """
        Genera una imagen usando el prompt proporcionado
        
        Args:
            prompt: Texto descriptivo de la imagen
            negative_prompt: No usado en SD3.5 (usa prompt vacío internamente)
            width: Ancho de la imagen (múltiplo de 64, recomendado 1024)
            height: Alto de la imagen (múltiplo de 64, recomendado 1024)
            num_inference_steps: Pasos de inferencia (40 recomendado para SD3.5 Large)
            guidance_scale: CFG scale (4.5 recomendado para SD3.5 Large)
            seed: Semilla para reproducibilidad (-1 = aleatorio)
            
        Returns:
            tuple: (PIL.Image, dict) - Imagen generada y metadata
        """
        if not self.is_loaded:
            raise Exception("El modelo no está cargado. Llama a load_model() primero.")
        
        # Configurar semilla
        if seed < 0:
            seed = torch.randint(0, 100000, (1,)).item()
        
        # Preparar latent vacío
        latent = self.inferencer.get_empty_latent(1, width, height, seed, "cpu")
        latent = latent.cuda() if self.device == "cuda" else latent
        
        # Obtener condicionamiento
        conditioning = self.inferencer.get_cond(prompt)
        neg_cond = self.inferencer.get_cond("")  # SD3.5 usa prompt vacío en lugar de negative
        
        # Sampling
        sampled_latent = self.inferencer.do_sampling(
            latent=latent,
            seed=seed,
            conditioning=conditioning,
            neg_cond=neg_cond,
            steps=num_inference_steps,
            cfg_scale=guidance_scale,
            sampler=self.default_config["sampler"],
            controlnet_cond=None,
            denoise=1.0,
            skip_layer_config={}
        )
        
        # Decodificar a imagen
        image = self.inferencer.vae_decode(sampled_latent)
        
        # Preparar metadata
        metadata = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,  # Guardado para compatibilidad
            "width": width,
            "height": height,
            "steps": num_inference_steps,
            "guidance_scale": guidance_scale,
            "seed": seed,
            "model": "SD3.5 Large",
            "sampler": self.default_config["sampler"],
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
                    width=custom_params.get("width", 1024),
                    height=custom_params.get("height", 1024),
                    num_inference_steps=custom_params.get("num_inference_steps", 40),
                    guidance_scale=custom_params.get("guidance_scale", 4.5),
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
        if self.inferencer is not None:
            # Limpiar modelos
            if hasattr(self.inferencer, 'sd3'):
                del self.inferencer.sd3
            if hasattr(self.inferencer, 'vae'):
                del self.inferencer.vae
            if hasattr(self.inferencer, 'clip_l'):
                del self.inferencer.clip_l
            if hasattr(self.inferencer, 'clip_g'):
                del self.inferencer.clip_g
            if hasattr(self.inferencer, 't5xxl'):
                del self.inferencer.t5xxl
            
            del self.inferencer
            self.inferencer = None
            
            # Limpiar cache de CUDA
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            self.is_loaded = False
