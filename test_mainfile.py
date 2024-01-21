from yt2flp import *

def test_startup():
    assert startup_and_options(True) == {"boost": True, "debug": True, "name": "output"}



class TestUrls:
    def test_valid_url(self):
        assert stripurl("https://www.youtube.com/watch?v=EIyixC9NsLI&si=ksjrhgksjrbg") == "https://youtu.be/EIyixC9NsLI"

    def test_random_url(self):
        import secrets
        urldata = secrets.token_hex(15)
        assert stripurl(f"https://www.youtube.com/watch?v={urldata}&si={secrets.token_hex(10)}") == f"https://youtu.be/{urldata}"