import database
import sqlite3
import asyncio
import queue
import time

class DatabaseSqlite(database.Database):
    pool = None
    database_name = "database.db"


    def setup_db(self, database_name : str, pool_size : int = 1) -> None:
        assert pool_size > 0
        assert database_name

        self.pool = queue.LifoQueue(pool_size)
        for _ in range(pool_size):
            self.pool.put_nowait(sqlite3.connect(database_name, check_same_thread=False))

        db = self.pool.get()
        try:
            print("table create")
            db.execute(
                """
                CREATE TABLE IF NOT EXISTS requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT
                );
                """)
        finally:
            print("return resource")
            self.pool.put(db)
        print("db setup")

    async def insert_request(self):
        assert self.pool is not None
        db = self.pool.get()
        cursor = db.cursor()
        cursor.execute("INSERT INTO requests DEFAULT VALUES;")
        db.commit()
        cursor.close()
        self.pool.put(db)

    async def get_requests(self):
        assert self.pool is not None
        db = self.pool.get()
        cursor = db.cursor()
        res = cursor.execute("SELECT * FROM REQUESTS;")
        data = res.fetchall()
        self.pool.put(db)
        return data

    async def insert_project(self):
        assert self.pool is not None

    async def insert_server(self):
        assert self.pool is not None

async def __main():
    print("queue tests")
    db = DatabaseSqlite()
    db.setup_db("test.db", pool_size=1)

    async def insert_read():
        await db.insert_request()
        await db.get_requests()


    start = time.time()
    tasks = [asyncio.create_task(insert_read()) for _ in range(10000)]
    await asyncio.gather(*tasks)
    end = time.time()


    print(len(await db.get_requests()))
    print(end - start)

if __name__=="__main__":
    asyncio.run(__main())