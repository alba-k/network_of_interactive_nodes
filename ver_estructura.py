# ver_estructura.py
import os

# Carpetas que no nos importan
IGNORE = {'venv', '__pycache__', '.git', '.idea', '.vscode', 'build', 'dist'}

def print_tree(startpath):
    print(f"\n📂 ESTRUCTURA DEL PROYECTO: {os.path.basename(os.getcwd())}")
    print("="*40)
    
    for root, dirs, files in os.walk(startpath):
        # Filtrar carpetas ignoradas
        dirs[:] = [d for d in dirs if d not in IGNORE]
        
        level = root.replace(startpath, '').count(os.sep)
        indent = '    ' * level
        print(f'{indent}📁 {os.path.basename(root)}/')
        
        subindent = '    ' * (level + 1)
        for f in files:
            if f.endswith(".py") or f.endswith(".pem") or f.endswith(".txt"):
                print(f'{subindent}📄 {f}')

if __name__ == "__main__":
    print_tree('.')
    print("="*40)