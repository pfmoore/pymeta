from zipfile import ZipFile
from pathlib import Path
from email import message_from_bytes
from tempfile import TemporaryDirectory
from shutil import unpack_archive
import subprocess
import sys

from build import ProjectBuilder

def get_wheel_deps(name):
    with open(name, "rb") as fd:
        with ZipFile(fd) as z:
            metadata_files = [n for n in z.namelist() if n.endswith(".dist-info/METADATA")]
            assert len(metadata_files) == 1
            metadata = z.read(metadata_files[0])
    msg = message_from_bytes(metadata)
    return msg.get_all("Requires-Dist") or []

def get_sdist_deps(name):
    with TemporaryDirectory() as t:
        temp = Path(t)
        src = temp / "src"
        src.mkdir()
        unpack_archive(name, src)
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
        return get_wheel_deps(wheels[0])


if __name__ == "__main__":
    import sys
    for dep in get_sdist_deps(sys.argv[1]):
        print(dep)
