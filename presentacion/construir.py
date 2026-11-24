# -*- coding: utf-8 -*-
"""Arma la presentacion del proyecto integrador sobre la plantilla institucional."""
import copy, math, os, sys
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from contenido import SLIDES

BASE = os.path.dirname(os.path.abspath(__file__))
ORIG = os.path.join(BASE, "plantilla.pptx")
SAL  = os.path.join(BASE, "proyecto_integrador.pptx")

SERIF = "Times New Roman"
NEGRO = RGBColor(0x00, 0x00, 0x00)
BLANCO = RGBColor(0xFF, 0xFF, 0xFF)
GRIS = RGBColor(0x59, 0x59, 0x59)

L_TITULO, L_UNO, L_DOS, L_TRES, L_BLANCO, L_CONTRA = range(6)


# --- utilidades de bajo nivel -------------------------------------------------

def quitar_diapositivas(prs, conservar):
    """Deja en el mazo solo las diapositivas cuyos indices se indican."""
    lst = prs.slides._sldIdLst
    ids = list(lst)
    for i, sld in enumerate(ids):
        if i not in conservar:
            prs.part.drop_rel(sld.rId)
            lst.remove(sld)


def mover_al_final(prs, indice):
    """Traslada una diapositiva al final del mazo."""
    lst = prs.slides._sldIdLst
    el = list(lst)[indice]
    lst.remove(el)
    lst.append(el)


def sin_vineta(parrafo):
    """Suprime la vineta heredada del diseno en un parrafo."""
    pPr = parrafo._p.get_or_add_pPr()
    for t in ("a:buChar", "a:buAutoNum", "a:buNone"):
        for e in pPr.findall(qn(t)):
            pPr.remove(e)
    pPr.append(pPr.makeelement(qn("a:buNone"), {}))


def numero_pagina(prs, slide, total):
    """Copia el marcador de numero de pagina del diseno a la diapositiva."""
    for ph in slide.slide_layout.placeholders:
        if ph.placeholder_format.idx != 12:
            continue
        nuevo = copy.deepcopy(ph._element)
        slide.shapes._spTree.append(nuevo)
        sp = slide.shapes[-1]
        tf = sp.text_frame
        p = tf.paragraphs[0]._p
        for hijo in list(p):
            if hijo.tag in (qn("a:r"), qn("a:fld"), qn("a:br")):
                p.remove(hijo)
        fld = p.makeelement(qn("a:fld"), {
            "id": "{D0B5107D-F546-44DA-835A-BAFFDBE9CB93}", "type": "slidenum"})
        rPr = fld.makeelement(qn("a:rPr"), {"lang": "es-MX"})
        t = fld.makeelement(qn("a:t"), {})
        t.text = "1"
        fld.append(rPr); fld.append(t)
        p.append(fld)
        r = p.makeelement(qn("a:r"), {})
        rPr2 = r.makeelement(qn("a:rPr"), {"lang": "es-MX", "dirty": "0"})
        t2 = r.makeelement(qn("a:t"), {})
        t2.text = " /%d" % total
        r.append(rPr2); r.append(t2)
        p.append(r)
        return


def poner_titulo(slide, texto, lineas=1, ancho=7.6, tope=40):
    """Escribe el titulo ajustando el tamano a la caja disponible."""
    pt = int(min(tope, lineas * ancho * 72.0 / (0.52 * max(1, len(texto)))))
    pt = max(24, pt)
    p = slide.shapes.title.text_frame.paragraphs[0]
    r = p.add_run()
    r.text = texto
    r.font.size = Pt(pt)
    return pt


def encajar(ruta, x, y, w, h):
    """Devuelve posicion y tamano de la imagen centrada dentro del recuadro."""
    from PIL import Image
    iw, ih = Image.open(ruta).size
    asp = iw / float(ih)
    if w / h > asp:
        hh = h; ww = h * asp
    else:
        ww = w; hh = w / asp
    return x + (w - ww) / 2.0, y + (h - hh) / 2.0, ww, hh


def caja(slide, x, y, w, h):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = 0
    tf.margin_top = tf.margin_bottom = 0
    return tb


# --- composicion de texto -----------------------------------------------------

ANCHO_CAR = {0: 1.00, 1: 1.08, 2: 1.16}   # factor de sangria por nivel


def alto_estimado(cuerpo, ancho, pt):
    """Estima el alto en pulgadas que ocupara el bloque de texto."""
    car_pulg = 14.3 * (11.0 / pt)          # caracteres por pulgada, Times
    alto_lin = pt * 1.22 / 72.0
    total = 0.0
    for nivel, texto in cuerpo:
        n = 0 if nivel == "B" else nivel
        util = (ancho - 0.30 * n) * car_pulg
        lineas = max(1, math.ceil(len(texto) / util))
        total += lineas * alto_lin
        total += (0.10 if nivel == "B" else 0.05)
    return total


def escribir(tb, cuerpo, pt):
    tf = tb.text_frame
    primero = True
    for nivel, texto in cuerpo:
        p = tf.paragraphs[0] if primero else tf.add_paragraph()
        primero = False
        negrita = (nivel == "B")
        n = 0 if negrita else nivel
        p.level = 0
        sin_vineta(p)
        pPr = p._p.get_or_add_pPr()
        pPr.set("marL", str(Emu(Inches(0.30 * n + (0.0 if negrita else 0.22))).emu))
        pPr.set("indent", str(-Emu(Inches(0.22)).emu if not negrita else "0"))
        if not negrita:
            bu = pPr.makeelement(qn("a:buFont"), {"typeface": "Arial"})
            bc = pPr.makeelement(qn("a:buChar"), {"char": "•" if n == 0 else "–"})
            for e in pPr.findall(qn("a:buNone")):
                pPr.remove(e)
            pPr.append(bu); pPr.append(bc)
        p.space_before = Pt(6 if negrita else 2)
        p.space_after = Pt(0)
        r = p.add_run()
        r.text = texto
        r.font.name = SERIF
        r.font.size = Pt(pt)
        r.font.bold = negrita
        r.font.color.rgb = NEGRO


def pie(slide, x, y, w, texto, pt=10):
    tb = caja(slide, x, y, w, 0.4)
    p = tb.text_frame.paragraphs[0]
    r = p.add_run(); r.text = texto
    r.font.name = SERIF; r.font.size = Pt(pt); r.font.italic = True
    r.font.color.rgb = GRIS
    return tb


# --- tablas -------------------------------------------------------------------

def tabla(slide, x, y, w, encabezados, filas, pt=11):
    nf, nc = len(filas) + 1, len(encabezados)
    alto_enc, alto_fila = 0.30, 0.27
    h = alto_enc + alto_fila * (nf - 1)
    gf = slide.shapes.add_table(nf, nc, Inches(x), Inches(y), Inches(w), Inches(h))
    tabla_ = gf.table
    tabla_.first_row = True
    tabla_.horz_banding = False
    # ancho: primera columna mas amplia
    resto = (w - w * 0.34) / max(1, nc - 1) if nc > 1 else w
    tabla_.columns[0].width = Inches(w * 0.34 if nc > 1 else w)
    for j in range(1, nc):
        tabla_.columns[j].width = Inches(resto)
    tabla_.rows[0].height = Inches(alto_enc)
    for i in range(1, nf):
        tabla_.rows[i].height = Inches(alto_fila)

    def celda(i, j, texto, negrita, color, fondo, alin):
        c = tabla_.cell(i, j)
        c.margin_left = Inches(0.08); c.margin_right = Inches(0.08)
        c.margin_top = Inches(0.02); c.margin_bottom = Inches(0.02)
        c.vertical_anchor = MSO_ANCHOR.MIDDLE
        c.fill.solid(); c.fill.fore_color.rgb = fondo
        p = c.text_frame.paragraphs[0]
        p.alignment = alin
        r = p.add_run(); r.text = texto
        r.font.name = SERIF; r.font.size = Pt(pt)
        r.font.bold = negrita; r.font.color.rgb = color

    for j, t in enumerate(encabezados):
        celda(0, j, t, True, BLANCO, NEGRO,
              PP_ALIGN.LEFT if j == 0 else PP_ALIGN.CENTER)
    for i, fila in enumerate(filas, start=1):
        fondo = BLANCO if i % 2 else RGBColor(0xF2, 0xF2, 0xF2)
        for j, t in enumerate(fila):
            celda(i, j, t, False, NEGRO, fondo,
                  PP_ALIGN.LEFT if j == 0 else PP_ALIGN.CENTER)
    return h


# --- armado -------------------------------------------------------------------

def main():
    prs = Presentation(ORIG)
    n_orig = len(prs.slides._sldIdLst)
    quitar_diapositivas(prs, {0, n_orig - 1})

    # portada + contenido + cuerpo + referencias + contraportada
    total = 1 + 1 + len(SLIDES) + 1 + 1

    # ---- portada
    port = prs.slides[0]
    titulo_sh = port.shapes.title
    sub_sh = port.placeholders[1]
    etiqueta = fecha = None
    for sh in port.shapes:
        if sh.shape_type != 17 or not sh.has_text_frame:
            continue
        if Emu(sh.top).inches < 4:
            etiqueta = sh
        else:
            fecha = sh
    cambios = [
        (titulo_sh, "Predicción de mortalidad hospitalaria en el conjunto SUPPORT2", 24),
        (sub_sh, "Mtro. José Guadalupe Méndez Pérez", 16),
        (etiqueta, "Proyecto Integrador \u2013 Realidad Virtual", 15),
        (fecha, "Noviembre 2026", 12),
    ]
    for sh, texto, tam in cambios:
        if sh is None:
            continue
        p = sh.text_frame.paragraphs[0]
        for hijo in list(p._p):
            if hijo.tag in (qn("a:r"), qn("a:br")):
                p._p.remove(hijo)
        for extra_p in sh.text_frame.paragraphs[1:]:
            extra_p._p.getparent().remove(extra_p._p)
        r = p.add_run()
        r.text = texto
        r.font.size = Pt(tam)

    # ---- contenido
    s = prs.slides.add_slide(prs.slide_layouts[L_UNO])
    poner_titulo(s, "CONTENIDO DE LA PRESENTACIÓN", lineas=1, ancho=11.2, tope=40)
    cuerpo = s.placeholders[1].text_frame
    cuerpo.word_wrap = True
    temas = ["Introducción y planteamiento", "Objetivos", "Metodología",
             "Origen y explicación de los datos", "Modelo y algoritmos aplicados",
             "Resultados y evaluaciones", "Recomendaciones de mejora", "Conclusiones"]
    primero = True
    for i, t in enumerate(temas, 1):
        p = cuerpo.paragraphs[0] if primero else cuerpo.add_paragraph()
        primero = False
        sin_vineta(p)
        p.space_after = Pt(10)
        r = p.add_run(); r.text = "%d.   %s" % (i, t)
        r.font.name = "Verdana"; r.font.size = Pt(18); r.font.color.rgb = NEGRO
    numero_pagina(prs, s, total)

    # ---- cuerpo
    for tipo, titulo, bloque, extra in SLIDES:
        if tipo == "diagrama":
            sl = prs.slides.add_slide(prs.slide_layouts[L_TRES])
            poner_titulo(sl, titulo, lineas=1, ancho=7.5, tope=34)
            for ph in list(sl.placeholders):
                if ph.placeholder_format.idx == 1:
                    ph._element.getparent().remove(ph._element)
            ix, iy, iw, ih = encajar(*extra)
            sl.shapes.add_picture(extra[0], Inches(ix), Inches(iy),
                                  width=Inches(iw), height=Inches(ih))
        elif tipo == "figura":
            sl = prs.slides.add_slide(prs.slide_layouts[L_DOS])
            t = sl.shapes.title
            t.left, t.top, t.width, t.height = (Inches(0.30), Inches(0.60),
                                                Inches(7.67), Inches(1.24))
            poner_titulo(sl, titulo, lineas=2, ancho=7.4, tope=40)
            for ph in list(sl.placeholders):
                if ph.placeholder_format.idx in (1, 2):
                    ph._element.getparent().remove(ph._element)
            x, y, w = 0.55, 2.05, 6.10
            pt = 16
            while alto_estimado(bloque, w, pt) > 4.25 and pt > 11:
                pt -= 1
            tb = caja(sl, x, y, w, 4.3)
            escribir(tb, bloque, pt)
            ix, iy, iw, ih = encajar(*extra)
            sl.shapes.add_picture(extra[0], Inches(ix), Inches(iy),
                                  width=Inches(iw), height=Inches(ih))
        else:
            sl = prs.slides.add_slide(prs.slide_layouts[L_TRES])
            poner_titulo(sl, titulo, lineas=1, ancho=7.5, tope=34)
            for ph in list(sl.placeholders):
                if ph.placeholder_format.idx == 1:
                    ph._element.getparent().remove(ph._element)
            x, y, w = 0.92, 1.90, 11.50
            tope = 6.25
            if extra and extra[0] == "tabla":
                _, enc, filas, nota = extra
                h_tab = 0.30 + 0.27 * len(filas) + (0.30 if nota else 0.0)
                disp = tope - y - h_tab - 0.28
            else:
                disp = tope - y
            pt = 18
            while alto_estimado(bloque, w, pt) > disp and pt > 12:
                pt -= 1
            if extra and extra[0] == "tabla":
                sobra = (tope - y) - (alto_estimado(bloque, w, pt) + 0.26 + h_tab)
                y += max(0.0, sobra) / 2.0
            tb = caja(sl, x, y, w, disp)
            escribir(tb, bloque, pt)
            if extra and extra[0] == "tabla":
                _, enc, filas, nota = extra
                ancho_t = 10.6 if len(enc) <= 4 else 11.5
                xt = (13.333 - ancho_t) / 2
                yt = y + alto_estimado(bloque, w, pt) + 0.26
                h = tabla(sl, xt, yt, ancho_t, enc, filas,
                          pt=11 if len(enc) <= 5 else 10)
                if nota:
                    pie(sl, xt, yt + h + 0.08, ancho_t, nota, pt=10)
        numero_pagina(prs, sl, total)

    # ---- referencias
    sl = prs.slides.add_slide(prs.slide_layouts[L_DOS])
    t = sl.shapes.title
    t.left, t.top, t.width, t.height = (Inches(0.30), Inches(0.60),
                                        Inches(7.67), Inches(1.24))
    poner_titulo(sl, "Referencias", lineas=2, ancho=7.4, tope=40)
    for ph in list(sl.placeholders):
        if ph.placeholder_format.idx in (1, 2):
            ph._element.getparent().remove(ph._element)
    refs = [
        "Knaus, W. A., Harrell, F. E., Lynn, J., & Connors, A. F. (2000). Study to Understand "
        "Prognoses and Preferences for Outcomes and Risks of Treatments (SUPPORT) "
        "[Conjunto de datos]. Inter-university Consortium for Political and Social Research. "
        "https://doi.org/10.3886/ICPSR02957.v2",
        "Knaus, W. A., Harrell, F. E., Lynn, J., Goldman, L., Phillips, R. S., & "
        "Connors, A. F. (1995). The SUPPORT prognostic model: Objective estimates of survival "
        "for seriously ill hospitalized adults. Annals of Internal Medicine, 122(3), 191\u2013203.",
        "Dem\u0161ar, J. (2006). Statistical comparisons of classifiers over multiple data sets. "
        "Journal of Machine Learning Research, 7, 1\u201330.",
        "Pedregosa, F., Varoquaux, G., Gramfort, A., y otros. (2011). Scikit-learn: Machine "
        "learning in Python. Journal of Machine Learning Research, 12, 2825\u20132830.",
    ]
    tb = caja(sl, 0.60, 2.05, 12.10, 4.40)
    primero = True
    for ref in refs:
        p = tb.text_frame.paragraphs[0] if primero else tb.text_frame.add_paragraph()
        primero = False
        sin_vineta(p)
        pPr = p._p.get_or_add_pPr()
        pPr.set("marL", str(Emu(Inches(0.35)).emu))
        pPr.set("indent", str(-Emu(Inches(0.35)).emu))
        p.space_after = Pt(8)
        r = p.add_run(); r.text = ref
        r.font.name = SERIF; r.font.size = Pt(13); r.font.color.rgb = NEGRO
    numero_pagina(prs, sl, total)

    # ---- contraportada al final
    mover_al_final(prs, 1)
    contra = prs.slides[len(prs.slides) - 1]
    for sh in contra.shapes:
        if sh.has_text_frame and "GRACIAS" in sh.text_frame.text:
            tf = sh.text_frame
            p = tf.paragraphs[0]
            for hijo in list(p._p):
                if hijo.tag in (qn("a:r"), qn("a:br")):
                    p._p.remove(hijo)
            r = p.add_run(); r.text = "GRACIAS POR SU ATENCIÓN"

    prs.save(SAL)
    print("diapositivas:", len(prs.slides), "->", SAL)


if __name__ == "__main__":
    main()
