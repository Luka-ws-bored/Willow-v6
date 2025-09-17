import psutil
from rich import print

# Tiny Helper: chooses best model depending on free RAM
def select_model():
    available_gb = psutil.virtual_memory().available / (1024**3)
    if available_gb > 8:
        print('[green]Using Josiefied Qwen3.1.7b (goekdenizguelmez/josiefied-qwen3:1.7b)[/green]')
        return 'goekdenizguelmez/josiefied-qwen3:1.7b'
    elif available_gb > 4:
        print('[yellow]Falling back to qwen3:0.6b (lighter model)[/yellow]')
        return 'qwen3:0.6b'
    else:
        print('[red]Low RAM, using qwen3:0.6b (lightest available)[/red]')
        return 'qwen3:0.6b'