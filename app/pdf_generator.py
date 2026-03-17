"""
app/pdf_generator.py  —  v4
Requisición liquidada — PDF imprimible ProHygiene.

CONVENCIÓN DE COORDENADAS (importante para entender el código):
  - ReportLab usa y desde abajo. Internamente trabajamos con 'top':
    la coordenada Y de la PARTE SUPERIOR de cada elemento.
  - Para dibujar texto: baseline = top - font_size
  - Para dibujar un rectángulo de alto H empezando en 'top': rect(x, top-H, w, H)
  - Cada función recibe 'top' y devuelve 'top - altura_consumida'.

Uso:
    from app.pdf_generator import generate_requisicion_pdf
    pdf_bytes = generate_requisicion_pdf(req_dict)
"""

import io
import json
import os
from collections import Counter
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as rl_canvas

# ─── Página ───────────────────────────────────────────────────────────────────
PW, PH = letter          # 612 × 792 pt
ML  = 14 * mm
MR  = 14 * mm
MT  = 12 * mm
MB  = 12 * mm
UW  = PW - ML - MR       # ≈ 533 pt
PAGE_BOTTOM_LIMIT = MB + 12 * mm

GAP = 5 * mm             # separación vertical entre secciones
LOGO_PATH = os.path.join(os.path.dirname(__file__), "..", "static", "branding", "logo-prohygiene-es.png")

# ─── Paleta (Eco-Ink: bordes + grises + acentos mínimos) ───────────────────
C_PAGE_BG   = colors.white                 # fondo pagina blanco
C_HDR_BG    = colors.HexColor("#1e3a5f")  # azul corporativo solo en textos/bordes clave
C_PRI       = colors.HexColor("#1d4ed8")  # azul primario para lineas y acentos
C_PRI_LIGHT = colors.HexColor("#f8fbff")  # tinte azul casi blanco (~5%)
C_PRI_BORDER= colors.HexColor("#1d4ed8")  # borde corporativo
C_CARD_TOP  = colors.HexColor("#1d4ed8")
C_WHITE     = colors.white
C_CARD_BG   = colors.HexColor("#fafafa")  # gris muy tenue
C_TBL_ALT   = colors.HexColor("#f6f6f6")  # gris 5% aprox
C_BLACK     = colors.HexColor("#111111")
C_GRAY1     = colors.HexColor("#303030")  # texto normal
C_GRAY2     = colors.HexColor("#707070")  # labels / secundario
C_SEP       = colors.HexColor("#d9d9d9")  # separadores tenues

C_GREEN     = colors.HexColor("#166534")
C_GREEN_BG  = colors.HexColor("#fbfefb")
C_GREEN_BD  = colors.HexColor("#9fc8ab")
C_AMBER     = colors.HexColor("#92400e")
C_AMBER_BG  = colors.HexColor("#fffdfa")
C_AMBER_BD  = colors.HexColor("#d6b58f")
C_RED       = colors.HexColor("#991b1b")
C_RED_BG    = colors.HexColor("#fffafa")
C_RED_BD    = colors.HexColor("#d8aaaa")

ALERT_MAP = {
    "ALERTA_FALTANTE":           "Faltante",
    "ALERTA_EXCEDENTE":          "Excedente",
    "ALERTA_CONSUMO_CERO":       "Consumo cero",
    "ALERTA_RETORNO_INCOMPLETO": "Retorno incompleto",
    "ALERTA_SIN_PROKEY":         "Sin ProKey",
}


# ─── Primitivos de dibujo ────────────────────────────────────────────────────

def _box(cv, x, top, w, h, *, fill=None, stroke=None, lw=0.5, r=0):
    """Rectángulo. 'top' = coordenada Y superior."""
    if fill:
        cv.setFillColor(fill)
    if stroke:
        cv.setStrokeColor(stroke)
        cv.setLineWidth(lw)
    kw = dict(fill=1 if fill else 0, stroke=1 if stroke else 0)
    if r:
        cv.roundRect(x, top - h, w, h, r, **kw)
    else:
        cv.rect(x, top - h, w, h, **kw)


def _hline(cv, x, y, w, color=C_SEP, lw=0.4):
    cv.setStrokeColor(color)
    cv.setLineWidth(lw)
    cv.line(x, y, x + w, y)


def _str(cv, x, top, text, *, font="Helvetica", size=8, color=C_BLACK,
         align="left", max_ch=None):
    """
    Dibuja texto. 'top' = parte superior del bloque de texto.
    baseline = top - size  (texto crece hacia abajo desde top).
    Retorna la coordenada Y de la parte inferior del texto (= baseline).
    """
    s = str(text)
    if max_ch and len(s) > max_ch:
        s = s[:max_ch - 1] + "…"
    baseline = top - size
    cv.setFont(font, size)
    cv.setFillColor(color)
    if align == "center":
        cv.drawCentredString(x, baseline, s)
    elif align == "right":
        cv.drawRightString(x, baseline, s)
    else:
        cv.drawString(x, baseline, s)
    return baseline   # == top - size


def _label_val(cv, x, top, label, value, *,
               lsize=5.5, vsize=8.5, gap=2,
               vfont="Helvetica-Bold", vcolor=C_BLACK,
               max_ch=30):
    """
    Dibuja:  LABEL (pequeño, gris)     ← empieza en 'top'
             Valor (grande, negrita)    ← empieza en top - lsize - gap

    Retorna el 'top' de la siguiente fila (= top - lsize - gap - vsize - padding_bottom).
    'gap' es el espacio entre la parte inferior del label y la parte superior del valor.
    """
    # Label: su parte superior es 'top', baseline = top - lsize
    _str(cv, x, top, label.upper(), font="Helvetica", size=lsize, color=C_GRAY2)

    # Valor: su parte superior es top - lsize - gap
    val_top = top - lsize - gap
    _str(cv, x, val_top, str(value),
         font=vfont, size=vsize, color=vcolor, max_ch=max_ch)

    # Devuelve dónde acaba el bloque completo (parte inferior del valor)
    return val_top - vsize   # == top - lsize - gap - vsize


# ─── Helpers de datos ────────────────────────────────────────────────────────

def _parse_alerts(raw):
    if not raw:
        return []
    if isinstance(raw, list):
        return raw
    try:
        return json.loads(raw)
    except Exception:
        return []


def _fmt(val, *, date_only=False):
    if not val:
        return "—"
    try:
        s = str(val)[:19].replace("T", " ")
        dt = datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%d/%m/%Y") if date_only else dt.strftime("%d/%m/%Y %H:%M")
    except Exception:
        return str(val)[:16]


def _estado_style(estado):
    """(fg, bg, border)"""
    return {
        "liquidada": (C_GREEN,    C_GREEN_BG,  C_GREEN_BD),
        "pendiente_prokey": (C_PRI, C_PRI_LIGHT, C_PRI_BORDER),
        "finalizada_sin_prokey": (C_GREEN, C_GREEN_BG, C_GREEN_BD),
        "entregada": (C_PRI,      C_PRI_LIGHT, C_PRI_BORDER),
        "no_entregada": (C_RED,   C_RED_BG,   C_RED_BD),
        "aprobada":  (colors.HexColor("#7c3aed"),
                      colors.HexColor("#ede9fe"),
                      colors.HexColor("#c4b5fd")),
        "preparado": (C_AMBER, C_AMBER_BG, C_AMBER_BD),
        "pendiente": (C_AMBER, C_AMBER_BG, C_AMBER_BD),
        "rechazada": (C_RED,   C_RED_BG,   C_RED_BD),
    }.get(str(estado).lower(), (C_GRAY2, C_CARD_BG, C_SEP))


def _dif_chip(item):
    """(label, fg, bg, border)"""
    mode = (item.get("liquidation_mode") or "").upper()
    contexto = str(item.get("contexto_operacion") or "").strip().lower()
    ent  = item.get("cantidad_entregada") or 0
    ret  = item.get("cantidad_retorna")   or 0
    usd  = item.get("cantidad_usada")     or 0
    nou  = item.get("cantidad_no_usada")  or 0
    # Alineado con la lógica web:
    # - CONSUMIBLE: esperado = no usado
    # - RETORNABLE + instalacion_inicial: esperado = no usado
    # - RETORNABLE + reposicion: esperado = usado + no usado
    if mode == "CONSUMIBLE" or contexto == "instalacion_inicial":
        expected_return = nou
    else:
        expected_return = usd + nou
    d = expected_return - ret
    if d == 0:
        return "OK", C_GREEN, C_GREEN_BG, C_GREEN_BD
    if d > 0:
        return f"Falta {d:g}", C_RED, C_RED_BG, C_RED_BD
    return f"Extra {abs(d):g}", C_AMBER, C_AMBER_BG, C_AMBER_BD


def _wrap(text, max_ch=55):
    words = str(text).split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if len(t) > max_ch:
            if cur: lines.append(cur)
            cur = w
        else:
            cur = t
    if cur: lines.append(cur)
    return lines


def _estado_label(estado: str | None) -> str:
    estado_norm = str(estado or "").lower()
    return {
        "pendiente_prokey": "Pendiente Prokey",
        "finalizada_sin_prokey": "Finalizada sin Prokey",
        "liquidada_en_prokey": "Finalizada en Prokey",
        "no_entregada": "No Entregada - Finalizada",
        "liquidada": "Pendiente Prokey",
    }.get(estado_norm, str(estado or ""))


def _timeline_liquidation_label(req: dict) -> str:
    estado_norm = str(req.get("estado") or "").lower()
    if estado_norm == "pendiente_prokey":
        return "Pend. Prokey"
    if estado_norm == "finalizada_sin_prokey":
        return "Finalizada"
    return "Liquidación"


# ─── Generador principal ─────────────────────────────────────────────────────

def generate_requisicion_pdf(req: dict) -> bytes:
    buf = io.BytesIO()
    cv  = rl_canvas.Canvas(buf, pagesize=letter)

    folio = req.get("folio") or f"REQ-{req.get('id', 0):04d}"
    cv.setTitle(f"Requisicion {folio}")
    cv.setAuthor("Sistema de Requisiciones ProHygiene")

    # Fondo de página
    _box(cv, 0, PH, PW, PH, fill=C_PAGE_BG)

    top = PH - MT   # cursor: parte superior disponible

    top = _header(cv, req, folio, top)  ;  top -= GAP
    top = _cards(cv, req, top)          ;  top -= GAP
    top = _items_table(cv, req, top, folio)    ;  top -= GAP
    just_h = _just_com_height(req)
    top = _ensure_space(cv, top, just_h, folio)
    top = _just_com(cv, req, top)       ;  top -= GAP
    top = _ensure_space(cv, top, TL_H, folio)
    top = _timeline(cv, req, top)

    _footer(cv, folio)
    cv.save()
    buf.seek(0)
    return buf.read()


def _advance_page(cv, folio):
    _footer(cv, folio)
    cv.showPage()
    _box(cv, 0, PH, PW, PH, fill=C_PAGE_BG)
    return PH - MT


def _ensure_space(cv, top, needed_height, folio):
    if top - needed_height < PAGE_BOTTOM_LIMIT:
        return _advance_page(cv, folio)
    return top


# ─── 1. HEADER ───────────────────────────────────────────────────────────────

def _header(cv, req, folio, top):
    H = 19 * mm
    _box(cv, ML, top, UW, H, stroke=C_HDR_BG, lw=1.1, r=5)

    # Empresa (izquierda)
    logo_x = ML + 6
    logo_top = top - 2
    logo_w = 34 * mm
    logo_h = 11 * mm
    try:
        cv.drawImage(
            LOGO_PATH,
            logo_x,
            logo_top - logo_h,
            width=logo_w,
            height=logo_h,
            preserveAspectRatio=True,
            mask="auto",
        )
    except Exception:
        _str(cv, logo_x, top - 3, "ProHygiene",
             font="Helvetica-Bold", size=13, color=C_HDR_BG)
    _str(cv, ML + 14, top - 29, "ENMANUEL, S.A. DE C.V.",
         font="Helvetica", size=6.5,
         color=C_GRAY2)
    _str(cv, ML + 14, top - 36,
         "Sistema interno de requisiciones",
         font="Helvetica", size=5.5,
         color=C_GRAY2)

    # Folio (centro)
    cx = ML + UW / 2
    _str(cv, cx, top - 4, "REQUISICIÓN",
         font="Helvetica", size=6.5,
         color=C_HDR_BG, align="center")
    _str(cv, cx, top - 4 - 6.5 - 2, folio,
         font="Helvetica-Bold", size=15,
         color=C_BLACK, align="center")

    # Badge estado (derecha)
    estado = str(req.get("estado", "liquidada")).lower()
    fc, bg, bd = _estado_style(estado)
    BW, BH = 30 * mm, 7 * mm
    bx  = ML + UW - BW - 5
    b_top = top - H / 2 + BH / 2
    _box(cv, bx, b_top, BW, BH, fill=bg, stroke=bd, lw=0.8, r=3)
    _str(cv, bx + BW / 2, b_top - (BH - 7) / 2,
         _estado_label(estado).upper(), font="Helvetica-Bold",
         size=7, color=fc, align="center")

    return top - H


# ─── 2. CARDS (3 columnas) ───────────────────────────────────────────────────

# Altura fija de la card.  Calculamos: franja(3mm) + título(5mm) + sep(2mm) + 4filas×(5.5+2+8.5+4)mm
# Cada fila label+valor: lsize=5.5 gap=2 vsize=8 padding_bajo=4 → 19.5pt ≈ 7mm
# 4 filas = 28mm  +  título 5mm  +  franja 3mm  +  padding top 3mm = 39mm → redondeamos a 44mm
CARD_H      = 66 * mm
CARD_FRANJA = 3 * mm    # franja de color top
CARD_PAD    = 4 * mm    # padding horizontal interior


def _cards(cv, req, top):
    GAP3 = 3 * mm
    CW   = (UW - GAP3 * 2) / 3

    for i, fn in enumerate([_card_info, _card_estado, _card_alertas]):
        cx = ML + i * (CW + GAP3)

        # Sombra/card blanca
        _box(cv, cx, top, CW, CARD_H,
             fill=C_WHITE, stroke=C_SEP, lw=0.7, r=4)
        _hline(cv, cx + 3, top - CARD_FRANJA / 2, CW - 6, color=C_PRI, lw=1.0)

        # Contenido de la card: top del contenido = top - franja - padding
        content_top = top - CARD_FRANJA - CARD_PAD
        fn(cv, req, cx + CARD_PAD, content_top, CW - CARD_PAD * 2)

    return top - CARD_H


def _card_header(cv, x, top, w, title):
    """Dibuja el título de la card y devuelve el top del contenido bajo él."""
    _str(cv, x, top, title,
         font="Helvetica-Bold", size=7.5, color=C_HDR_BG)
    sep_y = top - 7.5 - 2          # 2pt bajo la baseline del título
    _hline(cv, x, sep_y, w, color=C_SEP, lw=0.8)
    return sep_y - 3               # 3pt de aire bajo el separador


def _card_row(cv, x, top, label, value, *,
              vcolor=C_BLACK, lsize=5.5, vsize=8, gap=1.5, row_gap=5):
    """
    Dibuja label + value y devuelve el 'top' de la siguiente fila.
    - label: baseline en top - lsize
    - value: top en top - lsize - gap  →  baseline en top - lsize - gap - vsize
    - siguiente fila: top - lsize - gap - vsize - row_gap
    """
    _str(cv, x, top, label.upper(),
         font="Helvetica", size=lsize, color=C_GRAY2)
    val_top = top - lsize - gap
    _str(cv, x, val_top, str(value),
         font="Helvetica-Bold", size=vsize, color=vcolor, max_ch=28)
    return val_top - vsize - row_gap


def _card_info(cv, req, x, top, w):
    cur = _card_header(cv, x, top, w, "Información general")
    ROW_GAP = 5
    receptor_designado = req.get("receptor_designado_nombre") or "—"
    receptor_rol = req.get("receptor_designado_rol")
    if receptor_rol:
        receptor_designado = f"{receptor_designado} ({receptor_rol})"
    for lbl, val in [
        ("Cliente",        req.get("cliente") or "—"),
        ("Código cliente", str(req.get("codigo_cliente") or "—")),
        ("Ruta principal", req.get("ruta") or "—"),
        ("Solicitante",    req.get("solicitante_nombre") or "—"),
        ("Recibe",         receptor_designado),
    ]:
        cur = _card_row(cv, x, cur, lbl, val, row_gap=ROW_GAP)


def _card_estado(cv, req, x, top, w):
    cur = _card_header(cv, x, top, w, "Estado liquidación")

    # ESTADO label
    _str(cv, x, cur, "ESTADO", font="Helvetica", size=5.5, color=C_GRAY2)
    cur -= 5.5 + 1.5    # bajo el label

    # Badge de estado
    estado = str(req.get("estado", "liquidada")).lower()
    fc, bg, bd = _estado_style(estado)
    BW, BH = w * 0.65, 6.5 * mm
    _box(cv, x, cur, BW, BH, fill=bg, stroke=bd, lw=0.6, r=3)
    _str(cv, x + BW / 2, cur - (BH - 7) / 2,
         estado, font="Helvetica-Bold", size=7, color=fc, align="center")
    cur -= BH + 4       # bajo el badge

    ROW_GAP = 5
    for lbl, val, col in [
        ("Por",          req.get("liquidado_por_nombre") or "—",        C_BLACK),
        ("Recibido por", (req.get("recibido_por_nombre")
                          or req.get("tecnico_nombre") or "—"),         C_BLACK),
        ("Hora firma",   _fmt(req.get("recibido_at")
                              or req.get("delivered_at")),              C_BLACK),
        ("Ref ProKey",   "No aplica" if req.get("prokey_not_applicable") else (req.get("prokey_ref") or "Pendiente"),
                         C_BLACK if req.get("prokey_not_applicable") or req.get("prokey_ref") else C_AMBER),
    ]:
        cur = _card_row(cv, x, cur, lbl, val, vcolor=col, row_gap=ROW_GAP)


def _card_alertas(cv, req, x, top, w):
    cur = _card_header(cv, x, top, w, "Alertas de conciliación")

    items = req.get("items", [])
    all_al = []
    for it in items:
        all_al.extend(_parse_alerts(it.get("liquidation_alerts")))
    high  = sum(1 for a in all_al
                if any(k in a for k in ("FALTANTE", "INCOMPLETO", "EXCEDENTE")))
    total = len(all_al)

    ROW_GAP = 5
    cur = _card_row(cv, x, cur, "Total",
                    f"{total} detectadas" if total else "0 detectadas",
                    vcolor=C_RED if total else C_GREEN,
                    row_gap=ROW_GAP)
    cur = _card_row(cv, x, cur, "Alta severidad",
                    str(high),
                    vcolor=C_RED if high else C_GREEN,
                    row_gap=ROW_GAP)

    _str(cv, x, cur, "TIPOS FRECUENTES",
         font="Helvetica", size=5.5, color=C_GRAY2)
    cur -= 5.5 + 1.5
    if all_al:
        cnt    = Counter(all_al)
        top_k  = cnt.most_common(1)[0][0]
        top_lb = ALERT_MAP.get(top_k, top_k)
        _str(cv, x, cur, top_lb, font="Helvetica-Bold",
             size=8, color=C_RED, max_ch=24)
    else:
        _str(cv, x, cur, "Ninguno", font="Helvetica-Bold",
             size=8, color=C_GREEN)


# ─── 3. TABLA DE ÍTEMS ───────────────────────────────────────────────────────

def _table_columns(req):
    qty_label = "Solicitado" if str(req.get("estado", "")).lower() in {"aprobada", "preparado"} else "Entregado"
    return [
        ("Descripción",  0.255, "left"),
        (qty_label,      0.07,  "center"),
        ("Tipo",         0.09,  "center"),
        ("Contexto",     0.10,  "center"),
        ("Usado",        0.065, "center"),
        ("No usado",     0.065, "center"),
        ("Regresa",      0.065, "center"),
        ("DIF",          0.075, "center"),
        ("Ingreso PK",   0.075, "center"),
        ("Alertas",      0.135, "center"),
    ]

HDR_H  = 8   * mm   # altura cabecera tabla
ROW_H  = 11  * mm   # altura base por fila (1 línea de descripción)
NOTE_H = 4.5 * mm   # altura extra si tiene nota
DESC_LINE_H = 7      # pt adicionales por línea extra en descripción
# Chars aprox que caben en 1 línea de la col Descripción (ancho ≈ 0.255 × UW)
_DESC_CHARS = 26


def _desc_lines(text):
    """Divide la descripción en líneas que caben en la columna."""
    return _wrap(str(text), max_ch=_DESC_CHARS)


def _row_height(item):
    """Calcula la altura real de la fila según líneas de descripción y nota."""
    desc_l  = len(_desc_lines(item.get("descripcion", "")))
    extra_l = max(0, desc_l - 1) * DESC_LINE_H   # líneas extra más allá de la 1ª
    nota_h  = NOTE_H if item.get("nota_liquidacion") else 0
    return ROW_H + extra_l + nota_h


def _draw_items_table_chunk(cv, req, items, top):
    cols    = _table_columns(req)
    widths  = [UW * f for _, f, _ in cols]
    x0      = ML

    rows_h  = [_row_height(it) for it in items]
    T_H     = HDR_H + sum(rows_h)

    # Fondo blanco de toda la tabla
    _box(cv, x0, top, UW, T_H,
         fill=C_WHITE, stroke=C_SEP, lw=0.8, r=4)

    # ── Cabecera ──
    _hline(cv, x0 + 1, top - HDR_H, UW - 2, color=C_GRAY2, lw=1.1)

    cx = x0
    for (lbl, _, align), w in zip(cols, widths):
        tx = cx + w / 2 if align == "center" else cx + 3
        _str(cv, tx, top - (HDR_H - 7) / 2,
             lbl, font="Helvetica-Bold", size=6.5,
             color=C_BLACK, align=align)
        cx += w

    cur_top = top - HDR_H

    # ── Filas de datos ──
    for i, item in enumerate(items):
        rh     = rows_h[i]
        nota   = item.get("nota_liquidacion")
        alerts = _parse_alerts(item.get("liquidation_alerts"))

        # Fondo alternado
        if i % 2 == 0:
            _box(cv, x0 + 1, cur_top, UW - 2, rh, fill=C_TBL_ALT)

        # Separador inferior
        _hline(cv, x0, cur_top - rh, UW, color=C_SEP, lw=0.3)

        # Altura de la zona de datos (sin nota)
        data_h  = rh - (NOTE_H if nota else 0)
        row_mid = cur_top - data_h / 2   # centro vertical de la zona de datos

        dif_lbl, dif_fc, dif_bg, dif_bd = _dif_chip(item)
        mode_s  = (item.get("liquidation_mode") or "—").capitalize()
        ctx_s   = (item.get("contexto_operacion") or "—").replace("_", " ").title()
        pk_qty = item.get("pk_ingreso_qty")
        pk_val = "—" if pk_qty is None else f"{pk_qty:g}"
        al_txt  = (ALERT_MAP.get(alerts[0], alerts[0])
                   if alerts else "Sin alertas")
        al_col  = C_RED if alerts else C_GRAY2
        qty_ref = (
            item.get("cantidad_solicitada")
            if str(req.get("estado", "")).lower() in {"aprobada", "preparado"}
            else item.get("cantidad_entregada")
        )

        row_vals = [
            f"{item.get('descripcion', '—')}{' [Para Demo]' if item.get('es_demo') else ''}",
            str(qty_ref or 0),
            mode_s, ctx_s,
            str(item.get("cantidad_usada")    or 0),
            str(item.get("cantidad_no_usada") or 0),
            str(item.get("cantidad_retorna")  or 0),
            dif_lbl,
            pk_val,
            al_txt,
        ]

        cx = x0
        for j, ((_, _, align), w, val) in enumerate(zip(cols, widths, row_vals)):
            mid_x = cx + w / 2

            if j == 0:   # Descripción — wrap a múltiples líneas
                d_lines = _desc_lines(str(val))
                # Centrar el bloque verticalmente en la zona de datos
                block_h = len(d_lines) * (7.5 + 2) - 2
                line_top = row_mid + block_h / 2
                for dl in d_lines:
                    _str(cv, cx + 3, line_top, dl,
                         font="Helvetica-Bold", size=7.5, color=C_BLACK)
                    line_top -= 7.5 + 2   # size + interlineado

            elif j == 7: # DIF chip
                cw, ch = w - 6, 5 * mm
                _box(cv, cx + 3, row_mid + ch / 2, cw, ch,
                     fill=dif_bg, stroke=dif_bd, lw=0.8, r=2)
                _str(cv, mid_x, row_mid + ch / 2 - (ch - 7) / 2,
                     dif_lbl, font="Helvetica-Bold",
                     size=7, color=dif_fc, align="center")

            elif j == 9: # Alertas
                _str(cv, mid_x, row_mid + 3,
                     al_txt, font="Helvetica", size=6,
                     color=C_BLACK, align="center", max_ch=20)

            elif j == 3: # Contexto
                _str(cv, mid_x, row_mid + 3,
                     str(val), font="Helvetica", size=6,
                     color=C_BLACK, align="center", max_ch=14)

            elif j == 2: # Tipo
                _str(cv, mid_x, row_mid + 3,
                     str(val), font="Helvetica-Bold", size=6.5,
                     color=C_GRAY1, align="center", max_ch=12)

            else:
                col = C_GRAY2 if (j == 8 and pk_val == "—") else C_GRAY1
                _str(cv, mid_x, row_mid + 3,
                     str(val), font="Helvetica", size=7.5,
                     color=col, align="center")
            cx += w

        # Nota del ítem
        if nota:
            note_top = cur_top - data_h - 1
            _str(cv, x0 + 5, note_top,
                 f"↳ {str(nota)[:110]}",
                 font="Helvetica-Oblique", size=5.5, color=C_GRAY2)

        cur_top -= rh

    # Líneas verticales de columnas
    cv.setStrokeColor(C_SEP)
    cv.setLineWidth(0.3)
    cx = x0
    for w in widths[:-1]:
        cx += w
        cv.line(cx, cur_top, cx, top - HDR_H)

    return cur_top


def _items_table(cv, req, top, folio):
    items = req.get("items", [])
    if not items:
        return top

    index = 0
    total = len(items)
    while index < total:
        available_h = top - PAGE_BOTTOM_LIMIT
        if available_h <= HDR_H + ROW_H:
            top = _advance_page(cv, folio)
            available_h = top - PAGE_BOTTOM_LIMIT

        chunk = []
        used_h = HDR_H
        while index < total:
            row_h = _row_height(items[index])
            if chunk and used_h + row_h > available_h:
                break
            chunk.append(items[index])
            used_h += row_h
            index += 1
            if used_h >= available_h:
                break

        if not chunk:
            chunk.append(items[index])
            index += 1

        top = _draw_items_table_chunk(cv, req, chunk, top)
        if index < total:
            top = _advance_page(cv, folio)

    return top


# ─── 4. JUSTIFICACIÓN + COMENTARIO ──────────────────────────────────────────

JUST_HDR_H = 8  * mm
JUST_PAD   = 4  * mm
JUST_LINE_H = 12.5   # pt por línea de texto (size 7 + interlineado)
JUST_MIN_H  = 18 * mm
JUST_MAX_LINES = 6


def _just_height(text):
    """Altura dinámica del panel según cantidad de líneas de contenido."""
    lines = _wrap(str(text), max_ch=50)
    n = min(len(lines), JUST_MAX_LINES) if lines else 1
    return JUST_HDR_H + JUST_PAD + n * JUST_LINE_H + JUST_PAD


def _just_com_height(req):
    texts = [
        req.get("justificacion") or "—",
        req.get("comentario_liquidacion") or "—",
    ]
    h = max(_just_height(text) for text in texts)
    return max(h, JUST_MIN_H)


def _just_com(cv, req, top):
    HALF = (UW - 3 * mm) / 2

    texts = [
        ("Justificación",             req.get("justificacion") or "—"),
        ("Comentario de liquidación", req.get("comentario_liquidacion") or "—"),
    ]
    # Altura = máximo entre los dos paneles para que queden iguales
    h = max(_just_height(t) for _, t in texts)
    h = max(h, JUST_MIN_H)

    for (label, text), rx in zip(texts, [ML, ML + HALF + 3 * mm]):
        # Card blanca
        _box(cv, rx, top, HALF, h,
             fill=C_WHITE, stroke=C_SEP, lw=0.7, r=4)
        _str(cv, rx + JUST_PAD, top - (JUST_HDR_H - 7.5) / 2,
             label, font="Helvetica-Bold", size=7.5, color=C_HDR_BG)
        _hline(cv, rx + JUST_PAD, top - JUST_HDR_H,
               HALF - JUST_PAD * 2, color=C_SEP, lw=0.8)

        # Texto con wrap dinámico
        is_empty = str(text).strip() in ("", "—")
        lines    = _wrap(str(text), max_ch=50)
        cv.setFont("Helvetica", 7)
        cv.setFillColor(C_GRAY2 if is_empty else C_GRAY1)
        # Primera línea arranca bajo la franja + padding
        line_top = top - JUST_HDR_H - JUST_PAD
        for line in lines[:JUST_MAX_LINES]:
            cv.drawString(rx + JUST_PAD, line_top - 7, line)
            line_top -= JUST_LINE_H

    return top - h


# ─── 5. TIMELINE ────────────────────────────────────────────────────────────

TL_H       = 28 * mm
TL_HDR_H   = 8  * mm
TL_PAD     = 4  * mm


def _timeline(cv, req, top):
    events = []
    for lbl, actor_key, ts_key in [
        ("Req. creada",    "solicitante_nombre", "created_at"),
        ("Req. aprobada",  "aprobador_nombre",   "approved_at"),
        ("Prep. bodega",   "preparador_nombre", "prepared_at"),
        ("Entregada",      "jefe_bodega_nombre", "delivered_at"),
        ("Recibido firma", "recibido_por_nombre","recibido_at"),
        (_timeline_liquidation_label(req), "liquidado_por_nombre","liquidated_at"),
    ]:
        ts = (req.get(ts_key)
              or (req.get("delivered_at") if ts_key == "recibido_at" else None))
        if ts:
            actor = (req.get(actor_key)
                     or req.get("tecnico_nombre") or "—")
            events.append((lbl, actor, ts))

    if not events:
        return top

    _box(cv, ML, top, UW, TL_H,
         fill=C_WHITE, stroke=C_SEP, lw=0.7, r=4)

    _str(cv, ML + TL_PAD, top - (TL_HDR_H - 7.5) / 2,
         "Línea de tiempo del flujo",
         font="Helvetica-Bold", size=7.5, color=C_HDR_BG)
    _hline(cv, ML + TL_PAD, top - TL_HDR_H,
           UW - TL_PAD * 2, color=C_SEP, lw=0.8)

    # Zona del timeline
    tz_top = top - TL_HDR_H    # top de la zona gráfica
    tz_h   = TL_H - TL_HDR_H  # altura disponible
    line_y = tz_top - tz_h * 0.45  # Y de la línea horizontal

    n     = len(events)
    step  = UW / n
    x1    = ML + step * 0.5
    x2    = ML + step * (n - 0.5)

    # Línea base
    cv.setStrokeColor(C_PRI)
    cv.setLineWidth(1.5)
    cv.line(x1, line_y, x2, line_y)

    R = 5  # radio del nodo

    for i, (lbl, actor, ts) in enumerate(events):
        nx = ML + step * (i + 0.5)

        # Nodo
        _box(cv, nx - R, line_y + R, R * 2, R * 2,
             fill=C_WHITE, stroke=C_PRI, lw=0.9, r=R)
        _str(cv, nx, line_y + R - (R * 2 - 7) / 2,
             str(i + 1), font="Helvetica-Bold",
             size=6, color=C_PRI, align="center")

        # Texto encima del nodo: label
        lbl_top = line_y + R + 3 + 6    # 3pt sobre el nodo, texto size 6
        _str(cv, nx, lbl_top, lbl,
             font="Helvetica-Bold", size=6,
             color=C_HDR_BG, align="center", max_ch=18)

        # Texto debajo del nodo: actor y fecha
        actor_top = line_y - R - 2       # 2pt bajo el nodo
        _str(cv, nx, actor_top, str(actor),
             font="Helvetica", size=5,
             color=C_GRAY2, align="center", max_ch=20)

        # Fecha debajo del actor
        fecha_top = actor_top - 5 - 2    # size 5, luego 2pt gap
        _str(cv, nx, fecha_top, _fmt(ts),
             font="Helvetica", size=5,
             color=C_BLACK, align="center")

    return top - TL_H


# ─── FOOTER ──────────────────────────────────────────────────────────────────

def _footer(cv, folio):
    y_line = MB + 7   # Y de la línea separadora
    _hline(cv, ML, y_line, UW, color=C_PRI_BORDER, lw=0.5)

    ts = _fmt(datetime.now().isoformat())
    # Texto baseline = y_line - gap
    cv.setFont("Helvetica", 5.5)
    cv.setFillColor(C_GRAY2)
    cv.drawString(ML, y_line - 6, f"Documento generado: {ts}")
    cv.drawRightString(ML + UW, y_line - 6,
                       f"Sistema de Requisiciones ProHygiene  |  {folio}")


# ─── PRUEBA LOCAL ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    sample = {
        "id": 2, "folio": "REQ-0002", "estado": "liquidada",
        "created_at":    "2026-03-03 14:48:41",
        "approved_at":   "2026-03-03 14:48:47",
        "delivered_at":  "2026-03-03 14:48:56",
        "recibido_at":   "2026-03-03 14:48:56",
        "liquidated_at": "2026-03-03 15:05:13",
        "cliente":             "Cliente C",
        "codigo_cliente":      "125",
        "ruta":                "RD03",
        "solicitante_nombre":  "Administrador",
        "aprobador_nombre":    "Administrador",
        "jefe_bodega_nombre":  "Administrador",
        "recibido_por_nombre": "Julio Gonzalez",
        "tecnico_nombre":      None,
        "prokey_ref":          None,
        "justificacion": (
            "Lorem ipsum dolor sit amet consectetur adipiscing elit "
            "eu tortor augue, fringilla enim et scelerisque posuere "
            "placerat inceptos cubilia curae."
        ),
        "comentario_liquidacion": None,
        "items": [
            {
                "descripcion":        "ALFOMBRA 2X3 AZUL",
                "cantidad_entregada": 2,
                "cantidad_usada":     2,
                "cantidad_no_usada":  0,
                "cantidad_retorna":   2,
                "liquidation_mode":   "RETORNABLE",
                "contexto_operacion": "instalacion_inicial",
                "prokey_ref":         "2",
                "liquidation_alerts": [],
                "nota_liquidacion":   None,
            },
            {
                "descripcion":        "SPRAY AROM FRUTAL",
                "cantidad_entregada": 2,
                "cantidad_usada":     1,
                "cantidad_no_usada":  1,
                "cantidad_retorna":   1,
                "liquidation_mode":   "CONSUMIBLE",
                "contexto_operacion": "reposicion",
                "prokey_ref":         None,
                "liquidation_alerts": [],
                "nota_liquidacion":   None,
            },
        ],
    }

    out = "/mnt/user-data/outputs/requisicion_REQ0002_v4.pdf"
    with open(out, "wb") as f:
        f.write(generate_requisicion_pdf(sample))
    print(f"✓ PDF → {out}")
