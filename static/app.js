let itemCount = 1;

function normalizeSearchText(value) {
    return String(value || "")
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .toLowerCase()
        .trim();
}

function applySelectFilter(select, rawTerm) {
    if (!select) return;
    const term = normalizeSearchText(rawTerm);
    const options = Array.from(select.options || []);
    for (const [index, option] of options.entries()) {
        if (index === 0) {
            option.hidden = false;
            continue;
        }
        const label = normalizeSearchText(option.textContent);
        const matches = !term || label.includes(term) || option.selected;
        option.hidden = !matches;
    }
}

function initSearchableSelects(root = document) {
    const inputs = root.querySelectorAll("[data-select-search]");
    for (const input of inputs) {
        const targetId = input.getAttribute("data-select-search");
        if (!targetId) continue;
        const select = document.getElementById(targetId);
        if (!select) continue;
        applySelectFilter(select, input.value);
        input.addEventListener("input", () => applySelectFilter(select, input.value));
    }
}

function escapeHtml(text) {
    const value = String(text ?? "");
    return value
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
}

function fmtQty(value) {
    if (value === null || value === undefined || Number.isNaN(Number(value))) return "-";
    return Number(value).toLocaleString("es-ES", { maximumFractionDigits: 2 });
}

function fmtDateTime(value) {
    if (!value) return "-";
    const raw = String(value).trim();
    const match = raw.match(/^(\d{4})-(\d{2})-(\d{2})[T\s](\d{2}):(\d{2}):(\d{2})/);
    if (match) {
        const [, yyyy, mm, dd, hh, mi, ss] = match;
        return `${dd}/${mm}/${yyyy} ${hh}:${mi}:${ss}`;
    }
    const date = new Date(raw);
    if (Number.isNaN(date.getTime())) return escapeHtml(raw.split(".")[0]);
    const dd = String(date.getDate()).padStart(2, "0");
    const mm = String(date.getMonth() + 1).padStart(2, "0");
    const yyyy = String(date.getFullYear());
    const hh = String(date.getHours()).padStart(2, "0");
    const mi = String(date.getMinutes()).padStart(2, "0");
    const ss = String(date.getSeconds()).padStart(2, "0");
    return `${dd}/${mm}/${yyyy} ${hh}:${mi}:${ss}`;
}

function alertLabel(type) {
    const key = String(type || "").toUpperCase();
    const map = {
        ALERTA_FALTANTE: "Faltante",
        ALERTA_SOBRANTE: "Sobrante",
        ALERTA_RETORNO_EXTRA: "Retorno extra",
        ALERTA_RETORNO_INCOMPLETO: "Retorno incompleto",
        ALERTA_SALIDA_SIN_SOPORTE: "Inconsistencia",
    };
    return map[key] || String(type || "Alerta");
}

function alertMessage(alert) {
    const type = String(alert?.type || "").toUpperCase();
    const data = alert?.data && typeof alert.data === "object" ? alert.data : {};
    if (type === "ALERTA_FALTANTE" || type === "ALERTA_SOBRANTE") {
        if (
            data.expected_return !== undefined &&
            data.returned !== undefined &&
            (data.diferencia !== undefined || data.difference !== undefined)
        ) {
            const diff = data.diferencia !== undefined ? data.diferencia : data.difference;
            return `Esperado regrese ${fmtQty(data.expected_return)}, regresó ${fmtQty(data.returned)}, dif ${fmtQty(diff)}`;
        }
        return "";
    }
    if (type === "ALERTA_RETORNO_EXTRA") {
        if (data.delivered !== undefined && data.returned !== undefined) {
            return `Regresó ${fmtQty(data.returned)}, entregado ${fmtQty(data.delivered)}`;
        }
        return "";
    }
    if (type === "ALERTA_RETORNO_INCOMPLETO") {
        const missing = data.missing !== undefined ? data.missing : data.delta;
        if (data.delivered !== undefined && data.returned !== undefined && missing !== undefined) {
            return `Entregado ${fmtQty(data.delivered)}, regresó ${fmtQty(data.returned)}, faltan ${fmtQty(missing)}`;
        }
        return "";
    }
    if (type === "ALERTA_SALIDA_SIN_SOPORTE") {
        if (data.total_out !== undefined && data.delivered !== undefined) {
            return `Salió ${fmtQty(data.total_out)}, entregado ${fmtQty(data.delivered)}`;
        }
        return "";
    }
    return "";
}

function contextoOperacionLabel(value) {
    const key = String(value || "").toLowerCase();
    if (key === "instalacion_inicial") return "Instalación inicial";
    if (key === "reposicion") return "Reposición";
    return "";
}

function getCurrentSelectedValues() {
    return Array.from(document.querySelectorAll("#items-container input[name*='[descripcion]']"))
        .map((input) => input.value.trim())
        .filter((v) => v);
}

function getCatalogItemMeta(name) {
    const value = normalizeSearchText(name);
    const catalogo = Array.isArray(window.CATALOGO_ITEMS) ? window.CATALOGO_ITEMS : [];
    for (const item of catalogo) {
        if (typeof item === "string") {
            if (normalizeSearchText(item) === value) {
                return { nombre: item, permite_decimal: false };
            }
            continue;
        }
        if (item && normalizeSearchText(item.nombre) === value) {
            return item;
        }
    }
    return null;
}

function itemAllowsDecimal(name) {
    const meta = getCatalogItemMeta(name);
    return Boolean(meta?.permite_decimal);
}

function validateQtyInput(input, report = false) {
    if (!input) return false;
    const row = input.closest(".item-row");
    const itemInput = row?.querySelector("input[name*='[descripcion]']");
    const rawValue = String(input.value || "").trim();
    const qty = Number(rawValue);
    const allowsDecimal = itemAllowsDecimal(itemInput?.value);

    if (!rawValue || Number.isNaN(qty) || qty <= 0) {
        input.setCustomValidity("Ingresa una cantidad válida mayor que cero.");
        if (report) input.reportValidity();
        return false;
    }
    if (!allowsDecimal && !Number.isInteger(qty)) {
        input.setCustomValidity("Este item solo permite cantidades enteras.");
        if (report) input.reportValidity();
        return false;
    }

    input.setCustomValidity("");
    return true;
}

function syncQtyInputForRow(row) {
    if (!row) return;
    const itemInput = row.querySelector("input[name*='[descripcion]']");
    const qtyInput = row.querySelector("input[name*='[cantidad]']");
    if (!itemInput || !qtyInput) return;
    const allowsDecimal = itemAllowsDecimal(itemInput.value);
    qtyInput.step = allowsDecimal ? "0.01" : "1";
    qtyInput.min = allowsDecimal ? "0.01" : "1";
    qtyInput.placeholder = allowsDecimal ? "Cantidad (admite decimal)" : "Cantidad entera";
    if (qtyInput.value.trim()) {
        validateQtyInput(qtyInput, false);
    }
}

function setItemError(message) {
    const errorEl = document.getElementById("item-error");
    if (!errorEl) return;
    errorEl.textContent = message || "";
}

function validateCatalogItemInput(input, report = false) {
    if (!input) return false;
    const value = input.value.trim();
    const existe = Boolean(getCatalogItemMeta(value));

    if (!value) {
        input.setCustomValidity("Selecciona un item válido del catálogo.");
        if (report) input.reportValidity();
        return false;
    }
    if (!existe) {
        input.setCustomValidity("Selecciona un item válido del catálogo.");
        if (report) input.reportValidity();
        return false;
    }

    const duplicate = Array.from(document.querySelectorAll("#items-container input[name*='[descripcion]']"))
        .some((other) => other !== input && other.value.trim() === value);
    if (duplicate) {
        input.setCustomValidity("Este item ya fue agregado en otra fila.");
        if (report) input.reportValidity();
        return false;
    }

    input.setCustomValidity("");
    syncQtyInputForRow(input.closest(".item-row"));
    return true;
}

function handleItemInputChange(input) {
    const ok = validateCatalogItemInput(input);
    if (ok) {
        setItemError("");
    }
    syncItemInputs();
}

function syncItemInputs() {
    const rows = Array.from(document.querySelectorAll("#items-container .item-row"));
    if (rows.length === 0) return;
    let hasInvalid = false;
    for (const row of rows) {
        const input = row.querySelector("input[name*='[descripcion]']");
        const qtyInput = row.querySelector("input[name*='[cantidad]']");
        if (!input) continue;
        const valid = validateCatalogItemInput(input, false);
        if (!valid && input.value.trim()) {
            hasInvalid = true;
        }
        if (qtyInput && qtyInput.value.trim() && !validateQtyInput(qtyInput, false)) {
            hasInvalid = true;
        }
    }
    if (hasInvalid) {
        setItemError("Revisa item y cantidad. Solo los items marcados en catálogo permiten decimales.");
        return;
    }
    setItemError("");
}

function eliminarItem(button) {
    const row = button.closest(".item-row");
    if (row) row.remove();
    syncItemInputs();
}

function canAddItemRow(container) {
    const rows = Array.from(container.querySelectorAll(".item-row"));
    if (rows.length === 0) return true;

    const lastRow = rows[rows.length - 1];
    const itemInput = lastRow.querySelector("input[name*='[descripcion]']");
    const qtyInput = lastRow.querySelector("input[name*='[cantidad]']");

    if (itemInput && !validateCatalogItemInput(itemInput, true)) {
        setItemError(itemInput.validationMessage || "Selecciona un item válido del catálogo.");
        return false;
    }
    if (qtyInput) {
        const qtyValida = validateQtyInput(qtyInput, false);
        if (!qtyValida) {
            qtyInput.reportValidity();
            qtyInput.focus();
            return false;
        }
    }
    setItemError("");
    return true;
}

function agregarItem() {
    const container = document.getElementById("items-container");
    if (!container) return;
    if (!canAddItemRow(container)) return;

    const div = document.createElement("div");
    div.className = "item-row";
    const input = document.createElement("input");
    input.type = "text";
    input.name = `items[${itemCount}][descripcion]`;
    input.setAttribute("list", "catalogo-items");
    input.placeholder = "Buscar item...";
    input.autocomplete = "off";
    input.required = true;
    input.addEventListener("change", () => handleItemInputChange(input));
    input.addEventListener("blur", () => handleItemInputChange(input));
    input.addEventListener("input", () => syncQtyInputForRow(div));

    const qty = document.createElement("input");
    qty.type = "number";
    qty.name = `items[${itemCount}][cantidad]`;
    qty.placeholder = "Cantidad entera";
    qty.step = "1";
    qty.min = "1";
    qty.required = true;
    qty.addEventListener("input", () => validateQtyInput(qty, false));
    qty.addEventListener("blur", () => validateQtyInput(qty, false));

    const contexto = document.createElement("select");
    contexto.name = `items[${itemCount}][contexto_operacion]`;
    contexto.setAttribute("aria-label", "Contexto operativo del item");

    const reposicion = document.createElement("option");
    reposicion.value = "reposicion";
    reposicion.textContent = "Reposicion";
    reposicion.selected = true;

    const instalacion = document.createElement("option");
    instalacion.value = "instalacion_inicial";
    instalacion.textContent = "Instalacion inicial";

    contexto.append(reposicion, instalacion);

    const contextoWrap = document.createElement("div");
    contextoWrap.className = "item-context-block";
    const contextoRow = document.createElement("div");
    contextoRow.className = "field-help-row";
    const contextoHelp = document.createElement("div");
    contextoHelp.className = "field-help-inline";
    contextoHelp.innerHTML = `
        <button type="button" class="field-help-trigger" aria-label="Ayuda sobre contexto operativo">?</button>
        <div class="field-help-popover" role="note">
            Usa <strong>Instalacion inicial</strong> solo para <strong>R1E</strong> o <strong>Demostracion</strong>, cuando el equipo se instala por primera vez en el cliente. Para el resto, usa <strong>Reposicion</strong>.
        </div>
    `;
    contextoRow.append(contexto, contextoHelp);
    contextoWrap.appendChild(contextoRow);

    const demoLabel = document.createElement("label");
    demoLabel.className = "item-demo-check";
    const demoCheck = document.createElement("input");
    demoCheck.type = "checkbox";
    demoCheck.name = `es_demo_${itemCount}`;
    demoCheck.value = "on";
    demoLabel.append(demoCheck, document.createTextNode(" Para Demo"));
    contextoWrap.appendChild(demoLabel);

    const btn = document.createElement("button");
    btn.type = "button";
    btn.textContent = "X";
    btn.addEventListener("click", () => eliminarItem(btn));

    div.append(input, qty, contextoWrap, btn);
    container.appendChild(div);
    itemCount++;
    syncItemInputs();
}

document.addEventListener("DOMContentLoaded", () => {
    initSearchableSelects(document);
    const itemInputs = document.querySelectorAll("#items-container input[name*='[descripcion]']");
    for (const input of itemInputs) {
        input.addEventListener("change", () => handleItemInputChange(input));
        input.addEventListener("blur", () => handleItemInputChange(input));
    }
    const itemRows = document.querySelectorAll("#items-container .item-row");
    if (itemRows.length > 0) {
        itemCount = itemRows.length;
    }
    const requisicionForm = document.querySelector("form[data-requisicion-form='true']");
    if (requisicionForm) {
        requisicionForm.addEventListener("submit", (event) => {
            const rows = Array.from(document.querySelectorAll("#items-container .item-row"));
            const invalidInput = rows
                .map((row) => row.querySelector("input[name*='[descripcion]']"))
                .find((input) => input && !validateCatalogItemInput(input, false));
            if (invalidInput) {
                event.preventDefault();
                setItemError(invalidInput.validationMessage || "Selecciona un item válido del catálogo.");
                invalidInput.reportValidity();
                return;
            }
            const invalidQtyInput = rows
                .map((row) => row.querySelector("input[name*='[cantidad]']"))
                .find((input) => input && !validateQtyInput(input, false));
            if (invalidQtyInput) {
                event.preventDefault();
                setItemError(invalidQtyInput.validationMessage || "Cantidad inválida.");
                invalidQtyInput.reportValidity();
            }
        });
    }
    const qtyInputs = document.querySelectorAll("#items-container input[name*='[cantidad]']");
    for (const qtyInput of qtyInputs) {
        qtyInput.addEventListener("input", () => validateQtyInput(qtyInput, false));
        qtyInput.addEventListener("blur", () => validateQtyInput(qtyInput, false));
        syncQtyInputForRow(qtyInput.closest(".item-row"));
    }
    syncItemInputs();
});

function verDetalle(id) {
    fetch(`/api/requisiciones/${id}`)
        .then((r) => r.json())
        .then((data) => {
            const content = document.getElementById("modal-content");
            const modal = document.getElementById("modal-detalle");
            if (!content || !modal) return;
            const headerTitle = modal.querySelector("header h3");
            if (headerTitle) {
                headerTitle.textContent = `Detalle de Requisici\u00f3n: ${data.folio || "-"}`;
            }

            const items = Array.isArray(data.items) ? data.items : [];
            const isLiquidada = ["liquidada", "pendiente_prokey", "finalizada_sin_prokey", "liquidada_en_prokey"].includes(data.estado);
            const showDelivered = items.some(
                (i) => i.cantidad_entregada !== null && i.cantidad_entregada !== undefined
            );
            const itemRows = items
                .map((i) => {
                    const qe = i.cantidad_entregada;
                    const hasQe = qe !== null && qe !== undefined;
                    const isZero = hasQe && Number(qe) === 0;
                    const contexto = contextoOperacionLabel(i.contexto_operacion);
                    const demoBadge = i.es_demo
                        ? '<span class="badge warning item-demo-badge">Para Demo</span>'
                        : "";
                    const despCls = isZero
                        ? "qty-col qty-despachada qty-zero"
                        : "qty-col qty-despachada";
                    return `<tr>
                    <td><strong>${escapeHtml(i.descripcion || "-")}</strong>${demoBadge}${contexto ? `<div class="liq-type-context muted">${escapeHtml(contexto)}</div>` : ""}</td>
                    <td class="qty-col qty-solicitada">${fmtQty(i.cantidad)}</td>
                    ${showDelivered ? `<td class="${despCls}">${fmtQty(qe)}</td>` : ""}
                </tr>`;
                })
                .join("");
            const liquidacionRows = items
                .map((i) => {
                    const difference = Number(i.difference ?? i.delta ?? 0);
                    const differenceCls = difference > 0 ? "dif dif--pos" : difference < 0 ? "dif dif--neg" : "dif dif--zero";
                    const alerts = Array.isArray(i.liquidation_alerts) ? i.liquidation_alerts : [];
                    const alertBadges = alerts.length
                        ? alerts
                              .map((a) => {
                                  const sev = a?.severity === "high" ? "high" : "warn";
                                  const code = escapeHtml(a?.type || "ALERTA");
                                  const label = escapeHtml(alertLabel(a?.type));
                                  const detail = alertMessage(a);
                                  const detailText = detail ? `${escapeHtml(detail)} · ` : "";
                                  const title = `${label}: ${detailText}(interno: ${code})`;
                                  return `<span class="alert-badge alert-badge--${sev} liq-alert-badge ${sev}" title="${title}">${label}</span>`;
                              })
                              .join("")
                        : '<span class="liq-alert-empty">Sin alertas</span>';
                    const noteAttentionClass = alerts.length ? "item-note--attention" : "";
                    const noteHtml = i.item_liquidation_note
                        ? `<div class="liq-item-note item-note ${noteAttentionClass}">${escapeHtml(i.item_liquidation_note)}</div>`
                        : "";
                    const demoBadge = i.es_demo
                        ? '<span class="badge warning item-demo-badge">Para Demo</span>'
                        : "";
                    const mode = (i.mode || "RETORNABLE").toUpperCase();
                    const contexto = contextoOperacionLabel(i.contexto_operacion);
                    const tipoContexto = contexto
                        ? `<div class="liq-type-main">${escapeHtml(mode)}</div><div class="liq-type-context muted">${escapeHtml(contexto)}</div>`
                        : escapeHtml(mode);
                    const ingresoPk = mode === "RETORNABLE" ? fmtQty(i.pk_ingreso_qty) : '<span class="muted">—</span>';
                    const differenceText = difference > 0
                        ? `Falta ${fmtQty(difference)}`
                        : difference < 0
                            ? `Extra ${fmtQty(Math.abs(difference))}`
                            : "OK";
                    return `<tr>
                        <td><strong>${escapeHtml(i.descripcion || "-")}</strong>${demoBadge}${noteHtml}</td>
                        <td class="qty-col td-num">${fmtQty(i.cantidad_entregada)}</td>
                        <td class="qty-col td-center">${tipoContexto}</td>
                        <td class="qty-col td-num">${fmtQty(i.used ?? i.qty_used)}</td>
                        <td class="qty-col td-num">${fmtQty(i.not_used ?? i.qty_left_at_client)}</td>
                        <td class="qty-col td-num">${fmtQty(i.returned ?? i.qty_returned_to_warehouse)}</td>
                        <td class="qty-col td-num"><span class="${differenceCls}" title="Diferencia de retorno: esperado ${fmtQty(i.expected_return ?? 0)}, regresó ${fmtQty(i.returned ?? i.qty_returned_to_warehouse ?? 0)}">${differenceText}</span></td>
                        <td class="qty-col td-num">
                            <span class="pk-help" title="Cantidad aplicable para ingreso en Prokey por bodega. En instalación inicial no genera ingreso PK.">${ingresoPk}</span>
                        </td>
                        <td>${alertBadges}</td>
                    </tr>`;
                })
                .join("");

            const resultLabels = {
                completa: "Completa",
                parcial: "Parcial",
                no_entregada: "No Entregada",
            };
            const resultVal = data.delivery_result ? resultLabels[data.delivery_result] || data.delivery_result : "-";
            const chipCls =
                { completa: "resultado-completa", parcial: "resultado-parcial", no_entregada: "resultado-no-entregada" }[
                    data.delivery_result
                ] || "";
            const resultHtml = data.delivery_result
                ? `<span class="resultado-chip ${chipCls}">${escapeHtml(resultVal)}</span>`
                : `<span class="flujo-value">${escapeHtml(resultVal)}</span>`;
            const timeline = Array.isArray(data.timeline) ? data.timeline : [];
            const timelineRows = timeline
                .map(
                    (event) => `<li class="dd-timeline__item">
                                    <div class="dd-timeline__title">${escapeHtml(event.evento || "-")}</div>
                                    <div class="dd-timeline__meta">${escapeHtml(event.actor || "-")} · ${fmtDateTime(event.fecha_hora)}</div>
                                </li>`
                )
                .join("");
            const allAlerts = items.flatMap((i) => (Array.isArray(i.liquidation_alerts) ? i.liquidation_alerts : []));
            const highAlerts = allAlerts.filter((a) => a?.severity === "high").length;
            const alertCounts = allAlerts.reduce((acc, current) => {
                const key = alertLabel(current?.type);
                acc[key] = (acc[key] || 0) + 1;
                return acc;
            }, {});
            const topAlertEntries = Object.entries(alertCounts)
                .sort((a, b) => b[1] - a[1])
                .slice(0, 3);
            const topAlertTypes = topAlertEntries.length
                ? topAlertEntries.map(([label, count]) => `${escapeHtml(label)} (${count})`).join(", ")
                : "Ninguno";
            const alertCardClass = highAlerts > 0 ? "dd-card--alert dd-card--alert-high" : allAlerts.length > 0 ? "dd-card--alert" : "";
            const prokeyEditorNote = data.prokey_ref_actualizada_por_nombre
                ? `<div class="dd-kv-note">Registrada por ${escapeHtml(data.prokey_ref_actualizada_por_nombre)}${data.prokey_ref_actualizada_por_rol ? ` (${escapeHtml(data.prokey_ref_actualizada_por_rol)})` : ""}</div>`
                : "";
            const prokeyRefHtml = data.prokey_not_applicable
                ? 'No aplica'
                : data.prokey_ref
                ? `${escapeHtml(data.prokey_ref)}${prokeyEditorNote}`
                : data.puede_editar_prokey_ref
                    ? `Pendiente <span class="badge warning prokey-pending-badge">Prokey pendiente</span>
                       <a href="/requisiciones/${data.id}/prokey-ref" class="prokey-add-link">Agregar referencia Prokey</a>`
                    : 'Pendiente <span class="badge warning prokey-pending-badge">Prokey pendiente</span>';
            const receptorDesignadoHtml = data.receptor_designado
                ? `${escapeHtml(data.receptor_designado.nombre || "-")} (${escapeHtml(data.receptor_designado.rol || "-")})`
                : "-";
            const receptorRealHtml = data.recibido_por_detalle
                ? `${escapeHtml(data.recibido_por_detalle.nombre || "-")} (${escapeHtml(data.recibido_por_detalle.rol || "-")})`
                : data.delivered_to
                    ? escapeHtml(data.delivered_to)
                    : "Pendiente";
            const liquidationComment = data.liquidation_comment
                ? escapeHtml(data.liquidation_comment)
                : "—";
            const prokeyClosedBy = escapeHtml(data.prokey_liquidado_por_nombre || "-");
            const prokeyClosedAt = fmtDateTime(data.prokey_liquidada_at);
            const itemsSection = isLiquidada
                ? `<section class="detalle-items-section">
                    <h4><span class="icon-items">\u2299</span> Items Liquidados</h4>
                    <div class="detalle-items-wrap liquidacion-paper-wrap">
                        <table class="detalle-items-table liquidacion-paper-table">
                            <thead><tr>
                                <th>Descripcion</th>
                                <th class="qty-col">Entregado</th>
                                <th class="qty-col">Tipo</th>
                                <th class="qty-col">Usado</th>
                                <th class="qty-col">No usado</th>
                                <th class="qty-col">Regresa</th>
                                <th class="qty-col" title="Diferencia de retorno: si falta equipo por regresar muestra 'Falta'; si regresó de más muestra 'Extra'">DIF</th>
                                <th class="qty-col" title="Retornables en reposición usados que regresaron, más excedentes recibidos en bodega. Instalación inicial no genera ingreso PK.">Ingreso PK (Bodega)</th>
                                <th>Alertas</th>
                            </tr></thead>
                            <tbody>
                                ${liquidacionRows || '<tr><td colspan="9">Sin items</td></tr>'}
                            </tbody>
                        </table>
                    </div>
                </section>`
                : `<section class="detalle-items-section">
                    <h4><span class="icon-items">\u2299</span> Items Solicitados</h4>
                    <div class="detalle-items-wrap">
                        <table class="detalle-items-table">
                            <thead><tr>
                                <th>Item / Producto</th>
                                <th class="qty-col">Cant. Solicitada</th>
                                ${showDelivered ? '<th class="qty-col">Cant. Despachada</th>' : ""}
                            </tr></thead>
                            <tbody>
                                ${itemRows || '<tr><td colspan="3">Sin items</td></tr>'}
                            </tbody>
                        </table>
                    </div>
                </section>`;
            const isPdfEnabled = ["aprobada", "preparado", "entregada", "no_entregada", "liquidada", "pendiente_prokey", "finalizada_sin_prokey", "liquidada_en_prokey"].includes(data.estado) && !!data.pdf_url;
            const pdfAction = isPdfEnabled
                ? `<a class="secondary" role="button" href="${escapeHtml(data.pdf_url)}" target="_blank" rel="noopener noreferrer">Ver PDF</a>`
                : `<button type="button" class="secondary btn-disabled" disabled title="${data.estado === "pendiente" ? "Disponible al aprobar" : "No disponible para este estado"}">Ver PDF</button>`;
            const commentsToggleHtml = `
                <details class="detalle-collapsible dd-collapse">
                    <summary>Otros comentarios y proceso</summary>
                    <div class="comentarios-list">
                        <div class="comentario-item">
                            <span class="meta-label label-muted">APROBACIÓN</span>
                            <p>${escapeHtml(data.approval_comment || "-")}</p>
                        </div>
                        <div class="comentario-item">
                            <span class="meta-label label-muted">RAZÓN RECHAZO</span>
                            <p>${escapeHtml(data.rejection_reason || "-")}</p>
                        </div>
                        <div class="comentario-item">
                            <span class="meta-label label-muted">COMENTARIO RECHAZO</span>
                            <p>${escapeHtml(data.rejection_comment || "-")}</p>
                        </div>
                        <div class="comentario-item">
                            <span class="meta-label label-muted">COMENTARIO ENTREGA</span>
                            <p>${escapeHtml(data.delivery_comment || "-")}</p>
                        </div>
                    </div>
                </details>
            `;

            modal.classList.add("modal--detail-dashboard");
            content.innerHTML = `
                <div class="detail-dashboard">
                <section class="detalle-dashboard-header">
                    <div>
                        <h4 class="detalle-dashboard-title">Requisición ${escapeHtml(data.folio || "-")}</h4>
                        <span class="badge info">Creada: ${fmtDateTime(data.created_at)}</span>
                    </div>
                    <div class="detalle-dashboard-actions">
                        ${pdfAction}
                    </div>
                </section>
                <section class="detalle-dashboard-grid dd-grid">
                    <article class="detalle-block dashboard-card dd-card">
                        <h4 class="dd-card-title">Información general</h4>
                        <div class="dd-kv"><div class="dd-kv-label">Cliente</div><div class="dd-kv-value">${escapeHtml(data.cliente_nombre || "-")}</div></div>
                        <div class="dd-kv"><div class="dd-kv-label">Código cliente</div><div class="dd-kv-value">${escapeHtml(data.cliente_codigo || "-")}</div></div>
                        <div class="dd-kv"><div class="dd-kv-label">Ruta principal</div><div class="dd-kv-value">${escapeHtml(data.cliente_ruta_principal || "-")}</div></div>
                        <div class="dd-kv"><div class="dd-kv-label">Solicitante</div><div class="dd-kv-value">${escapeHtml(data.solicitante || "-")}</div></div>
                        <div class="dd-kv"><div class="dd-kv-label">Receptor designado</div><div class="dd-kv-value">${receptorDesignadoHtml}</div></div>
                        <div class="dd-kv"><div class="dd-kv-label">Recibió / firmó</div><div class="dd-kv-value">${receptorRealHtml}</div></div>
                    </article>
                    <article class="detalle-block dashboard-card dd-card">
                        <h4 class="dd-card-title">Estado liquidación</h4>
                        <div class="dd-kv"><div class="dd-kv-label">Estado</div><div class="dd-kv-value">${escapeHtml(data.estado || "-")}</div></div>
                        <div class="dd-kv"><div class="dd-kv-label">Resultado entrega</div><div class="dd-kv-value">${resultHtml}</div></div>
                        <div class="dd-kv"><div class="dd-kv-label">Ref Prokey</div><div class="dd-kv-value">${prokeyRefHtml}</div></div>
                    </article>
                    <article class="detalle-block dashboard-card dd-card ${alertCardClass}">
                        <h4 class="dd-card-title">Alertas de conciliación</h4>
                        <div class="dd-kv"><div class="dd-kv-label">Total</div><div class="dd-kv-value">${allAlerts.length} detectadas</div></div>
                        <div class="dd-kv"><div class="dd-kv-label">Alta severidad</div><div class="dd-kv-value">${highAlerts}</div></div>
                        <div class="dd-kv"><div class="dd-kv-label">Tipos frecuentes</div><div class="dd-kv-value">${topAlertTypes}</div></div>
                    </article>
                    <article class="detalle-block dashboard-card dd-card dashboard-timeline">
                        <h4 class="dd-card-title">Línea de tiempo del flujo</h4>
                        <div class="dd-timeline-scroll">
                            <ol class="dd-timeline">
                                ${timelineRows || '<li class="dd-timeline__item"><div class="dd-timeline__title">Sin movimientos</div><div class="dd-timeline__meta">-</div></li>'}
                            </ol>
                        </div>
                    </article>
                </section>
                ${itemsSection}
                <section class="detalle-bottom-grid">
                    <article class="detalle-block dashboard-card dd-card">
                        <h4 class="dd-card-title">Justificación</h4>
                        <p>${escapeHtml(data.justificacion || "-")}</p>
                    </article>
                    <article class="detalle-block dashboard-card dd-card">
                        <h4 class="dd-card-title">Comentario de liquidación</h4>
                        <p class="liquidation-comment">${liquidationComment}</p>
                    </article>
                </section>
                ${commentsToggleHtml}
                </div>
            `;
            modal.showModal();
        });
}

function cerrarModal() {
    const modal = document.getElementById("modal-detalle");
    if (modal) {
        modal.classList.remove("modal--detail-dashboard");
        modal.close();
    }
}
