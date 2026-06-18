"""PDF do RIPD — Relatório de Impacto à Proteção de Dados (Art. 38)."""
import io

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def ripd_pdf(empresa, r) -> io.BytesIO:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, title="RIPD")
    st = getSampleStyleSheet()

    el = [
        Paragraph("Relatório de Impacto à Proteção de Dados (RIPD)", st["Title"]),
        Paragraph(empresa.nome, st["Heading2"]),
        Paragraph(r.titulo, st["Heading3"]),
        Spacer(1, 4 * mm),
    ]
    if r.ropa:
        el.append(Paragraph(f"<b>Tratamento (ROPA):</b> {r.ropa.atividade}", st["Normal"]))
    if r.descricao_tratamento:
        el.append(Paragraph(f"<b>Descrição:</b> {r.descricao_tratamento}", st["Normal"]))
    el.append(Spacer(1, 4 * mm))

    tabela = [
        ["Probabilidade", str(r.probabilidade)],
        ["Impacto", str(r.impacto)],
        ["Risco inerente", r.risco_inerente_nivel],
        ["Risco residual", r.risco_residual_label],
    ]
    t = Table(tabela, colWidths=[60 * mm, 100 * mm])
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f3f3f0")),
    ]))
    el.append(t)
    el.append(Spacer(1, 4 * mm))

    if r.medidas:
        el.append(Paragraph(f"<b>Medidas de mitigação:</b> {r.medidas}", st["Normal"]))
        el.append(Spacer(1, 3 * mm))
    if r.conclusao:
        el.append(Paragraph(f"<b>Conclusão:</b> {r.conclusao}", st["Normal"]))

    doc.build(el)
    buf.seek(0)
    return buf
