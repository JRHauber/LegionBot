class Database():
    def __init__(self, **kwargs) -> None:
        self.setup_db(**kwargs)

    async def setup_db(self):
        raise NotImplementedError()
