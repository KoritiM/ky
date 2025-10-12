import argparse
import os
from pathlib import Path
import tkinter as tk
from tkinter import scrolledtext, Entry, Frame, Label
import re
import sys

def parse_command_line_args():
    """Парсинг аргументов командной строки"""
    parser = argparse.ArgumentParser(description='VFS Emulator')
    parser.add_argument('--vfs-path', required=True, help='Путь к физическому расположению VFS')
    parser.add_argument('--script', help='Путь к стартовому скрипту')
    return parser.parse_args()

def execute_startup_script(vfs, script_path):
    """Выполняет стартовый скрипт с отладочным выводом"""
    script_file = Path(script_path)
    
    if not script_file.exists():
        return f"Ошибка: Скрипт {script_path} не найден\n"
    
    output = []
    output.append(f"=== Выполнение стартового скрипта: {script_path} ===\n")
    
    with open(script_path, 'r', encoding='utf-8') as file:
        for line_num, line in enumerate(file, 1):
            command = line.strip()
            if command and not command.startswith('#'):  # Пропускаем пустые строки и комментарии
                output.append(f"[Скрипт строка {line_num}] > {command}\n")
                result = vfs.execute_command(command)
                if result and result != "EXIT":
                    output.append(result)
                elif result == "EXIT":
                    output.append("Завершение работы по скрипту\n")
                    break
                output.append("\n")  # Пустая строка для разделения
    
    return "".join(output)

class VFSEmulator:
    def __init__(self, vfs_path=None):
        self.current_dir = "/home/user"
        self.vfs_path = Path(vfs_path) if vfs_path else None
        if self.vfs_path:
            self.vfs_path.mkdir(parents=True, exist_ok=True)
        
        self.commands = {
            "ls": self.ls_command,
            "cd": self.cd_command,
            "exit": self.exit_command,
            "pwd": self.pwd_command,
            "mkdir": self.mkdir_command,
            "touch": self.touch_command,
            "echo": self.echo_command,
            "cat": self.cat_command,
            "help": self.help_command
        }
    
    def parse_arguments(self, command_line):
        """Парсер аргументов с поддержкой кавычек"""
        # Регулярное выражение для разбивки с учетом кавычек
        pattern = r'\"[^\"]*\"|\'[^\']*\'|\S+'
        matches = re.findall(pattern, command_line)
        
        # Убираем кавычки вокруг аргументов
        cleaned_args = []
        for match in matches:
            if (match.startswith('"') and match.endswith('"')) or \
               (match.startswith("'") and match.endswith("'")):
                cleaned_args.append(match[1:-1])
            else:
                cleaned_args.append(match)
        
        return cleaned_args
    
    def execute_command(self, command_line):
        """Выполнение команды"""
        if not command_line.strip():
            return ""
        
        args = self.parse_arguments(command_line)
        command = args[0] if args else ""
        
        if command in self.commands:
            return self.commands[command](args[1:])
        else:
            return f"vfs: команда не найдена: {command}\n"
    
    def ls_command(self, args):
        """Заглушка команды ls"""
        return f"ls: аргументы {args} (текущая директория: {self.current_dir})\n"

        def pwd_command(self, args):
    """Команда pwd"""
    return f"{self.current_dir}\n"

def mkdir_command(self, args):
    """Команда mkdir"""
    if len(args) == 0:
        return "mkdir: отсутствует операнд\n"
    
    dir_name = args[0]
    # Здесь должна быть логика создания реальной директории в VFS
    return f"mkdir: создана директория '{dir_name}'\n"

def touch_command(self, args):
    """Команда touch"""
    if len(args) == 0:
        return "touch: отсутствует операнд\n"
    
    file_name = args[0]
    # Здесь должна быть логика создания реального файла в VFS
    return f"touch: создан файл '{file_name}'\n"

def echo_command(self, args):
    """Команда echo"""
    return " ".join(args) + "\n"

def cat_command(self, args):
    """Команда cat"""
    if len(args) == 0:
        return "cat: отсутствует операнд\n"
    
    file_name = args[0]
    # Здесь должна быть логика чтения реального файла из VFS
    return f"cat: содержимое файла '{file_name}'\n"

def help_command(self, args):
    """Команда help"""
    help_text = """
Доступные команды:
- ls - список файлов и директорий
- cd [путь] - сменить директорию  
- pwd - текущая директория
- mkdir [имя] - создать директорию
- touch [имя] - создать файл
- echo [текст] - вывести текст
- cat [имя] - прочитать файл
- help - справка
- exit - выход
"""
    return help_text
    
    def cd_command(self, args):
        """Заглушка команды cd"""
        if len(args) == 0:
            # cd без аргументов - переход в домашнюю директорию
            self.current_dir = "/home/user"
            return ""
        elif len(args) == 1:
            new_dir = args[0]
            # Простая имитация изменения директории
            if new_dir == "..":
                # Упрощенная логика для родительской директории
                if self.current_dir != "/":
                    parts = self.current_dir.rstrip('/').split('/')
                    self.current_dir = '/'.join(parts[:-1]) if len(parts) > 1 else "/"
            elif new_dir.startswith("/"):
                self.current_dir = new_dir
            else:
                self.current_dir = f"{self.current_dir.rstrip('/')}/{new_dir}"
            
            return f"cd: изменена директория на {self.current_dir}\n"
        else:
            return "cd: слишком много аргументов\n"
    
    def exit_command(self, args):
        """Команда exit"""
        return "EXIT"

class VFSGUI:
    def __init__(self, root, vfs_path=None, script_path=None):
        self.root = root
        self.root.title("VFS - Virtual File System Emulator")
        self.root.geometry("800x600")
        self.root.configure(bg='black')
        
        self.vfs = VFSEmulator(vfs_path)
        self.script_path = script_path
        
        # Создание интерфейса
        self.create_widgets()
        
        # Фокус на поле ввода
        self.entry.focus_set()
        
        # Отладочный вывод параметров
        self.display_configuration(vfs_path, script_path)
        
        # Выполнение стартового скрипта если указан
        if script_path:
            self.execute_startup_script()
        else:
            self.display_welcome()
    
    def create_widgets(self):
        """Создание элементов интерфейса"""
        # Основной текстовая область
        self.text_area = scrolledtext.ScrolledText(
            self.root,
            bg='black',
            fg='white',
            insertbackground='white',
            font=('Courier New', 12),
            wrap=tk.WORD
        )
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.text_area.config(state=tk.DISABLED)
        
        # Фрейм для ввода команды
        input_frame = Frame(self.root, bg='black')
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Приглашение командной строки
        self.prompt_label = Label(
            input_frame,
            text=f"vfs:{self.vfs.current_dir}$ ",
            bg='black',
            fg='green',
            font=('Courier New', 12, 'bold')
        )
        self.prompt_label.pack(side=tk.LEFT)
        
        # Поле ввода команды
        self.entry = Entry(
            input_frame,
            bg='black',
            fg='white',
            insertbackground='white',
            font=('Courier New', 12),
            width=80
        )
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry.bind('<Return>', self.execute_command)
        self.entry.bind('<Up>', self.command_history_up)
        self.entry.bind('<Down>', self.command_history_down)
        
        # История команд
        self.command_history = []
        self.history_index = -1
        
    def display_welcome(self):
        """Отображение приветственного сообщения"""
        welcome_msg = """Добро пожаловать в VFS Emulator v1.0
        Доступные команды: ls, cd, exit

        Для справки по конкретной команде используйте: команда --help

        """
        self.display_output(welcome_msg)
        self.update_prompt()
    
    def update_prompt(self):
        """Обновление приглашения командной строки"""
        self.prompt_label.config(text=f"vfs:{self.vfs.current_dir}$ ")
    
    def display_output(self, text):
        """Отображение вывода в текстовой области"""
        self.text_area.config(state=tk.NORMAL)
        self.text_area.insert(tk.END, text)
        self.text_area.see(tk.END)
        self.text_area.config(state=tk.DISABLED)
    
    def execute_command(self, event=None):
        """Выполнение команды"""
        command = self.entry.get().strip()
        self.entry.delete(0, tk.END)
        
        if command:
            # Добавляем команду в историю
            self.command_history.append(command)
            self.history_index = len(self.command_history)
            
            # Отображаем команду
            self.display_output(f"vfs:{self.vfs.current_dir}$ {command}\n")
            
            # Выполняем команду
            result = self.vfs.execute_command(command)
            
            if result == "EXIT":
                self.root.quit()
                return
            
            # Отображаем результат
            self.display_output(result)
            
            # Обновляем приглашение (особенно важно для cd)
            self.update_prompt()
    
    def command_history_up(self, event):
        """Переход к предыдущей команде в истории"""
        if self.command_history and self.history_index > 0:
            self.history_index -= 1
            self.entry.delete(0, tk.END)
            self.entry.insert(0, self.command_history[self.history_index])
    
    def command_history_down(self, event):
        """Переход к следующей команде в истории"""
        if self.command_history and self.history_index < len(self.command_history) - 1:
            self.history_index += 1
            self.entry.delete(0, tk.END)
            self.entry.insert(0, self.command_history[self.history_index])
        elif self.history_index == len(self.command_history) - 1:
            self.history_index = len(self.command_history)
            self.entry.delete(0, tk.END)

    def display_configuration(self, vfs_path, script_path):
        """Отладочный вывод конфигурации"""
        config_msg = f"""=== Конфигурация эмулятора VFS ===Путь к VFS: {vfs_path}
        Стартовый скрипт: {script_path if script_path else 'Не указан'}
        {"=" * 40}
        """
    self.display_output(config_msg)

def execute_startup_script(self):
    """Выполнение стартового скрипта"""
    if self.script_path:
        result = execute_startup_script(self.vfs, self.script_path)
        self.display_output(result)
        self.update_prompt()

def main():
    # Парсинг аргументов командной строки
    args = parse_command_line_args()
    
    root = tk.Tk()
    app = VFSGUI(root, args.vfs_path, args.script)
    root.mainloop()

if __name__ == "__main__":
    main()
    
