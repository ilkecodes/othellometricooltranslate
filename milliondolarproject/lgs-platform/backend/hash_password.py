#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/ilkeileri/milliondolarproject/lgs-platform/backend')

from app.api.v1.auth import get_password_hash

password = "password123"
hashed = get_password_hash(password)
print(hashed)
