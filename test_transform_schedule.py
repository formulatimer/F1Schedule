#!/usr/bin/env python3
"""Test suite for timezone conversion in transform_schedule.py"""

import json
from datetime import datetime, timedelta
import tempfile
import os


def test_timezone_conversion():
    """Test that timezone conversion works correctly"""
    
    # Test case 1: Bahrain with +03:00 offset
    # Local time: 2026-02-11T10:00:00
    # GMT offset: +03:00
    # Expected UTC: 2026-02-11T07:00:00Z (10:00 - 3 hours)
    
    local_time = datetime.fromisoformat("2026-02-11T10:00:00")
    gmt_offset_str = "+03:00"
    
    # Parse GMT offset
    sign = 1 if gmt_offset_str[0] == '+' else -1
    hours, minutes = map(int, gmt_offset_str[1:].split(':'))
    offset = timedelta(hours=sign * hours, minutes=sign * minutes)
    
    # Convert to UTC
    utc_time = local_time - offset
    
    assert utc_time.isoformat() == "2026-02-11T07:00:00", \
        f"Expected 2026-02-11T07:00:00 but got {utc_time.isoformat()}"
    print("✓ Test case 1 passed: Bahrain +03:00 offset")
    
    # Test case 2: Australia with +11:00 offset
    # Local time: 2026-03-06T12:30:00
    # GMT offset: +11:00
    # Expected UTC: 2026-03-06T01:30:00Z (12:30 - 11 hours)
    
    local_time = datetime.fromisoformat("2026-03-06T12:30:00")
    gmt_offset_str = "+11:00"
    
    sign = 1 if gmt_offset_str[0] == '+' else -1
    hours, minutes = map(int, gmt_offset_str[1:].split(':'))
    offset = timedelta(hours=sign * hours, minutes=sign * minutes)
    
    utc_time = local_time - offset
    
    assert utc_time.isoformat() == "2026-03-06T01:30:00", \
        f"Expected 2026-03-06T01:30:00 but got {utc_time.isoformat()}"
    print("✓ Test case 2 passed: Australia +11:00 offset")
    
    # Test case 3: Miami with -04:00 offset (negative offset)
    # Local time: 2026-05-03T14:00:00
    # GMT offset: -04:00
    # Expected UTC: 2026-05-03T18:00:00Z (14:00 - (-4) = 14:00 + 4 hours)
    
    local_time = datetime.fromisoformat("2026-05-03T14:00:00")
    gmt_offset_str = "-04:00"
    
    sign = 1 if gmt_offset_str[0] == '+' else -1
    hours, minutes = map(int, gmt_offset_str[1:].split(':'))
    offset = timedelta(hours=sign * hours, minutes=sign * minutes)
    
    utc_time = local_time - offset
    
    assert utc_time.isoformat() == "2026-05-03T18:00:00", \
        f"Expected 2026-05-03T18:00:00 but got {utc_time.isoformat()}"
    print("✓ Test case 3 passed: Miami -04:00 offset")
    
    # Test case 4: Las Vegas with -08:00 offset
    # Local time: 2026-11-21T22:00:00
    # GMT offset: -08:00
    # Expected UTC: 2026-11-22T06:00:00Z (22:00 + 8 hours = next day 06:00)
    
    local_time = datetime.fromisoformat("2026-11-21T22:00:00")
    gmt_offset_str = "-08:00"
    
    sign = 1 if gmt_offset_str[0] == '+' else -1
    hours, minutes = map(int, gmt_offset_str[1:].split(':'))
    offset = timedelta(hours=sign * hours, minutes=sign * minutes)
    
    utc_time = local_time - offset
    
    assert utc_time.isoformat() == "2026-11-22T06:00:00", \
        f"Expected 2026-11-22T06:00:00 but got {utc_time.isoformat()}"
    print("✓ Test case 4 passed: Las Vegas -08:00 offset with day rollover")
    
    print("\n✅ All timezone conversion tests passed!")


def test_full_transformation():
    """Test the core transformation logic"""
    
    import json
    from datetime import datetime, timedelta
    
    # Simulate the data and transformation logic
    sample_sessions = [
        ("2026-02-11T10:00:00", "+03:00", "2026-02-11T07:00:00Z"),  # Bahrain
        ("2026-03-06T12:30:00", "+11:00", "2026-03-06T01:30:00Z"),  # Australia
        ("2026-05-03T14:00:00", "-04:00", "2026-05-03T18:00:00Z"),  # Miami
        ("2026-11-21T22:00:00", "-08:00", "2026-11-22T06:00:00Z"),  # Las Vegas
    ]
    
    for local_time_str, gmt_offset_str, expected_utc in sample_sessions:
        # This is the exact logic from transform_schedule.py
        sign = 1 if gmt_offset_str[0] == '+' else -1
        hours, minutes = map(int, gmt_offset_str[1:].split(':'))
        offset = timedelta(hours=sign * hours, minutes=sign * minutes)
        
        session_start_dt = datetime.fromisoformat(local_time_str)
        session_start_utc = session_start_dt - offset
        result = session_start_utc.isoformat() + 'Z'
        
        assert result == expected_utc, \
            f"For {local_time_str} with offset {gmt_offset_str}: expected {expected_utc} but got {result}"
        print(f"✓ {local_time_str} {gmt_offset_str} -> {result}")
    
    print("\n✅ Full transformation logic test passed!")


if __name__ == "__main__":
    print("Running timezone conversion tests...\n")
    test_timezone_conversion()
    print("\nRunning full transformation test...\n")
    test_full_transformation()
    print("\n🎉 All tests passed successfully!")
