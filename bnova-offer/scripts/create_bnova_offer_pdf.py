#!/usr/bin/env python3
import argparse
import os
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent

parser = argparse.ArgumentParser(description="Create a B NOVA Studio branded access handover PDF.")
parser.add_argument(
    "--output",
    default="output/pdf/akt-peredachi-dostupov-lr-nsk.pdf",
    help="Output PDF path.",
)
args = parser.parse_args()

font_dir = Path(
    os.environ.get(
        "BNOVA_FONT_DIR",
        "/Users/aiassist/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/libreoffice-headless/libreoffice/LibreOfficeDev.app/Contents/Resources/fonts/truetype",
    )
)
font_files = {
    "Sans": font_dir / "NotoSans-Regular.ttf",
    "SansBold": font_dir / "NotoSans-Bold.ttf",
    "Mono": font_dir / "DejaVuSansMono.ttf",
}
fallback_files = {
    "Sans": font_dir / "DejaVuSans.ttf",
    "SansBold": font_dir / "DejaVuSans-Bold.ttf",
    "Mono": font_dir / "DejaVuSansMono.ttf",
}
for name, path in font_files.items():
    if not path.exists():
        path = fallback_files[name]
    if name not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont(name, str(path)))

out = Path(args.output).expanduser().resolve()
out.parent.mkdir(parents=True, exist_ok=True)
logo = SKILL_DIR / "assets" / "bnova-header-logo.png"

W, H = A4
LEFT = 37
RIGHT = W - 37
USABLE = RIGHT - LEFT
BLUE = colors.HexColor("#0037FF")
TEXT = colors.HexColor("#16191F")
MUTED = colors.HexColor("#7C838F")
SOFT = colors.HexColor("#EEF0F4")
DARK = colors.HexColor("#14171D")
WHITE = colors.white

c = canvas.Canvas(str(out), pagesize=A4)
c.setTitle("Передача доступов и мест хранения - ЛР-НСК")
c.setAuthor("B NOVA Studio")


def spaced(text, x, y, size=6, tracking=3, color=MUTED, align="left"):
    font = "Mono"
    total = sum(stringWidth(ch, font, size) for ch in text) + tracking * max(0, len(text) - 1)
    if align == "right":
        x -= total
    c.saveState()
    tx = c.beginText(x, y)
    tx.setFont(font, size)
    tx.setFillColor(color)
    tx.setCharSpace(tracking)
    tx.textLine(text)
    c.drawText(tx)
    c.restoreState()


def wrap_text(text, font, size, max_width):
    words = text.split(" ")
    lines = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if stringWidth(candidate, font, size) <= max_width:
            current = candidate
            continue
        if current:
            lines.append(current)
            current = word
            continue
        part = ""
        for char in word:
            if stringWidth(part + char, font, size) <= max_width:
                part += char
            else:
                lines.append(part)
                part = char
        current = part
    if current:
        lines.append(current)
    return lines


def draw_wrap(text, x, y, width, font="Sans", size=9.6, leading=14.2, color=TEXT):
    c.setFont(font, size)
    c.setFillColor(color)
    for line in wrap_text(text, font, size, width):
        c.drawString(x, y, line)
        y -= leading
    return y


def header(label):
    c.drawImage(ImageReader(str(logo)), LEFT, H - 64, width=135, height=24, mask="auto")
    spaced(label, RIGHT, H - 52, 5.5, 2.8, MUTED, "right")
    spaced("ДЛЯ ЛР-НСК · НОВОСИБИРСК", RIGHT, H - 64, 5.5, 2.8, MUTED, "right")


def page_number(page):
    c.setFont("Mono", 6)
    c.setFillColor(MUTED)
    c.drawRightString(RIGHT, 30, f"{page:02d}")


def title(lines):
    y = H - 110
    for index, line in enumerate(lines):
        c.setFillColor(TEXT)
        c.setFont("SansBold" if index == len(lines) - 1 else "Sans", 26)
        c.drawString(LEFT, y, line)
        y -= 35
    return y - 16


def section(text, y):
    spaced(text.upper(), LEFT, y, 6.2, 3.0, BLUE)
    return y - 22


def soft_note(y, heading, text):
    lines = wrap_text(text, "Sans", 9.2, USABLE - 32)
    height = 43 + len(lines) * 13
    c.setFillColor(SOFT)
    c.rect(LEFT, y - height, USABLE, height, stroke=0, fill=1)
    spaced(heading.upper(), LEFT + 16, y - 21, 6.2, 3.0, BLUE)
    draw_wrap(text, LEFT + 16, y - 43, USABLE - 32, "Sans", 9.2, 13.2, colors.HexColor("#474D59"))
    return y - height - 25


def info_rows(y, heading, rows, note=None):
    row_heights = []
    for _, value, _ in rows:
        row_heights.append(max(31, len(wrap_text(value, "Sans", 9.4, USABLE - 176)) * 14 + 9))
    note_height = 26 if note else 0
    height = 38 + sum(row_heights) + note_height
    c.setFillColor(SOFT)
    c.rect(LEFT, y - height, USABLE, height, stroke=0, fill=1)
    spaced(heading.upper(), LEFT + 16, y - 20, 6.0, 3.0, BLUE)
    cy = y - 48
    for (label, value, url), row_height in zip(rows, row_heights):
        c.setFillColor(MUTED)
        c.setFont("Mono", 6.1)
        c.drawString(LEFT + 16, cy, label.upper())
        start_y = cy + 1
        after = draw_wrap(value, LEFT + 150, start_y, USABLE - 176, "Sans", 9.4, 13.4, BLUE if url else TEXT)
        if url:
            c.linkURL(url, (LEFT + 150, after + 1, RIGHT - 16, start_y + 11), relative=0)
        cy -= row_height
    if note:
        draw_wrap(note, LEFT + 16, y - height + 18, USABLE - 32, "Sans", 8.0, 11.2, MUTED)
    return y - height - 25


def dash_list(y, items):
    for item in items:
        c.setStrokeColor(BLUE)
        c.setLineWidth(1.0)
        c.line(LEFT, y + 5, LEFT + 12, y + 5)
        y = draw_wrap(item, LEFT + 24, y, USABLE - 24, "Sans", 9.6, 14.4, colors.HexColor("#404650"))
        y -= 8
    return y


def feedback_block(y):
    height = 160
    c.setFillColor(DARK)
    c.rect(LEFT, y - height, USABLE, height, stroke=0, fill=1)
    c.setFillColor(WHITE)
    c.setFont("SansBold", 18)
    c.drawString(LEFT + 30, y - 48, "Обсудим детали?")
    c.setFillColor(colors.HexColor("#C4C8D0"))
    c.setFont("SansBold", 10.8)
    for offset, line in enumerate(["Напишите или позвоните –", "отвечу на вопросы и покажу,", "где лежат доступы."]):
        c.drawString(LEFT + 30, y - 80 - offset * 18, line)
    x = RIGHT - 250
    c.setFillColor(WHITE)
    c.setFont("SansBold", 15)
    c.drawRightString(RIGHT - 30, y - 48, "B NOVA STUDIO")
    c.setFillColor(colors.HexColor("#C4C8D0"))
    c.setFont("SansBold", 10.7)
    contact_lines = [
        ("+7 913 004-61-62 · WhatsApp · Telegram", "tel:+79130046162"),
        ("@E_Berest", "https://t.me/E_Berest"),
        ("berestenkoea@gmail.com", "mailto:berestenkoea@gmail.com"),
        ("bnova.site", "https://bnova.site/"),
    ]
    cy = y - 80
    for text, url in contact_lines:
        c.drawRightString(RIGHT - 30, cy, text)
        c.linkURL(url, (x, cy - 2, RIGHT - 30, cy + 11), relative=0)
        cy -= 20
    return y - height - 20


# Page 1
header("ПЕРЕДАЧА ДОСТУПОВ И МЕСТ ХРАНЕНИЯ")
y = title(["Передача доступов", "и мест хранения", "ЛР-НСК"])
y = draw_wrap(
    "Карта проекта: сайт, админка, GitHub, VPS и домен. В документе нет паролей, токенов, SSH-ключей и 2FA-кодов.",
    LEFT,
    y,
    USABLE * 0.70,
    "Sans",
    10.2,
    15.4,
    TEXT,
) - 22
y = soft_note(
    y,
    "Важно",
    "Пароли и одноразовые коды передаются отдельно. После приемки стоит сменить пароли в GitHub и Timeweb, проверить резервную почту и включить 2FA.",
)
y = section("Основные рабочие адреса", y)
y = info_rows(
    y,
    "Сайт и админка",
    [
        ("Сайт", "https://landrover-nsk.ru/", "https://landrover-nsk.ru/"),
        ("Админка", "https://landrover-nsk.ru/admin/", "https://landrover-nsk.ru/admin/"),
        ("Для чего", "Публичный сайт и панель редактирования.", None),
    ],
)
y = section("GitHub", y)
y = info_rows(
    y,
    "Копия сайта и логотипы",
    [
        ("Профиль", "github.com/NataliaZidkova", "https://github.com/NataliaZidkova/"),
        ("Вход", "natashazidkova84@gmail.com", None),
        ("Логотипы", "github.com/NataliaZidkova/.../logos", "https://github.com/NataliaZidkova/lr-nsk-landing/tree/main/logos"),
        ("Для чего", "Копия сайта, исходные файлы и отдельная папка с логотипами.", None),
    ],
)
page_number(1)
c.showPage()

# Page 2
header("ИНФРАСТРУКТУРА И ДОМЕН")
y = title(["Инфраструктура", "где что лежит"])
y = section("VPS: где работает сайт", y)
y = info_rows(
    y,
    "Timeweb Cloud",
    [
        ("Панель", "https://timeweb.cloud/", "https://timeweb.cloud/"),
        ("Почта", "ol.burtuleva@gmail.com", None),
        ("Логин", "yk455059", None),
        ("Для чего", "VPS-сервер. Здесь лежит сайт и отсюда он работает.", None),
    ],
)
y = section("Домен и DNS", y)
y = info_rows(
    y,
    "Timeweb Hosting",
    [
        ("Панель", "https://hosting.timeweb.ru/", "https://hosting.timeweb.ru/"),
        ("Почта", "ol.burtuleva@gmail.com", None),
        ("Для чего", "Домен landrover-nsk.ru и настройки DNS.", None),
    ],
)
y = soft_note(
    y,
    "Карта владения",
    "Сайт работает на VPS в Timeweb Cloud. Домен и DNS находятся в Timeweb Hosting. Копия исходников и логотипы лежат в GitHub-аккаунте NataliaZidkova.",
)
page_number(2)
c.showPage()

# Page 3
header("ЧТО ПЕРЕДАЕТСЯ ОТДЕЛЬНО")
y = title(["Что передать", "отдельным каналом"])
y = draw_wrap(
    "Чек-лист для финальной передачи. Секретные значения сюда не добавляем.",
    LEFT,
    y,
    USABLE * 0.70,
    "Sans",
    10.2,
    15.4,
    TEXT,
) - 24
y = section("Секретные доступы", y)
y = dash_list(
    y,
    [
        "Пароль от GitHub-аккаунта заказчика.",
        "Пароль от Timeweb Cloud.",
        "Пароль от Timeweb Hosting.",
        "2FA-коды и резервные коды, если используются.",
        "SSH-ключи или другие технические ключи, если используются.",
    ],
)
y = section("После передачи", y)
y = dash_list(
    y,
    [
        "Сменить пароли в GitHub и Timeweb после приемки.",
        "Проверить, что DNS в Timeweb Hosting указывает на актуальный VPS.",
        "Проверить, что доступ к GitHub есть у владельца проекта.",
        "Хранить пароли в менеджере паролей, а не в документах и чатах.",
    ],
)
y = soft_note(
    y,
    "Финальная пометка",
    "Этот PDF можно отправлять заказчику как карту проекта. Пароли, токены и ключи передаются отдельно и не добавляются в документ.",
)
feedback_block(235)
page_number(3)

c.save()

print(out)
