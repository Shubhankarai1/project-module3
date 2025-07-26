import json
import os
from datetime import datetime

class CostTracker:
    def __init__(self, data_file="usage_data.json"):
        self.data_file = data_file
        self.daily_limit = 450  # USD
        self.monthly_limit = 2000  # USD
        self._load_usage_data()

    def _load_usage_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, "r") as f:
                self.usage_data = json.load(f)
        else:
            self.usage_data = {"daily": {}, "monthly": {}}

    def _save_usage_data(self):
        with open(self.data_file, "w") as f:
            json.dump(self.usage_data, f, indent=4)

    def _get_current_month_key(self):
        return datetime.now().strftime("%Y-%m")

    def _get_current_day_key(self):
        return datetime.now().strftime("%Y-%m-%d")

    def record_usage(self, cost):
        day_key = self._get_current_day_key()
        month_key = self._get_current_month_key()

        if day_key not in self.usage_data["daily"]:
            self.usage_data["daily"][day_key] = 0
        self.usage_data["daily"][day_key] += cost

        if month_key not in self.usage_data["monthly"]:
            self.usage_data["monthly"][month_key] = 0
        self.usage_data["monthly"][month_key] += cost

        self._save_usage_data()

    def get_daily_usage(self):
        day_key = self._get_current_day_key()
        return self.usage_data["daily"].get(day_key, 0)

    def get_monthly_usage(self):
        month_key = self._get_current_month_key()
        return self.usage_data["monthly"].get(month_key, 0)

    def get_remaining_daily_budget(self):
        return self.daily_limit - self.get_daily_usage()

    def get_remaining_monthly_budget(self):
        return self.monthly_limit - self.get_monthly_usage()

    def can_afford(self, estimated_cost):
        return (self.get_remaining_daily_budget() >= estimated_cost and
                self.get_remaining_monthly_budget() >= estimated_cost)

    def calculate_cost(self, tokens, model="gpt-4o"):
        # Placeholder for OpenAI pricing. This needs to be updated with actual pricing.
        # As of my last update, gpt-4o pricing is:
        # Input: $5.00 / 1M tokens
        # Output: $15.00 / 1M tokens
        # Assuming a simple calculation for now, treating all tokens equally for cost estimation.
        # This should be refined to differentiate input/output tokens if possible.
        
        # For simplicity, let's assume an average cost per token for now.
        # Example: $10.00 per 1M tokens = $0.00001 per token
        cost_per_token = 0.00001 
        return tokens * cost_per_token

if __name__ == "__main__":
    tracker = CostTracker()
    print(f"Daily usage: {tracker.get_daily_usage()}")
    print(f"Monthly usage: {tracker.get_monthly_usage()}")
    print(f"Remaining daily budget: {tracker.get_remaining_daily_budget()}")
    print(f"Remaining monthly budget: {tracker.get_remaining_monthly_budget()}")

    # Simulate some usage
    cost_of_analysis = tracker.calculate_cost(10000) # 10,000 tokens
    print(f"Cost of 10,000 tokens: {cost_of_analysis}")

    if tracker.can_afford(cost_of_analysis):
        tracker.record_usage(cost_of_analysis)
        print(f"Recorded usage: {cost_of_analysis}")
    else:
        print("Cannot afford this analysis.")

    print(f"Daily usage after recording: {tracker.get_daily_usage()}")
    print(f"Monthly usage after recording: {tracker.get_monthly_usage()}")
    print(f"Remaining daily budget: {tracker.get_remaining_daily_budget()}")
    print(f"Remaining monthly budget: {tracker.get_remaining_monthly_budget()}")
