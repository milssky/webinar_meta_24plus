import os


class ApiClient:
    def __init__(self) -> None:
        self.api_key = os.getenv('API_KEY')  # <-- зависимость
        self.timeout = os.getenv('TIMEOUT')  # <-- зависимость


class Service:
    def __init__(self) -> None:
        self.api_client = ApiClient()  # <-- зависимость


def main():
    service = Service()  # <-- зависимость
    ...

if __name__ == '__main__':
    main()