import pyautogui
import keyboard
import time
import tkinter as tk
from tkinter import simpledialog, messagebox
import queue
import threading
import sys
import pyperclip
import csv
import re


fornecedores = {}
try:
    with open("fornecedores.csv", newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            fornecedores[row["codigo"]] = row["nome"]
except FileNotFoundError:
    messagebox.showerror("Erro", "Arquivo 'fornecedores.csv' não encontrado.")
    sys.exit()

root = tk.Tk()
root.withdraw()
messagebox.showinfo("Instruções", 
    "Preencha os dados e use Ctrl+B para iniciar o macro.")

dia = simpledialog.askstring("Entrada do Dia", "Digite o dia:")
mes = simpledialog.askstring("Entrada do Mês", "Digite o mês:")
ano = simpledialog.askstring("Entrada do Ano", "Digite o ano:")
doc = simpledialog.askstring("Entrada do Documento", "Digite o Documento:")
seq = simpledialog.askstring("Entrada do Contador", "Digite o próximo número sequencial:")

try:
    seq = int(seq)
except:
    seq = 0

parar_macro = threading.Event()
event_queue = queue.Queue()
executando = False  # controle para impedir Ctrl+B múltiplos

def apertar_enter(n=1):
    for _ in range(n):
        pyautogui.press("enter")

def executar_macro():
    global seq, executando

    if executando:
        return

    executando = True
    try:
        doc1 = f"{doc} - {seq}"

        if parar_macro.is_set():
            return

        apertar_enter(6)
        pyautogui.write("1846")
        pyautogui.press("enter")
        pyautogui.write("100")
        apertar_enter(3)
        pyautogui.write("36")
        pyautogui.press("enter")
        pyautogui.write("100")
        apertar_enter(3)
        pyautogui.write("VI")
        apertar_enter(4)
        pyautogui.write("2")
        apertar_enter()

        seq += 1
        
        aguardar_quatro_numeros()

        pyautogui.hotkey('ctrl', 'a')
        pyautogui.hotkey('ctrl', 'c')
        texto = pyperclip.paste()

        apertar_enter(2)
        time.sleep(0.4)
        pyautogui.write("RE")
        time.sleep(0.5)
        pyautogui.press("enter")
        pyautogui.write("5")
        pyautogui.press("enter")
        pyautogui.write(doc1)
        pyautogui.press("enter")    
        time.sleep(0.3)
        pyautogui.write(dia)
        pyautogui.write(mes)
        pyautogui.write(ano)
        time.sleep(0.3)
        pyautogui.write(dia)
        pyautogui.write(mes)
        pyautogui.write(ano)

        match = re.search(r'(\d{4})', texto)
        if match:
            codigo = match.group(1)
            nome = fornecedores.get(codigo)
            if nome:
                for _ in range(12):
                    pyautogui.press("tab")

                pyperclip.copy(nome.upper())
                time.sleep(0.1)

                if codigo != "1001":
                    pyautogui.hotkey('ctrl', 'v')
                    
                    for _ in range(5):
                        pyautogui.press("tab")
                    pyautogui.hotkey('ctrl', 'a')

            else:
                print(f"Código {codigo} não encontrado.")
        else:
            print("Código não identificado.")
    finally:
        executando = False  # libera novamente Ctrl+B

def ouvir_teclado():
    def tentar_executar():
        global executando
        if not executando:
            event_queue.put("executar")

    keyboard.add_hotkey("ctrl+b", tentar_executar)
    keyboard.wait()

def loop_macro():
    while not parar_macro.is_set():
        try:
            evento = event_queue.get(timeout=0.1)
            if evento == "executar":
                executar_macro()
        except queue.Empty:
            pass

def aguardar_quatro_numeros():
    digitos = ""
    while True:
        tecla = keyboard.read_event()
        if tecla.event_type == keyboard.KEY_DOWN:
            if tecla.name.isdigit():
                digitos += tecla.name
                if len(digitos) == 4:
                    return digitos

janela = tk.Tk()
janela.title("Macro Ativo")
janela.geometry("200x100")
botao = tk.Button(janela, text="Parar Macro", bg="red", fg="white", command=lambda: (parar_macro.set(), janela.quit(), sys.exit()))
botao.pack(expand=True, fill="both")
janela.after(1000, lambda: janela.iconify())

threading.Thread(target=ouvir_teclado, daemon=True).start()
threading.Thread(target=loop_macro, daemon=True).start()

janela.mainloop()
