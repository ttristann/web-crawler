import hashlib

class ContentHashManager:
    """
    This class is to only check for exact duplication.
    Keeps track of all the url and their hash numbners
    to compare with other hash numbers to check for 
    duplicates between two websites
    """
    def __init__(self):
        self.content_hashes = {}

    def generate_hash(self, text):
        """
        Generates a special hash number based on the textual
        content of the web page
        """
        if isinstance(text, bytes):
            try:
                normalized_text = text.decode('utf-8')
            except UnicodeDecodeError as e:
                print(f"UnicodeDecodeError: {e} - using fallback encoding.")
                # You can choose a different encoding or handle it differently
                normalized_text = text.decode('latin-1', errors='ignore')
        else:
            normalized_text = text  # If it's already a string

        normalized_text = " ".join(normalized_text.split()).lower()  # Normalize so capitalization
        return hashlib.md5(normalized_text.encode()).hexdigest()

    def is_duplicate(self, url, content_text):
        """
        Checks if the content is a duplicate.
        Returns True if duplicate; otherwise, 
        stores the hash and returns False.
        """
        content_hash = self.generate_hash(content_text)

        if content_hash in self.content_hashes: # it is a duplicate
            return True
        else:
            # Store the hash with its URL
            self.content_hashes[content_hash] = url
            return False



