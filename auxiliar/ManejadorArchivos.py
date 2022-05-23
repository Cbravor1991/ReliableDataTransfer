import os.path
from pathlib import Path

def crear_directorio(directorio):
    
    Path(directorio).mkdir(parents= True, exist_ok= True)