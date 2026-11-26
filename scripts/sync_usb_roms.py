import hashlib
import os
import shutil
import sys

USB_DIR = sys.argv[1] if len(sys.argv) > 1 else "/mnt/usb"
ROMS_DIR = sys.argv[2] if len(sys.argv) > 2 else "/home/embebidos/mame/roms"
REPORT_FILE = sys.argv[3] if len(sys.argv) > 3 else "/tmp/roms_importadas.txt"

EXTS = (".zip", ".7z", ".chd")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


os.makedirs(ROMS_DIR, exist_ok=True)

existing_hashes = set()
existing_names = set()

for fname in os.listdir(ROMS_DIR):
    fpath = os.path.join(ROMS_DIR, fname)
    if os.path.isfile(fpath) and fname.lower().endswith(EXTS):
        existing_names.add(fname.lower())
        existing_hashes.add(sha256_file(fpath))

copied = []

for root, dirs, files in os.walk(USB_DIR):
    for fname in files:
        if not fname.lower().endswith(EXTS):
            continue

        src = os.path.join(root, fname)
        fhash = sha256_file(src)

        if fname.lower() in existing_names or fhash in existing_hashes:
            continue

        dst = os.path.join(ROMS_DIR, fname)
        shutil.copy2(src, dst)

        existing_names.add(fname.lower())
        existing_hashes.add(fhash)
        copied.append(fname)

with open(REPORT_FILE, "w", encoding="utf-8") as out:
    for item in copied:
        out.write(item + "\n")

print(f"ROMs nuevas importadas: {len(copied)}")

