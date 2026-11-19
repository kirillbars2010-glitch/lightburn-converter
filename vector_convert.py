#!/usr/bin/env python3
"""Vector outline conversion for monochrome PCB PDFs on Windows."""
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    import pymupdf as fitz
except ImportError:
    sys.exit('Установите библиотеку: python -m pip install pymupdf')


def num(v):
    return f'{v:.6f}'.rstrip('0').rstrip('.') or '0'


def xy(pt):
    return f'{num(pt.x)},{num(pt.y)}'


def make_path(items, close=False):
    result = []
    current = None
    start = None
    for item in items:
        kind = item[0]
        if kind in ('re', 'qu'):
            if close and current is not None:
                result.append('Z')
            if kind == 'qu':
                q = item[1]
                result.append('M' + xy(q.ul) + ' L' + xy(q.ll) + ' L' + xy(q.lr) + ' L' + xy(q.ur) + ' Z')
                current = start = None
                continue
            r = item[1]
            result.append(f'M{num(r.x0)},{num(r.y0)} L{num(r.x1)},{num(r.y0)} L{num(r.x1)},{num(r.y1)} L{num(r.x0)},{num(r.y1)} Z')
            current = start = None
        elif kind in ('l', 'c'):
            a = item[1]
            if current is None or abs(a.x-current.x) > 1e-4 or abs(a.y-current.y) > 1e-4:
                if close and current is not None:
                    result.append('Z')
                result.append('M' + xy(a))
                start = a
            if kind == 'l':
                result.append('L' + xy(item[2]))
                current = item[2]
            else:
                result.append('C' + ' '.join(xy(pt) for pt in item[2:5]))
                current = item[4]
        else:
            raise ValueError(f'Неподдерживаемый тип геометрии: {kind}')
    if close and current is not None:
        result.append('Z')
    return ' '.join(result)


def run():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(errors='replace')
    p = argparse.ArgumentParser(description='Векторный PDF или SVG платы в контуры SVG/PDF и PNG. Windows, чёрно-белая графика.')
    p.add_argument('input', type=Path)
    p.add_argument('-o', '--output', type=Path)
    p.add_argument('--dpi', type=int, default=600)
    p.add_argument('--page', type=int)
    p.add_argument('--tolerance', type=float, default=0.01, help='допуск геометрии в pt (по умолчанию 0.01, около 0.0035 мм)')
    a = p.parse_args()
    if not 72 <= a.dpi <= 2400 or not 0 < a.tolerance <= 0.1:
        p.error('DPI: 72–2400; допуск: больше 0 и не больше 0.1 pt')
    if a.input.suffix.lower() == '.svg':
        svg_doc = fitz.open(a.input, filetype='svg')
        try:
            doc = fitz.open(stream=svg_doc.convert_to_pdf(), filetype='pdf')
        finally:
            svg_doc.close()
    else:
        doc = fitz.open(a.input)
    if a.page is not None and not 1 <= a.page <= len(doc):
        p.error('Неверный номер страницы')
    pages = [a.page-1] if a.page else range(len(doc))
    out = a.output or a.input.parent / (a.input.stem + '_vectors')
    out.mkdir(parents=True, exist_ok=True)
    helper = Path(__file__).with_name('vector_wpf.ps1')
    for index in pages:
        page = doc[index]
        if page.get_images() or page.get_text().strip():
            raise ValueError('В PDF обнаружены текст или растровые изображения: они не поддерживаются. Экспортируйте текст в контуры.')
        drawings = page.get_drawings(extended=True)
        if any(d.get('type') in ('clip', 'group') for d in drawings):
            raise ValueError('PDF содержит clipping/group: преобразование без потерь не гарантируется.')
        shapes = []
        for d in drawings:
            if d['type'] not in ('s', 'f'):
                raise ValueError('Неподдерживаемый тип объекта: ' + d['type'])
            color = d['fill'] if d['type'] == 'f' else d['color']
            if color is None or len(color) != 3 or max(color)-min(color) > 0.001 or min(abs(color[0]), abs(color[0]-1)) > 0.001:
                raise ValueError('Обнаружена цветная или серая геометрия. Поддерживаются только чёрные и белые объекты; измените цвета в исходном файле и повторите конвертацию.')
            opacity = d['fill_opacity'] if d['type'] == 'f' else d['stroke_opacity']
            if opacity is not None and abs(opacity-1) > 0.001:
                raise ValueError('Прозрачность не поддерживается.')
            if d['type'] == 's' and (d['lineJoin'] != 1 or tuple(d['lineCap']) != (1, 1, 1) or d['dashes'] != '[] 0'):
                raise ValueError('Поддерживаются только сплошные линии со скруглёнными концами и соединениями.')
            shapes.append({'path': make_path(d['items'], bool(d['closePath'])), 'type': d['type'], 'white': color[0] > 0.5,
                           'width': d['width'] or 0, 'evenodd': bool(d['even_odd'])})
        name = a.input.stem + (f'_page_{index+1}' if len(doc) > 1 else '')
        inp, result = out / (name + '_shapes.tmp.json'), out / (name + '_path.tmp.txt')
        inp.write_text(json.dumps(shapes), encoding='utf-8')
        cmd = ['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', str(helper.resolve()), str(inp.resolve()), str(result.resolve()), str(a.tolerance)]
        print(f'Страница {index+1}: обработка {len(shapes)} векторных фигур...', flush=True)
        subprocess.run(cmd, check=True)
        path = result.read_text(encoding='utf-8-sig').strip()
        inp.unlink()
        result.unlink()
        w, h = page.rect.width, page.rect.height
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{w*25.4/72:.9f}mm" height="{h*25.4/72:.9f}mm" viewBox="0 0 {w:.8f} {h:.8f}"><path fill="black" fill-rule="evenodd" stroke="none" d="{path}"/></svg>'
        (out/(name+'.svg')).write_text(svg, encoding='utf-8')
        vector = fitz.open(stream=svg.encode(), filetype='svg')
        pdf = fitz.open(stream=vector.convert_to_pdf(), filetype='pdf')
        pdf.save(out/(name+'.pdf'), deflate=True)
        pdf[0].get_pixmap(dpi=a.dpi, alpha=False).save(out/(name+'.png'))
        print(f'Размер страницы: {w*25.4/72:.3f} × {h*25.4/72:.3f} мм. Результат: {out.resolve()}')
        pdf.close()
        vector.close()

if __name__ == '__main__':
    try:
        run()
    except Exception as exc:
        sys.exit(f'Ошибка: {exc}')
