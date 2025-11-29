import argparse
import sys
import os
from typing import Dict, Any, List, Optional, Set, Tuple
from collections import deque
import re
import urllib.request
import urllib.error
from xml.etree import ElementTree as ET
import gzip
import tempfile

class DependencyCollector:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.dependencies_cache = {}
    
    def fetch_repository_data(self) -> str:
        """Получение данных из репозитория"""
        repository = self.config['repository']
        
        if self.config['test_mode']:
            # Работа с локальным файлом
            try:
                with open(repository, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                raise Exception(f"Ошибка чтения файла репозитория: {e}")
        else:
            # Работа с URL
            try:
                with urllib.request.urlopen(repository) as response:
                    content = response.read()
                    
                    # Обработка gzip сжатия
                    if repository.endswith('.gz'):
                        with gzip.open(tempfile.TemporaryFile(), 'w') as f:
                            f.write(content)
                            f.seek(0)
                            return f.read().decode('utf-8')
                    else:
                        return content.decode('utf-8')
                        
            except urllib.error.URLError as e:
                raise Exception(f"Ошибка доступа к репозиторию: {e}")
            except Exception as e:
                raise Exception(f"Ошибка обработки данных репозитория: {e}")
    
    def parse_apkindex(self, content: str) -> Dict[str, Dict]:
        """Парсинг APKINDEX"""
        packages = {}
        current_package = None
        
        for line in content.split('\n'):
            line = line.strip()
            
            if line.startswith('P:'):
                # Начало нового пакета
                if current_package:
                    packages[current_package['name']] = current_package
                current_package = {'name': line[2:], 'dependencies': [], 'version': ''}
            
            elif line.startswith('V:') and current_package:
                current_package['version'] = line[2:]
            
            elif line.startswith('D:') and current_package:
                # Зависимости
                deps = line[2:].split()
                for dep in deps:
                    if dep and dep != 'so:':
                        # Убираем версии из зависимостей
                        clean_dep = re.sub(r'[<=>].*', '', dep)
                        if clean_dep and clean_dep not in current_package['dependencies']:
                            current_package['dependencies'].append(clean_dep)
        
        # Добавляем последний пакет
        if current_package:
            packages[current_package['name']] = current_package
        
        return packages
    
    def get_package_dependencies(self, package_name: str, version: str = 'latest') -> List[str]:
        """Получение зависимостей для конкретного пакета"""
        cache_key = f"{package_name}_{version}"
        if cache_key in self.dependencies_cache:
            return self.dependencies_cache[cache_key]
        
        try:
            # Получаем данные репозитория
            repo_data = self.fetch_repository_data()
            packages = self.parse_apkindex(repo_data)
            
            # Ищем нужный пакет
            target_package = None
            for pkg_name, pkg_info in packages.items():
                if pkg_name == package_name:
                    if version == 'latest' or pkg_info['version'] == version:
                        target_package = pkg_info
                        break
            
            if not target_package:
                raise Exception(f"Пакет {package_name} версии {version} не найден")
            
            # Применяем фильтр если задан
            dependencies = target_package['dependencies']
            if self.config['filter']:
                dependencies = [dep for dep in dependencies 
                              if self.config['filter'] in dep]
            
            self.dependencies_cache[cache_key] = dependencies
            return dependencies
            
        except Exception as e:
            raise Exception(f"Ошибка получения зависимостей: {e}")
    
    def run_stage2(self):
        """Запуск второго этапа"""
        print("\n=== Этап 2: Сбор данных ===")
        
        try:
            package_name = self.config['package']
            version = self.config['version']
            
            print(f"Получение зависимостей для пакета: {package_name} версии {version}")
            
            dependencies = self.get_package_dependencies(package_name, version)
            
            print(f"\nПрямые зависимости пакета {package_name}:")
            print("-" * 40)
            for dep in dependencies:
                print(f"  - {dep}")
            print("-" * 40)
            
            print(f"Всего зависимостей: {len(dependencies)}")
            
        except Exception as e:
            print(f"Ошибка на этапе 2: {e}")
            sys.exit(1)


class DependencyGraph:
    def __init__(self, collector: 'DependencyCollector'):
        self.collector = collector
        self.graph = {}
        self.visited = set()
    
    def build_dependency_tree(self, package: str, depth: int = 0, max_depth: int = 10) -> Dict:
        """Рекурсивное построение дерева зависимостей"""
        if depth > max_depth or package in self.visited:
            return {'name': package, 'children': []}
        
        self.visited.add(package)
        
        try:
            dependencies = self.collector.get_package_dependencies(package)
            children = []
            
            for dep in dependencies:
                child_tree = self.build_dependency_tree(dep, depth + 1, max_depth)
                children.append(child_tree)
            
            return {'name': package, 'children': children}
            
        except Exception:
            return {'name': package, 'children': []}
    
    def generate_ascii_tree(self, tree: Dict, prefix: str = "", is_last: bool = True) -> str:
        """Генерация ASCII-дерева"""
        if not tree:
            return ""
        
        result = []
        connector = "└── " if is_last else "├── "
        result.append(prefix + connector + tree['name'])
        
        new_prefix = prefix + ("    " if is_last else "│   ")
        
        children = tree['children']
        for i, child in enumerate(children):
            is_last_child = i == len(children) - 1
            result.append(self.generate_ascii_tree(child, new_prefix, is_last_child))
        
        return "\n".join(result)
    
    def generate_graphviz(self, tree: Dict) -> str:
        """Генерация кода Graphviz"""
        nodes = set()
        edges = set()
        
        def traverse(t: Dict, parent: str = None):
            node_name = t['name'].replace('-', '_').replace('.', '_')
            nodes.add(node_name)
            
            if parent:
                edges.add(f'"{parent}" -> "{node_name}"')
            
            for child in t['children']:
                traverse(child, node_name)
        
        traverse(tree)
        
        graphviz_code = [
            "digraph DependencyTree {",
            "    rankdir=TB;",
            "    node [shape=box, style=filled, fillcolor=lightblue];",
            "    edge [arrowhead=vee];",
            ""
        ]
        
        # Добавляем узлы
        for node in nodes:
            graphviz_code.append(f'    "{node}" [label="{node.replace("_", "-")}"];')
        
        graphviz_code.append("")
        
        # Добавляем ребра
        for edge in edges:
            graphviz_code.append(f"    {edge};")
        
        graphviz_code.append("}")
        
        return "\n".join(graphviz_code)


class DependencyVisualizer:
    def __init__(self):
        self.config = {}
        
    def parse_arguments(self) -> Dict[str, Any]:
        """Парсинг аргументов командной строки"""
        parser = argparse.ArgumentParser(
            description='Визуализатор графа зависимостей пакетов Alpine Linux',
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        parser.add_argument(
            '--package',
            type=str,
            required=True,
            help='Имя анализируемого пакета'
        )
        
        parser.add_argument(
            '--repository',
            type=str,
            required=True,
            help='URL-адрес репозитория или путь к файлу тестового репозитория'
        )
        
        parser.add_argument(
            '--test-mode',
            action='store_true',
            help='Режим работы с тестового репозитория'
        )
        
        parser.add_argument(
            '--version',
            type=str,
            default='latest',
            help='Версия пакета (по умолчанию: latest)'
        )
        
        parser.add_argument(
            '--ascii-tree',
            action='store_true',
            help='Режим вывода зависимостей в формате ASCII-дерева'
        )
        
        parser.add_argument(
            '--filter',
            type=str,
            default='',
            help='Подстрока для фильтрации пакетов'
        )
        
        parser.add_argument(
            '--max-depth',
            type=int,
            default=3,
            help='Максимальная глубина рекурсии для построения дерева'
        )
        
        try:
            args = parser.parse_args()
            return vars(args)
        except SystemExit:
            print("Ошибка: Неправильные аргументы командной строки")
            sys.exit(1)
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Валидация конфигурации"""
        errors = []
        
        if not config['package'] or not isinstance(config['package'], str):
            errors.append("Имя пакета должно быть непустой строкой")
        
        if not config['repository']:
            errors.append("Репозиторий должен быть указан")
        elif config['test_mode']:
            if not os.path.exists(config['repository']):
                errors.append(f"Файл репозитория не найден: {config['repository']}")
        
        if config['version'] and not isinstance(config['version'], str):
            errors.append("Версия должна быть строкой")
        
        if config['filter'] is not None and not isinstance(config['filter'], str):
            errors.append("Фильтр должен быть строкой")
        
        if config['max_depth'] <= 0:
            errors.append("Максимальная глубина должна быть положительным числом")
        
        if errors:
            print("Ошибки валидации конфигурации:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        return True
    
    def print_config(self, config: Dict[str, Any]):
        """Вывод конфигурации в формате ключ-значение"""
        print("Конфигурация приложения:")
        print("-" * 30)
        for key, value in config.items():
            print(f"{key}: {value}")
        print("-" * 30)
    
    def run_stage1(self):
        """Запуск первого этапа"""
        print("=== Этап 1: Минимальный прототип с конфигурацией ===")
        
        try:
            config = self.parse_arguments()
            
            if not self.validate_config(config):
                sys.exit(1)
            
            self.config = config
            self.print_config(config)
            
            print("Этап 1 выполнен успешно!")
            
        except Exception as e:
            print(f"Критическая ошибка: {e}")
            sys.exit(1)
    
    def run_stage2(self):
        """Запуск второго этапа"""
        collector = DependencyCollector(self.config)
        collector.run_stage2()
        return collector
    
    def run_stage5(self, collector: DependencyCollector):
        """Запуск пятого этапа"""
        print("\n=== Этап 5: Визуализация ===")
        
        try:
            graph_builder = DependencyGraph(collector)
            package_name = self.config['package']
            
            print(f"Построение дерева зависимостей для {package_name}...")
            dependency_tree = graph_builder.build_dependency_tree(
                package_name, 
                max_depth=self.config['max_depth']
            )
            
            # Генерация Graphviz
            print("\n1. Описание графа на языке Graphviz:")
            print("-" * 50)
            graphviz_code = graph_builder.generate_graphviz(dependency_tree)
            print(graphviz_code)
            print("-" * 50)
            
            # Сохранение в файл
            with open(f"{package_name}_dependencies.dot", "w") as f:
                f.write(graphviz_code)
            print(f"\nGraphviz код сохранен в {package_name}_dependencies.dot")
            
            # ASCII-дерево если запрошено
            if self.config['ascii_tree']:
                print("\n2. ASCII-дерево зависимостей:")
                print("-" * 50)
                ascii_tree = graph_builder.generate_ascii_tree(dependency_tree)
                print(ascii_tree)
                print("-" * 50)
            
            # Демонстрация для разных пакетов
            self.demonstrate_multiple_packages(collector)
            
        except Exception as e:
            print(f"Ошибка на этапе 5: {e}")
            import traceback
            traceback.print_exc()
    
    def demonstrate_multiple_packages(self, collector: DependencyCollector):
        """Демонстрация для нескольких пакетов"""
        print("\n3. Примеры визуализации для различных пакетов:")
        
        test_packages = [
            "busybox",
            "nginx",
            "python3"
        ]
        
        for pkg in test_packages:
            print(f"\n--- Пакет: {pkg} ---")
            try:
                graph_builder = DependencyGraph(collector)
                tree = graph_builder.build_dependency_tree(pkg, max_depth=2)
                
                # Простая статистика
                deps = collector.get_package_dependencies(pkg)
                print(f"Прямые зависимости: {len(deps)}")
                if deps:
                    print(f"Примеры: {', '.join(deps[:3])}{'...' if len(deps) > 3 else ''}")
                
                # Сравнение с штатными инструментами
                print("Сравнение: используйте 'apk info -R {pkg}' для проверки")
                
            except Exception as e:
                print(f"Ошибка анализа {pkg}: {e}")
    
    def compare_with_native_tools(self, package: str):
        """Сравнение с штатными инструментами"""
        print(f"\n4. Сравнение для пакета {package}:")
        print("Для точного сравнения выполните в системе Alpine Linux:")
        print(f"  apk info -R {package}")
        print("\nВозможные расхождения:")
        print("  - Разные версии пакетов в репозиториях")
        print("  - Обработка виртуальных пакетов (provides)")
        print("  - Учет архитектуры и веток репозитория")
        print("  - Обработка опциональных зависимостей")


def main():
    visualizer = DependencyVisualizer()
    visualizer.run_stage1()
    collector = visualizer.run_stage2()
    visualizer.run_stage5(collector)
    visualizer.compare_with_native_tools(visualizer.config['package'])

if __name__ == "__main__":
    main()
