import struct

def read_dbf(filename):
    try:
        with open(filename, 'rb') as f:
            # Read header
            header = f.read(32)
            num_records = struct.unpack('<I', header[4:8])[0]
            header_len = struct.unpack('<H', header[8:10])[0]
            record_len = struct.unpack('<H', header[10:12])[0]
            
            print(f"Number of records: {num_records}")
            
            # Read field descriptors
            fields = []
            while f.tell() < header_len - 1:
                field_data = f.read(32)
                if field_data[0] == 0x0D: break
                name = field_data[:11].replace(b'\x00', b'').decode('ascii', 'ignore')
                fields.append(name)
            
            print(f"Fields: {fields}")
            
            # Read first 10 records
            f.seek(header_len)
            for i in range(10):
                record = f.read(record_len)
                # This is a very rough parser, just to see some text
                # Assuming standard encoding (EUC-KR or CP949 for Korean shapefiles)
                try:
                    print(f"Record {i}: {record.decode('cp949', errors='ignore')}")
                except:
                    print(f"Record {i}: (binary data)")
                    
    except Exception as e:
        print(f"Error reading DBF: {e}")

if __name__ == "__main__":
    # Path inside the container (mapped volume)
    # Assuming frontend/public is accessible or I need to copy it?
    # The user said public folder. In the container, source is mounted.
    # d:\final_project\source -> /app (in backend?)
    # Let's try the absolute path relative to the workspace root if running locally
    # But I am running in the backend container usually?
    # No, I am running `run_command` which executes in the shell.
    # The CWD is `d:\final_project\source`.
    # So I can access `frontend/public/sig.dbf`.
    
    read_dbf("frontend/public/sig.dbf")
