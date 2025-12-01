class RealtimeNotification:
    def __init__(self, host_name, price):
        self.host_name = host_name
        self.price = price

    def display_info(self):
        print(f"Host: {self.host_name}, Price: ${self.price}")

    def get_host_initial(self):
        # This will fail if host_name is None
        return self.host_name[0].upper()


def main():
    # Simulate a null pointer scenario
    listing = RealtimeNotification(None, 170.0)  # host_name is None

    listing.display_info()  # This works
    print("Host initial:", listing.get_host_initial())  # This throws an error


if __name__ == "__main__":
    main()
