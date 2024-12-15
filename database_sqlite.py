import database
import sqlite3
import asyncio
import re
import resource_requests

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
                requestor_id INTEGER NOT NULL,
                claimant_id INTEGER,
                resource_message VARCHAR(20) NOT NULL
            );
            """
        )

        self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS resources (
                resource_id  INTEGER PRIMARY KEY,
                project_id INTEGER,
                name TEXT NOT NULL,
                total_amount INTEGER NOT NULL,
                UNIQUE(name, project_id) ON CONFLICT ABORT,
                FOREIGN KEY(project_id) REFERENCES projects(project_id)
            );
            """
        )

        self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS contributors (
                contributor_id INTEGER NOT NULL,
                project_id INTEGER NOT NULL,
                PRIMARY KEY(contributor_id, project_id),
                FOREIGN KEY(project_id) REFERENCES projects(project_id)
            );
            """
        )

        self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS contributions (
                resource_id INTEGER,
                contributor_id INTEGER,
                amount INTEGER NOT NULL,
                PRIMARY KEY(resource_id, contributor_id),
                FOREIGN KEY(resource_id) REFERENCES resoruces(resource_id),
                FOREIGN KEY(contributor_id) REFERENCES contributors(contributor_id)
            );
            """
        )

        self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS projects (
                project_id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                time INTEGER NOT NULL,
                completed BOOL NOT NULL
            );
            """
        )

    async def insert_request(self, server_id : int, requestor_id : int, resource_message : str) -> int:
        await self.lock.acquire()
        try:
            cursor = self.db.cursor()
            res = cursor.execute(f"""
                INSERT INTO requests
                (server_id, requestor_id, resource_message, filled)
                VALUES ({server_id}, {requestor_id}, "{sanitize(resource_message)}", FALSE)
                RETURNING id;
                """
            )
            data = res.fetchone()
            self.db.commit()
            cursor.close()
        finally:
            self.lock.release()
        return data[0]

    async def claim_request(self, id : int, server_id : int, claimant_id : int):
        await self.lock.acquire()
        try:
            cursor = self.db.cursor()
            res = cursor.execute(f"""
                UPDATE requests
                SET claimant_id = {claimant_id}
                WHERE id = {id} AND server_id = {server_id} AND claimant_id IS NULL AND not filled
                RETURNING *;
                """
            )
            data = res.fetchone()
            self.db.commit()
            cursor.close()
        except Exception as e:
            print(e)
        finally:
            self.lock.release()
        return convertTuple(data)

    async def finish_request(self, id : int, server_id : int, claimant_id : int):
        await self.lock.acquire()
        try:
            cursor = self.db.cursor()
            res = cursor.execute(f"""
                UPDATE requests
                SET filled = {claimant_id}
                WHERE id = {id} AND server_id = {server_id} AND claimant_id = {claimant_id} AND not filled
                RETURNING *;
                """
            )
            data = res.fetchone()
            self.db.commit()
            cursor.close()
        finally:
            self.lock.release()
        return convertTuple(data)

    async def unclaim_request(self, id : int, server_id : int, claimant_id : int):
        await self.lock.acquire()
        try:
            cursor = self.db.cursor()
            res = cursor.execute(f"""
                UPDATE requests
                SET claimant_id = NULL
                WHERE id = {id} AND server_id = {server_id} AND claimant_id = {claimant_id} AND not filled
                RETURNING *;
            """)
            data = res.fetchone()
            self.db.commit()
            cursor.close()
        finally:
            self.lock.release()
        return convertTuple(data)

    async def get_claims(self, server_id : int, uid : int):
        await self.lock.acquire()
        try:
            cursor = self.db.cursor()
            res = cursor.execute(f"""
                SELECT * FROM REQUESTS
                WHERE server_id = {server_id} AND claimant_id = {uid} AND not filled
            """)
            data = res.fetchall()
            cursor.close()
        finally:
            self.lock.release()
        return list(map(convertTuple, data))

    async def get_user_requests(self, server_id : int, uid : int):
        await self.lock.acquire()
        try:
            cursor = self.db.cursor()
            res = cursor.execute(f"""
                SELECT * FROM REQUESTS
                WHERE server_id = {server_id} AND requestor_id = {uid} AND not filled
            """)
            data = res.fetchall()
            cursor.close()
        finally:
            self.lock.release()
        return list(map(convertTuple, data))

    # dont use this
    async def get_requests(self, server_id : int):
        await self.lock.acquire()
        try:
            cursor = self.db.cursor()
            res = cursor.execute(f"""
                SELECT * FROM REQUESTS
                WHERE not filled AND server_id = {server_id};
            """)
            data = res.fetchall()
            cursor.close()
        finally:
            self.lock.release()
        return list(map(convertTuple, data))

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

    async def new_project(self, server_id : int, name : str, time : int):
        await self.lock.acquire()
        try:
            cursor = self.db.cursor()
            res = cursor.execute(f"""
                INSERT INTO projects
                (server_id, name, time, completed)
                VALUES ({server_id}, '{sanitize(name)}', {time}, FALSE)
                RETURNING project_id;
                """
            )
            data = res.fetchone()
            self.db.commit()
            cursor.close()
        finally:
            self.lock.release()
        return data[0]

    async def add_resource(self, resource : str, count : int, pid : int, server_id : int):
        await self.lock.acquire()
        try:
            cursor = self.db.cursor()
            servcheck = cursor.execute(f"""
                SELECT server_id FROM projects
                WHERE project_id = {pid} AND not completed;
            """).fetchone()[0]
            if servcheck == server_id:
                res = cursor.execute(f"""
                    INSERT INTO resources
                    (project_id, name, total_amount)
                    VALUES ({pid}, '{sanitize(resource)}', {count});
                """)
            self.db.commit()
            cursor.close()
        finally:
            self.lock.release()

    async def remove_resource(self, resource : str, pid : int, server_id : int):
        await self.lock.acquire()
        try:
            cursor = self.db.cursor()
            servcheck = cursor.execute(f"""
                SELECT server_id FROM projects
                WHERE project_id = {pid} AND not completed;
            """).fetchone()[0]
            if servcheck == server_id:
                res = cursor.execute(f"""
                    DELETE FROM resources
                    WHERE project_id = {pid} and name = '{sanitize(resource)}';
                """)
            self.db.commit()
            cursor.close()
        finally:
            self.lock.release()

    async def list_projects(self, server_id : int):
        await self.lock.acquire()
        try:
            cursor = self.db.cursor()
            res = cursor.execute(f"""
                SELECT name, project_id FROM projects
                WHERE server_id = {server_id} AND not completed;
            """)
            data = res.fetchall()
            cursor.close()
        finally:
            self.lock.release()
        return data

    async def list_contributors(self, pid : int, server_id : int):
        await self.lock.acquire()
        try:
            cursor = self.db.cursor()
            servcheck = cursor.execute(f"""
                SELECT server_id FROM projects
                WHERE project_id = {pid};
            """).fetchone()[0]
            if servcheck == server_id:
                res = cursor.execute(f"""
                    SELECT DISTINCT contributor_id FROM contributors
                    WHERE project_id = {pid};
                """)
                data = res.fetchall()
            cursor.close()
        finally:
            self.lock.release()
        return data

    async def list_contributions(self, pid : int, server_id : int):
        await self.lock.acquire()
        try:
            cursor = self.db.cursor()
            servcheck = cursor.execute(f"""
                SELECT server_id FROM projects
                WHERE project_id = {pid};
            """).fetchone()[0]
            if servcheck == server_id:
                res = cursor.execute(f"""
                SELECT contributors.contributor_id, resources.name, contributions.amount
                FROM projects JOIN contributors ON projects.project_id = contributors.project_id
                JOIN contributions ON contributors.contributor_id = contributions.contributor_id
                JOIN resources ON contributions.resource_id = resources.resource_id
                ORDER BY contributors.contributor_id, resources.name;
            """)
                data = res.fetchall()
            cursor.close()
        finally:
            self.lock.release()
        return data

    async def list_resources(self, pid : int, server_id : int):
        await self.lock.acquire()
        try:
            cursor = self.db.cursor()
            servcheck = cursor.execute(f"""
                SELECT server_id FROM projects
                WHERE project_id = {pid};
            """).fetchone()[0]
            if servcheck == server_id:
                res = cursor.execute(f"""
                SELECT resources.name, COALESCE(SUM(contributions.amount), 0), total_amount
                FROM projects JOIN resources ON projects.project_id = resources.project_id
                LEFT JOIN contributions ON resources.resource_id = contributions.resource_id
                GROUP BY resources.name, resources.resource_id, total_amount
                ORDER BY resources.name, total_amount;
            """)
                data = res.fetchall()
            cursor.close()
        finally:
            self.lock.release()
        return data

    async def contribute_resources(self, pid : int, name : str, amount : int, uid : int, server_id : int):
        await self.lock.acquire()
        try:
            cursor = self.db.cursor()
            servcheck = cursor.execute(f"""
                SELECT server_id FROM projects
                WHERE project_id = {pid} AND not completed;
            """).fetchone()[0]
            if servcheck == server_id:
                res = cursor.execute(f"""
                    INSERT INTO contributors
                    (contributor_id, project_id)
                    VALUES ({uid}, {pid})
                    ON CONFLICT DO NOTHING;
                """)
                rid = cursor.execute(f"""
                    SELECT resource_id FROM resources WHERE name = '{sanitize(name)}' and project_id = {pid}
                """).fetchone()[0]
                res = cursor.execute(f"""
                    INSERT INTO contributions
                    (contributor_id, amount, resource_id)
                    VALUES ({uid}, {amount}, {rid})
                    ON CONFLICT (contributor_id, resource_id) DO
                    UPDATE
                    SET amount = amount + {amount}
                    WHERE contributor_id = {uid} AND resource_id = {rid} AND not completed;
                """)
            self.db.commit()
            cursor.close()
        finally:
            self.lock.release()

    async def complete_project(self, pid, server_id):
        await self.lock.acquire()
        try:
            cursor = self.db.cursor()
            res = cursor.execute(f"""
                UPDATE projects
                SET completed = TRUE
                WHERE project_id = {pid} AND server_id = {server_id}
                RETURNING name;
            """)
            data = res.fetchone()
            self.db.commit()
            cursor.close()
        finally:
            self.lock.release()
        return data[0]

def convertTuple(args):
    if args != None:
        return resource_requests.resourceRequest(*args)
    else:
        return None

def sanitize(stringy):
    return re.sub(r'[^a-zA-Z0-9 ]+', '', stringy)

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
