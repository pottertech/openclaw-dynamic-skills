#!/usr/bin/env python3
"""
Generate XID-style time-sorted IDs for skills

Format: 20 characters, base62-encoded, time-sorted
Structure: [timestamp_ms:8chars][random:12chars]
"""

import time
import hashlib
import base64

def generate_xid():
    """Generate a time-sorted XID-style ID"""
    
    # Get current timestamp in milliseconds
    timestamp_ms = int(time.time() * 1000)
    
    # Convert to base62 (8 chars for timestamp)
    base62_chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    
    # Timestamp part (8 chars)
    ts = timestamp_ms
    ts_part = ''
    for _ in range(8):
        ts_part = base62_chars[ts % 62] + ts_part
        ts //= 62
    
    # Random part (12 chars)
    random_data = hashlib.md5(f"{timestamp_ms}{time.time()}".encode()).digest()
    random_part = ''
    for byte in random_data[:9]:
        random_part += base62_chars[byte % 62]
    
    return ts_part + random_part

if __name__ == '__main__':
    print("Generating 10 sample XIDs:")
    for i in range(10):
        xid = generate_xid()
        print(f"  {xid}")
        time.sleep(0.001)  # Small delay to show time-sorting
