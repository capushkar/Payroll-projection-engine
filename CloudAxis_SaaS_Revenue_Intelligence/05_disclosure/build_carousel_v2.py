"""
CloudAxis LinkedIn Carousel v2 — Light/professional theme
6 slides, 800×800 each
"""
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white, black

W = H = 800

# ── Light palette ─────────────────────────────────────────────────────────
BG      = HexColor('#FFFFFF')
BG2     = HexColor('#F8FAFC')
BG3     = HexColor('#F1F5F9')
BG4     = HexColor('#E2E8F0')
BLUE    = HexColor('#2563EB')
BLUE_LT = HexColor('#3B82F6')
BLUE_BG = HexColor('#EFF6FF')
GREEN   = HexColor('#059669')
GREEN_BG= HexColor('#ECFDF5')
AMBER   = HexColor('#D97706')
AMBER_BG= HexColor('#FFFBEB')
RED     = HexColor('#DC2626')
RED_BG  = HexColor('#FEF2F2')
NAVY    = HexColor('#0F172A')
TEXT    = HexColor('#1E293B')
TEXT2   = HexColor('#475569')
TEXT3   = HexColor('#94A3B8')
RULE    = HexColor('#E2E8F0')
DARK_BG = HexColor('#0F172A')

def slide_bg(c, color=BG):
    c.setFillColor(color)
    c.rect(0, 0, W, H, fill=1, stroke=0)

def top_bar(c, color=BLUE, h=5):
    c.setFillColor(color)
    c.rect(0, H-h, W, h, fill=1, stroke=0)

def left_bar(c, y1, y2, color=BLUE, w=4):
    c.setFillColor(color)
    c.rect(0, y1, w, y2-y1, fill=1, stroke=0)

def hrule(c, x1, y, x2, color=RULE, t=0.8):
    c.setStrokeColor(color)
    c.setLineWidth(t)
    c.line(x1, y, x2, y)

def card(c, x, y, w, h, fill=BG2, radius=6, stroke_color=None, stroke_w=0.8):
    c.setFillColor(fill)
    if stroke_color:
        c.setStrokeColor(stroke_color)
        c.setLineWidth(stroke_w)
        c.roundRect(x, y, w, h, radius, fill=1, stroke=1)
    else:
        c.roundRect(x, y, w, h, radius, fill=1, stroke=0)

def eyebrow(c, text, y, color=BLUE, size=9):
    c.setFillColor(color)
    c.setFont('Helvetica-Bold', size)
    c.drawString(44, y, text.upper())

def label_tag(c, text, x, y, bg=BLUE_BG, fg=BLUE, size=8.5):
    w = c.stringWidth(text, 'Helvetica-Bold', size) + 16
    card(c, x, y-2, w, 17, bg, 3)
    c.setFillColor(fg)
    c.setFont('Helvetica-Bold', size)
    c.drawString(x+8, y+2, text)
    return w + 6

def slide_num(c, n, total=6):
    c.setFillColor(TEXT3)
    c.setFont('Helvetica', 8)
    c.drawRightString(W-28, 16, f'{n} / {total}')

def footer(c, text='CLOUDAXIS · REVENUE INTELLIGENCE'):
    c.setFillColor(TEXT3)
    c.setFont('Helvetica', 8)
    c.drawString(44, 16, text)

# ══════════════════════════════════════════════════════════════════════════
out = '/home/claude/linkedin_carousel_v2.pdf'
c = canvas.Canvas(out, pagesize=(W, H))

# ══════════════════════════════════════════════════════════════════════════
# SLIDE 1 — HOOK (dark hero, then light for rest)
# ══════════════════════════════════════════════════════════════════════════
slide_bg(c, DARK_BG)
top_bar(c, BLUE, 5)
left_bar(c, 80, H-60, BLUE, 4)

eyebrow(c, 'ASC 606 · SaaS Revenue Recognition · AI in Finance', H-36,
        HexColor('#60A5FA'), 9)

# Main lines
c.setFillColor(white)
c.setFont('Helvetica-Bold', 62)
c.drawString(44, H-138, 'BUILT IN DAYS.')

c.setFillColor(BLUE_LT)
c.setFont('Helvetica-Bold', 62)
c.drawString(44, H-210, 'WHAT TAKES')
c.drawString(44, H-278, 'MONTHS.')

hrule(c, 44, H-308, 340, HexColor('#1E3A5F'), 1)

c.setFillColor(HexColor('#CBD5E1'))
c.setFont('Helvetica', 15)
c.drawString(44, H-338, 'The tools made that possible.')
c.setFillColor(white)
c.setFont('Helvetica-Bold', 15)
c.drawString(44, H-362, "But they couldn't tell me if the output")
c.drawString(44, H-384, 'was right.')

# Stats row
stats = [('61', 'Contracts'), ('948', 'Monthly rows'), ('12', 'Checks pass'), ('8', 'Output types')]
sx = 44
for val, lbl in stats:
    card(c, sx, 68, 158, 58, HexColor('#1E293B'), 6)
    c.setFillColor(BLUE_LT)
    c.setFont('Helvetica-Bold', 24)
    c.drawString(sx+12, 106, val)
    c.setFillColor(HexColor('#64748B'))
    c.setFont('Helvetica', 9)
    c.drawString(sx+12, 89, lbl)
    sx += 168

footer(c)
slide_num(c, 1)
c.showPage()

# ══════════════════════════════════════════════════════════════════════════
# SLIDE 2 — WHAT WAS BUILT (light)
# ══════════════════════════════════════════════════════════════════════════
slide_bg(c)
top_bar(c, BLUE, 5)

eyebrow(c, 'The Scope', H-36)

c.setFillColor(NAVY)
c.setFont('Helvetica-Bold', 32)
c.drawString(44, H-94, 'What was built')

c.setFillColor(TEXT2)
c.setFont('Helvetica', 12)
c.drawString(44, H-118, 'One accounting professional. AI as execution tool. Complete output across 6 areas.')

hrule(c, 44, H-136, W-44, RULE)

# 6 output cards — 2 cols × 3 rows, no background bleed elements
outputs = [
    ('Recognition Engine',   '8-step loop · 12 validation checks', BLUE,  BLUE_BG),
    ('SaaS Metrics Suite',   'MRR · NRR/GRR · LTV:CAC · Cohort',  GREEN, GREEN_BG),
    ('Excel Model',          '9 tabs · charts · colour-coded',      BLUE,  BLUE_BG),
    ('Interactive Dashboard','5 pages · all data embedded',         GREEN, GREEN_BG),
    ('ASC 606 Disclosures',  '8-page 10-K footnote · 6 notes',     BLUE,  BLUE_BG),
    ('Validation Log',       '4 real bugs found · diagnosed · fixed',AMBER,AMBER_BG),
]
cw, ch = 350, 95
xs = [44, 412]
oy = H - 162

for i, (title, sub, accent, bg) in enumerate(outputs):
    col = i % 2; row = i // 2
    cx = xs[col]; cy = oy - row * (ch + 10)
    card(c, cx, cy, cw, ch, bg, 6, RULE, 0.7)
    # Left accent
    c.setFillColor(accent)
    c.rect(cx, cy, 3, ch, fill=1, stroke=0)
    # Check badge
    card(c, cx+cw-34, cy+ch-28, 26, 20, accent, 4)
    c.setFillColor(white)
    c.setFont('Helvetica-Bold', 11)
    c.drawCentredString(cx+cw-21, cy+ch-22, '✓')
    # Text
    c.setFillColor(TEXT)
    c.setFont('Helvetica-Bold', 13)
    c.drawString(cx+14, cy+ch-26, title)
    c.setFillColor(TEXT2)
    c.setFont('Helvetica', 11)
    c.drawString(cx+14, cy+ch-44, sub)

footer(c)
slide_num(c, 2)
c.showPage()

# ══════════════════════════════════════════════════════════════════════════
# SLIDE 3 — THE NUMBERS (light)
# ══════════════════════════════════════════════════════════════════════════
slide_bg(c)
top_bar(c, GREEN, 5)

eyebrow(c, 'CloudAxis · Key Metrics · December 2024', H-36, GREEN)

c.setFillColor(NAVY)
c.setFont('Helvetica-Bold', 32)
c.drawString(44, H-94, 'The output — real numbers')

hrule(c, 44, H-112, W-44, RULE)

# KPI cards
kpis = [('$2.37M', 'ARR', GREEN, GREEN_BG),
        ('$197K',  'Monthly MRR', BLUE, BLUE_BG),
        ('41',     'Active Customers', AMBER, AMBER_BG),
        ('83.6%',  'NRR (Dec 2024)', GREEN, GREEN_BG)]
kw = 170; kx = 44
for val, lbl, col, bg in kpis:
    card(c, kx, H-240, kw, 100, bg, 6, RULE, 0.7)
    c.setFillColor(col)
    c.setFont('Helvetica-Bold', 26)
    c.drawCentredString(kx+kw/2, H-186, val)
    c.setFillColor(TEXT2)
    c.setFont('Helvetica', 10)
    c.drawCentredString(kx+kw/2, H-208, lbl)
    kx += kw + 10

# Revenue comparison
card(c, 44, H-370, W-88, 100, BG2, 6, RULE, 0.7)
# FY24
c.setFillColor(TEXT3)
c.setFont('Helvetica', 9)
c.drawString(64, H-300, 'FY 2024')
c.setFillColor(GREEN)
c.setFont('Helvetica-Bold', 22)
c.drawString(64, H-328, '$2,328,108')
# FY23
c.setFillColor(TEXT3)
c.setFont('Helvetica', 9)
c.drawString(310, H-300, 'FY 2023')
c.setFillColor(TEXT2)
c.setFont('Helvetica-Bold', 22)
c.drawString(310, H-328, '$1,225,893')
# YoY
card(c, 540, H-364, 170, 88, GREEN_BG, 5, RULE, 0.7)
c.setFillColor(GREEN)
c.setFont('Helvetica-Bold', 32)
c.drawCentredString(625, H-318, '+89.9%')
c.setFillColor(TEXT2)
c.setFont('Helvetica', 9)
c.drawCentredString(625, H-340, 'Year-over-year')

# Product bar — fixed with outside labels for narrow segments
c.setFillColor(TEXT3)
c.setFont('Helvetica-Bold', 9)
c.drawString(44, H-400, 'FY 2024 REVENUE BY PRODUCT')

products = [
    ('Core',         1860749, 0.80, BLUE,  BLUE_BG),
    ('Analytics',    277346,  0.12, GREEN, GREEN_BG),
    ('DataPipeline', 190013,  0.08, AMBER, AMBER_BG),
]
bar_y  = H - 480
bar_h  = 46
bar_tw = W - 88   # 712px total
MIN_W  = 56        # minimum to show text inside

cx = 44
for name, val, pct, col, bg in products:
    bw = int(bar_tw * pct)
    card(c, cx, bar_y, bw - 2, bar_h, col, 0)
    
    if bw >= MIN_W:
        # Label inside bar
        c.setFillColor(white)
        c.setFont('Helvetica-Bold', 11)
        c.drawCentredString(cx + bw/2, bar_y + bar_h - 16, f'{int(round(pct*100))}%')
        if bw > 90:
            c.setFont('Helvetica', 9)
            c.drawCentredString(cx + bw/2, bar_y + bar_h - 30, name)
    else:
        # Label outside bar (above) for narrow segments
        c.setFillColor(col)
        c.setFont('Helvetica-Bold', 10)
        c.drawCentredString(cx + bw/2, bar_y + bar_h + 8, f'{int(round(pct*100))}%')
    cx += bw

# Legend row
cx = 44
for name, val, pct, col, bg in products:
    bw = int(bar_tw * pct)
    c.setFillColor(col)
    c.rect(cx, bar_y - 26, 10, 10, fill=1, stroke=0)
    c.setFillColor(TEXT2)
    c.setFont('Helvetica', 9)
    c.drawString(cx+14, bar_y - 25, f'{name}  ${val/1e6:.2f}M  ({int(round(pct*100))}%)')
    cx += bw

# Bottom line — 3 balance sheet items
bdata = [('$447,719', 'Remaining Perf. Obligations', BLUE),
         ('$207,428', 'Commission Asset (ASC 340-40)', GREEN),
         ('$30,650',  'Deferred Revenue (closing)', AMBER)]
bx = 44; bw3 = 232
for bval, blbl, col in bdata:
    card(c, bx, 44, bw3, 56, BG2, 5, RULE, 0.7)
    c.setFillColor(col)
    c.setFont('Helvetica-Bold', 15)
    c.drawString(bx+10, 82, bval)
    c.setFillColor(TEXT3)
    c.setFont('Helvetica', 9)
    c.drawString(bx+10, 64, blbl)
    bx += bw3 + 10

footer(c)
slide_num(c, 3)
c.showPage()

# ══════════════════════════════════════════════════════════════════════════
# SLIDE 4 — DISCLOSURE (light)
# ══════════════════════════════════════════════════════════════════════════
slide_bg(c)
top_bar(c, BLUE, 5)

eyebrow(c, '10-K formatted financial statement footnote', H-36)

c.setFillColor(NAVY)
c.setFont('Helvetica-Bold', 32)
c.drawString(44, H-94, 'ASC 606 Disclosure Package')

c.setFillColor(TEXT2)
c.setFont('Helvetica', 12)
c.drawString(44, H-116, '8 pages · 6 notes · every number cross-checked against source data')

hrule(c, 44, H-134, W-44, RULE)

# Left: document mock
card(c, 44, 44, 330, H-200, BG2, 6, RULE, 0.8)

# Doc header
c.setFillColor(NAVY)
c.rect(44, H-200, 330, 56, fill=1, stroke=0)
c.setFillColor(white)
c.setFont('Helvetica-Bold', 12)
c.drawCentredString(209, H-162, 'CloudAxis Inc.')
c.setFillColor(HexColor('#93C5FD'))
c.setFont('Helvetica', 9)
c.drawCentredString(209, H-178, 'Notes to Financial Statements')
c.setFillColor(HexColor('#64748B'))
c.setFont('Helvetica', 8)
c.drawCentredString(209, H-193, 'Years Ended Dec 31, 2024 and 2023')

notes = [
    ('Note 1', 'Revenue Recognition Policy'),
    ('Note 2', 'Revenue Disaggregation — 4 ways'),
    ('Note 3', 'Deferred Revenue Roll-Forward'),
    ('Note 4', 'Remaining Performance Obligations'),
    ('Note 5', 'Commission Asset (ASC 340-40)'),
    ('Note 6', 'Assumptions & ASC References'),
]
ny = H - 226
for num, title in notes:
    c.setFillColor(BLUE)
    c.setFont('Helvetica-Bold', 9)
    c.drawString(60, ny, num)
    c.setFillColor(TEXT)
    c.setFont('Helvetica', 10)
    c.drawString(108, ny, title)
    hrule(c, 60, ny - 10, 358, RULE, 0.4)
    ny -= 32

# Right: highlight cards
cx2 = 394
items = [
    (BLUE,  BLUE_BG,  '$2.33M',   'Revenue disaggregated',  'Product · segment · billing type · geography'),
    (GREEN, GREEN_BG, 'All tie',   'Roll-forwards correct',  'Additions vs releases · write-offs disclosed'),
    (AMBER, AMBER_BG, '606-10-50','Practical expedients',   'Month-to-month & variable consideration excluded'),
    (BLUE,  BLUE_BG,  '6 cited',   'ASC paragraphs',         'Every judgement referenced to the standard'),
]
dy = H - 162
for col, bg, val, head, sub in items:
    card(c, cx2, dy-80, 362, 90, bg, 6, RULE, 0.7)
    c.setFillColor(col)
    c.rect(cx2, dy-80, 3, 90, fill=1, stroke=0)
    c.setFont('Helvetica-Bold', 20)
    c.drawString(cx2+16, dy-32, val)
    c.setFillColor(TEXT)
    c.setFont('Helvetica-Bold', 11)
    c.drawString(cx2+16, dy-52, head)
    c.setFillColor(TEXT2)
    c.setFont('Helvetica', 10)
    c.drawString(cx2+16, dy-68, sub)
    dy -= 104

footer(c)
slide_num(c, 4)
c.showPage()

# ══════════════════════════════════════════════════════════════════════════
# SLIDE 5 — VALIDATION (light with amber accent)
# ══════════════════════════════════════════════════════════════════════════
slide_bg(c)
top_bar(c, AMBER, 5)

eyebrow(c, 'The part nobody shows you', H-36, AMBER)

c.setFillColor(NAVY)
c.setFont('Helvetica-Bold', 32)
c.drawString(44, H-94, 'What the AI got wrong')

c.setFillColor(TEXT2)
c.setFont('Helvetica', 12)
c.drawString(44, H-116, 'Mathematically correct. Wrong for this context. Found through manual review.')

hrule(c, 44, H-134, W-44, RULE)

bugs = [
    (RED,     BLUE_LT, '01', 'LTV:CAC showed 255×',
     'Spot monthly churn on lumpy data = near zero most months.',
     'Fix: trailing 12-month avg + 6% floor + 5-year cap → 12×'),

    (AMBER,   AMBER,   '02', "Deferred roll-forward didn't tie",
     'Wrong columns: total billings ≠ additions to deferred.',
     'Fix: balance-movement approach. All 8 quarters now tie.'),

    (BLUE,    BLUE_LT, '03', 'Commission table missing write-offs',
     'Early terminations write off commission asset (ASC 340-40-35-1).',
     'Fix: Added write-off column. FY24 write-offs: $50,939.'),

    (GREEN,   GREEN,   '04', 'Billing guard on wrong product',
     'Annual upfront guard zeroed DataPipeline monthly usage billing.',
     'Fix: Guard now excludes DataPipeline. Contract asset reduced $44K.'),
]

by = H - 160
for col, badge_col, num, title, why, fix in bugs:
    card(c, 44, by - 95, W-88, 102, BG2, 5, RULE, 0.7)
    c.setFillColor(col)
    c.rect(44, by-95, 3, 102, fill=1, stroke=0)

    # Number badge
    card(c, 58, by-68, 32, 28, col, 4)
    c.setFillColor(white)
    c.setFont('Helvetica-Bold', 13)
    c.drawCentredString(74, by-49, num)

    # Text
    c.setFillColor(NAVY)
    c.setFont('Helvetica-Bold', 12)
    c.drawString(102, by-38, title)
    c.setFillColor(TEXT2)
    c.setFont('Helvetica', 10)
    c.drawString(102, by-56, why)

    # Fix line
    c.setFillColor(col)
    c.setFont('Helvetica-Bold', 10)
    c.drawString(102, by-74, fix)

    by -= 120

footer(c)
slide_num(c, 5)
c.showPage()

# ══════════════════════════════════════════════════════════════════════════
# SLIDE 6 — CLOSING (dark, personal)
# ══════════════════════════════════════════════════════════════════════════
slide_bg(c, DARK_BG)
top_bar(c, BLUE, 5)
left_bar(c, 80, H-60, BLUE, 4)

eyebrow(c, 'Closing thought', H-36, HexColor('#60A5FA'))

# Quote
c.setFillColor(HexColor('#94A3B8'))
c.setFont('Helvetica', 16)
c.drawString(44, H-118, 'The skill that matters now')

c.setFillColor(white)
c.setFont('Helvetica-Bold', 42)
c.drawString(44, H-176, "isn't building")
c.drawString(44, H-228, 'the model.')

hrule(c, 44, H-256, 340, HexColor('#1E3A5F'), 1)

c.setFillColor(HexColor('#94A3B8'))
c.setFont('Helvetica', 16)
c.drawString(44, H-292, "It's knowing whether")

c.setFillColor(BLUE_LT)
c.setFont('Helvetica-Bold', 34)
c.drawString(44, H-340, 'the output is right')

c.setFillColor(HexColor('#CBD5E1'))
c.setFont('Helvetica', 16)
c.drawString(44, H-378, 'for your organisation, your auditors,')
c.drawString(44, H-402, 'your context.')

hrule(c, 44, H-432, W-44, HexColor('#1E293B'), 1)

# Name block
c.setFillColor(white)
c.setFont('Helvetica-Bold', 16)
c.drawString(44, H-468, 'Pushkar Agrawal, CA')
c.setFillColor(HexColor('#60A5FA'))
c.setFont('Helvetica', 11)
c.drawString(44, H-488, 'Finance Transformation Lead')

# FinanceForge mention
card(c, 44, H-534, 380, 32, HexColor('#1E293B'), 5)
c.setFillColor(HexColor('#64748B'))
c.setFont('Helvetica', 10)
c.drawString(60, H-512, 'Full methodology at')
c.setFillColor(BLUE_LT)
c.setFont('Helvetica-Bold', 10)
c.drawString(178, H-512, 'financeforge.com')

# CTA
card(c, 44, 68, W-88, 58, HexColor('#1E2D40'), 6)
c.setFillColor(BLUE_LT)
c.setFont('Helvetica-Bold', 12)
c.drawString(62, 108, 'Read the full methodology →  link in comments')
c.setFillColor(HexColor('#64748B'))
c.setFont('Helvetica', 10)
c.drawString(62, 88, 'Part 2: deep technical breakdown for finance professionals')

slide_num(c, 6)
c.save()

import os
print(f'✓ Carousel v2 built: {out}')
print(f'  {os.path.getsize(out)//1024} KB  |  6 slides')
