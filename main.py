"""
Interfaz gráfica principal para IGIA - Generador de imágenes con IA
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
import os
import json
from datetime import datetime
from PIL import Image, ImageTk

from src.image_generator import ImageGenerator
from src.prompt_manager import PromptManager


class IGIAApp:
    """Aplicación principal con interfaz gráfica"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("IGIA - Generador IA para Roguecat")
        self.root.geometry("1200x800")
        
        # Managers
        self.prompt_manager = PromptManager()
        self.image_generator = None
        self.is_generating = False
        
        # Variables
        self.selected_category = tk.StringVar(value="personajes")
        self.selected_animation = tk.StringVar()
        self.selected_bioma = tk.StringVar(value="ninguno")
        self.resolution = tk.StringVar(value="512x512")
        self.batch_size = tk.IntVar(value=1)
        
        # Crear interfaz
        self.create_ui()
        
        # Actualizar listas
        self.update_categories()
    
    def create_ui(self):
        """Crea la interfaz de usuario"""
        
        # Frame principal con dos paneles
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Panel izquierdo - Configuración
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=1)
        
        # Panel derecho - Preview y log
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=1)
        
        # ===== PANEL IZQUIERDO =====
        
        # Sección: Modelo
        model_frame = ttk.LabelFrame(left_frame, text="⚙ Configuración del Modelo", padding=10)
        model_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(model_frame, text="🔄 Cargar Modelo IA", 
                  command=self.load_model).pack(fill=tk.X, pady=2)
        
        self.model_status = ttk.Label(model_frame, text="Modelo no cargado", 
                                     foreground="orange")
        self.model_status.pack(pady=2)
        
        # Sección: Categoría y Pre-prompts
        category_frame = ttk.LabelFrame(left_frame, text="📁 Categoría", padding=10)
        category_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.category_combo = ttk.Combobox(category_frame, 
                                          textvariable=self.selected_category,
                                          state="readonly")
        self.category_combo.pack(fill=tk.X, pady=2)
        self.category_combo.bind("<<ComboboxSelected>>", self.on_category_change)
        
        ttk.Button(category_frame, text="📝 Editar Pre-prompts", 
                  command=self.edit_preprompts).pack(fill=tk.X, pady=2)
        
        # Sección: Descripción específica
        desc_frame = ttk.LabelFrame(left_frame, text="✏ Descripción Específica", padding=10)
        desc_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Label(desc_frame, text="Describe el asset que quieres generar:").pack(anchor=tk.W)
        
        self.desc_text = scrolledtext.ScrolledText(desc_frame, height=4, wrap=tk.WORD)
        self.desc_text.pack(fill=tk.BOTH, expand=True, pady=5)
        self.desc_text.insert("1.0", "warrior character with blue armor and sword")
        
        # Sección: Animaciones
        anim_frame = ttk.LabelFrame(left_frame, text="🎬 Animaciones (Opcional)", padding=10)
        anim_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.use_animation = tk.BooleanVar(value=False)
        ttk.Checkbutton(anim_frame, text="Generar animación completa", 
                       variable=self.use_animation,
                       command=self.toggle_animation).pack(anchor=tk.W)
        
        self.animation_combo = ttk.Combobox(anim_frame, 
                                           textvariable=self.selected_animation,
                                           state="disabled")
        self.animation_combo.pack(fill=tk.X, pady=2)
        
        # Sección: Bioma
        bioma_frame = ttk.LabelFrame(left_frame, text="🌍 Bioma/Contexto", padding=10)
        bioma_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.bioma_combo = ttk.Combobox(bioma_frame, 
                                       textvariable=self.selected_bioma,
                                       state="readonly")
        self.bioma_combo.pack(fill=tk.X)
        
        # Sección: Parámetros de generación
        params_frame = ttk.LabelFrame(left_frame, text="⚡ Parámetros de Generación", padding=10)
        params_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Resolución
        ttk.Label(params_frame, text="Resolución:").grid(row=0, column=0, sticky=tk.W, pady=2)
        resolutions = ["16x16", "32x32", "64x64", "128x128", "256x256", "512x512"]
        res_combo = ttk.Combobox(params_frame, textvariable=self.resolution, 
                                values=resolutions, state="readonly", width=15)
        res_combo.grid(row=0, column=1, sticky=tk.W, pady=2)
        
        # Steps
        ttk.Label(params_frame, text="Steps:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.steps_var = tk.IntVar(value=50)
        steps_spin = ttk.Spinbox(params_frame, from_=20, to=150, 
                                textvariable=self.steps_var, width=15)
        steps_spin.grid(row=1, column=1, sticky=tk.W, pady=2)
        
        # Guidance Scale
        ttk.Label(params_frame, text="Guidance:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.guidance_var = tk.DoubleVar(value=7.5)
        guidance_spin = ttk.Spinbox(params_frame, from_=1.0, to=20.0, increment=0.5,
                                   textvariable=self.guidance_var, width=15)
        guidance_spin.grid(row=2, column=1, sticky=tk.W, pady=2)
        
        # Seed
        ttk.Label(params_frame, text="Seed (-1=random):").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.seed_var = tk.IntVar(value=-1)
        seed_spin = ttk.Spinbox(params_frame, from_=-1, to=999999, 
                               textvariable=self.seed_var, width=15)
        seed_spin.grid(row=3, column=1, sticky=tk.W, pady=2)
        
        # Cantidad en batch
        ttk.Label(params_frame, text="Cantidad:").grid(row=4, column=0, sticky=tk.W, pady=2)
        batch_spin = ttk.Spinbox(params_frame, from_=1, to=50, 
                                textvariable=self.batch_size, width=15)
        batch_spin.grid(row=4, column=1, sticky=tk.W, pady=2)
        
        # Botón de generación
        gen_button_frame = ttk.Frame(left_frame)
        gen_button_frame.pack(fill=tk.X, padx=5, pady=10)
        
        self.gen_button = ttk.Button(gen_button_frame, text="🎨 GENERAR IMÁGENES", 
                                     command=self.generate_images)
        self.gen_button.pack(fill=tk.X, ipady=10)
        
        # ===== PANEL DERECHO =====
        
        # Preview de prompt final
        prompt_preview_frame = ttk.LabelFrame(right_frame, text="👁 Preview del Prompt", padding=10)
        prompt_preview_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.prompt_preview = scrolledtext.ScrolledText(prompt_preview_frame, 
                                                        height=6, wrap=tk.WORD,
                                                        state=tk.DISABLED)
        self.prompt_preview.pack(fill=tk.X)
        
        ttk.Button(prompt_preview_frame, text="🔄 Actualizar Preview", 
                  command=self.update_prompt_preview).pack(fill=tk.X, pady=5)
        
        # Log de generación
        log_frame = ttk.LabelFrame(right_frame, text="📋 Log de Generación", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(log_frame, variable=self.progress_var, 
                                           maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        # Botones de utilidad
        util_frame = ttk.Frame(right_frame)
        util_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(util_frame, text="📂 Abrir carpeta output", 
                  command=self.open_output_folder).pack(side=tk.LEFT, padx=2)
        ttk.Button(util_frame, text="🗑 Limpiar log", 
                  command=self.clear_log).pack(side=tk.LEFT, padx=2)
    
    def update_categories(self):
        """Actualiza las listas de categorías, animaciones y biomas"""
        categories = self.prompt_manager.get_categories()
        self.category_combo['values'] = categories
        if categories:
            self.selected_category.set(categories[0])
        
        animations = self.prompt_manager.get_animations()
        self.animation_combo['values'] = animations
        if animations:
            self.selected_animation.set(animations[0])
        
        biomas = ["ninguno"] + self.prompt_manager.get_biomas()
        self.bioma_combo['values'] = biomas
        self.selected_bioma.set("ninguno")
    
    def on_category_change(self, event=None):
        """Callback cuando cambia la categoría"""
        self.update_prompt_preview()
    
    def toggle_animation(self):
        """Activa/desactiva el selector de animaciones"""
        if self.use_animation.get():
            self.animation_combo['state'] = 'readonly'
        else:
            self.animation_combo['state'] = 'disabled'
    
    def load_model(self):
        """Carga el modelo de IA en un thread separado"""
        if self.image_generator and self.image_generator.is_loaded:
            messagebox.showinfo("Info", "El modelo ya está cargado")
            return
        
        def load_thread():
            self.log("🔄 Iniciando carga del modelo...")
            self.model_status.config(text="Cargando...", foreground="orange")
            
            self.image_generator = ImageGenerator()
            
            success = self.image_generator.load_model(callback=self.log)
            
            if success:
                self.log("✅ Modelo cargado correctamente")
                self.model_status.config(text="✅ Modelo cargado", foreground="green")
            else:
                self.log("❌ Error al cargar el modelo")
                self.model_status.config(text="❌ Error", foreground="red")
        
        thread = threading.Thread(target=load_thread, daemon=True)
        thread.start()
    
    def edit_preprompts(self):
        """Abre ventana para editar pre-prompts"""
        editor_window = tk.Toplevel(self.root)
        editor_window.title("Editar Pre-prompts")
        editor_window.geometry("600x400")
        
        # Frame para selección de categoría
        top_frame = ttk.Frame(editor_window, padding=10)
        top_frame.pack(fill=tk.X)
        
        ttk.Label(top_frame, text="Categoría:").pack(side=tk.LEFT)
        
        cat_var = tk.StringVar(value=self.selected_category.get())
        cat_combo = ttk.Combobox(top_frame, textvariable=cat_var,
                                values=self.prompt_manager.get_categories(),
                                state="readonly")
        cat_combo.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Frame para campos
        fields_frame = ttk.Frame(editor_window, padding=10)
        fields_frame.pack(fill=tk.BOTH, expand=True)
        
        # Campos de texto
        ttk.Label(fields_frame, text="Base:").pack(anchor=tk.W)
        base_text = scrolledtext.ScrolledText(fields_frame, height=4)
        base_text.pack(fill=tk.X, pady=2)
        
        ttk.Label(fields_frame, text="Estilo:").pack(anchor=tk.W)
        estilo_text = scrolledtext.ScrolledText(fields_frame, height=4)
        estilo_text.pack(fill=tk.X, pady=2)
        
        ttk.Label(fields_frame, text="Calidad:").pack(anchor=tk.W)
        calidad_text = scrolledtext.ScrolledText(fields_frame, height=4)
        calidad_text.pack(fill=tk.X, pady=2)
        
        def load_preprompt():
            """Carga el pre-prompt de la categoría seleccionada"""
            categoria = cat_var.get()
            preprompts = self.prompt_manager.config.get("preprompts", {})
            data = preprompts.get(categoria, {})
            
            base_text.delete("1.0", tk.END)
            base_text.insert("1.0", data.get("base", ""))
            
            estilo_text.delete("1.0", tk.END)
            estilo_text.insert("1.0", data.get("estilo", ""))
            
            calidad_text.delete("1.0", tk.END)
            calidad_text.insert("1.0", data.get("calidad", ""))
        
        def save_preprompt():
            """Guarda los cambios"""
            categoria = cat_var.get()
            
            self.prompt_manager.update_preprompt(categoria, "base", 
                                                base_text.get("1.0", tk.END).strip())
            self.prompt_manager.update_preprompt(categoria, "estilo", 
                                                estilo_text.get("1.0", tk.END).strip())
            self.prompt_manager.update_preprompt(categoria, "calidad", 
                                                calidad_text.get("1.0", tk.END).strip())
            
            messagebox.showinfo("Éxito", "Pre-prompt guardado correctamente")
            self.log(f"📝 Pre-prompt '{categoria}' actualizado")
        
        # Cargar datos iniciales
        cat_combo.bind("<<ComboboxSelected>>", lambda e: load_preprompt())
        load_preprompt()
        
        # Botones
        btn_frame = ttk.Frame(editor_window, padding=10)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="💾 Guardar", 
                  command=save_preprompt).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="❌ Cerrar", 
                  command=editor_window.destroy).pack(side=tk.LEFT)
    
    def update_prompt_preview(self):
        """Actualiza el preview del prompt final"""
        categoria = self.selected_category.get()
        descripcion = self.desc_text.get("1.0", tk.END).strip()
        bioma = self.selected_bioma.get() if self.selected_bioma.get() != "ninguno" else None
        
        full_prompt = self.prompt_manager.build_full_prompt(categoria, descripcion, bioma)
        
        self.prompt_preview.config(state=tk.NORMAL)
        self.prompt_preview.delete("1.0", tk.END)
        self.prompt_preview.insert("1.0", full_prompt)
        self.prompt_preview.config(state=tk.DISABLED)
    
    def generate_images(self):
        """Inicia la generación de imágenes"""
        if not self.image_generator or not self.image_generator.is_loaded:
            messagebox.showerror("Error", "Primero debes cargar el modelo de IA")
            return
        
        if self.is_generating:
            messagebox.showwarning("Advertencia", "Ya hay una generación en curso")
            return
        
        # Preparar parámetros
        categoria = self.selected_category.get()
        descripcion = self.desc_text.get("1.0", tk.END).strip()
        bioma = self.selected_bioma.get() if self.selected_bioma.get() != "ninguno" else None
        
        # Parsear resolución
        res_str = self.resolution.get()
        width, height = map(int, res_str.split('x'))
        
        # Parámetros base
        base_params = {
            "negative_prompt": self.prompt_manager.get_default_params().get("negative_prompt", ""),
            "width": width,
            "height": height,
            "num_inference_steps": self.steps_var.get(),
            "guidance_scale": self.guidance_var.get(),
            "seed": self.seed_var.get()
        }
        
        # Preparar lista de prompts
        if self.use_animation.get():
            # Generar animación completa
            anim_type = self.selected_animation.get()
            prompts_list = self.prompt_manager.get_animation_prompts(
                anim_type, categoria, descripcion, bioma
            )
            output_name = f"{anim_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        else:
            # Generar cantidad específica del mismo prompt
            full_prompt = self.prompt_manager.build_full_prompt(categoria, descripcion, bioma)
            prompts_list = [full_prompt] * self.batch_size.get()
            output_name = f"{categoria}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Crear directorio de salida
        output_dir = os.path.join("output", output_name)
        
        # Generar en thread separado
        def generate_thread():
            self.is_generating = True
            self.gen_button.config(state=tk.DISABLED)
            self.progress_var.set(0)
            
            try:
                def progress_callback(current, total, message):
                    progress = (current / total) * 100
                    self.progress_var.set(progress)
                    self.log(f"[{current}/{total}] {message}")
                
                self.log(f"🎨 Iniciando generación de {len(prompts_list)} imagen(es)...")
                self.log(f"📁 Guardando en: {output_dir}")
                
                generated = self.image_generator.generate_batch(
                    prompts_list, base_params, output_dir, 
                    output_name, progress_callback
                )
                
                self.log(f"✅ Generación completada: {len(generated)} imágenes creadas")
                messagebox.showinfo("Éxito", f"Se generaron {len(generated)} imágenes")
                
            except Exception as e:
                self.log(f"❌ Error durante la generación: {str(e)}")
                messagebox.showerror("Error", f"Error: {str(e)}")
            
            finally:
                self.is_generating = False
                self.gen_button.config(state=tk.NORMAL)
                self.progress_var.set(0)
        
        thread = threading.Thread(target=generate_thread, daemon=True)
        thread.start()
    
    def log(self, message):
        """Añade mensaje al log"""
        self.log_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")
        self.log_text.see(tk.END)
    
    def clear_log(self):
        """Limpia el log"""
        self.log_text.delete("1.0", tk.END)
    
    def open_output_folder(self):
        """Abre la carpeta de salida"""
        output_path = os.path.abspath("output")
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        os.startfile(output_path)


def main():
    """Función principal"""
    root = tk.Tk()
    app = IGIAApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
