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

function ensureMaterialSymbolsFont() {
    const linkId = "material-symbols-outlined-font";
    if (document.getElementById(linkId)) return;
    const link = document.createElement("link");
    link.id = linkId;
    link.rel = "stylesheet";
    link.href = "https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap";
    document.head.appendChild(link);
}

function findDatalistOptionByValue(list, rawValue) {
    if (!list) return null;
    const term = normalizeSearchText(rawValue);
    if (!term) return null;
    return Array.from(list.options || []).find((option) => normalizeSearchText(option.value) === term) || null;
}

function validateReceptorDesignadoInput(input, report = false) {
    if (!input) return false;
    const hiddenId = input.getAttribute("data-receptor-picker");
    const hidden = hiddenId ? document.getElementById(hiddenId) : null;
    const listId = input.getAttribute("list");
    const list = listId ? document.getElementById(listId) : null;
    const value = String(input.value || "").trim();
    const option = findDatalistOptionByValue(list, value);
    const receptorId = option?.dataset?.id ? String(option.dataset.id).trim() : "";

    if (!value) {
        if (hidden) hidden.value = "";
        input.setCustomValidity("Debes seleccionar receptor designado.");
        if (report) input.reportValidity();
        return false;
    }
    if (!option || !receptorId) {
        if (hidden) hidden.value = "";
        input.setCustomValidity("Selecciona un receptor válido del catálogo.");
        if (report) input.reportValidity();
        return false;
    }

    if (hidden) hidden.value = receptorId;
    input.setCustomValidity("");
    return true;
}

function initReceptorDesignadoPickers(root = document) {
    const inputs = root.querySelectorAll("[data-receptor-picker]");
    for (const input of inputs) {
        const sync = () => validateReceptorDesignadoInput(input, false);
        input.addEventListener("input", sync);
        input.addEventListener("change", sync);
        input.addEventListener("blur", () => validateReceptorDesignadoInput(input, true));
        sync();
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

function bindDeleteButton(button) {
    if (!button) return;
    button.onclick = function () {
        eliminarItem(this);
    };
}

function renumberItemRows() {
    const rows = Array.from(document.querySelectorAll("#items-container .item-row"));
    rows.forEach((row, index) => {
        const itemInput = row.querySelector("input[name*='[descripcion]']");
        const qtyInput = row.querySelector("input[name*='[cantidad]']");
        const contextoInput = row.querySelector("select[name*='[contexto_operacion]']");
        const demoInput = row.querySelector("input[type='checkbox']");
        const deleteButton = row.querySelector(".item-action-cell button");

        if (itemInput) itemInput.name = `items[${index}][descripcion]`;
        if (qtyInput) qtyInput.name = `items[${index}][cantidad]`;
        if (contextoInput) contextoInput.name = `items[${index}][contexto_operacion]`;
        if (demoInput) demoInput.name = `es_demo_${index}`;
        bindDeleteButton(deleteButton);
    });
    itemCount = rows.length;
}

function buildItemRowMarkup(index) {
    return `
        <td>
            <input type="text" name="items[${index}][descripcion]" list="catalogo-items" placeholder="Buscar item..." autocomplete="off" required>
        </td>
        <td>
            <input type="number" step="1" min="1" name="items[${index}][cantidad]" placeholder="Cantidad" required>
        </td>
        <td>
            <div class="item-context-block">
                <div class="field-help-row">
                    <select name="items[${index}][contexto_operacion]" aria-label="Contexto operativo del item">
                        <option value="reposicion" selected>Reposicion</option>
                        <option value="instalacion_inicial">Instalacion inicial</option>
                    </select>
                    <div class="field-help-inline">
                        <button type="button" class="field-help-trigger" aria-label="Ayuda sobre contexto operativo">?</button>
                        <div class="field-help-popover" role="note">
                            Usa <strong>Instalacion inicial</strong> solo para <strong>R1E</strong> o <strong>Demostracion</strong>, cuando el equipo se instala por primera vez en el cliente. Para el resto, usa <strong>Reposicion</strong>.
                        </div>
                    </div>
                    <label class="item-demo-check">
                        <input type="checkbox" name="es_demo_${index}" value="on">
                        Para Demo
                    </label>
                </div>
            </div>
        </td>
        <td class="item-action-cell">
            <button type="button" aria-label="Eliminar item">Eliminar Item</button>
        </td>
    `;
}

function eliminarItem(btn) {
    const row = btn?.closest?.(".item-row");
    if (!row) return;
    const container = document.getElementById("items-container");
    if (!container) return;
    const rows = Array.from(container.querySelectorAll(".item-row"));
    if (rows.length <= 1) {
        setItemError("Debes conservar al menos un item.");
        return;
    }
    row.remove();
    renumberItemRows();
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

    const index = container.querySelectorAll(".item-row").length;
    const tr = document.createElement("tr");
    tr.className = "item-row";
    tr.innerHTML = buildItemRowMarkup(index);

    const input = tr.querySelector("input[name*='[descripcion]']");
    const qty = tr.querySelector("input[name*='[cantidad]']");
    const contexto = tr.querySelector("select[name*='[contexto_operacion]']");
    const btn = tr.querySelector(".item-action-cell button");

    input.name = `items[${index}][descripcion]`;
    input.setAttribute("list", "catalogo-items");
    input.placeholder = "Buscar item...";
    input.autocomplete = "off";
    input.required = true;
    input.addEventListener("change", () => handleItemInputChange(input));
    input.addEventListener("blur", () => handleItemInputChange(input));
    input.addEventListener("input", () => syncQtyInputForRow(tr));

    qty.placeholder = "Cantidad";
    qty.step = "1";
    qty.min = "1";
    qty.required = true;
    qty.addEventListener("input", () => validateQtyInput(qty, false));
    qty.addEventListener("blur", () => validateQtyInput(qty, false));

    contexto.setAttribute("aria-label", "Contexto operativo del item");
    bindDeleteButton(btn);

    container.appendChild(tr);
    itemCount = container.querySelectorAll(".item-row").length;
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
    for (const row of itemRows) {
        bindDeleteButton(row.querySelector(".item-action-cell button"));
    }
    const requisicionForm = document.querySelector("form[data-requisicion-form='true']");
    if (requisicionForm) {
        requisicionForm.addEventListener("submit", (event) => {
            const receptorInput = requisicionForm.querySelector("[data-receptor-picker]");
            if (receptorInput && !validateReceptorDesignadoInput(receptorInput, false)) {
                event.preventDefault();
                receptorInput.reportValidity();
                return;
            }
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
    initReceptorDesignadoPickers(document);
    const qtyInputs = document.querySelectorAll("#items-container input[name*='[cantidad]']");
    for (const qtyInput of qtyInputs) {
        qtyInput.addEventListener("input", () => validateQtyInput(qtyInput, false));
        qtyInput.addEventListener("blur", () => validateQtyInput(qtyInput, false));
        syncQtyInputForRow(qtyInput.closest(".item-row"));
    }
    syncItemInputs();
});

function verDetalle(id) {
    ensureMaterialSymbolsFont();
    fetch(`/api/requisiciones/${id}`)
        .then((r) => r.json())
        .then((data) => {
            const content = document.getElementById("modal-content");
            const modal = document.getElementById("modal-detalle");
            if (!content || !modal) return;
            const headerTitle = modal.querySelector("header h3");
            if (headerTitle) headerTitle.textContent = "Detalle";

            const items = Array.isArray(data.items) ? data.items : [];
            const isLiquidada = ["liquidada", "pendiente_prokey", "finalizada_sin_prokey", "liquidada_en_prokey"].includes(data.estado);
            const showDelivered = items.some((i) => i.cantidad_entregada !== null && i.cantidad_entregada !== undefined);
            const itemEmptyColspan = showDelivered ? 3 : 2;

            const itemRows = items
                .map((i) => {
                    const qe = i.cantidad_entregada;
                    const hasQe = qe !== null && qe !== undefined;
                    const isZero = hasQe && Number(qe) === 0;
                    const contexto = contextoOperacionLabel(i.contexto_operacion);
                    const demoBadge = i.es_demo ? '<span class="detail-badge detail-badge--demo">Para Demo</span>' : "";
                    const despCls = isZero ? "qty-col qty-despachada qty-zero" : "qty-col qty-despachada";
                    return `<tr>
                    <td><strong>${escapeHtml(i.descripcion || "-")}</strong>${demoBadge}${contexto ? `<div class="detail-type-context detail-muted">${escapeHtml(contexto)}</div>` : ""}</td>
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
                                  return `<span class="detail-alert-badge detail-alert-badge--${sev}" title="${title}">${label}</span>`;
                              })
                              .join("")
                        : '<span class="detail-muted">Sin alertas</span>';
                    const noteAttentionClass = alerts.length ? "detail-item-note--attention" : "";
                    const noteHtml = i.item_liquidation_note
                        ? `<div class="detail-item-note ${noteAttentionClass}">${escapeHtml(i.item_liquidation_note)}</div>`
                        : "";
                    const demoBadge = i.es_demo ? '<span class="detail-badge detail-badge--demo">Para Demo</span>' : "";
                    const mode = (i.mode || "RETORNABLE").toUpperCase();
                    const contexto = contextoOperacionLabel(i.contexto_operacion);
                    const tipoContexto = contexto
                        ? `<div class="detail-type-main">${escapeHtml(mode)}</div><div class="detail-type-context detail-muted">${escapeHtml(contexto)}</div>`
                        : escapeHtml(mode);
                    const ingresoPk = mode === "RETORNABLE" ? fmtQty(i.pk_ingreso_qty) : '<span class="detail-muted">—</span>';
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
            const chipCls = { completa: "resultado-completa", parcial: "resultado-parcial", no_entregada: "resultado-no-entregada" }[data.delivery_result] || "";
            const resultHtml = data.delivery_result
                ? `<span class="resultado-chip ${chipCls}">${escapeHtml(resultVal)}</span>`
                : `<span class="flujo-value">${escapeHtml(resultVal)}</span>`;
            const timeline = Array.isArray(data.timeline) ? data.timeline : [];
            const timelineRows = timeline
                .map(
                    (event) => `<li class="detail-timeline__item">
                                    <div class="detail-timeline__title">${escapeHtml(event.evento || "-")}</div>
                                    <div class="detail-timeline__meta">${escapeHtml(event.actor || "-")} · ${fmtDateTime(event.fecha_hora)}</div>
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
            const alertCardClass = highAlerts > 0 ? "detail-card--alert detail-card--alert-high" : allAlerts.length > 0 ? "detail-card--alert" : "";
            const prokeyEditorNote = data.prokey_ref_actualizada_por_nombre
                ? `<div class="detail-kv-note">Registrada por ${escapeHtml(data.prokey_ref_actualizada_por_nombre)}${data.prokey_ref_actualizada_por_rol ? ` (${escapeHtml(data.prokey_ref_actualizada_por_rol)})` : ""}</div>`
                : "";
            const prokeyRefHtml = data.prokey_not_applicable
                ? "No aplica"
                : data.prokey_ref
                    ? `${escapeHtml(data.prokey_ref)}${prokeyEditorNote}`
                    : data.puede_editar_prokey_ref
                        ? `Pendiente <span class="detail-badge detail-badge--warn">Prokey pendiente</span>
                           <a href="/requisiciones/${data.id}/prokey-ref" class="detail-inline-link">Agregar referencia Prokey</a>`
                        : 'Pendiente <span class="detail-badge detail-badge--warn">Prokey pendiente</span>';
            const receptorDesignadoHtml = data.receptor_designado
                ? `${escapeHtml(data.receptor_designado.nombre || "-")} (${escapeHtml(data.receptor_designado.rol || "-")})`
                : "-";
            const receptorRealHtml = data.recibido_por_detalle
                ? `${escapeHtml(data.recibido_por_detalle.nombre || "-")} (${escapeHtml(data.recibido_por_detalle.rol || "-")})`
                : data.delivered_to
                    ? escapeHtml(data.delivered_to)
                    : "Pendiente";
            const liquidationComment = data.liquidation_comment ? escapeHtml(data.liquidation_comment) : "—";
            const itemsSection = isLiquidada
                ? `<section class="detail-card detail-items-panel">
                    <div class="detail-panel-bar">
                        <h3 class="detail-card__title"><span class="material-symbols-outlined" aria-hidden="true">list</span>Items liquidados</h3>
                    </div>
                    <div class="detail-table-shell">
                        <table class="detail-items-table detail-items-table--liquidation">
                            <thead>
                                <tr>
                                    <th>Descripción del Item</th>
                                    <th class="qty-col">Entregado</th>
                                    <th class="qty-col">Tipo</th>
                                    <th class="qty-col">Usado</th>
                                    <th class="qty-col">No usado</th>
                                    <th class="qty-col">Regresa</th>
                                    <th class="qty-col" title="Diferencia de retorno: si falta equipo por regresar muestra 'Falta'; si regresó de más muestra 'Extra'">DIF</th>
                                    <th class="qty-col" title="Retornables en reposición usados que regresaron, más excedentes recibidos en bodega. Instalación inicial no genera ingreso PK.">Ingreso PK (Bodega)</th>
                                    <th>Alertas</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${liquidacionRows || '<tr><td colspan="9" class="detail-empty-row">Sin items</td></tr>'}
                            </tbody>
                        </table>
                    </div>
                </section>`
                : `<section class="detail-card detail-items-panel">
                    <div class="detail-panel-bar">
                        <h3 class="detail-card__title"><span class="material-symbols-outlined" aria-hidden="true">list</span>Items solicitados</h3>
                    </div>
                    <div class="detail-table-shell">
                        <table class="detail-items-table detail-items-table--requested">
                            <thead>
                                <tr>
                                    <th>Descripción del Item</th>
                                    <th class="qty-col">Cantidad</th>
                                    ${showDelivered ? '<th class="qty-col">Cant. Despachada</th>' : ""}
                                </tr>
                            </thead>
                            <tbody>
                                ${itemRows || `<tr><td colspan="${itemEmptyColspan}" class="detail-empty-row">Sin items</td></tr>`}
                            </tbody>
                        </table>
                    </div>
                </section>`;
            const isPdfEnabled = ["aprobada", "preparado", "entregada", "no_entregada", "liquidada", "pendiente_prokey", "finalizada_sin_prokey", "liquidada_en_prokey"].includes(data.estado) && !!data.pdf_url;
            const pdfAction = isPdfEnabled
                ? `<a class="detail-action-btn detail-action-btn--pdf" role="button" href="${escapeHtml(data.pdf_url)}" target="_blank" rel="noopener noreferrer"><span class="material-symbols-outlined" aria-hidden="true">picture_as_pdf</span>Ver PDF</a>`
                : `<button type="button" class="detail-action-btn detail-action-btn--disabled" disabled title="${data.estado === "pendiente" ? "Disponible al aprobar" : "No disponible para este estado"}"><span class="material-symbols-outlined" aria-hidden="true">picture_as_pdf</span>Ver PDF</button>`;
            const commentsToggleHtml = `
                <details class="detail-card detail-accordion">
                    <summary>
                        <span class="material-symbols-outlined" aria-hidden="true">expand_more</span>
                        Otros comentarios y proceso
                    </summary>
                    <div class="detail-accordion__content">
                        <div class="detail-comment-block">
                            <span class="detail-kv-label">Aprobación</span>
                            <p>${escapeHtml(data.approval_comment || "-")}</p>
                        </div>
                        <div class="detail-comment-block">
                            <span class="detail-kv-label">Razón rechazo</span>
                            <p>${escapeHtml(data.rejection_reason || "-")}</p>
                        </div>
                        <div class="detail-comment-block">
                            <span class="detail-kv-label">Comentario rechazo</span>
                            <p>${escapeHtml(data.rejection_comment || "-")}</p>
                        </div>
                        <div class="detail-comment-block">
                            <span class="detail-kv-label">Comentario entrega</span>
                            <p>${escapeHtml(data.delivery_comment || "-")}</p>
                        </div>
                    </div>
                </details>
            `;

            modal.classList.add("modal--detail-dashboard");
            content.innerHTML = `
                <div class="detail-dashboard detail-dashboard--stitch">
                    <section class="detail-dashboard-header">
                        <div class="detail-dashboard-heading">
                            <div class="detail-dashboard-title-row">
                                <span class="material-symbols-outlined detail-dashboard-icon" aria-hidden="true">assignment</span>
                                <div>
                                    <h2 class="detail-dashboard-title">Requisición ${escapeHtml(data.folio || "-")}</h2>
                                    <span class="badge info detail-dashboard-created">Creada: ${fmtDateTime(data.created_at)}</span>
                                </div>
                            </div>
                        </div>
                        <div class="detail-dashboard-actions">
                            ${pdfAction}
                        </div>
                    </section>
                    <section class="detail-dashboard-grid detail-dashboard-grid--top">
                        <div class="detail-card detail-card--general">
                            <h3 class="detail-card__title"><span class="material-symbols-outlined" aria-hidden="true">business</span>Información general</h3>
                            <div class="detail-kv-list">
                                <div class="detail-kv"><span class="detail-kv-label">Cliente</span><span class="detail-kv-value">${escapeHtml(data.cliente_nombre || "-")}</span></div>
                                <div class="detail-kv"><span class="detail-kv-label">Código cliente</span><span class="detail-kv-value">${escapeHtml(data.cliente_codigo || "-")}</span></div>
                                <div class="detail-kv"><span class="detail-kv-label">Ruta principal</span><span class="detail-kv-value">${escapeHtml(data.cliente_ruta_principal || "-")}</span></div>
                                <div class="detail-kv"><span class="detail-kv-label">Solicitante</span><span class="detail-kv-value">${escapeHtml(data.solicitante || "-")}</span></div>
                                <div class="detail-kv"><span class="detail-kv-label">Receptor designado</span><span class="detail-kv-value">${receptorDesignadoHtml}</span></div>
                                <div class="detail-kv"><span class="detail-kv-label">Recibió / firmó</span><span class="detail-kv-value">${receptorRealHtml}</span></div>
                            </div>
                        </div>
                        <div class="detail-card detail-card--status">
                            <h3 class="detail-card__title"><span class="material-symbols-outlined" aria-hidden="true">fact_check</span>Estado liquidación</h3>
                            <div class="detail-kv-list">
                                <div class="detail-kv"><span class="detail-kv-label">Estado</span><span class="detail-kv-value">${escapeHtml(data.estado || "-")}</span></div>
                                <div class="detail-kv"><span class="detail-kv-label">Resultado entrega</span><span class="detail-kv-value">${resultHtml}</span></div>
                                <div class="detail-kv"><span class="detail-kv-label">Ref Prokey</span><span class="detail-kv-value">${prokeyRefHtml}</span></div>
                            </div>
                        </div>
                        <div class="detail-card detail-card--alerts ${alertCardClass}">
                            <h3 class="detail-card__title"><span class="material-symbols-outlined" aria-hidden="true">warning</span>Alertas de conciliación</h3>
                            <div class="detail-kv-list">
                                <div class="detail-kv"><span class="detail-kv-label">Total</span><span class="detail-kv-value">${allAlerts.length} detectadas</span></div>
                                <div class="detail-kv"><span class="detail-kv-label">Alta severidad</span><span class="detail-kv-value">${highAlerts}</span></div>
                                <div class="detail-kv"><span class="detail-kv-label">Tipos frecuentes</span><span class="detail-kv-value">${topAlertTypes}</span></div>
                            </div>
                        </div>
                        <div class="detail-card detail-card--timeline">
                            <h3 class="detail-card__title"><span class="material-symbols-outlined" aria-hidden="true">schedule</span>Línea de tiempo del flujo</h3>
                            <div class="detail-timeline-wrap">
                                <ol class="detail-timeline">
                                    ${timelineRows || '<li class="detail-timeline__item detail-timeline__item--empty"><div class="detail-timeline__title">Sin movimientos</div><div class="detail-timeline__meta">-</div></li>'}
                                </ol>
                            </div>
                        </div>
                    </section>
                    ${itemsSection}
                    <section class="detail-dashboard-grid detail-dashboard-grid--bottom">
                        <div class="detail-card detail-card--text">
                            <h3 class="detail-card__title"><span class="material-symbols-outlined" aria-hidden="true">description</span>Justificación</h3>
                            <p class="detail-copy">${escapeHtml(data.justificacion || "-")}</p>
                        </div>
                        <div class="detail-card detail-card--text">
                            <h3 class="detail-card__title"><span class="material-symbols-outlined" aria-hidden="true">chat</span>Comentario de liquidación</h3>
                            <p class="detail-copy detail-copy--muted">${liquidationComment}</p>
                        </div>
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
