import database
import sqlite3
import asyncio
import re

class DatabaseSqlite(database.Database):
    db = None
    database_name = "database.db"
    lock = None

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def setup_db(self, database_name : str = "database.db") -> None:
        assert database_name

        self.db = sqlite3.connect(database_name, check_same_thread=False)

        self.lock = asyncio.Lock()

        self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_id INTEGER NOT NULL,
                filled BOOL NOT NULL,
                requester_id INTEGER NOT NULL,
                claimant_id INTEGER,
                resource_message TEXT NOT NULL
            );
            """
        )

    async def insert_request(self, server_id : int, requester_id : int, resource_message : str) -> int:
        await self.lock.acquire()
        try:
            cursor = self.db.cursor()
            sanitary_message = re.sub(r'[^a-zA-Z0-9 ]+', '', resource_message)
            res = cursor.execute(f"""
                INSERT INTO requests
                (server_id, requester_id, resource_message, filled)
                VALUES ({server_id}, {requester_id}, "{sanitary_message}", FALSE)
                RETURNING *;
                """
            )
            data = res.fetchone()
            self.db.commit()
            cursor.close()
        finally:
            self.lock.release()
        return data

    async def claim_request(self, id : int, server_id : int, claimant_id : int):
        await self.lock.acquire()
        try:
            cursor = self.db.cursor()
            res = cursor.execute(f"""
                UPDATE requests
                SET claimant_id = {claimant_id}
                WHERE id = {id} AND server_id = {server_id} AND claimant_id IS NULL
                RETURNING *;
                """
            )
            data = res.fetchone()
            self.db.commit()
            cursor.close()
        finally:
            self.lock.release()
        return data

    async def finish_request(self, id : int, server_id : int, claimant_id : int):
        await self.lock.acquire()
        try:
            cursor = self.db.cursor()
            res = cursor.execute(f"""
                UPDATE requests
                SET filled = {claimant_id}
                WHERE id = {id} AND server_id = {server_id} AND claimant_id = {claimant_id}
                RETURNING *;
                """
            )
            data = res.fetchone()
            self.db.commit()
            cursor.close()
        finally:
            self.lock.release()
        return data

    # dont use this
    async def get_requests(self):
        await self.lock.acquire()
        try:
            cursor = self.db.cursor()
            res = cursor.execute("SELECT * FROM REQUESTS;")
            data = res.fetchall()
            cursor.close()
        finally:
            self.lock.release()
        return data

    async def insert_project(self):
        pass

    async def insert_server(self):
        pass

    async def clear_all(self):
        await self.lock.acquire()
        try:
            self.db.execute("DELETE FROM requests WHERE 1;")
        finally:
            self.lock.release()


async def __test_insert(db : DatabaseSqlite):
    await db.clear_all()
    await db.insert_request(1, 1, "this is the message")
    print(await db.get_requests())

async def __test_claim(db : DatabaseSqlite):
    await db.clear_all()
    id, *rest = await db.insert_request(1, 1, "this is the message")
    print(await db.claim_request(id, 1, 1))
    print(await db.get_requests())

async def __test_complete(db : DatabaseSqlite):
    await db.clear_all()
    id, *rest = await db.insert_request(1, 1, "this is the message")
    print(await db.claim_request(id, 1, 1))
    print(await db.finish_request(id, 1, 1))
    print(await db.get_requests())

async def __main():
    print("queue tests")
    db = DatabaseSqlite(database_name="test.db")

    await __test_insert(db)
    print()
    await __test_claim(db)
    print()
    await __test_complete(db)
    print()


if __name__=="__main__":
    asyncio.run(__main())
