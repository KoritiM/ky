import argparse
import sys
import os


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


if __name__ == "__main__":
    main()
