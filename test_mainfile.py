import hashlib
import shutil

from yt2flp import *
import os


def test_startup():
    assert startup_and_options(["you", "--debug"]) == {"boost": False, "debug": True, "name": "DEBUGoutput", "url":"you"}


class TestUrls:
    def test_valid_url(self):
        assert (
            stripurl("https://www.youtube.com/watch?v=EIyixC9NsLI&si=ksjrhgksjrbg")
            == "https://youtu.be/EIyixC9NsLI"
        )

    def test_random_url(self):
        import secrets

        urldata = secrets.token_hex(15)
        assert (
            stripurl(
                f"https://www.youtube.com/watch?v={urldata}&si={secrets.token_hex(10)}"
            )
            == f"https://youtu.be/{urldata}"
        )


def getPython():
    return "python3" if not os.system("python3 -c 'exit(0)'") else "python"


def hashFile(file):
    with open(file, "rb") as fd:
        return hashlib.sha256(fd.read()).hexdigest()


def copyNeeded(temppth):
    shutil.copy("examples/rickroll.bnd", temppth)
    shutil.copy("test/output.mp4", temppth)
    shutil.copy("helper1.py", temppth)
    shutil.copy("yt2flp.py", temppth)


# def test_ALL(tmp_path):
#     copyNeeded(tmp_path)
#     origDir = os.path.abspath(".")
#     os.chdir(tmp_path)
#     os.system(f"{getPython()} yt2flp.py https://www.youtube.com/watch?v=dQw4w9WgXcQ DEBUG")
#     assert hashFile("rickroll.bnd") == hashFile("output.bnd")
#     os.chdir(origDir)


class TestConsistency:
    def test_downloader(self, tmp_path):
        copyNeeded(tmp_path)
        origDir = os.path.abspath(".")
        os.chdir(tmp_path)
        download("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        shutil.move("vid.mp4", "vid1.mp4")
        download("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        assert hashFile("vid.mp4") == hashFile("vid.mp4")
        os.chdir(origDir)

    def test_booster(self, tmp_path):
        copyNeeded(tmp_path)
        origDir = os.path.abspath(".")
        os.chdir(tmp_path)
        shutil.copy("output.mp4", "vid.mp4")
        shutil.move("output.mp4", "oldput.mp4")
        boost(True)
        shutil.move("oldput.mp4", "vid.mp4")
        shutil.move("output.mp4", "output1.mp4")
        boost(True)
        assert hashFile("output1.mp4") == hashFile("output.mp4")
        os.chdir(origDir)

    def test_converter(self, tmp_path):
        copyNeeded(tmp_path)
        origDir = os.path.abspath(".")
        os.chdir(tmp_path)
        os.system(f"{getPython()} helper1.py output.mp4 output.bnd")
        os.system(f"{getPython()} helper1.py output.mp4 output1.bnd")
        assert hashFile("output1.bnd") == hashFile("output.bnd")
        os.chdir(origDir)
