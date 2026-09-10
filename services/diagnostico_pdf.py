"""PDF do resultado do diagnóstico de maturidade."""
import io

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from services.pdf_utils import esc


def diagnostico_pdf(empresa, diag, score, nivel, linhas, plano) -> io.BytesIO:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, title="Diagnóstico de maturidade LGPD")
    estilos = getSampleStyleSheet()

    elementos = [
        Paragraph("Diagnóstico de maturidade — LGPD", estilos["Title"]),
        Paragraph(esc(empresa.nome), estilos["Heading2"]),
        Paragraph(f"Score: <b>{score}%</b> — Nível: <b>{nivel}</b>", estilos["Heading3"]),
        Paragraph(f"Realizado em {diag.finalizado_em.strftime('%d/%m/%Y')}.", estilos["Normal"]),
        Spacer(1, 6 * mm),
    ]

    tabela = [["Dimensão", "%"]]
    for linha in linhas:
        tabela.append([linha["label"], f"{linha['pct']}%"])
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


def comparativo_pdf(empresa, escopos, dimensoes) -> io.BytesIO:
    """Tabela dimensões × escopos (empresa toda e setores) com o último diagnóstico de cada um."""
    from reportlab.lib.pagesizes import landscape

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=landscape(A4), title="Diagnóstico de maturidade — comparativo")
    st = getSampleStyleSheet()
    el = [
        Paragraph("Diagnóstico de maturidade — comparativo por setor", st["Title"]),
        Paragraph(esc(empresa.nome), st["Heading2"]),
        Spacer(1, 6 * mm),
    ]
    cab = ["Dimensão"] + [f"{e['label']}\n{e['diag'].finalizado_em:%d/%m/%Y}" for e in escopos]
    dados = [cab]
    for code, label in dimensoes:
        dados.append([label] + [f"{e['por_dim'].get(code, '—')}%" if e["por_dim"].get(code) is not None else "—"
                                for e in escopos])
    dados.append(["Score geral"] + [f"{e['score']}% ({e['nivel']})" for e in escopos])
    t = Table(dados, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f4c5c")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f3f0")]),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
    ]))
    el.append(t)
    doc.build(el)
    buf.seek(0)
    return buf
