import os
import glob
import zipfile
import pandas as pd
from icalendar import Calendar, Event, vText
from datetime import datetime, timedelta
import pytz

# Configuration
OUTPUT_FILE = 'all_courses.ics'

# Section Time Mapping (Start Time, End Time)
SECTION_TIMES = {
    1:  ("08:00", "08:40"),
    2:  ("08:45", "09:25"),
    3:  ("09:40", "10:20"),
    4:  ("10:25", "11:05"),
    5:  ("11:10", "11:50"),
    6:  ("11:55", "12:35"),
    7:  ("12:40", "13:20"),
    8:  ("13:30", "14:10"),
    9:  ("14:15", "14:55"),
    10: ("15:00", "15:40"),
    11: ("15:45", "16:25"),
    12: ("16:30", "17:10"),
    13: ("17:15", "17:55"),
    14: ("18:20", "19:00"),
    15: ("19:05", "19:45"),
    16: ("19:50", "20:30"),
    # Extended slots
    17: ("20:35", "21:15"),
    18: ("21:20", "22:00"),
    19: ("22:05", "22:45"),
    20: ("22:50", "23:30"),
    21: ("23:35", "00:15"),
    22: ("00:20", "01:00"),
}

def parse_section_range(val):
    """
    Parses section value which could be int (1), str ("1"), or range ("14-17").
    Returns (start_section, end_section) as integers.
    """
    if pd.isna(val):
        return None, None
    
    s = str(val).strip()
    if not s:
        return None, None
        
    try:
        if '-' in s:
            parts = s.split('-')
            return int(parts[0]), int(parts[1])
        else:
            v = int(float(s)) # handle 1.0
            return v, v
    except Exception as e:
        print(f"Warning: Could not parse section '{val}': {e}")
        return None, None

def get_datetime_range(date_val, start_sec, end_sec):
    """
    Combines date and section times into UTC start/end datetimes.
    """
    if start_sec not in SECTION_TIMES or end_sec not in SECTION_TIMES:
        print(f"Warning: Section {start_sec} or {end_sec} not in configuration map.")
        return None, None
    
    # Parse Date
    try:
        if isinstance(date_val, str):
            date_obj = datetime.strptime(date_val.strip(), '%Y-%m-%d').date()
        elif isinstance(date_val, datetime):
            date_obj = date_val.date()
        else:
            # Try pandas timestamp
            date_obj = date_val.date()
    except Exception as e:
        print(f"Warning: Could not parse date '{date_val}': {e}")
        return None, None

    start_time_str = SECTION_TIMES[start_sec][0]
    end_time_str = SECTION_TIMES[end_sec][1]
    
    start_h, start_m = map(int, start_time_str.split(':'))
    end_h, end_m = map(int, end_time_str.split(':'))
    
    # Localize to Beijing Time (Asia/Shanghai)
    tz = pytz.timezone('Asia/Shanghai')
    
    dt_start = datetime.combine(date_obj, datetime.min.time()).replace(hour=start_h, minute=start_m)
    dt_end = datetime.combine(date_obj, datetime.min.time()).replace(hour=end_h, minute=end_m)
    
    # Handle overnight
    if dt_end < dt_start:
        dt_end += timedelta(days=1)
        
    dt_start = tz.localize(dt_start)
    dt_end = tz.localize(dt_end)
    
    # Convert to UTC
    dt_start_utc = dt_start.astimezone(pytz.utc)
    dt_end_utc = dt_end.astimezone(pytz.utc)
    
    return dt_start_utc, dt_end_utc

def process_zip_files(zip_files):
    """
    Processes a list of zip file paths or file-like objects.
    Returns the ICS content as bytes.
    """
    cal = Calendar()
    cal.add('prodid', '-//Course Schedule//pkx07.github.io//CN')
    cal.add('version', '2.0')
    
    total_events = 0
    
    for zip_file in zip_files:
        try:
            # zip_file can be a path (str) or a file-like object
            with zipfile.ZipFile(zip_file, 'r') as z:
                xls_files = [f for f in z.namelist() if f.endswith('.xls') or f.endswith('.xlsx')]
                if not xls_files:
                    print(f"  No excel file found in {zip_file}")
                    continue
                
                xls_filename = xls_files[0]
                with z.open(xls_filename) as f:
                    # Read header from row 3 (index 2)
                    df = pd.read_excel(f, header=2)
                    
                    for idx, row in df.iterrows():
                        if pd.isna(row.get('日期')) or pd.isna(row.get('节次')):
                            continue
                            
                        s_start, s_end = parse_section_range(row['节次'])
                        if not s_start:
                            continue
                            
                        dt_start, dt_end = get_datetime_range(row['日期'], s_start, s_end)
                        if not dt_start:
                            continue
                            
                        event = Event()
                        course_name = row.get('课程名称', 'Unknown Course')
                        if pd.isna(course_name): course_name = "Unknown Course"
                        event.add('summary', str(course_name))
                        
                        loc = row.get('授课地点', '')
                        if pd.notna(loc):
                            event.add('location', str(loc))
                            
                        desc_parts = []
                        if pd.notna(row.get('授课内容')):
                            desc_parts.append(f"授课内容：{row['授课内容']}")
                        if pd.notna(row.get('授课要求')):
                            desc_parts.append(f"授课要求：{row['授课要求']}")
                        if pd.notna(row.get('授课备注')):
                            desc_parts.append(f"授课备注：{row['授课备注']}")
                        if pd.notna(row.get('授课教师')):
                            desc_parts.append(f"授课教师：{row['授课教师']}")
                        if pd.notna(row.get('授课性质')):
                            desc_parts.append(f"授课性质：{row['授课性质']}")
                            
                        if desc_parts:
                            event.add('description', "\n".join(desc_parts))
                            
                        event.add('dtstart', dt_start)
                        event.add('dtend', dt_end)
                        event.add('dtstamp', datetime.now(pytz.utc))
                        
                        cal.add_component(event)
                        total_events += 1
                        
        except Exception as e:
            print(f"  Error processing zip: {e}")
            import traceback
            traceback.print_exc()

    print(f"Total events created: {total_events}")
    return cal.to_ical()

def main():
    zip_files = glob.glob('*.zip')
    print(f"Found {len(zip_files)} zip files.")
    
    ics_content = process_zip_files(zip_files)
    
    with open(OUTPUT_FILE, 'wb') as f:
        f.write(ics_content)
        
    print(f"\nSuccessfully generated {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
