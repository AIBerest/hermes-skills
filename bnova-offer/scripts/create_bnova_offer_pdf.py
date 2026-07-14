#!/usr/bin/env python3
import argparse
import os
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent

parser = argparse.ArgumentParser(description='Create a B NOVA Studio branded example PDF.')
parser.add_argument(
    '--output',
    default='output/pdf/akt-peredachi-dostupov-lr-nsk.pdf',
    help='Output PDF path.',
)
args = parser.parse_args()

font_dir = os.environ.get(
    'BNOVA_FONT_DIR',
    '/Users/aiassist/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/libreoffice-headless/libreoffice/LibreOfficeDev.app/Contents/Resources/fonts/truetype',
)
fonts={'Sans':f'{font_dir}/DejaVuSans.ttf','SansBold':f'{font_dir}/DejaVuSans-Bold.ttf','Mono':f'{font_dir}/DejaVuSansMono.ttf'}
for n,p in fonts.items():
    if n not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont(n,p))
out=Path(args.output).expanduser().resolve()
out.parent.mkdir(parents=True, exist_ok=True)
logo=SKILL_DIR / 'assets' / 'bnova-header-logo.png'
W,H=A4; left=37; right=W-37; usable=right-left
BLUE=colors.HexColor('#0037FF'); TEXT=colors.HexColor('#111318'); MUTED=colors.HexColor('#7D8490')
c=canvas.Canvas(str(out), pagesize=A4); c.setTitle('Передача доступов и мест хранения - ЛР-НСК'); c.setAuthor('B NOVA Studio')
def spaced(text,x,y,size=6,tracking=3,color=MUTED,align='left'):
    font='Mono'; total=sum(stringWidth(ch,font,size) for ch in text)+tracking*max(0,len(text)-1)
    if align=='right': x-=total
    c.saveState()
    tx=c.beginText(x,y); tx.setFont(font,size); tx.setFillColor(color); tx.setCharSpace(tracking); tx.textLine(text); c.drawText(tx)
    c.restoreState()
def header(label):
    c.drawImage(ImageReader(str(logo)), left, H-64, width=135, height=24, mask='auto')
    spaced(label,right,H-52,5.5,2.6,MUTED,'right')
    spaced('ДЛЯ ЛР-НСК · НОВОСИБИРСК',right,H-64,5.5,2.6,MUTED,'right')
def footer(page):
    spaced('B NOVA STUDIO · РАБОЧИЙ ДОКУМЕНТ · БЕЗ ПАРОЛЕЙ',left,34,5.4,2.2,MUTED)
    c.setFont('Mono',6); c.setFillColor(MUTED); c.drawRightString(right,34,f'{page:02d}')
def wrap_text(text,font,size,maxw):
    words=text.split(' '); lines=[]; cur=''
    for w in words:
        test=w if not cur else cur+' '+w
        if stringWidth(test,font,size)<=maxw: cur=test
        else:
            if cur: lines.append(cur); cur=w
            else:
                part=''
                for ch in w:
                    if stringWidth(part+ch,font,size)<=maxw: part+=ch
                    else: lines.append(part); part=ch
                cur=part
    if cur: lines.append(cur)
    return lines
def draw_wrap(text,x,y,w,font='Sans',size=9.2,leading=14,color=TEXT):
    c.setFont(font,size); c.setFillColor(color)
    for line in wrap_text(text,font,size,w):
        c.drawString(x,y,line); y-=leading
    return y
def title(lines):
    y=H-108
    for i,line in enumerate(lines):
        c.setFillColor(TEXT); c.setFont('SansBold' if i==len(lines)-1 else 'Sans',25)
        c.drawString(left,y,line); y-=34
    return y-14
def sect(t,y): spaced(t.upper(),left,y,6,2.8,BLUE); return y-18
def note_box(y,heading,text):
    h=78; c.setStrokeColor(BLUE); c.setLineWidth(1); c.rect(left,y-h,usable,h,stroke=1,fill=0)
    spaced(heading.upper(),left+15,y-23,6,2.8,BLUE)
    draw_wrap(text,left+15,y-43,usable-30,'Sans',8.2,12.5,MUTED)
    return y-h-24
def calc_box_h(items,note):
    h=35
    for _,disp,_ in items:
        lines=max(1,len(wrap_text(disp,'Sans',9.2,usable-156)))
        h += max(34, 16 + lines*13)
    if note: h+=30
    return h
def box(y,title,items,note=None):
    h=calc_box_h(items,note)
    c.setStrokeColor(BLUE); c.setLineWidth(.9); c.rect(left,y-h,usable,h,stroke=1,fill=0)
    spaced(title.upper(),left+15,y-20,5.9,2.8,BLUE)
    cy=y-48
    for label,disp,url in items:
        c.setFillColor(MUTED); c.setFont('Mono',6.1); c.drawString(left+15,cy,label.upper())
        start_y=cy+1
        after=draw_wrap(disp,left+130,cy+1,usable-150,'Sans',9.2,13,BLUE if url else TEXT)
        if url: c.linkURL(url,(left+130,after+1,right-15,start_y+11),relative=0)
        cy=min(cy-34, after-16)
    if note: draw_wrap(note,left+15,y-h+21,usable-30,'Sans',8.0,12,MUTED)
    return y-h-20
def bullets(y,items):
    for item in items:
        c.setFillColor(BLUE); c.circle(left+3,y+3,1.7,fill=1,stroke=0)
        y2=draw_wrap(item,left+16,y,usable-16,'Sans',9.2,14,TEXT); y=y2-8
    return y
def contact_block(y):
    h=94
    c.setStrokeColor(BLUE); c.setLineWidth(1); c.rect(left,y-h,usable,h,stroke=1,fill=0)
    spaced('КОНТАКТЫ B NOVA STUDIO',left+15,y-20,6,2.8,BLUE)
    rows=[
        ('Телефон', '+7 913 004-61-62 · WhatsApp · Telegram', 'tel:+79130046162'),
        ('Telegram', '@E_Berest', 'https://t.me/E_Berest'),
        ('Почта', 'berestenkoea@gmail.com', 'mailto:berestenkoea@gmail.com'),
        ('Сайт', 'bnova.site', 'https://bnova.site/'),
    ]
    cy=y-41
    for label,disp,url in rows:
        c.setFillColor(MUTED); c.setFont('Mono',6.1); c.drawString(left+15,cy,label.upper())
        c.setFillColor(BLUE if url else TEXT); c.setFont('Sans',9.0); c.drawString(left+98,cy-1,disp)
        if url:
            c.linkURL(url,(left+98,cy-3,right-15,cy+10),relative=0)
        cy-=16
    return y-h-18
# Page 1
header('ПЕРЕДАЧА ДОСТУПОВ И МЕСТ ХРАНЕНИЯ')
y=title(['Передача доступов','и мест хранения','ЛР-НСК'])
y=draw_wrap('Рабочий документ для заказчика: где находится сайт, админка, копия исходников, логотипы, VPS и домен. Документ не содержит пароли, токены, SSH-ключи и коды двухфакторной аутентификации.',left,y,usable*.72,'Sans',9.4,15,TEXT)-18
y=note_box(y,'Важно','Все пароли и одноразовые коды передаются отдельно защищенным каналом. После получения доступов рекомендуется сменить пароли, проверить резервную почту и включить 2FA там, где это возможно.')
y=sect('Основные рабочие адреса',y)
y=box(y,'Сайт и админка',[('Сайт','https://landrover-nsk.ru/','https://landrover-nsk.ru/'),('Админка','https://landrover-nsk.ru/admin/','https://landrover-nsk.ru/admin/')],'Назначение: публичный сайт и панель редактирования/администрирования.')
y=sect('GitHub: копия сайта и логотипы',y)
y=box(y,'Аккаунт GitHub заказчика',[('Профиль','github.com/NataliaZidkova','https://github.com/NataliaZidkova/'),('Вход по почте','natashazidkova84@gmail.com',None),('Логотипы','github.com/NataliaZidkova/.../logos','https://github.com/NataliaZidkova/lr-nsk-landing/tree/main/logos')],'Назначение: копия сайта, исходные файлы и отдельная папка с логотипами.')
footer(1); c.showPage()
# Page 2
header('ИНФРАСТРУКТУРА И ДОМЕН')
y=title(['Инфраструктура','где что лежит'])
y=sect('VPS: где работает сайт',y)
y=box(y,'Timeweb Cloud',[('Панель','https://timeweb.cloud/','https://timeweb.cloud/'),('Почта','ol.burtuleva@gmail.com',None),('Логин аккаунта','yk455059',None),('Назначение','VPS-сервер: здесь лежит сайт и отсюда он работает',None)],'Не хранить пароли в этом документе. Доступы передаются отдельно.')
y=sect('Домен и DNS',y)
y=box(y,'Timeweb Hosting',[('Панель','https://hosting.timeweb.ru/','https://hosting.timeweb.ru/'),('Почта','ol.burtuleva@gmail.com',None),('Назначение','Домен landrover-nsk.ru и настройки DNS',None)],'Изменение DNS влияет на доступность сайта и почты.')
y=sect('Краткая карта владения',y)
y=draw_wrap('Сайт работает на VPS в Timeweb Cloud. Домен и DNS находятся в панели Timeweb Hosting. Копия исходников и логотипы лежат в GitHub-аккаунте заказчика NataliaZidkova.',left,y,usable,'Sans',9.2,14,TEXT)
footer(2); c.showPage()
# Page 3
header('ЧТО ПЕРЕДАЕТСЯ ОТДЕЛЬНО')
y=title(['Что передать','отдельным каналом'])
y=draw_wrap('Этот лист нужен как чек-лист передачи. Он намеренно не содержит секретные значения.',left,y,usable*.72,'Sans',9.4,15,TEXT)-18
y=sect('Секретные доступы',y)
y=bullets(y,['Пароль от GitHub-аккаунта заказчика','Пароль от Timeweb Cloud','Пароль от Timeweb Hosting','2FA-коды и резервные коды, если используются','SSH-ключи или другие технические ключи, если используются'])
y-=4; y=sect('Рекомендации после передачи',y)
y=bullets(y,['Сменить пароли в GitHub и Timeweb после приемки.','Проверить, что в Timeweb Hosting DNS указывает на актуальный VPS.','Проверить, что доступ к GitHub есть у владельца проекта.','Хранить пароли в менеджере паролей, а не в документах и чатах.'])
y-=8; y=note_box(y,'Финальная пометка','Документ можно передавать заказчику как карту доступов. Для безопасности пароли, токены и ключи должны идти отдельным защищенным каналом и не добавляться в этот PDF.')
y=contact_block(y)
footer(3); c.save(); print(out)
