class Monitor:
    def __init__(self, block_threshold=0.5):
        self.block_count = 0
        self.total = 0
        self.block_threshold = block_threshold

    def update(self, blocked):
        self.total += 1
        if blocked:
            self.block_count += 1
        self.check_alerts()

    def check_alerts(self):
        if self.total > 0:
            rate = self.block_count / self.total
            if rate > self.block_threshold:
                print(f"⚠️ ALERT: High block rate detected! Current rate: {rate:.2f}")

    def report(self):
        rate = self.block_count / max(1, self.total)
        print(f"Final Monitoring Report:")
        print(f"- Total Requests: {self.total}")
        print(f"- Blocked Requests: {self.block_count}")
        print(f"- Block rate: {rate:.2f}")
