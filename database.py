class Database():
    def __init__(self) -> None:
        self.setup_db()

    async def setup_db(self):
        raise NotImplementedError()
