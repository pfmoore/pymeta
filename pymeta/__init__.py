from zipfile import ZipFile
from tarfile import TarFile
from pathlib import Path
from email import message_from_bytes
from tempfile import TemporaryDirectory
import subprocess
import sys

from .metadata import Metadata

def get_wheel_metadata(fd):
    with ZipFile(fd) as z:
        metadata_files = [n for n in z.namelist() if n.endswith(".dist-info/METADATA")]
        assert len(metadata_files) == 1
        metadata = z.read(metadata_files[0])
    meta = Metadata.from_rfc822(metadata.decode("utf-8"))
    return meta

def get_sdist_metadata(fd):
    with TemporaryDirectory() as t:
        temp = Path(t)
        src = temp / "src"
        src.mkdir()
        with TarFile(fileobj=fd) as t:
            t.extractall(src)
        pkg = next(src.iterdir())
        subprocess.run(
            [
                sys.executable, "-m", "build",
                "--wheel",
                "--outdir", str(temp),
                str(pkg)
            ],
            capture_output=True
        )
        wheels = list(temp.glob("*.whl"))
        assert len(wheels) == 1
        with open(wheels[0], "rb") as w:
            return get_wheel_metadata(w)


if __name__ == "__main__":
    meta = get_sdist_metadata(sys.argv[1])
    print(meta)
