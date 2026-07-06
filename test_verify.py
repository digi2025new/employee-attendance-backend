from app.auth.hashing import verify_password

hash_from_db = "$2b$12$WHSonxqFD1qguh.e./YqyuA6irE5Oy4R0UimptrvWFwh3AfkxcYym"

print(verify_password("Suru@911", hash_from_db))