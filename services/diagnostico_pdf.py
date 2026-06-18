"""PDF do resultado do diagnóstico de maturidade."""
import io

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def diagnostico_pdf(empresa, diag, score, nivel, linhas, plano) -> io.BytesIO:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, title="Diagnóstico de maturidade LGPD")
    estilos = getSampleStyleSheet()

    elementos = [
        Paragraph("Diagnóstico de maturidade — LGPD", estilos["Title"]),
        Paragraph(empresa.nome, estilos["Heading2"]),
        Paragraph(f"Score: <b>{score}%</b> — Nível: <b>{nivel}</b>", estilos["Heading3"]),
        Paragraph(f"Realizado em {diag.finalizado_em.strftime('%d/%m/%Y')}.", estilos["Normal"]),
        Spacer(1, 6 * mm),
    ]

    tabela = [["Dimensão", "%"]]
    for l in linhas:
        tabela.append([l["label"], f"{l['pct']}%"])
    t = Table(tabela, repeatRows=1, colWidths=[130 * mm, 30 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f4c5c")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f3f0")]),
    ]))
    elementos.append(t)

    if plano:
        elementos.append(Spacer(1, 6 * mm))
        elementos.append(Paragraph("Plano de ação", estilos["Heading3"]))
        for item in plano:
            elementos.append(Paragraph(f"<b>{item['label']}.</b> {item['tip']}", estilos["Normal"]))
            elementos.append(Spacer(1, 2 * mm))

    doc.build(elementos)
    buf.seek(0)
    return buf
