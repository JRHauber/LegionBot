import time
class Project:
    def __init__(self, name, resources):
        self.name = name
        self.resources = resources
        self.contributors = {}
        self.maxResources = resources.copy()
        self.start = time.time()
    
    def getContributions(self):
        totalResources = 0
        output = "```"
        for v in self.maxResources.values():
            totalResources += v
        
        for i in self.contributors:
            name = i
            con = float(self.contributors[i])/float(totalResources)*100.0
            output += f"\n{name}: {con:.2f}%"
        output += '\n```'
        return output
    
    def completeProject(self):
        end = time.time()
        dif = (end - self.start)/86400
        output = f"This project took {dif:.2f} days."
        return output

    def addContribution(self, newContributor, type, count):
        if not newContributor in self.contributors:
            self.contributors[newContributor] = count
            self.resources[type] = self.resources[type] - count
            if self.resources[type] < 0:
                self.resources[type] = 0
        elif newContributor in self.contributors:
            self.contributors[newContributor] = self.contributors[newContributor] + count
            self.resources[type] = self.resources[type] - count
            if self.resources[type] < 0:
                self.resources[type] = 0
        else:
            return -1
