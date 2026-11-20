#!/usr/bin/env python3
"""Local-only PDF converter web interface."""
import email
from email import policy
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import threading
import uuid
import webbrowser

ROOT = Path(__file__).resolve().parent
DATA = (Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'LightBurnConverter' / 'web_results'
        if getattr(sys, 'frozen', False) else ROOT / 'web_results')
MAX_SIZE = 50 * 1024 * 1024

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(fmt % args)

    def send_data(self, status, data, content_type):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(data)))
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(data)

    def send_json(self, status, value):
        self.send_data(status, json.dumps(value, ensure_ascii=False).encode('utf-8'), 'application/json; charset=utf-8')

    def do_GET(self):
        path = self.path.split('?', 1)[0]
        if path == '/':
            return self.send_data(200, (ROOT / 'interface.html').read_bytes(), 'text/html; charset=utf-8')
        match = re.fullmatch(r'/files/([a-f0-9]{32})/(result\.(?:svg|pdf|png))', path)
        if not match:
            return self.send_error(404)
        file = DATA / match.group(1) / 'output' / match.group(2)
        if not file.is_file():
            return self.send_error(404)
        mime = {'svg': 'image/svg+xml', 'pdf': 'application/pdf', 'png': 'image/png'}[file.suffix[1:]]
        data = file.read_bytes()
        self.send_response(200)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Disposition', f'attachment; filename="lightburn.{file.suffix[1:]}"')
        self.send_header('Content-Length', str(len(data)))
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        if self.path != '/api/convert':
            return self.send_error(404)
        # A browser page from another origin must not access this local service.
        origin = self.headers.get('Origin')
        if origin and origin != f'http://{self.headers.get("Host")}':
            return self.send_json(403, {'error': 'Недопустимый источник запроса.'})
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if not 0 < size <= MAX_SIZE:
                raise ValueError('Файл слишком большой или пустой (максимум 50 МБ).')
            content_type = self.headers.get('Content-Type', '')
            if not content_type.startswith('multipart/form-data;'):
                raise ValueError('Ожидается загрузка файла PDF или SVG.')
            body = self.rfile.read(size)
            msg = email.message_from_bytes(('Content-Type: ' + content_type + '\r\nMIME-Version: 1.0\r\n\r\n').encode() + body, policy=policy.default)
            fields = {}
            filename = ''
            for part in msg.iter_parts():
                name = part.get_param('name', header='content-disposition')
                if name:
                    fields[name] = part.get_payload(decode=True)
                    if name == 'file':
                        filename = part.get_filename() or ''
            data = fields.get('file', b'')
            extension = Path(filename).suffix.lower()
            if extension not in ('.pdf', '.svg') or not data:
                raise ValueError('Выберите корректный файл PDF или SVG.')
            if extension == '.pdf' and not data.startswith(b'%PDF-'):
                raise ValueError('Выберите корректный PDF-файл.')
            dpi = int(fields.get('dpi', b'600'))
            tolerance = float(fields.get('tolerance', b'0.01'))
            if not 72 <= dpi <= 2400 or not 0 < tolerance <= 0.1:
                raise ValueError('DPI должен быть от 72 до 2400, допуск — больше 0 и не больше 0,1 pt.')
            import pymupdf
            try:
                doc = pymupdf.open(stream=data, filetype=extension[1:])
                try:
                    if len(doc) != 1:
                        raise ValueError('Сейчас поддерживается PDF с одной страницей. Сохраните нужную страницу отдельно.')
                finally:
                    doc.close()
            except (RuntimeError, pymupdf.FileDataError) as exc:
                raise ValueError('Не удалось открыть файл PDF или SVG.') from exc
            run = uuid.uuid4().hex
            folder = DATA / run
            folder.mkdir(parents=True)
            source = folder / ('result' + extension)
            source.write_bytes(data)
            output = folder / 'output'
            worker = [sys.executable, '--convert-worker'] if getattr(sys, 'frozen', False) else [sys.executable, str(ROOT / 'vector_convert.py')]
            cmd = worker + [str(source), '-o', str(output), '--dpi', str(dpi), '--tolerance', str(tolerance)]
            completed = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=300, env={**__import__('os').environ, 'PYTHONUTF8': '1'})
            if completed.returncode:
                raise ValueError((completed.stderr or completed.stdout or 'Ошибка конвертации.').strip())
            files = {ext: f'/files/{run}/result.{ext}' for ext in ('svg', 'pdf', 'png')}
            self.send_json(200, {'files': files, 'message': completed.stdout.strip()})
        except (ValueError, subprocess.TimeoutExpired) as exc:
            self.send_json(400, {'error': str(exc)})
        except Exception as exc:
            self.send_json(500, {'error': 'Ошибка: ' + str(exc)})


def main():
    DATA.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    url = f'http://127.0.0.1:{server.server_port}/'
    print('Откройте в браузере: ' + url, flush=True)
    print('Для остановки закройте это окно или нажмите Ctrl+C.', flush=True)
    if '--no-browser' not in sys.argv:
        threading.Timer(0.7, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--convert-worker':
        sys.argv.pop(1)
        import vector_convert
        try:
            vector_convert.run()
        except Exception as exc:
            sys.exit(f'Ошибка: {exc}')
    else:
        main()
