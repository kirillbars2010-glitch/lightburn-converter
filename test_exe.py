import json
import os
import subprocess
import tempfile
import time
import unittest
from pathlib import Path
from urllib.request import Request, urlopen

EXE = Path(__file__).resolve().parent / 'dist' / 'LightBurnConverter.exe'

class ExeTest(unittest.TestCase):
    def test_server_and_conversion(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / 'server.log'
            env = dict(os.environ, LOCALAPPDATA=tmp, TEMP=tmp, TMP=tmp, PYTHONUTF8='1')
            with log.open('w+', encoding='utf-8') as stream:
                process = subprocess.Popen([str(EXE), '--no-browser'], stdout=stream, stderr=stream, env=env)
                try:
                    url = None
                    for _ in range(150):
                        time.sleep(.2)
                        text = log.read_text(encoding='utf-8', errors='replace')
                        import re
                        match = re.search(r'http://127\.0\.0\.1:\d+/', text)
                        if match:
                            url = match.group(0)
                            break
                        if process.poll() is not None:
                            self.fail(text)
                    self.assertIsNotNone(url, log.read_text(encoding='utf-8', errors='replace'))
                    self.assertIn('LightBurn', urlopen(url).read().decode('utf-8'))
                    svg = b'<svg xmlns="http://www.w3.org/2000/svg" width="20mm" height="10mm"><rect x="1" y="1" width="10" height="5" fill="white"/></svg>'
                    boundary = 'testboundary'
                    body = (b'--testboundary\r\nContent-Disposition: form-data; name="file"; filename="test.svg"\r\nContent-Type: image/svg+xml\r\n\r\n' + svg + b'\r\n--testboundary\r\nContent-Disposition: form-data; name="dpi"\r\n\r\n72\r\n--testboundary--\r\n')
                    request = Request(url + 'api/convert', data=body, headers={'Content-Type': 'multipart/form-data; boundary=' + boundary})
                    result = json.loads(urlopen(request, timeout=60).read())
                    for ext, path in result['files'].items():
                        data = urlopen(url.rstrip('/') + path).read()
                        self.assertTrue(data, ext)
                finally:
                    subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    process.wait(timeout=10)

if __name__ == '__main__':
    unittest.main()
