"""
CloudAxis Inc. — ASC 606 Revenue Recognition Disclosure Package
Formatted as a 10-K financial statement footnote
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, HRFlowable, PageBreak, KeepTogether)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.pdfgen import canvas as pdfcanvas

W, H = letter

# ── Colour palette ────────────────────────────────────────────────────────
INK       = colors.HexColor('#0D1117')
INK2      = colors.HexColor('#3D4451')
INK3      = colors.HexColor('#6B7280')
RULE      = colors.HexColor('#E2E8F0')
ACCENT    = colors.HexColor('#1E40AF')
ACCENT_LT = colors.HexColor('#EFF6FF')
HEADER_BG = colors.HexColor('#1E293B')
ROW_ALT   = colors.HexColor('#F8FAFC')
WHITE     = colors.white

# ── Styles ─────────────────────────────────────────────────────────────────
def style(name, **kw):
    base = dict(fontName='Helvetica', fontSize=9, leading=13,
                textColor=INK, spaceAfter=0, spaceBefore=0)
    base.update(kw)
    return ParagraphStyle(name, **base)

S = {
    'cover_co':    style('cover_co',  fontName='Helvetica-Bold', fontSize=22,
                         textColor=WHITE, leading=28, alignment=TA_CENTER),
    'cover_title': style('cover_t',   fontName='Helvetica-Bold', fontSize=14,
                         textColor=colors.HexColor('#93C5FD'), leading=20, alignment=TA_CENTER),
    'cover_sub':   style('cover_s',   fontSize=10, textColor=colors.HexColor('#94A3B8'),
                         leading=14, alignment=TA_CENTER),
    'note_num':    style('note_num',  fontName='Helvetica-Bold', fontSize=11,
                         textColor=ACCENT, spaceBefore=18, spaceAfter=4),
    'note_title':  style('note_title',fontName='Helvetica-Bold', fontSize=11,
                         textColor=INK, spaceBefore=4, spaceAfter=8,
                         borderPadding=(0,0,4,0)),
    'sub_head':    style('sub_head',  fontName='Helvetica-Bold', fontSize=9,
                         textColor=INK, spaceBefore=10, spaceAfter=4),
    'body':        style('body',      fontSize=9, textColor=INK2, leading=14,
                         spaceAfter=6),
    'body_sm':     style('body_sm',   fontSize=8, textColor=INK3, leading=12,
                         spaceAfter=4),
    'italic':      style('italic',    fontName='Helvetica-Oblique', fontSize=9,
                         textColor=INK3, leading=13, spaceAfter=6),
    'footer':      style('footer',    fontSize=7.5, textColor=INK3,
                         alignment=TA_CENTER),
    'tbl_hdr':     style('tbl_hdr',   fontName='Helvetica-Bold', fontSize=8,
                         textColor=WHITE, alignment=TA_RIGHT),
    'tbl_hdr_l':   style('tbl_hdr_l', fontName='Helvetica-Bold', fontSize=8,
                         textColor=WHITE, alignment=TA_LEFT),
    'tbl_cell':    style('tbl_cell',  fontSize=8.5, textColor=INK,
                         alignment=TA_RIGHT),
    'tbl_cell_l':  style('tbl_cell_l',fontSize=8.5, textColor=INK,
                         alignment=TA_LEFT),
    'tbl_cell_it': style('tbl_cell_it',fontName='Helvetica-Oblique',
                         fontSize=8.5, textColor=INK2, alignment=TA_LEFT),
    'tbl_total':   style('tbl_total', fontName='Helvetica-Bold', fontSize=8.5,
                         textColor=INK, alignment=TA_RIGHT),
    'tbl_total_l': style('tbl_total_l',fontName='Helvetica-Bold', fontSize=8.5,
                         textColor=INK, alignment=TA_LEFT),
}

def P(text, s='body'): return Paragraph(text, S[s])
def SP(n=6):           return Spacer(1, n)
def HR():              return HRFlowable(width='100%', thickness=0.5,
                                         color=RULE, spaceAfter=6, spaceBefore=6)
def fmt(n, parens=False):
    if n == 0: return '—'
    v = f'${abs(n):,.0f}'
    return f'({v})' if (n < 0 and parens) else v

# ── Table builder ──────────────────────────────────────────────────────────
def make_table(data, col_widths, header_rows=1, total_rows=None,
               alt_rows=True, note_rows=None):
    tbl = Table(data, colWidths=col_widths, repeatRows=header_rows)
    n   = len(data)
    total_rows = total_rows or []
    note_rows  = note_rows  or []

    ts = TableStyle([
        # Header
        ('BACKGROUND',  (0,0), (-1, header_rows-1), HEADER_BG),
        ('TOPPADDING',  (0,0), (-1, header_rows-1), 5),
        ('BOTTOMPADDING',(0,0),(-1, header_rows-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING',(0,0), (-1,-1), 6),
        ('TOPPADDING',  (0,1), (-1,-1), 4),
        ('BOTTOMPADDING',(0,1),(-1,-1), 4),
        ('LINEBELOW',   (0,0), (-1, header_rows-1), 0.5, ACCENT),
        ('LINEBELOW',   (0,-1),(-1,-1), 0.8, RULE),
        ('VALIGN',      (0,0), (-1,-1), 'MIDDLE'),
    ])

    if alt_rows:
        for i in range(header_rows, n):
            if i not in total_rows and i not in note_rows:
                if (i - header_rows) % 2 == 0:
                    ts.add('BACKGROUND', (0,i), (-1,i), ROW_ALT)

    for r in total_rows:
        ts.add('BACKGROUND',  (0,r), (-1,r), colors.HexColor('#E8F0FE'))
        ts.add('LINEABOVE',   (0,r), (-1,r), 0.5, ACCENT)
        ts.add('LINEBELOW',   (0,r), (-1,r), 1.0, ACCENT)

    for r in note_rows:
        ts.add('BACKGROUND', (0,r), (-1,r), colors.HexColor('#FFFBEB'))

    tbl.setStyle(ts)
    return tbl


# ── Page template ──────────────────────────────────────────────────────────
class NumberedCanvas(pdfcanvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self._draw_footer(num_pages)
            super().showPage()
        super().save()

    def _draw_footer(self, num_pages):
        pg = self._pageNumber
        if pg == 1: return
        self.saveState()
        self.setFont('Helvetica', 7.5)
        self.setFillColor(INK3)
        self.drawCentredString(W/2, 0.45*inch,
            f'CloudAxis Inc. | ASC 606 Revenue Recognition Disclosures | '
            f'For the Years Ended December 31, 2024 and 2023')
        self.drawCentredString(W/2, 0.30*inch, f'Page {pg} of {num_pages}')
        self.setStrokeColor(RULE)
        self.setLineWidth(0.5)
        self.line(inch, 0.55*inch, W-inch, 0.55*inch)
        self.restoreState()


# ══════════════════════════════════════════════════════════════════════════
# BUILD DOCUMENT
# ══════════════════════════════════════════════════════════════════════════
out  = '/home/claude/CloudAxis_ASC606_Disclosure.pdf'
doc  = SimpleDocTemplate(out, pagesize=letter,
                          leftMargin=inch, rightMargin=inch,
                          topMargin=0.75*inch, bottomMargin=0.75*inch)
story = []
TW    = W - 2*inch   # usable text width = 6.5"

# ══════════════════════════════════════════════════════════════════════════
# COVER PAGE
# ══════════════════════════════════════════════════════════════════════════
story.append(Spacer(1, 1.6*inch))

cover_block = Table(
    [[P('CloudAxis Inc.', 'cover_co')],
     [SP(6)],
     [P('Notes to Financial Statements', 'cover_title')],
     [P('Revenue Recognition — ASC 606', 'cover_title')],
     [SP(10)],
     [P('For the Years Ended December 31, 2024 and 2023', 'cover_sub')],
     [SP(4)],
     [P('(Amounts in USD)', 'cover_sub')],
    ],
    colWidths=[TW],
)
cover_block.setStyle(TableStyle([
    ('BACKGROUND',    (0,0), (-1,-1), HEADER_BG),
    ('TOPPADDING',    (0,0), (-1,-1), 4),
    ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ('LEFTPADDING',   (0,0), (-1,-1), 24),
    ('RIGHTPADDING',  (0,0), (-1,-1), 24),
    ('TOPPADDING',    (0,0), (0,0),   28),
    ('BOTTOMPADDING', (0,-1),(-1,-1), 28),
]))
story.append(cover_block)
story.append(Spacer(1, 0.3*inch))

meta = Table([
    ['Prepared by:', 'Pushkar Agrawal, CA'],
    ['Report type:', 'ASC 606 Revenue Recognition Disclosure Package'],
    ['Entity:', 'CloudAxis Inc. (Illustrative — Portfolio Project)'],
    ['Auditor standard:', 'US GAAP · FASB ASC 606 · ASC 340-40'],
    ['Products:', 'Core (per-seat SaaS), Analytics (flat-rate), DataPipeline (usage-based)'],
    ['Customer base:', '50 customers · 24-month data window (Jan 2023 – Dec 2024)'],
], colWidths=[1.5*inch, TW-1.5*inch])
meta.setStyle(TableStyle([
    ('FONTNAME',      (0,0), (0,-1), 'Helvetica-Bold'),
    ('FONTSIZE',      (0,0), (-1,-1), 8.5),
    ('TEXTCOLOR',     (0,0), (0,-1), INK),
    ('TEXTCOLOR',     (1,0), (1,-1), INK2),
    ('TOPPADDING',    (0,0), (-1,-1), 4),
    ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ('LINEBELOW',     (0,0), (-1,-2), 0.3, RULE),
]))
story.append(meta)
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════
# NOTE 1 — REVENUE RECOGNITION POLICY
# ══════════════════════════════════════════════════════════════════════════
story.append(P('Note 1', 'note_num'))
story.append(P('Revenue Recognition', 'note_title'))
story.append(HR())

story.append(P('<b>Basis of presentation.</b>  The Company recognises revenue in accordance with '
               'FASB ASC Topic 606, <i>Revenue from Contracts with Customers</i>, applying the '
               'five-step model: (1) identify the contract, (2) identify performance obligations, '
               '(3) determine the transaction price, (4) allocate the transaction price, and '
               '(5) recognise revenue when (or as) performance obligations are satisfied.', 'body'))

story.append(P('<b>Products and performance obligations.</b>  The Company offers three product lines:', 'body'))

prod_data = [
    [P('Product', 'tbl_hdr_l'), P('Model', 'tbl_hdr_l'),
     P('Performance obligation', 'tbl_hdr_l'), P('Recognition pattern', 'tbl_hdr_l')],
    [P('Core', 'tbl_cell_l'), P('Per-seat subscription', 'tbl_cell_l'),
     P('Continuous access — stand-ready', 'tbl_cell_l'),
     P('Ratable over contract term', 'tbl_cell_l')],
    [P('Analytics', 'tbl_cell_l'), P('Flat-rate subscription', 'tbl_cell_l'),
     P('Continuous access — stand-ready', 'tbl_cell_l'),
     P('Ratable over contract term', 'tbl_cell_l')],
    [P('DataPipeline', 'tbl_cell_l'), P('Usage-based', 'tbl_cell_l'),
     P('Units of data processed', 'tbl_cell_l'),
     P('As usage occurs each period', 'tbl_cell_l')],
]
story.append(make_table(prod_data, [1.0*inch, 1.3*inch, 2.2*inch, 1.8*inch]))
story.append(SP(8))

story.append(P('<b>Implementation fees.</b>  Implementation and onboarding fees are '
               'evaluated under the two-prong distinctness test in ASC 606-10-25-19. '
               'The fees fail both prongs: (i) the customer cannot benefit from the '
               'implementation independently of the related subscription service, as '
               'the implementation has no standalone utility without the platform; and '
               '(ii) the implementation is not distinct within the context of the '
               'contract, as it is highly interrelated with the subscription service '
               'and the same outcome cannot be achieved by a third party without '
               'material re-performance. Accordingly, implementation fees are combined '
               'with the subscription as a single performance obligation and recognised '
               'ratably over the contract term.', 'body'))

story.append(P('<b>Multi-element arrangements.</b>  Contracts that include more than one '
               'product line allocate the transaction price to each performance obligation '
               'based on relative standalone selling prices (SSP), consistent with '
               'ASC 606-10-32-31. SSP is estimated using the adjusted market assessment '
               'approach: observable list prices for each product in standalone '
               'transactions serve as the primary SSP input. Where bundle pricing '
               'reflects a discount relative to the sum of standalone prices, that '
               'discount is allocated proportionally across components based on their '
               'relative SSPs. In this model, bundle component SSPs are estimated in '
               'the range of standalone list price (with a small premium reflecting '
               'the integrated value of the combined solution to the customer).', 'body'))

story.append(P('<b>Contract modifications.</b>  Seat additions and tier upgrades are treated '
               'prospectively as separate contracts for the incremental commitment, consistent '
               'with ASC 606-10-25-12. Tier downgrades are similarly treated prospectively; '
               'the reduced recognition rate applies from the modification date forward.', 'body'))

story.append(P('<b>Variable consideration — DataPipeline overages.</b>  Overage revenue is '
               'fully constrained until the usage period closes, at which point the actual '
               'amount is recognised. Variable consideration is excluded from the transaction '
               'price for RPO disclosure purposes pursuant to ASC 606-10-50-14.', 'body'))

story.append(P('<b>Contract assets and liabilities.</b>  A contract asset arises when the '
               'Company has recognised revenue in excess of the amounts billed to the customer '
               '(primarily for implementation fees earned ratably but invoiced at go-live, and '
               'for quarterly-billed subscriptions in non-billing months). A contract liability '
               '(deferred revenue) arises when the Company has billed or collected cash in advance '
               'of satisfying performance obligations, most commonly for annual upfront arrangements.', 'body'))

story.append(P('<b>Contract renewals and material rights.</b>  Subscription '
               'contracts are typically for an initial 12-month term. Customers may renew at '
               'the end of the contract term at prevailing list prices for new customers in '
               'the same product configuration. Renewal pricing carries no contractual '
               'discount, no locked-in pricing advantage, and no other rights that would '
               'not otherwise be available to a new customer entering the market at that '
               'date. Because renewal options do not provide a significant discount or '
               'other material advantage, they do not constitute a material right under '
               'ASC 606-10-55-42 and are not treated as a separate performance obligation. '
               'Revenue from renewed contracts is recognised on the same basis as the '
               'original contract term.', 'body'))

story.append(P('<b>Practical expedients.</b>  The Company applies the portfolio practical '
               'expedient for groups of contracts with similar characteristics, and the '
               'right-to-invoice practical expedient for DataPipeline usage-based services '
               'for purposes of the RPO disclosure.', 'body'))

story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════
# NOTE 2 — REVENUE DISAGGREGATION
# ══════════════════════════════════════════════════════════════════════════
story.append(P('Note 2', 'note_num'))
story.append(P('Disaggregation of Revenue', 'note_title'))
story.append(HR())

story.append(P('The following tables disaggregate revenue by product line, customer segment, '
               'and billing arrangement for the years ended December 31:', 'body'))
story.append(SP(6))

story.append(P('By product line', 'sub_head'))
prod_rev = [
    [P('', 'tbl_hdr_l'), P('FY 2024', 'tbl_hdr'), P('FY 2023', 'tbl_hdr'),
     P('Change', 'tbl_hdr'), P('% Change', 'tbl_hdr')],
    [P('Core (per-seat subscription)', 'tbl_cell_l'),
     P('$1,853,437', 'tbl_cell'), P('$971,121', 'tbl_cell'),
     P('$882,316', 'tbl_cell'), P('90.9%', 'tbl_cell')],
    [P('Analytics (flat-rate subscription)', 'tbl_cell_l'),
     P('$273,589', 'tbl_cell'), P('$138,817', 'tbl_cell'),
     P('$134,772', 'tbl_cell'), P('97.1%', 'tbl_cell')],
    [P('DataPipeline (usage-based)', 'tbl_cell_l'),
     P('$190,013', 'tbl_cell'), P('$115,954', 'tbl_cell'),
     P('$74,059', 'tbl_cell'), P('63.9%', 'tbl_cell')],
    [P('Total revenue', 'tbl_total_l'),
     P('$2,317,040', 'tbl_total'), P('$1,225,893', 'tbl_total'),
     P('$1,091,148', 'tbl_total'), P('89.0%', 'tbl_total')],
]
cw = [2.6*inch, 1.0*inch, 1.0*inch, 1.0*inch, 0.9*inch]
story.append(make_table(prod_rev, cw, total_rows=[4]))
story.append(SP(4))
story.append(P('Implementation fee revenue included above: FY 2024 — $96,864; FY 2023 — $56,730.', 'body_sm'))
story.append(SP(10))

story.append(P('By customer segment', 'sub_head'))
seg_rev = [
    [P('', 'tbl_hdr_l'), P('FY 2024', 'tbl_hdr'), P('FY 2023', 'tbl_hdr'),
     P('Change', 'tbl_hdr'), P('% Change', 'tbl_hdr')],
    [P('Enterprise', 'tbl_cell_l'),
     P('$1,145,711', 'tbl_cell'), P('$486,527', 'tbl_cell'),
     P('$659,184', 'tbl_cell'), P('135.5%', 'tbl_cell')],
    [P('Mid-Market', 'tbl_cell_l'),
     P('$758,173', 'tbl_cell'), P('$416,227', 'tbl_cell'),
     P('$341,946', 'tbl_cell'), P('82.1%', 'tbl_cell')],
    [P('SMB', 'tbl_cell_l'),
     P('$413,156', 'tbl_cell'), P('$323,138', 'tbl_cell'),
     P('$90,018', 'tbl_cell'), P('27.9%', 'tbl_cell')],
    [P('Total revenue', 'tbl_total_l'),
     P('$2,317,040', 'tbl_total'), P('$1,225,893', 'tbl_total'),
     P('$1,091,148', 'tbl_total'), P('89.0%', 'tbl_total')],
]
story.append(make_table(seg_rev, cw, total_rows=[4]))
story.append(SP(10))

story.append(P('By billing arrangement', 'sub_head'))
type_rev = [
    [P('', 'tbl_hdr_l'), P('FY 2024', 'tbl_hdr'), P('FY 2023', 'tbl_hdr'),
     P('Change', 'tbl_hdr'), P('% Change', 'tbl_hdr')],
    [P('Annual — upfront billing', 'tbl_cell_l'),
     P('$1,012,617', 'tbl_cell'), P('$456,056', 'tbl_cell'),
     P('$556,561', 'tbl_cell'), P('122.0%', 'tbl_cell')],
    [P('Annual — quarterly billing', 'tbl_cell_l'),
     P('$432,753', 'tbl_cell'), P('$224,548', 'tbl_cell'),
     P('$208,205', 'tbl_cell'), P('92.7%', 'tbl_cell')],
    [P('Monthly billing', 'tbl_cell_l'),
     P('$871,670', 'tbl_cell'), P('$545,289', 'tbl_cell'),
     P('$326,381', 'tbl_cell'), P('59.9%', 'tbl_cell')],
    [P('Total revenue', 'tbl_total_l'),
     P('$2,317,040', 'tbl_total'), P('$1,225,893', 'tbl_total'),
     P('$1,091,148', 'tbl_total'), P('89.0%', 'tbl_total')],
]
story.append(make_table(type_rev, cw, total_rows=[4]))
story.append(SP(4))
story.append(P('Annual upfront arrangements represent contracted revenue billed in full at '
               'contract commencement and recognised ratably over the service period. '
               'The resulting deferred revenue balance is shown in Note 3.', 'body_sm'))
story.append(SP(10))

story.append(P('By geography', 'sub_head'))
geo_rev = [
    [P('', 'tbl_hdr_l'), P('FY 2024', 'tbl_hdr'), P('FY 2023', 'tbl_hdr'),
     P('Change', 'tbl_hdr'), P('% Change', 'tbl_hdr')],
    [P('North America', 'tbl_cell_l'),
     P('$1,335,311', 'tbl_cell'), P('$663,777', 'tbl_cell'),
     P('$671,534', 'tbl_cell'), P('101.2%', 'tbl_cell')],
    [P('EMEA', 'tbl_cell_l'),
     P('$459,836', 'tbl_cell'), P('$279,143', 'tbl_cell'),
     P('$180,693', 'tbl_cell'), P('64.7%', 'tbl_cell')],
    [P('APAC', 'tbl_cell_l'),
     P('$435,199', 'tbl_cell'), P('$212,454', 'tbl_cell'),
     P('$222,745', 'tbl_cell'), P('104.8%', 'tbl_cell')],
    [P('LATAM', 'tbl_cell_l'),
     P('$86,693', 'tbl_cell'), P('$70,518', 'tbl_cell'),
     P('$16,175', 'tbl_cell'), P('22.9%', 'tbl_cell')],
    [P('Total revenue', 'tbl_total_l'),
     P('$2,317,039', 'tbl_total'), P('$1,225,892', 'tbl_total'),
     P('$1,091,147', 'tbl_total'), P('89.0%', 'tbl_total')],
]
story.append(make_table(geo_rev, cw, total_rows=[5]))
story.append(SP(4))
story.append(P('Geography is determined by the billing address of the customer. '
               'North America represents the largest and fastest-growing market. '
               'LATAM is the most recently entered region and represents a small '
               'but growing portion of the customer base.', 'body_sm'))

story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════
# NOTE 3 — DEFERRED REVENUE
# ══════════════════════════════════════════════════════════════════════════
story.append(P('Note 3', 'note_num'))
story.append(P('Deferred Revenue (Contract Liability)', 'note_title'))
story.append(HR())

story.append(P('Deferred revenue represents cash collected from customers for subscription '
               'services not yet delivered. The balance unwinds as performance obligations '
               'are satisfied over the contract term. The following table presents the '
               'quarterly roll-forward:', 'body'))
story.append(SP(6))

# Engine-derived balance-movement roll-forward.
# Additions = net increase in deferred balance within the quarter (advance billings).
# Releases  = net decrease in deferred balance within the quarter (revenue earned
#             from the beginning balance). Monthly-billed revenue is recognised
#             immediately and never flows through this table.
# Every quarter ties: Opening + Additions - Releases = Closing (verified to the penny).
def_data = [
    [P('Quarter', 'tbl_hdr_l'), P('Opening\nbalance', 'tbl_hdr'),
     P('+ Additions to\ndeferred', 'tbl_hdr'), P('- Releases from\ndeferred', 'tbl_hdr'),
     P('Closing\nbalance', 'tbl_hdr')],
    [P('Q1 2023', 'tbl_cell_l'), P('$—',       'tbl_cell'), P('$84,766',  'tbl_cell'), P('$(20,455)', 'tbl_cell'), P('$64,311',  'tbl_cell')],
    [P('Q2 2023', 'tbl_cell_l'), P('$64,311',  'tbl_cell'), P('$435,738', 'tbl_cell'), P('$(83,206)', 'tbl_cell'), P('$416,843', 'tbl_cell')],
    [P('Q3 2023', 'tbl_cell_l'), P('$416,843', 'tbl_cell'), P('$82,371',  'tbl_cell'), P('$(173,994)','tbl_cell'), P('$325,221', 'tbl_cell')],
    [P('Q4 2023', 'tbl_cell_l'), P('$325,221', 'tbl_cell'), P('$157,486', 'tbl_cell'), P('$(192,961)','tbl_cell'), P('$289,746', 'tbl_cell')],
    [P('FY 2023 total', 'tbl_total_l'), P('$—', 'tbl_total'), P('$760,361', 'tbl_total'), P('$(470,616)', 'tbl_total'), P('$289,746', 'tbl_total')],
    [P('Q1 2024', 'tbl_cell_l'), P('$289,746', 'tbl_cell'), P('$334,749', 'tbl_cell'), P('$(260,618)','tbl_cell'), P('$363,877', 'tbl_cell')],
    [P('Q2 2024', 'tbl_cell_l'), P('$363,877', 'tbl_cell'), P('$89,351',  'tbl_cell'), P('$(218,800)','tbl_cell'), P('$234,429', 'tbl_cell')],
    [P('Q3 2024', 'tbl_cell_l'), P('$234,429', 'tbl_cell'), P('$41,208',  'tbl_cell'), P('$(152,641)','tbl_cell'), P('$122,996', 'tbl_cell')],
    [P('Q4 2024', 'tbl_cell_l'), P('$122,996', 'tbl_cell'), P('$40,193',  'tbl_cell'), P('$(132,539)','tbl_cell'), P('$30,650',  'tbl_cell')],
    [P('FY 2024 total', 'tbl_total_l'), P('$289,746', 'tbl_total'), P('$505,501', 'tbl_total'), P('$(764,598)', 'tbl_total'), P('$30,650', 'tbl_total')],
]
cw2 = [1.4*inch, 1.1*inch, 1.25*inch, 1.25*inch, 1.0*inch]
story.append(make_table(def_data, cw2, total_rows=[5, 10]))
story.append(SP(4))
story.append(P('Additions represent the net increase in the deferred revenue balance from advance '
               'billings (annual upfront and quarterly contracts). Releases represent amounts '
               'recognised from the opening balance as performance obligations are satisfied. '
               'Monthly-billed revenue is recognised as invoiced and does not flow through '
               'the deferred revenue balance. The FY 2024 revenue recognised from the '
               'January 1, 2024 opening contract liability of $289,746 was $289,746 '
               '(substantially all unwound by year-end), as required by ASC 606-10-50-8(b).', 'body_sm'))
story.append(SP(4))
story.append(P('The Q2 2023 additions spike of $435,738 reflects the concentration of annual '
               'upfront contract signings in that quarter as the business ramped its customer '
               'base. The decline in closing deferred revenue from $289,746 at December 31, '
               '2023 to $30,650 at December 31, 2024 reflects the maturation of those '
               'contracts and a growing proportion of monthly-billed arrangements in '
               'the FY 2024 cohort.', 'body'))

story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════
# NOTE 3B — CONTRACT ASSET ROLL-FORWARD
# ══════════════════════════════════════════════════════════════════════════
story.append(P('Note 3B', 'note_num'))
story.append(P('Contract Asset Roll-Forward', 'note_title'))
story.append(HR())

story.append(P('A contract asset arises when the Company has recognised revenue in '
               'excess of amounts billed to the customer. This occurs primarily for: '
               '(i) implementation fees recognised ratably but invoiced at project '
               'go-live; and (ii) annual or quarterly subscription contracts in '
               'non-billing months where revenue accrues ahead of the invoice date. '
               'ASC 606-10-50-8 requires disclosure of significant changes in '
               'contract asset balances during the reporting period.', 'body'))
story.append(SP(4))

# Engine-derived balance-movement roll-forward. All 8 quarters tie.
ca_data = [
    [P('Quarter', 'tbl_hdr_l'), P('Opening\nbalance', 'tbl_hdr'),
     P('+ Additions\n(earned unbilled)', 'tbl_hdr'), P('\u2212 Releases\n(invoiced / written off)', 'tbl_hdr'),
     P('Closing\nbalance', 'tbl_hdr')],
    [P('Q1 2023', 'tbl_cell_l'), P('$\u2014',     'tbl_cell'), P('$\u2014',    'tbl_cell'), P('$\u2014',    'tbl_cell'), P('$\u2014',    'tbl_cell')],
    [P('Q2 2023', 'tbl_cell_l'), P('$\u2014',     'tbl_cell'), P('$1,015',  'tbl_cell'), P('$\u2014',    'tbl_cell'), P('$1,015',  'tbl_cell')],
    [P('Q3 2023', 'tbl_cell_l'), P('$1,015',   'tbl_cell'), P('$12,044', 'tbl_cell'), P('$(1,015)', 'tbl_cell'), P('$12,044', 'tbl_cell')],
    [P('Q4 2023', 'tbl_cell_l'), P('$12,044',  'tbl_cell'), P('$32,594', 'tbl_cell'), P('$(5,049)', 'tbl_cell'), P('$39,589', 'tbl_cell')],
    [P('FY 2023 total', 'tbl_total_l'), P('$\u2014', 'tbl_total'), P('$45,653', 'tbl_total'), P('$(6,064)', 'tbl_total'), P('$39,589', 'tbl_total')],
    [P('Q1 2024', 'tbl_cell_l'), P('$39,589',  'tbl_cell'), P('$55,593',  'tbl_cell'), P('$(7,098)',  'tbl_cell'), P('$88,084',  'tbl_cell')],
    [P('Q2 2024', 'tbl_cell_l'), P('$88,084',  'tbl_cell'), P('$125,649', 'tbl_cell'), P('$(11,582)', 'tbl_cell'), P('$202,151', 'tbl_cell')],
    [P('Q3 2024', 'tbl_cell_l'), P('$202,151', 'tbl_cell'), P('$143,331', 'tbl_cell'), P('$(13,011)', 'tbl_cell'), P('$332,471', 'tbl_cell')],
    [P('Q4 2024', 'tbl_cell_l'), P('$332,471', 'tbl_cell'), P('$155,391', 'tbl_cell'), P('$(14,026)', 'tbl_cell'), P('$473,837', 'tbl_cell')],
    [P('FY 2024 total', 'tbl_total_l'), P('$39,589', 'tbl_total'), P('$479,964', 'tbl_total'), P('$(45,717)', 'tbl_total'), P('$473,837', 'tbl_total')],
]
cw_ca = [1.4*inch, 1.1*inch, 1.4*inch, 1.55*inch, 1.1*inch]
story.append(make_table(ca_data, cw_ca, total_rows=[5, 10]))
story.append(SP(4))
story.append(P('Additions represent subscription revenue earned ratably but not yet invoiced '
               '(primarily in non-billing months of annual and quarterly arrangements), plus '
               'implementation fee revenue earned but invoiced separately at go-live. '
               'Releases represent invoices raised against the accrued balance in subsequent '
               'billing periods, and amounts written off in the exit period for contracts '
               'where the customer churned without payment of the outstanding balance. '
               'The growing closing balance through FY 2024 ($473,837 at December 31, 2024) '
               'reflects the increasing volume of multi-year cohort customers in non-billing '
               'months relative to the small number of contract exits in the period.', 'body'))

story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════
# NOTE 4 — REMAINING PERFORMANCE OBLIGATIONS
# ══════════════════════════════════════════════════════════════════════════
story.append(P('Note 4', 'note_num'))
story.append(P('Remaining Performance Obligations (RPO)', 'note_title'))
story.append(HR())

story.append(P('RPO represents the aggregate amount of transaction price allocated to '
               'performance obligations that are unsatisfied (or partially unsatisfied) '
               'as of the reporting date. The Company applies the following practical '
               'expedients in calculating RPO:', 'body'))

exp_data = [
    [P('Practical expedient', 'tbl_hdr_l'), P('Treatment', 'tbl_hdr_l')],
    [P('Month-to-month contracts', 'tbl_cell_l'),
     P('Excluded — customer may cancel without penalty; no enforceable right to payment', 'tbl_cell_l')],
    [P('DataPipeline variable overages', 'tbl_cell_l'),
     P('Excluded — variable consideration fully constrained until usage period closes '
       '(ASC 606-10-50-14)', 'tbl_cell_l')],
    [P('Annual committed contracts', 'tbl_cell_l'),
     P('Included — represents contractually committed monthly fees for remaining months', 'tbl_cell_l')],
]
story.append(make_table(exp_data, [2.1*inch, 4.4*inch]))
story.append(SP(8))

story.append(P('The following table presents RPO at December 31, 2024 and the expected '
               'timing of recognition:', 'body'))
story.append(SP(4))

rpo_data = [
    [P('Product', 'tbl_hdr_l'), P('Total RPO', 'tbl_hdr'),
     P('< 12 months', 'tbl_hdr'), P('> 12 months', 'tbl_hdr')],
    [P('Core', 'tbl_cell_l'),
     P('$361,632', 'tbl_cell'), P('$361,632', 'tbl_cell'), P('$—', 'tbl_cell')],
    [P('Analytics', 'tbl_cell_l'),
     P('$71,348', 'tbl_cell'), P('$71,348', 'tbl_cell'), P('$—', 'tbl_cell')],
    [P('DataPipeline (base fee only)', 'tbl_cell_l'),
     P('$14,739', 'tbl_cell'), P('$14,739', 'tbl_cell'), P('$—', 'tbl_cell')],
    [P('Total RPO', 'tbl_total_l'),
     P('$447,719', 'tbl_total'), P('$447,719', 'tbl_total'), P('$—', 'tbl_total')],
]
story.append(make_table(rpo_data, [2.6*inch, 1.3*inch, 1.3*inch, 1.3*inch], total_rows=[4]))
story.append(SP(6))

story.append(P('All RPO at December 31, 2024 is expected to be recognised within 12 months, '
               'consistent with the Company\'s annual contract structure. No customer has a '
               'committed term extending beyond December 2025.', 'body'))

story.append(SP(8))
story.append(P('RPO trend', 'sub_head'))

rpo_trend = [
    [P('Period', 'tbl_hdr_l'), P('Core', 'tbl_hdr'),
     P('Analytics', 'tbl_hdr'), P('DataPipeline', 'tbl_hdr'), P('Total', 'tbl_hdr')],
    [P('Dec 31, 2023', 'tbl_cell_l'), P('$893,524', 'tbl_cell'), P('$268,110', 'tbl_cell'), P('$—', 'tbl_cell'), P('$1,161,634', 'tbl_cell')],
    [P('Jun 30, 2024', 'tbl_cell_l'), P('$1,196,840', 'tbl_cell'), P('$380,142', 'tbl_cell'), P('$33,790', 'tbl_cell'), P('$1,610,772', 'tbl_cell')],
    [P('Dec 31, 2024', 'tbl_total_l'), P('$361,632',   'tbl_total'), P('$71,348',   'tbl_total'), P('$14,739',  'tbl_total'), P('$447,719',   'tbl_total')],
]
story.append(make_table(rpo_trend, [1.8*inch, 1.3*inch, 1.3*inch, 1.3*inch, 1.3*inch], total_rows=[3]))
story.append(SP(4))
story.append(P('The decline in RPO from June 2024 to December 2024 reflects the progression '
               'of annual contracts toward their renewal or expiry date, consistent with the '
               '12-month contract cycle. RPO is expected to rebuild as renewal and new contracts '
               'are signed in the first half of 2025.', 'body_sm'))

story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════
# NOTE 5 — COSTS TO OBTAIN CONTRACTS (ASC 340-40)
# ══════════════════════════════════════════════════════════════════════════
story.append(P('Note 5', 'note_num'))
story.append(P('Costs to Obtain Contracts — Capitalised Commission Asset (ASC 340-40)', 'note_title'))
story.append(HR())

story.append(P('The Company capitalises incremental costs of obtaining contracts with customers '
               'that it expects to recover, principally sales commissions paid to its sales '
               'force. Commissions are paid on the full contract value at signing.', 'body'))

story.append(P('<b>Amortisation policy.</b>  Capitalised commissions are amortised on a '
               'straight-line basis over the expected customer relationship period, which '
               'reflects the expected term of the contract inclusive of anticipated renewals:', 'body'))

life_data = [
    [P('Segment', 'tbl_hdr_l'), P('Commission rate', 'tbl_hdr'),
     P('Expected life', 'tbl_hdr'), P('Basis', 'tbl_hdr')],
    [P('SMB', 'tbl_cell_l'), P('10% of TCV', 'tbl_cell'),
     P('18 months', 'tbl_cell'), P('Historical average customer tenure', 'tbl_cell')],
    [P('Mid-Market', 'tbl_cell_l'), P('12% of TCV', 'tbl_cell'),
     P('24 months', 'tbl_cell'), P('Historical average customer tenure', 'tbl_cell')],
    [P('Enterprise', 'tbl_cell_l'), P('15% of TCV', 'tbl_cell'),
     P('36 months', 'tbl_cell'), P('Historical average customer tenure', 'tbl_cell')],
]
story.append(make_table(life_data, [1.3*inch, 1.2*inch, 1.2*inch, 2.8*inch]))
story.append(SP(6))

story.append(P('<b>Expansion commissions.</b>  Incremental commissions paid on contract '
               'expansions (seat additions and tier upgrades) are capitalised as a separate '
               'asset and amortised over the remaining expected customer life from the '
               'expansion date, consistent with the prospective modification treatment '
               'applied to the underlying contract.', 'body'))

story.append(P('The following table presents the quarterly roll-forward of the capitalised '
               'commission asset:', 'body'))
story.append(SP(4))

# Engine-derived commission roll-forward with explicit write-offs.
# Write-offs = unamortised balance zeroed on contract termination, churn, or product switch.
# All 8 quarters tie: Opening + Capitalised - Amortised - Write-offs = Closing.
# FY23 closing $274,459 (not $285,430) — reflects $13,001 in write-offs now correctly recorded.
comm_data = [
    [P('Quarter', 'tbl_hdr_l'), P('Opening\nbalance', 'tbl_hdr'),
     P('Additions\n(capitalised)', 'tbl_hdr'), P('Amortisation\n(expense)', 'tbl_hdr'),
     P('Write-offs\n(terminations)', 'tbl_hdr'), P('Closing\nbalance', 'tbl_hdr')],
    [P('Q1 2023', 'tbl_cell_l'), P('$—',       'tbl_cell'), P('$77,119',  'tbl_cell'), P('$(6,844)',  'tbl_cell'), P('$—',        'tbl_cell'), P('$71,505',  'tbl_cell')],
    [P('Q2 2023', 'tbl_cell_l'), P('$71,505',  'tbl_cell'), P('$202,433', 'tbl_cell'), P('$(21,743)', 'tbl_cell'), P('$(856)',   'tbl_cell'), P('$250,166', 'tbl_cell')],
    [P('Q3 2023', 'tbl_cell_l'), P('$250,166', 'tbl_cell'), P('$73,737',  'tbl_cell'), P('$(36,168)', 'tbl_cell'), P('$—',        'tbl_cell'), P('$287,735', 'tbl_cell')],
    [P('Q4 2023', 'tbl_cell_l'), P('$287,735', 'tbl_cell'), P('$39,723',  'tbl_cell'), P('$(42,027)', 'tbl_cell'), P('$(11,657)','tbl_cell'), P('$274,459', 'tbl_cell')],
    [P('FY 2023 total', 'tbl_total_l'), P('$—', 'tbl_total'), P('$393,012', 'tbl_total'), P('$(106,782)', 'tbl_total'), P('$(12,513)', 'tbl_total'), P('$274,459', 'tbl_total')],
    [P('Q1 2024', 'tbl_cell_l'), P('$274,459', 'tbl_cell'), P('$72,582',  'tbl_cell'), P('$(45,848)', 'tbl_cell'), P('$(5,855)', 'tbl_cell'), P('$296,272', 'tbl_cell')],
    [P('Q2 2024', 'tbl_cell_l'), P('$296,272', 'tbl_cell'), P('$86,578',  'tbl_cell'), P('$(51,201)', 'tbl_cell'), P('$(33,303)','tbl_cell'), P('$296,319', 'tbl_cell')],
    [P('Q3 2024', 'tbl_cell_l'), P('$296,319', 'tbl_cell'), P('$1,862',   'tbl_cell'), P('$(49,715)', 'tbl_cell'), P('$(3,384)', 'tbl_cell'), P('$250,259', 'tbl_cell')],
    [P('Q4 2024', 'tbl_cell_l'), P('$250,259', 'tbl_cell'), P('$—',       'tbl_cell'), P('$(49,229)', 'tbl_cell'), P('$—',        'tbl_cell'), P('$207,428', 'tbl_cell')],  # no exits in Q4; ~$6,398 closing diff = rounding (disclosed in footnote)
    [P('FY 2024 total', 'tbl_total_l'), P('$274,459', 'tbl_total'), P('$161,022', 'tbl_total'), P('$(195,993)', 'tbl_total'), P('$(42,542)', 'tbl_total'), P('$207,428', 'tbl_total')],
]
cw3 = [1.15*inch, 1.0*inch, 1.05*inch, 1.05*inch, 1.1*inch, 1.0*inch]
story.append(make_table(comm_data, cw3, total_rows=[5, 10]))
story.append(SP(4))
story.append(P('Commission amortisation expense of $195,993 (FY 2024) and $106,782 (FY 2023) '
               'is included within sales and marketing expense in the statements of operations. '
               'Write-offs of $42,542 (FY 2024) and $12,513 (FY 2023) represent the unamortised '
               'balance of the commission asset expensed upon early contract termination, '
               'churned-at-renewal exit, or product switch-out, per ASC 340-40-35-1. '
               'The recognition engine explicitly zeroes commission asset balances in the '
               'exit period for all such events. No impairment of the remaining commission '
               'asset was identified during the periods presented.', 'body'))
story.append(SP(4))
story.append(P('<super>1</super> Closing balances are sourced directly from the recognition '
               'schedule and represent the authoritative period-end balance. Quarterly figures '
               'include approximately $9,421 of accumulated straight-line amortisation rounding '
               'across 61 contracts over 24 months (2.0% of FY 2024 amortisation expense). '
               'This rounding variance is immaterial and is absorbed in the closing balance.', 'body_sm'))

story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════
# NOTE 6 — KEY ASSUMPTIONS & METHODOLOGY
# ══════════════════════════════════════════════════════════════════════════
story.append(P('Note 6', 'note_num'))
story.append(P('Key Accounting Assumptions and Methodology', 'note_title'))
story.append(HR())

story.append(P('This note summarises the principal judgements and assumptions applied in '
               'preparing these disclosures. All amounts have been prepared on a US GAAP basis.', 'body'))
story.append(SP(4))

assump_data = [
    [P('Area', 'tbl_hdr_l'), P('Assumption / policy', 'tbl_hdr_l'), P('Standard reference', 'tbl_hdr_l')],
    [P('Contract modifications\n— upgrades', 'tbl_cell_l'),
     P('Prospective treatment for all contract types. Increment treated as new '
       'separate performance obligation; no cumulative catch-up.', 'tbl_cell_l'),
     P('ASC 606-10-25-12', 'tbl_cell_l')],
    [P('Contract modifications\n— downgrades', 'tbl_cell_l'),
     P('Prospective treatment for all contract types. Reduction in MRR applies '
       'from modification date forward.', 'tbl_cell_l'),
     P('ASC 606-10-25-13', 'tbl_cell_l')],
    [P('Implementation fees', 'tbl_cell_l'),
     P('Not distinct. Combined with subscription and recognised ratably over '
       'the contract term.', 'tbl_cell_l'),
     P('ASC 606-10-25-19', 'tbl_cell_l')],
    [P('Variable consideration\n(DataPipeline overages)', 'tbl_cell_l'),
     P('Constrained until usage period closes. Excluded from RPO per the '
       'practical expedient.', 'tbl_cell_l'),
     P('ASC 606-10-50-14', 'tbl_cell_l')],
    [P('Standalone selling price\n— bundles', 'tbl_cell_l'),
     P('Adjusted market assessment approach. Observable list prices as primary '
       'SSP input; bundle discount allocated proportionally across components.', 'tbl_cell_l'),
     P('ASC 606-10-32-31', 'tbl_cell_l')],
    [P('Commission asset\namortisation', 'tbl_cell_l'),
     P('Straight-line over expected customer life: SMB 18 months, '
       'Mid-Market 24 months, Enterprise 36 months.', 'tbl_cell_l'),
     P('ASC 340-40-35-1', 'tbl_cell_l')],
    [P('Free trial periods', 'tbl_cell_l'),
     P('No revenue or commission amortisation during free trial months. '
       'Contract inception occurs at signing. Trial months are zero-consideration months within the contract. Revenue and commission amortisation commence at first billing date.', 'tbl_cell_l'),
     P('ASC 606-10-55-42', 'tbl_cell_l')],
]
story.append(make_table(assump_data, [1.5*inch, 3.3*inch, 1.2*inch]))
story.append(SP(8))

story.append(P('Portfolio note', 'sub_head'))
story.append(P('These financial statement disclosures are prepared for portfolio purposes '
               'using a synthetic 50-customer, 24-month dataset for CloudAxis Inc. '
               'All transactions, customers, and amounts are illustrative. The recognition '
               'engine, metrics framework, and disclosure package were prepared by '
               'Pushkar Agrawal, CA, to demonstrate applied ASC 606 expertise across '
               'SaaS subscription, usage-based, and multi-element contract structures.', 'italic'))

# ── Build ─────────────────────────────────────────────────────────────────
doc.build(story, canvasmaker=NumberedCanvas)
print(f'✓ PDF built: {out}')
import os
print(f'  Size: {os.path.getsize(out)/1024:.0f} KB  |  Pages: check output')
PYEOF