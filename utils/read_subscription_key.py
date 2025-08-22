def read_subscription_key(file_path="subscription_key.txt") -> str:
    """Read the subscription key from the file."""
    with open(file_path, "r") as f:
        return f.read().strip()
