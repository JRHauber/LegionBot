class resourceRequest:
    def __init__(self, id, server_id, filled, requestor_id, claimant_id, resource):
        self.id = id
        self.server_id = server_id
        self.filled = filled
        self.requestor_id = requestor_id
        self.claimant_id = claimant_id
        self.resource = resource