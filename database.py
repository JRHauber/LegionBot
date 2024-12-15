class Database():
    def __init__(self, **kwargs) -> None:
        self.setup_db(**kwargs)

    def setup_db(self):
        raise NotImplementedError()

    async def insert_request(self, server_id : int, requester_id : int, resource_message : str) -> int:
        raise NotImplementedError()

    async def claim_request(self, id : int, server_id : int, claimant_id : int):
        raise NotImplementedError()

    async def finish_request(self, id : int, server_id : int, claimant_id : int):
        raise NotImplementedError()

    async def get_requests(self, server_id : int):
        raise NotImplementedError()

    async def unclaim_request(self, id: int, server_id : int, claimant_id : int):
        raise NotImplementedError()

    async def get_claims(self, server_id : int, uid : int):
        raise NotImplementedError()

    async def get_user_requests(self, uid : int, server_id : int):
        raise NotImplementedError()

    async def new_project(self, server_id : int, name : str, time : int):
        raise NotImplementedError()

    async def add_resource(self, resource : str, count : int, pid : int, server_id : int):
        raise NotImplementedError()

    async def add_resource(self, resourc : str, pid : int, server_id : int):
        raise NotImplementedError()

    async def list_projects(self, server_id : int):
        raise NotImplementedError()

    async def list_contributors(self, pid : int, server_id : int):
        raise NotImplementedError()

    async def list_contributions(self, pid : int, server_id : int):
        raise NotImplementedError()

    async def list_resources (self, pid : int, server_id : int):
        raise NotImplementedError()

    async def contribute_resources (self, pid : int, name : str, amount : int, uid : int, server_id : int):
        raise NotImplementedError()

    async def complete_project(self, pid : int, server_id : int):
        raise NotImplementedError()