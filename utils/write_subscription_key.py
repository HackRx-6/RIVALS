# utils.py
def write_subscription_key(new_key: str, file_path="subscription_key.txt"):
    """Write a new subscription key to the file."""
    with open(file_path, "w") as f:
        f.write(new_key)
    print(f"Subscription key updated in {file_path}")
