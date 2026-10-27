import sys, tarfile, io, os

if __name__ == '__main__':
    deb_path = sys.argv[1]
    out_dir = sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)

    with open(deb_path, 'rb') as f:
        f.seek(8)
        while True:
            header = f.read(60)
            if len(header) < 60: break
            name = header[:16].decode('latin1').strip()
            size = int(header[48:58].decode('latin1').strip())
            if name.startswith('data.tar'):
                data = f.read(size)
                with tarfile.open(fileobj=io.BytesIO(data), mode='r:*') as tar:
                    tar.extractall(out_dir)
                break
            else:
                f.seek(size + (size % 2), 1)
    print(f"Extracted {deb_path} into {out_dir}")
