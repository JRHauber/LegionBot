class resourceRequest:
    def __init__(self, id, requestor_name, requestor_mention, requestor_id, claimant_name, claimant_mention, claimant_id, resource):
        self.id = id
        self.requestor_name = requestor_name
        self.requestor_mention = requestor_mention
        self.requestor_id = requestor_id
        self.claimant_name = claimant_name
        self.claimant_mention = claimant_mention
        self.claimant_id = claimant_id
        self.resource = resource
