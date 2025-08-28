class CostTracker:
    def __init__(self):
        self.total_cost = 0.0
        self.details = []

    def add(self, cost, details):
        self.total_cost += cost
        self.details.append(details)

    def summary(self):
        return {
            "total_cost": self.total_cost,
            "details": self.details
        }