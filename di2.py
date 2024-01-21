import os


class ApiClient:
    def __init__(self, api_key, timeout) -> None:
        self.api_key = api_key
        self.timeout = int(timeout)


class Service:
    def __init__(self, api_client) -> None:
        self.api_client = api_client  


def main(service: Service = Service(
        ApiClient(
            api_key=os.getenv('API_KEY'),
            timeout=os.getenv('TIMEOUT')
        )
    )
):
    in_service = service
    ...


if __name__ == '__main__':
    main()
