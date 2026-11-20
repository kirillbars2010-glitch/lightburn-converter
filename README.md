<div align="center">

# ◈ LightBurn Converter

**PDF / SVG → SVG · PDF · PNG**

Изготовление печатных плат методом лазерного выжигания краски<br>
PCB fabrication using laser paint removal

[🇷🇺 Русский](#-русский) · [🇬🇧 English](#-english) · [Сообщить об ошибке / Report an issue](../../issues)

![Windows](https://img.shields.io/badge/platform-Windows-0078D6?logo=windows&logoColor=white)
![Python](https://img.shields.io/badge/Python-3-blue?logo=python&logoColor=white)
![Input](https://img.shields.io/badge/input-PDF%20%7C%20SVG-8b5cf6)
![Output](https://img.shields.io/badge/output-SVG%20%7C%20PDF%20%7C%20PNG-10b981)

</div>

---

## 🇷🇺 Русский

**LightBurn Converter** — локальный инструмент для подготовки изображений печатных плат к изготовлению методом лазерного выжигания краски в LightBurn. Программа преобразует заливки и толстые линии в контуры и создаёт файлы SVG, PDF и PNG. Исходный файл не изменяется.

> [!IMPORTANT]
> Конвертер предназначен для изображений, в которых **белые фигуры — дорожки, а чёрные — вырезы**. Для обычной чёрной графики на белом фоне этот алгоритм не подходит. Перед работой на станке обязательно проверьте размер, отверстия и траектории в LightBurn.

### ✨ Возможности

- Загрузка PDF или SVG через простой локальный веб-интерфейс.
- Экспорт SVG, векторного PDF и PNG за одну конвертацию.
- Перевод толстых линий в контуры и объединение фигур средствами Windows WPF.
- Настройка DPI для PNG и допуска приближения векторной геометрии.
- Сохранение размеров страницы в векторных файлах.

### 📄 Настройки экспорта PDF

При экспорте платы выберите следующие параметры (названия пунктов могут отличаться в вашей программе):

| Параметр | Значение |
|---|---|
| Формат | PDF |
| Вывод | Локальный |
| Содержимое | Всё в графическом виде |
| Слои | Объединённые |
| Цвет | Чёрное на белом |

После экспорта проверьте результат: для этого конвертера **белые области должны соответствовать дорожкам, а чёрные — вырезам**. Название режима «чёрное на белом» само по себе не гарантирует нужную полярность; при необходимости инвертируйте изображение в исходной программе.

### 📦 Готовая сборка для Windows

Скачайте [LightBurnConverter.exe](releases/LightBurnConverter.exe) из папки релизов и запустите его двойным щелчком. Python устанавливать не нужно. Это экспериментальная standalone-сборка: если Windows покажет предупреждение SmartScreen, проверьте файл и разрешите запуск только если доверяете источнику.

Окно EXE должно оставаться открытым во время работы — оно запускает локальный веб-интерфейс в браузере. Для обработки линий Windows используются штатные PowerShell и WPF. Результаты сохраняются в `%LOCALAPPDATA%\\LightBurnConverter\\web_results`.

Если EXE не запускается, используйте исходный вариант через Python из раздела ниже и сообщите об ошибке в [Issues](../../issues).

### 🚀 Установка и запуск

1. Установите **Python 3** для Windows и убедитесь, что команда `python` доступна в терминале.
2. Скачайте проект через **Code → Download ZIP** и распакуйте архив или клонируйте репозиторий:
   ```powershell
   git clone https://github.com/kirillbars2010-glitch/lightburn-converter.git
   cd lightburn-converter
   ```
3. Установите зависимость:
   ```powershell
   python -m pip install pymupdf
   ```
4. Запустите **`ЗАПУСТИТЬ ПРОГРАММУ.bat`**. В браузере откроется локальная страница программы.
5. Выберите PDF или SVG, настройте параметры и нажмите **«Конвертировать»**. Скачайте нужный формат результата.

Также можно использовать командную строку:

```powershell
python vector_convert.py "файл.svg" --dpi 600 --tolerance 0.01
```

По умолчанию файлы сохраняются в папку `<имя_файла>_vectors` рядом с исходником. Параметр `-o` задаёт другую папку, а `--page 1` выбирает страницу PDF. В веб-интерфейсе поддерживается только одностраничный PDF.

### ⚠️ Ограничения и проверка результата

- Поддерживаются только **непрозрачные чёрные и белые** векторные объекты. Цветные и серые объекты нужно предварительно перекрасить.
- Текст, растровые изображения, обрезки и группы не поддерживаются. Переведите текст в контуры и упростите исходный файл.
- Линии должны быть сплошными, со скруглёнными концами и соединениями. Другие типы объектов могут быть отклонены.
- Геометрия приближённая: допуск по умолчанию — `0.01 pt` (около `0.0035 мм`).
- PNG может импортироваться без учёта DPI — при необходимости задайте размер вручную.
- Для резки границы могут создавать проходы по внутренним и внешним контурам. **Всегда проверяйте предпросмотр перед запуском лазера.**

---

## 🇬🇧 English

**LightBurn Converter** is a local tool for preparing PCB artwork for fabrication using laser paint removal with LightBurn. It converts filled shapes and thick lines into outlines and generates SVG, PDF, and PNG files without modifying the source.

> [!IMPORTANT]
> This converter is intended for artwork where **white shapes represent tracks and black shapes represent cutouts**. It is not suitable for ordinary black artwork on a white background. Always check dimensions, holes, and toolpaths in LightBurn before operating your machine.

### ✨ Features

- Load PDF or SVG through a simple local web interface.
- Export SVG, vector PDF, and PNG in one conversion.
- Convert thick lines into outlines and combine shapes using Windows WPF.
- Adjust PNG DPI and the vector geometry approximation tolerance.
- Preserve page dimensions in vector outputs.

### 📄 PDF export settings

When exporting the PCB, use the settings below (option names may vary between applications):

| Setting | Value |
|---|---|
| Format | PDF |
| Output | Local |
| Content | Everything as graphics |
| Layers | Merged |
| Color | Black on white |

After exporting, check the artwork: this converter requires **white areas to represent tracks and black areas to represent cutouts**. The name “black on white” alone does not guarantee the required polarity; invert the artwork in the source application if necessary.

### 📦 Windows build

Download [LightBurnConverter.exe](releases/LightBurnConverter.exe) from the releases folder and double-click it. Python is not required. This is an experimental standalone build; if Windows SmartScreen shows a warning, verify the source and run it only if you trust it.

Keep the EXE window open while using the app — it starts the local web interface in your browser. Line processing uses the PowerShell and WPF components already included with Windows. Results are stored in `%LOCALAPPDATA%\\LightBurnConverter\\web_results`.

If the EXE does not start, use the Python version below and report the problem in [Issues](../../issues).

### 🚀 Installation and usage

1. Install **Python 3** for Windows and make sure `python` is available in your terminal.
2. Download and extract the project using **Code → Download ZIP**, or clone the repository:
   ```powershell
   git clone https://github.com/kirillbars2010-glitch/lightburn-converter.git
   cd lightburn-converter
   ```
3. Install the dependency:
   ```powershell
   python -m pip install pymupdf
   ```
4. Run **`ЗАПУСТИТЬ ПРОГРАММУ.bat`**. The local application page opens in your browser.
5. Choose a PDF or SVG, adjust the settings, and click **«Конвертировать»** (Convert). Download the formats you need. The interface is currently in Russian.

You can also use the command line:

```powershell
python vector_convert.py "file.svg" --dpi 600 --tolerance 0.01
```

By default, outputs are saved beside the input in a `<filename>_vectors` folder. Use `-o` to select another output folder or `--page 1` to select a PDF page. The web interface accepts single-page PDFs only.

### ⚠️ Limitations and safety checks

- Only **opaque black and white** vector objects are supported. Recolor colored or gray objects before conversion.
- Text, raster images, clipping, and groups are not supported. Convert text to outlines and simplify the source artwork.
- Lines must be solid, with round caps and joins. Other object types may be rejected.
- Geometry is approximated: the default tolerance is `0.01 pt` (about `0.0035 mm`).
- PNG imports may ignore DPI; set the size manually when needed.
- For cutting, outlines may produce passes along both inner and outer contours. **Always preview toolpaths before starting the laser.**

---

<div align="center">
Made for makers · Сделано для тех, кто создаёт
</div>
