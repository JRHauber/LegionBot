class Candidate:
    def __init__(self, name: str, uid: int, cid: int):
        self.name = name
        self.uid = uid
        self.cid = cid
        self.votes = 0
        self.voters = []

    def Vote(self, uid: int):
        self.votes += 1
        self.voters.append(uid) if uid not in self.voters else None

    def RemoveVote(self, uid: int):
        if uid in self.voters:
            self.votes -= 1
            self.voters.remove(uid)