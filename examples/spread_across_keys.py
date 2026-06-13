"""
Example: spread an API workload across 3 free-tier accounts, each with its
own rate limit and daily quota. You supply the real call in `make_handler`.
"""
from tierbroker import Broker, Provider


def make_handler(api_key):
    def handler(prompt):
        # Replace with your real API call using this key, e.g.:
        #   return openai_call(api_key, prompt)
        return f"[{api_key[:6]}] processed: {prompt}"
    return handler


broker = Broker(max_retries=3)
broker.add(Provider("acct-1", make_handler("key_aaa111"), rate_per_sec=2, quota=100))
broker.add(Provider("acct-2", make_handler("key_bbb222"), rate_per_sec=2, quota=100))
broker.add(Provider("acct-3", make_handler("key_ccc333"), rate_per_sec=2, quota=100, weight=2))

for i in range(8):
    print(broker.submit(f"task {i}"))

print("\nstats:", broker.stats())
