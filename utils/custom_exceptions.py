class DataIntegrityError(Exception):
    """Custom exception for dictionary to dataclass conversion errors."""
    pass


class FileIOError(Exception):
    """Custom exception for file input/output errors."""
    pass

class DatabaseError(Exception):
    """Custom exception for database input-output errors."""
    pass