"""
blocklist.py

This file just contains the blocklist of the JWT tokens. It will be imported
by app and the logout resource so that tokens can be added to the blocklist
when the user logs out. In a real world scenario, this shouldn't be a set
as it is now.
"""

BLOCKLIST = set()
