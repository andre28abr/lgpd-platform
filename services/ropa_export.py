"""Exportação do ROPA (Art. 37) em Excel e PDF.

É o inventário que o Encarregado apresenta à ANPD ou a auditores — até aqui o
único módulo do Pilar 2 sem um artefato exportável.
"""
import io

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from services.pdf_utils import celula_planilha, esc
from utils import agora_utc

COLUNAS = ["Atividade", "Setor", "Titulares", "Categorias de dados", "Finalidade",
           "Base legal", "Retenção", "Compartilhamento", "Atualizado em"]


def _linha(r):
    quando = r.atualizado_em or r.criado_em
    return [r.atividade, r.setor_label, r.titulares or "", r.categorias_dados or "",
            r.finalidade or "", r.base_legal_label, r.retencao or "", r.compartilhamento or "",
            quando.strftime("%d/%m/%Y") if quando else ""]


def ropa_excel(empresa, registros) -> io.BytesIO:
    from openpyxl import Workbook

    wb = Workbook()
    ws = wb.active
    ws.title = "ROPA"
    ws.append([f"ROPA — Registro das Operações de Tratamento (Art. 37) — {empresa.nome}"])
    ws.append([f"Gerado em {agora_utc():%d/%m/%Y %H:%M} UTC — {len(registros)} registro(s)"])
    ws.append([])
    ws.append(COLUNAS)
    for r in registros:
        ws.append([celula_planilha(v) for v in _linha(r)])
    for coluna, largura in zip("ABCDEFGHI", (34, 20, 24, 36, 40, 32, 22, 32, 14), strict=True):
        ws.column_dimensions[coluna].width = largura
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf


def ropa_pdf(empresa, registros) -> io.BytesIO:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=landscape(A4), title="ROPA",
                            leftMargin=12 * mm, rightMargin=12 * mm)
    st = getSampleStyleSheet()
    celula = ParagraphStyle("celula", parent=st["Normal"], fontSize=8, leading=10)

    el = [
        Paragraph("Registro das Operações de Tratamento (ROPA) — Art. 37", st["Title"]),
        Paragraph(esc(empresa.nome), st["Heading2"]),
        Paragraph(f"Gerado em {agora_utc():%d/%m/%Y} — {len(registros)} registro(s)", st["Normal"]),
        Spacer(1, 4 * mm),
    ]
    cabecalho = ["Atividade", "Setor", "Titulares", "Finalidade", "Base legal", "Retenção", "Compartilhamento"]
    dados = [[Paragraph(f"<b>{c}</b>", celula) for c in cabecalho]]
    for r in registros:
        valores = (r.atividade, r.setor_label, r.titulares or "—", r.finalidade or "—",
                   r.base_legal_label, r.retencao or "—", r.compartilhamento or "—")
        dados.append([Paragraph(esc(v), celula) for v in valores])

    t = Table(dados, repeatRows=1, colWidths=[45 * mm, 28 * mm, 32 * mm, 60 * mm, 40 * mm, 30 * mm, 38 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f4c5c")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f3f0")]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    el.append(t)
    doc.build(el)
    buf.seek(0)
    return buf
