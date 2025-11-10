"""
Script de verificación para IGIA con SD3.5
Verifica que todas las dependencias y archivos estén correctamente configurados
"""
import sys
import os
from pathlib import Path

def print_status(check_name, status, message=""):
    """Imprime el estado de una verificación"""
    symbols = {"✓": "✓", "✗": "✗", "⚠": "⚠"}
    colors = {
        "green": "\033[92m",
        "red": "\033[91m",
        "yellow": "\033[93m",
        "reset": "\033[0m"
    }
    
    if status == "ok":
        symbol = symbols["✓"]
        color = colors["green"]
    elif status == "error":
        symbol = symbols["✗"]
        color = colors["red"]
    else:  # warning
        symbol = symbols["⚠"]
        color = colors["yellow"]
    
    print(f"{color}{symbol}{colors['reset']} {check_name}")
    if message:
        print(f"  {message}")

def check_python_version():
    """Verifica la versión de Python"""
    version = sys.version_info
    if version.major == 3 and version.minor in [10, 11]:
        print_status("Python Version", "ok", f"Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print_status("Python Version", "error", 
                    f"Python {version.major}.{version.minor}.{version.micro} - Se recomienda 3.10 o 3.11")
        return False

def check_pytorch():
    """Verifica PyTorch y CUDA"""
    try:
        import torch
        version = torch.__version__
        cuda_available = torch.cuda.is_available()
        
        if cuda_available:
            gpu_name = torch.cuda.get_device_name(0)
            vram = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            print_status("PyTorch + CUDA", "ok", 
                        f"PyTorch {version} con CUDA\n  GPU: {gpu_name} ({vram:.1f}GB VRAM)")
            
            if vram < 12:
                print_status("VRAM Warning", "warning",
                           "Menos de 12GB VRAM - SD3.5 Large puede tener problemas")
            return True
        else:
            print_status("PyTorch", "warning", 
                        f"PyTorch {version} sin CUDA - Solo funcionará en CPU (muy lento)")
            return False
    except ImportError:
        print_status("PyTorch", "error", "PyTorch no instalado")
        return False

def check_dependencies():
    """Verifica las dependencias necesarias"""
    deps = {
        "PIL": "Pillow",
        "numpy": "numpy",
        "safetensors": "safetensors",
        "fire": "fire",
        "tqdm": "tqdm",
        "tkinter": "tkinter (built-in)"
    }
    
    all_ok = True
    for module, name in deps.items():
        try:
            __import__(module)
            print_status(f"Dependencia: {name}", "ok")
        except ImportError:
            print_status(f"Dependencia: {name}", "error", "No instalado")
            all_ok = False
    
    return all_ok

def check_model_files():
    """Verifica que existan los archivos del modelo"""
    model_folder = Path("ia/sd3.5-main/models")
    
    required_files = {
        "clip_g.safetensors": 1.4,
        "clip_l.safetensors": 0.25,
        "t5xxl.safetensors": 4.9,
        "sd3.5_large.safetensors": 9.8
    }
    
    optional_files = {
        "sd3_vae.safetensors": 0.34
    }
    
    if not model_folder.exists():
        print_status("Carpeta de modelos", "error", 
                    f"No existe: {model_folder.absolute()}")
        return False
    
    print_status("Carpeta de modelos", "ok", f"{model_folder.absolute()}")
    
    all_present = True
    total_size = 0
    
    for filename, expected_size in required_files.items():
        filepath = model_folder / filename
        if filepath.exists():
            size = filepath.stat().st_size / (1024**3)  # GB
            total_size += size
            if abs(size - expected_size) < 0.5:  # Tolerancia de 0.5GB
                print_status(f"  {filename}", "ok", f"{size:.1f}GB")
            else:
                print_status(f"  {filename}", "warning", 
                           f"{size:.1f}GB (esperado ~{expected_size}GB)")
        else:
            print_status(f"  {filename}", "error", "No encontrado - REQUERIDO")
            all_present = False
    
    for filename, expected_size in optional_files.items():
        filepath = model_folder / filename
        if filepath.exists():
            size = filepath.stat().st_size / (1024**3)
            total_size += size
            print_status(f"  {filename}", "ok", f"{size:.1f}GB (opcional)")
        else:
            print_status(f"  {filename}", "warning", "No encontrado (opcional)")
    
    print(f"\n  Tamaño total de modelos: {total_size:.1f}GB")
    
    return all_present

def check_project_structure():
    """Verifica la estructura del proyecto"""
    required_paths = [
        "config/prompts_templates.json",
        "config/model_config.json",
        "src/__init__.py",
        "src/sd3_generator.py",
        "src/prompt_manager.py",
        "ia/sd3.5-main/sd3_infer.py",
        "main.py",
        "requirements.txt"
    ]
    
    all_ok = True
    for path_str in required_paths:
        path = Path(path_str)
        if path.exists():
            print_status(f"  {path_str}", "ok")
        else:
            print_status(f"  {path_str}", "error", "No encontrado")
            all_ok = False
    
    return all_ok

def main():
    """Ejecuta todas las verificaciones"""
    print("=" * 60)
    print("🔍 VERIFICACIÓN DE INSTALACIÓN - IGIA con SD3.5")
    print("=" * 60)
    print()
    
    results = {}
    
    print("📌 Verificando Python...")
    results['python'] = check_python_version()
    print()
    
    print("📌 Verificando PyTorch y CUDA...")
    results['pytorch'] = check_pytorch()
    print()
    
    print("📌 Verificando dependencias...")
    results['deps'] = check_dependencies()
    print()
    
    print("📌 Verificando archivos del modelo SD3.5...")
    results['models'] = check_model_files()
    print()
    
    print("📌 Verificando estructura del proyecto...")
    results['structure'] = check_project_structure()
    print()
    
    print("=" * 60)
    print("📊 RESUMEN")
    print("=" * 60)
    
    if all(results.values()):
        print_status("CONFIGURACIÓN COMPLETA", "ok", 
                    "Todo está listo para usar IGIA!")
        print("\nPuedes ejecutar: python main.py")
    else:
        print_status("CONFIGURACIÓN INCOMPLETA", "error",
                    "Revisa los errores arriba y corrígelos")
        print("\nPasos a seguir:")
        if not results['python']:
            print("  1. Instala Python 3.10 o 3.11")
        if not results['pytorch']:
            print("  2. Instala PyTorch con CUDA: pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118")
        if not results['deps']:
            print("  3. Instala dependencias: pip install -r requirements.txt")
        if not results['models']:
            print("  4. Descarga los archivos del modelo SD3.5 Large")
            print("     https://huggingface.co/stabilityai/stable-diffusion-3.5-large")
        if not results['structure']:
            print("  5. Verifica que todos los archivos del proyecto estén presentes")
    
    print()

if __name__ == "__main__":
    main()
