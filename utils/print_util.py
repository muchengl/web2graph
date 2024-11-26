import base64
import json


def pretty_print(obj, indent=4, max_length=100):
    """
    Pretty print a complex object with truncated Base64 content.

    Args:
        obj: The object to print (e.g., dict, list, etc.).
        indent: Indentation level for JSON-style formatting.
        max_length: Maximum length to display for Base64 content.
    """
    # def truncate_base64(value):
    #     """Truncate Base64 strings if they are too long."""
    #     if isinstance(value, str):
    #         try:
    #             # Check if the string is likely Base64 encoded
    #             if base64.b64encode(base64.b64decode(value)).decode() == value:
    #                 return value[:max_length] + "..." if len(value) > max_length else value
    #         except Exception:
    #             pass
    #     return value

    def truncate_data(value):
        """Truncate Base64 image data if it is too long."""
        if isinstance(value, str) and value.startswith("data:image"):
            # Truncate the Base64 image data
            parts = value.split(",", 1)  # Split the prefix and Base64 data
            if len(parts) == 2 and len(parts[1]) > max_length:
                return parts[0] + "," + parts[1][:max_length] + "..."
        return value

    def recursive_truncate(data):
        """Recursively truncate Base64 content in the data."""
        if isinstance(data, dict):
            return {k: recursive_truncate(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [recursive_truncate(item) for item in data]
        else:
            return truncate_data(data)

    truncated_obj = recursive_truncate(obj)
    print(json.dumps(truncated_obj, indent=indent, ensure_ascii=False))


# Example usage
if __name__ == "__main__":
    complex_object = {
        "name": "Example",
        "description": "This is a sample object with Base64 content.",
        "image": base64.b64encode(b"This is a simulated image binary data.").decode(),
        "nested": {
            "another_image": base64.b64encode(b"Another image data example.").decode(),
            "non_base64_text": "Regular text data"
        },
        "list": [
            base64.b64encode(b"List image binary data.").decode(),
            "Some other text"
        ]
    }

    pretty_print(complex_object)
