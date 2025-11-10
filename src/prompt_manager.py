"""
Utilidades para manejar prompts y configuración
"""
import json
import os


class PromptManager:
    """Gestiona los pre-prompts y templates de configuración"""
    
    def __init__(self, config_path="config/prompts_templates.json"):
        self.config_path = config_path
        self.config = {}
        self.load_config()
    
    def load_config(self):
        """Carga la configuración desde el archivo JSON"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            return True
        except FileNotFoundError:
            print(f"Archivo de configuración no encontrado: {self.config_path}")
            self.config = self._get_default_config()
            return False
        except json.JSONDecodeError as e:
            print(f"Error al parsear JSON: {e}")
            return False
    
    def save_config(self):
        """Guarda la configuración actual al archivo JSON"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error al guardar configuración: {e}")
            return False
    
    def get_preprompt(self, categoria):
        """
        Obtiene el pre-prompt completo para una categoría
        
        Args:
            categoria: 'personajes', 'mapas', 'items', etc.
            
        Returns:
            str: Pre-prompt combinado
        """
        preprompts = self.config.get("preprompts", {})
        cat_data = preprompts.get(categoria, {})
        
        # Combinar base + estilo + calidad
        parts = [
            cat_data.get("base", ""),
            cat_data.get("estilo", ""),
            cat_data.get("calidad", "")
        ]
        
        return ", ".join([p for p in parts if p])
    
    def build_full_prompt(self, categoria, descripcion_especifica, bioma=None):
        """
        Construye un prompt completo combinando pre-prompt + descripción
        
        Args:
            categoria: Categoría del pre-prompt
            descripcion_especifica: Descripción específica del asset
            bioma: Bioma opcional para agregar contexto
            
        Returns:
            str: Prompt completo
        """
        preprompt = self.get_preprompt(categoria)
        
        parts = [preprompt, descripcion_especifica]
        
        # Agregar bioma si existe
        if bioma:
            biomas = self.config.get("biomas", {})
            bioma_desc = biomas.get(bioma, "")
            if bioma_desc:
                parts.append(bioma_desc)
        
        return ", ".join([p for p in parts if p])
    
    def get_animation_prompts(self, tipo_animacion, categoria="personajes", 
                             descripcion_base="", bioma=None):
        """
        Genera lista de prompts para una animación completa
        
        Args:
            tipo_animacion: Clave de animación ('personaje_walk', 'personaje_attack', etc.)
            categoria: Categoría del pre-prompt
            descripcion_base: Descripción base del personaje
            bioma: Bioma opcional
            
        Returns:
            List[str]: Lista de prompts para cada frame
        """
        animaciones = self.config.get("animaciones", {})
        frames = animaciones.get(tipo_animacion, [])
        
        prompts = []
        for frame_desc in frames:
            # Combinar descripción base + frame específico
            full_desc = f"{descripcion_base}, {frame_desc}" if descripcion_base else frame_desc
            full_prompt = self.build_full_prompt(categoria, full_desc, bioma)
            prompts.append(full_prompt)
        
        return prompts
    
    def get_default_params(self):
        """Obtiene los parámetros por defecto de generación"""
        return self.config.get("configuracion_default", {
            "negative_prompt": "blurry, 3D, realistic",
            "num_inference_steps": 50,
            "guidance_scale": 7.5,
            "seed": -1
        })
    
    def get_categories(self):
        """Obtiene lista de categorías disponibles"""
        return list(self.config.get("preprompts", {}).keys())
    
    def get_animations(self):
        """Obtiene lista de animaciones disponibles"""
        return list(self.config.get("animaciones", {}).keys())
    
    def get_biomas(self):
        """Obtiene lista de biomas disponibles"""
        return list(self.config.get("biomas", {}).keys())
    
    def update_preprompt(self, categoria, campo, valor):
        """Actualiza un campo de un pre-prompt"""
        if "preprompts" not in self.config:
            self.config["preprompts"] = {}
        if categoria not in self.config["preprompts"]:
            self.config["preprompts"][categoria] = {}
        
        self.config["preprompts"][categoria][campo] = valor
        return self.save_config()
    
    def _get_default_config(self):
        """Retorna configuración por defecto si no existe archivo"""
        return {
            "preprompts": {
                "personajes": {
                    "base": "pixel art character sprite",
                    "estilo": "retro gaming style",
                    "calidad": "high quality pixel art"
                }
            },
            "animaciones": {},
            "biomas": {},
            "configuracion_default": {
                "negative_prompt": "blurry, 3D, realistic",
                "num_inference_steps": 50,
                "guidance_scale": 7.5,
                "seed": -1
            }
        }
