let itemCount = 1;

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

function getAccionSugerida(alertCounts) {
    const count = (label) => Number(alertCounts?.[label] || 0);
    if (count("Retorno extra") > 0) {
        return "Acción sugerida: Revisar retorno extra del cliente y preparar ingreso en Prokey.";
    }
    if (count("Faltante") > 0) {
        return "Acción sugerida: Conciliar faltante con técnico/cliente antes de cerrar en Prokey.";
    }
    if (count("Inconsistencia") > 0) {
        return "Acción sugerida: Revisar cantidades ingresadas (posible error de captura).";
    }
    if (count("Sobrante") > 0) {
        return "Acción sugerida: Validar sobrante y documentar motivo.";
    }
    return "";
}

function getCurrentSelectedValues() {
    return Array.from(document.querySelectorAll("#items-container input[name*='[descripcion]']"))
        .map((input) => input.value.trim())
        .filter((v) => v);
}

function setItemError(message) {
    const errorEl = document.getElementById("item-error");
    if (!errorEl) return;
    errorEl.textContent = message || "";
}

function validateCatalogItemInput(input, report = false) {
    if (!input) return false;
    const value = input.value.trim();
    const catalogo = window.CATALOGO_ITEMS || [];
    const existe = catalogo.includes(value);

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
    const inputs = Array.from(document.querySelectorAll("#items-container input[name*='[descripcion]']"));
    if (inputs.length === 0) return;
    let hasInvalid = false;
    for (const input of inputs) {
        const valid = validateCatalogItemInput(input, false);
        if (!valid && input.value.trim()) {
            hasInvalid = true;
        }
    }
    if (hasInvalid) {
        setItemError("Selecciona un item válido del catálogo.");
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
        const qty = Number(qtyInput.value);
        const qtyValida = qtyInput.value !== "" && !Number.isNaN(qty) && qty > 0;
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

    const qty = document.createElement("input");
    qty.type = "number";
    qty.name = `items[${itemCount}][cantidad]`;
    qty.placeholder = "Cantidad";
    qty.step = "0.01";
    qty.min = "0.01";
    qty.required = true;

    const btn = document.createElement("button");
    btn.type = "button";
    btn.textContent = "X";
    btn.addEventListener("click", () => eliminarItem(btn));

    div.append(input, qty, btn);
    container.appendChild(div);
    itemCount++;
    syncItemInputs();
}

document.addEventListener("DOMContentLoaded", () => {
    const itemInputs = document.querySelectorAll("#items-container input[name*='[descripcion]']");
    for (const input of itemInputs) {
        input.addEventListener("change", () => handleItemInputChange(input));
        input.addEventListener("blur", () => handleItemInputChange(input));
    }
    const crearForm = document.querySelector('form[action="/crear"]');
    if (crearForm) {
        crearForm.addEventListener("submit", (event) => {
            const inputs = Array.from(document.querySelectorAll("#items-container input[name*='[descripcion]']"));
            const invalidInput = inputs.find((input) => !validateCatalogItemInput(input, false));
            if (invalidInput) {
                event.preventDefault();
                setItemError(invalidInput.validationMessage || "Selecciona un item válido del catálogo.");
                invalidInput.reportValidity();
            }
        });
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
            const isLiquidada = data.estado === "liquidada";
            const showDelivered = items.some(
                (i) => i.cantidad_entregada !== null && i.cantidad_entregada !== undefined
            );
            const itemRows = items
                .map((i) => {
                    const qe = i.cantidad_entregada;
                    const hasQe = qe !== null && qe !== undefined;
                    const isZero = hasQe && Number(qe) === 0;
                    const despCls = isZero
                        ? "qty-col qty-despachada qty-zero"
                        : "qty-col qty-despachada";
                    return `<tr>
                    <td>${escapeHtml(i.descripcion || "-")}</td>
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
                    const mode = (i.mode || "RETORNABLE").toUpperCase();
                    const ingresoPk = mode === "RETORNABLE" ? fmtQty(i.pk_ingreso_qty) : '<span class="muted">—</span>';
                    const differenceText = difference > 0 ? `+${fmtQty(difference)}` : fmtQty(difference);
                    return `<tr>
                        <td><strong>${escapeHtml(i.descripcion || "-")}</strong>${noteHtml}</td>
                        <td class="qty-col td-num">${fmtQty(i.cantidad_entregada)}</td>
                        <td class="qty-col td-center">${escapeHtml(mode)}</td>
                        <td class="qty-col td-num">${fmtQty(i.used ?? i.qty_used)}</td>
                        <td class="qty-col td-num">${fmtQty(i.not_used ?? i.qty_left_at_client)}</td>
                        <td class="qty-col td-num">${fmtQty(i.returned ?? i.qty_returned_to_warehouse)}</td>
                        <td class="qty-col td-num"><span class="${differenceCls}">${differenceText}</span></td>
                        <td class="qty-col td-num">
                            <span class="pk-help" title="Pendiente de ingresar en Prokey por bodega (solo retornables)">${ingresoPk}</span>
                        </td>
                        <td>${alertBadges}</td>
                    </tr>`;
                })
                .join("");

            const resultVal = data.delivery_result || "-";
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
            const accionSugerida = getAccionSugerida(alertCounts);
            const alertCardClass = highAlerts > 0 ? "dd-card--alert dd-card--alert-high" : allAlerts.length > 0 ? "dd-card--alert" : "";
            const prokeyRefHtml = data.prokey_ref
                ? escapeHtml(data.prokey_ref)
                : `Pendiente <span class="badge warning prokey-pending-badge">Prokey pendiente</span>
                   <a href="/requisiciones/${data.id}/prokey-ref" class="prokey-add-link">Agregar referencia Prokey</a>`;
            const liquidationComment = data.liquidation_comment
                ? escapeHtml(data.liquidation_comment)
                : "—";
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
                                <th class="qty-col" title="Diferencia (Esperado - Regresa)">DIF</th>
                                <th class="qty-col" title="Pendiente de ingresar en Prokey por bodega (solo retornables)">Ingreso PK</th>
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
            const isPdfEnabled = data.estado === "liquidada" && !!data.pdf_url;
            const pdfAction = isPdfEnabled
                ? `<a class="secondary" role="button" href="${escapeHtml(data.pdf_url)}" target="_blank" rel="noopener noreferrer">Ver PDF</a>`
                : `<button type="button" class="secondary btn-disabled" disabled title="${data.estado === "liquidada" ? "En desarrollo" : "Disponible al liquidar"}">Ver PDF</button>`;
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
                    </article>
                    <article class="detalle-block dashboard-card dd-card">
                        <h4 class="dd-card-title">Estado liquidación</h4>
                        <div class="dd-kv"><div class="dd-kv-label">Estado</div><div class="dd-kv-value">${escapeHtml(data.estado || "-")}</div></div>
                        <div class="dd-kv"><div class="dd-kv-label">Resultado entrega</div><div class="dd-kv-value">${resultHtml}</div></div>
                        <div class="dd-kv"><div class="dd-kv-label">Por</div><div class="dd-kv-value">${escapeHtml(data.liquidated_by_name || data.delivered_by || "-")}</div></div>
                        <div class="dd-kv"><div class="dd-kv-label">Ref Prokey</div><div class="dd-kv-value">${prokeyRefHtml}</div></div>
                    </article>
                    <article class="detalle-block dashboard-card dd-card ${alertCardClass}">
                        <h4 class="dd-card-title">Alertas de conciliación</h4>
                        <div class="dd-kv"><div class="dd-kv-label">Total</div><div class="dd-kv-value">${allAlerts.length} detectadas</div></div>
                        <div class="dd-kv"><div class="dd-kv-label">Alta severidad</div><div class="dd-kv-value">${highAlerts}</div></div>
                        <div class="dd-kv"><div class="dd-kv-label">Tipos frecuentes</div><div class="dd-kv-value">${topAlertTypes}</div></div>
                        ${accionSugerida ? `<div class="dd-kv"><div class="dd-kv-label">Acción sugerida</div><div class="dd-kv-value dd-kv-muted">${escapeHtml(accionSugerida)}</div></div>` : ""}
                    </article>
                    <article class="detalle-block dashboard-card dd-card dashboard-timeline">
                        <h4 class="dd-card-title">Línea de tiempo del flujo</h4>
                        <ol class="dd-timeline">
                            ${timelineRows || '<li class="dd-timeline__item"><div class="dd-timeline__title">Sin movimientos</div><div class="dd-timeline__meta">-</div></li>'}
                        </ol>
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
