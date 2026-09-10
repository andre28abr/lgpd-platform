"""Geração do certificado de conformidade em PDF (reportlab)."""
from io import BytesIO

import qrcode
from flask import url_for
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

_AZUL = HexColor("#0f4c5c")
_CINZA = HexColor("#5f5e5a")
_CLARO = HexColor("#9fb3b8")


def gerar_pdf(cert) -> BytesIO:
    buffer = BytesIO()
    largura, altura = landscape(A4)
    c = canvas.Canvas(buffer, pagesize=landscape(A4))

    # Moldura dupla
    c.setStrokeColor(_AZUL)
    c.setLineWidth(3)
    c.rect(12 * mm, 12 * mm, largura - 24 * mm, altura - 24 * mm)
    c.setStrokeColor(_CLARO)
    c.setLineWidth(0.8)
    c.rect(16 * mm, 16 * mm, largura - 32 * mm, altura - 32 * mm)

    centro = largura / 2

    c.setFillColor(_CINZA)
    c.setFont("Helvetica", 12)
    c.drawCentredString(centro, altura - 38 * mm, "CERTIFICADO DE CONFORMIDADE")

    c.setFillColor(_AZUL)
    c.setFont("Helvetica-Bold", 26)
    c.drawCentredString(centro, altura - 52 * mm, "Lei Geral de Proteção de Dados")

    c.setFillColor(_CINZA)
    c.setFont("Helvetica", 13)
    c.drawCentredString(centro, altura - 70 * mm, "Certificamos que")

    c.setFillColor(HexColor("#1a1a1a"))
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(centro, altura - 82 * mm, cert.usuario.nome)

    empresa = cert.usuario.empresa.nome if cert.usuario.empresa else ""
    linha = (
        f"concluiu com aproveitamento a avaliação de LGPD da área "
        f"{cert.area_label}"
    )
    c.setFillColor(_CINZA)
    c.setFont("Helvetica", 13)
    c.drawCentredString(centro, altura - 94 * mm, linha)
    if empresa:
        c.drawCentredString(centro, altura - 102 * mm, f"na empresa {empresa}.")

    c.setFillColor(_AZUL)
    c.setFont("Helvetica-Bold", 15)
    c.drawCentredString(centro, altura - 118 * mm, f"Aproveitamento: {cert.nota:.0f}%")

    # Rodapé: emissão, validade, código e verificação
    emitido = cert.emitido_em.strftime("%d/%m/%Y")
    validade = cert.valido_ate.strftime("%d/%m/%Y")
    c.setFillColor(_CINZA)
    c.setFont("Helvetica", 10)
    c.drawString(28 * mm, 26 * mm, f"Emitido em: {emitido}")
    c.drawString(28 * mm, 21 * mm, f"Válido até: {validade}")

    try:
        url = url_for("certificados.verificar", codigo=cert.codigo, _external=True)
    except RuntimeError:  # fora de uma requisição (ex.: CLI) não há URL externa
        url = f"/certificados/verificar/{cert.codigo}"
    c.drawRightString(largura - 28 * mm, 26 * mm, f"Código: {cert.codigo}")
    c.setFont("Helvetica", 8)
    c.drawRightString(largura - 28 * mm, 21 * mm, f"Verifique em: {url}")

    # QR Code apontando para a verificação pública (leitura pelo celular).
    qr = BytesIO()
    qrcode.make(url).save(qr, format="PNG")
    qr.seek(0)
    lado = 26 * mm
    c.drawImage(ImageReader(qr), largura - 28 * mm - lado, 31 * mm, lado, lado)

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer
