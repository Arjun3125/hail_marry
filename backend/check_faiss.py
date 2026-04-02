import sqlite3, os, json

conn = sqlite3.connect('vidyaos_demo.db')
c = conn.cursor()

# Get tenant ID from DB
c.execute("SELECT id, name FROM tenants WHERE name LIKE '%Modern%'")
row = c.fetchone()
if row:
    db_tid = row[0]
    print(f"DB Tenant ID: {db_tid}")
    print(f"DB Tenant Name: {row[1]}")
else:
    print("ERROR: Modern Hustlers tenant not found!")
    exit(1)

# List FAISS vector store files
vs_dir = "vector_store"
if os.path.isdir(vs_dir):
    files = os.listdir(vs_dir)
    print(f"\nFAISS files: {files}")
    for f in files:
        if f.endswith(".meta.json"):
            with open(os.path.join(vs_dir, f)) as fp:
                data = json.load(fp)
            print(f"  {f}: {len(data)} chunks")
            # Extract the tenant namespace from filename
            namespace = f.replace(".meta.json", "")
            print(f"  namespace: {namespace}")
else:
    print(f"\nERROR: {vs_dir} directory not found!")

# Check what tenant_id the FAISS expects
# The FAISS stores use f"tenant_{tenant_id}" as namespace
expected_ns = f"tenant_{db_tid}"
expected_ns_nohyphen = f"tenant_{str(db_tid).replace('-','')}"
print(f"\nExpected namespace: {expected_ns}")
print(f"Expected (no hyphens): {expected_ns_nohyphen}")

conn.close()
