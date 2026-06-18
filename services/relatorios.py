"""Relatórios exportáveis: ranking em Excel e conformidade em PDF."""
import io

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from services.metricas import ranking_empresa, resumo_empresa

_CABECALHO = ["#", "Setor", "Área", "Colaboradores", "Avaliados", "Em dia (%)", "Média"]


def ranking_excel(empresa) -> io.BytesIO:
    from openpyxl import Workbook

    wb = Workbook()
    ws = wb.active
    ws.title = "Ranking"
    ws.append(_CABECALHO)
    for r in ranking_empresa(empresa.id):
        ws.append([
            r["posicao"], r["setor"].nome, r["setor"].area_label,
            r["n"], r["avaliados"], r["pct_em_dia"],
            r["media"] if r["media"] is not None else "",
        ])
    for coluna, largura in zip("ABCDEFG", (5, 28, 26, 14, 12, 12, 10)):
        ws.column_dimensions[coluna].width = largura
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf


def conformidade_pdf(empresa) -> io.BytesIO:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, title="Relatório de conformidade LGPD")
    estilos = getSampleStyleSheet()
    dados = resumo_empresa(empresa.id)

    elementos = [
        Paragraph("Relatório de conformidade — LGPD", estilos["Title"]),
        Paragraph(empresa.nome, estilos["Heading2"]),
        Paragraph(
            f"Conformidade geral: <b>{dados['pct_conformidade']}%</b> — "
            f"{dados['colaboradores']} colaboradores em {dados['setores']} setores.",
            estilos["Normal"],
        ),
        Spacer(1, 8 * mm),
    ]

    tabela = [["#", "Setor", "Área", "Colab.", "Aval.", "Em dia", "Média"]]
    for r in dados["ranking"]:
        tabela.append([
            r["posicao"], r["setor"].nome, r["setor"].area_label, r["n"], r["avaliados"],
            f"{r['pct_em_dia']}%", r["media"] if r["media"] is not None else "—",
        ])
    t = Table(tabela, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f4c5c")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f3f0")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    elementos.append(t)
    doc.build(elementos)
    buf.seek(0)
    return buf
