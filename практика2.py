import argparse
import sys
import os
import requests
import gzip
import io
from urllib.parse import urljoin
import xml.etree.ElementTree as ET

class Config:
    """Класс для хранения конфигурации приложения"""
    
    def __init__(self):
        self.package_name = None
        self.repository_url = None
        self.test_repo_mode = False
        self.package_version = None
        self.tree_output = False
        self.filter_substring = None


def validate_package_name(name):
    """Валидация имени пакета"""
    if not name:
        raise ValueError("Имя пакета не может быть пустым")
    if not name.replace('-', '').replace('_', '').replace('.', '').isalnum():
        raise ValueError("Имя пакета содержит недопустимые символы")
    return name


def validate_repository_url(url):
    """Валидация URL репозитория или пути к файлу"""
    if not url:
        raise ValueError("URL или путь к репозиторию не может быть пустым")
    
    # Проверка, является ли это путем к файлу
    if os.path.exists(url):
        if not os.path.isfile(url):
            raise ValueError(f"Путь '{url}' не является файлом")
        return url
    
    # Базовая проверка URL (можно расширить)
    if not (url.startswith('http://') or url.startswith('https://') or 
            url.startswith('git://') or url.startswith('file://')):
        raise ValueError(f"Некорректный формат URL: {url}")
    
    return url


def validate_version(version):
    """Валидация версии пакета"""
    if not version:
        return None
    
    # Простая проверка формата версии (можно расширить)
    version_parts = version.split('.')
    for part in version_parts:
        if not part.isdigit() and part != '*':
            raise ValueError(f"Некорректный формат версии: {version}")
    
    return version


def validate_filter_substring(substring):
    """Валидация подстроки для фильтрации"""
    if substring is None:
        return None
    
    if not substring.strip():
        raise ValueError("Подстрока для фильтрации не может быть пустой или состоять только из пробелов")
    
    return substring.strip()


def parse_arguments():
    """Парсинг аргументов командной строки"""
    parser = argparse.ArgumentParser(
        description='Анализатор зависимостей пакетов',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  %(prog)s --package requests --url https://github.com/psf/requests
  %(prog)s -p numpy -u /path/to/repo --tree --filter "test"
  %(prog)s --package django --version 4.2 --test-mode
        """
    )
    
    # Обязательные параметры
    parser.add_argument(
        '-p', '--package',
        dest='package_name',
        required=True,
        help='Имя анализируемого пакета (обязательный параметр)'
    )
    
    parser.add_argument(
        '-u', '--url',
        dest='repository_url',
        required=True,
        help='URL репозитория или путь к файлу тестового репозитория (обязательный параметр)'
    )
    
    # Опциональные параметры
    parser.add_argument(
        '-t', '--test-mode',
        dest='test_repo_mode',
        action='store_true',
        default=False,
        help='Режим работы с тестовым репозиторием'
    )
    
    parser.add_argument(
        '-v', '--version',
        dest='package_version',
        help='Версия пакета (формат: X.Y.Z или X.Y.*)'
    )
    
    parser.add_argument(
        '--tree',
        dest='tree_output',
        action='store_true',
        default=False,
        help='Режим вывода зависимостей в формате ASCII-дерева'
    )
    
    parser.add_argument(
        '-f', '--filter',
        dest='filter_substring',
        help='Подстрока для фильтрации пакетов'
    )
    
    return parser.parse_args()


def validate_config(config):
    """Полная валидация конфигурации"""
    errors = []
    
    try:
        validate_package_name(config.package_name)
    except ValueError as e:
        errors.append(f"Ошибка в имени пакета: {e}")
    
    try:
        validate_repository_url(config.repository_url)
    except ValueError as e:
        errors.append(f"Ошибка в URL/пути репозитория: {e}")
    
    try:
        validate_version(config.package_version)
    except ValueError as e:
        errors.append(f"Ошибка в версии пакета: {e}")
    
    try:
        validate_filter_substring(config.filter_substring)
    except ValueError as e:
        errors.append(f"Ошибка в подстроке фильтра: {e}")
    
    return errors


def print_config(config):
    """Вывод конфигурации в формате ключ-значение"""
    print("=" * 50)
    print("ТЕКУЩАЯ КОНФИГУРАЦИЯ ПРИЛОЖЕНИЯ")
    print("=" * 50)
    
    config_data = {
        "Имя пакета": config.package_name,
        "URL/путь репозитория": config.repository_url,
        "Режим тестового репозитория": "ВКЛ" if config.test_repo_mode else "ВЫКЛ",
        "Версия пакета": config.package_version or "Не указана",
        "Режим дерева зависимостей": "ВКЛ" if config.tree_output else "ВЫКЛ",
        "Подстрока для фильтрации": config.filter_substring or "Не указана"
    }
    
    for key, value in config_data.items():
        print(f"{key:<30}: {value}")
    
    print("=" * 50)


def main():
    """Основная функция приложения"""
    try:
        # Парсинг аргументов
        args = parse_arguments()
        
        # Создание конфигурации
        config = Config()
        config.package_name = args.package_name
        config.repository_url = args.repository_url
        config.test_repo_mode = args.test_repo_mode
        config.package_version = args.package_version
        config.tree_output = args.tree_output
        config.filter_substring = args.filter_substring
        
        # Валидация конфигурации
        validation_errors = validate_config(config)
        
        if validation_errors:
            print("ОШИБКИ ВАЛИДАЦИИ:", file=sys.stderr)
            for error in validation_errors:
                print(f"  - {error}", file=sys.stderr)
            sys.exit(1)
        
        # Вывод конфигурации (требование №3)
        print_config(config)
        
        # Здесь будет основная логика приложения
        print("\nПриложение успешно запущено с указанной конфигурацией!")
        print("В реальном приложении здесь будет анализ зависимостей...")
        
    except argparse.ArgumentError as e:
        print(f"Ошибка в аргументах командной строки: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nПриложение прервано пользователем", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Неожиданная ошибка: {e}", file=sys.stderr)
        sys.exit(1)
def fetch_apk_index(repo_url, arch="x86_64", branch="v3.20", repo="main"):
    """
    Загрузка и парсинг APKINDEX для Alpine Linux репозитория
    """
    # Формируем URL к APKINDEX
    if repo_url.endswith('/'):
        repo_url = repo_url[:-1]
    
    apkindex_url = f"{repo_url}/{branch}/{repo}/{arch}/APKINDEX.tar.gz"
    
    try:
        print(f"Загрузка APKINDEX из: {apkindex_url}")
        response = requests.get(apkindex_url, timeout=30)
        response.raise_for_status()
        
        # Распаковка и чтение gzip архива
        with gzip.open(io.BytesIO(response.content), 'rt', encoding='utf-8', errors='ignore') as f:
            return f.read()
            
    except requests.exceptions.RequestException as e:
        raise Exception(f"Ошибка при загрузке APKINDEX: {e}")


def parse_apkindex_content(content):
    """
    Парсинг содержимого APKINDEX и извлечение информации о пакетах
    """
    packages = {}
    current_pkg = {}
    
    for line in content.split('\n'):
        if not line.strip():
            if current_pkg and 'P' in current_pkg:
                pkg_name = current_pkg['P']
                packages[pkg_name] = current_pkg.copy()
            current_pkg = {}
            continue
            
        if ':' in line:
            key, value = line.split(':', 1)
            current_pkg[key] = value
    
    # Добавляем последний пакет
    if current_pkg and 'P' in current_pkg:
        pkg_name = current_pkg['P']
        packages[pkg_name] = current_pkg
    
    return packages


def get_package_dependencies(package_name, package_version, packages_data):
    """
    Получение прямых зависимостей для указанного пакета и версии
    """
    # Поиск пакета
    target_package = None
    
    for pkg_name, pkg_info in packages_data.items():
        if pkg_name == package_name:
            if not package_version or package_version == pkg_info.get('V', '').split('-')[0]:
                target_package = pkg_info
                break
    
    if not target_package:
        raise Exception(f"Пакет '{package_name}' (версия: {package_version or 'любая'}) не найден в репозитории")
    
    # Извлечение зависимостей
    dependencies_str = target_package.get('D', '')
    if not dependencies_str:
        return []
    
    # Парсинг зависимостей (формат: dep1 dep2 dep3)
    dependencies = []
    for dep in dependencies_str.split():
        # Убираем версии из зависимостей (формат: so:libc.musl-x86_64.so.1)
        if dep.startswith('so:'):
            continue
        # Убираем версии (формат: pkgname>=1.2.3)
        dep_name = dep.split('>')[0].split('<')[0].split('=')[0]
        if dep_name and dep_name not in dependencies:
            dependencies.append(dep_name)
    
    return dependencies


def print_dependencies(package_name, dependencies, version=None):
    """
    Вывод прямых зависимостей на экран
    """
    print("\n" + "=" * 60)
    print(f"ПРЯМЫЕ ЗАВИСИМОСТИ ПАКЕТА: {package_name}")
    if version:
        print(f"ВЕРСИЯ: {version}")
    print("=" * 60)
    
    if not dependencies:
        print("Прямые зависимости не найдены")
        return
    
    print(f"Найдено зависимостей: {len(dependencies)}")
    print("\nСписок прямых зависимостей:")
    
    for i, dep in enumerate(sorted(dependencies), 1):
        print(f"  {i:2d}. {dep}")
    
    print("=" * 60)


def analyze_alpine_dependencies(config):
    """
    Основная функция анализа зависимостей для Alpine Linux
    """
    try:
        # Загрузка и парсинг APKINDEX
        print("Загрузка информации о пакетах из репозитория Alpine...")
        apkindex_content = fetch_apk_index(config.repository_url)
        packages_data = parse_apkindex_content(apkindex_content)
        
        print(f"Загружено информации о {len(packages_data)} пакетах")
        
        # Получение зависимостей
        dependencies = get_package_dependencies(
            config.package_name, 
            config.package_version, 
            packages_data
        )
        
        # Вывод результатов
        print_dependencies(config.package_name, dependencies, config.package_version)
        
        return dependencies
        
    except Exception as e:
        print(f"Ошибка при анализе зависимостей: {e}", file=sys.stderr)
        return None

def main():
    """Основная функция приложения"""
    try:
        # Парсинг аргументов
        args = parse_arguments()
        
        # Создание конфигурации
        config = Config()
        config.package_name = args.package_name
        config.repository_url = args.repository_url
        config.test_repo_mode = args.test_repo_mode
        config.package_version = args.package_version
        config.tree_output = args.tree_output
        config.filter_substring = args.filter_substring
        
        # Валидация конфигурации
        validation_errors = validate_config(config)
        
        if validation_errors:
            print("ОШИБКИ ВАЛИДАЦИИ:", file=sys.stderr)
            for error in validation_errors:
                print(f"  - {error}", file=sys.stderr)
            sys.exit(1)
        
        # Вывод конфигурации (требование №3)
        print_config(config)
        
        # Анализ зависимостей Alpine Linux
        print("\nНачало анализа зависимостей...")
        dependencies = analyze_alpine_dependencies(config)
        
        if dependencies is not None:
            print("\nАнализ зависимостей завершен успешно!")
        else:
            print("\nАнализ зависимостей завершен с ошибками!", file=sys.stderr)
            sys.exit(1)
        
    except argparse.ArgumentError as e:
        print(f"Ошибка в аргументах командной строки: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nПриложение прервано пользователем", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Неожиданная ошибка: {e}", file=sys.stderr)
        sys.exit(1)
        
if __name__ == "__main__":
    main()

