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

function renderItemOptions() {
    const catalogo = window.CATALOGO_ITEMS || [];
    const options = ['<option value="">Seleccionar item...</option>'];
    for (const item of catalogo) {
        const safeItem = escapeHtml(item);
        options.push(`<option value="${safeItem}">${safeItem}</option>`);
    }
    return options.join("");
}

function getCurrentSelectedValues() {
    return Array.from(document.querySelectorAll("#items-container select[name*='[descripcion]']"))
        .map((s) => s.value)
        .filter((v) => v);
}

function handleItemSelectChange(select) {
    const selectedValue = select.value;
    if (!selectedValue) {
        syncItemSelectors();
        return;
    }

    const duplicate = Array.from(document.querySelectorAll("#items-container select[name*='[descripcion]']"))
        .some((other) => other !== select && other.value === selectedValue);

    if (duplicate) {
        select.value = "";
        select.setCustomValidity("Este item ya fue agregado en otra fila.");
        select.reportValidity();
        select.setCustomValidity("");
    }
    syncItemSelectors();
}

function syncItemSelectors() {
    const selects = Array.from(document.querySelectorAll("#items-container select[name*='[descripcion]']"));
    const selected = getCurrentSelectedValues();
    for (const select of selects) {
        const ownValue = select.value;
        for (const option of select.options) {
            if (!option.value) continue;
            option.disabled = option.value !== ownValue && selected.includes(option.value);
        }
    }
}

function eliminarItem(button) {
    const row = button.closest(".item-row");
    if (row) row.remove();
    syncItemSelectors();
}

function canAddItemRow(container) {
    const rows = Array.from(container.querySelectorAll(".item-row"));
    if (rows.length === 0) return true;

    const lastRow = rows[rows.length - 1];
    const select = lastRow.querySelector("select[name*='[descripcion]']");
    const qtyInput = lastRow.querySelector("input[name*='[cantidad]']");

    if (select && !select.value) {
        select.reportValidity();
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
    return true;
}

function agregarItem() {
    const container = document.getElementById("items-container");
    if (!container) return;
    if (!canAddItemRow(container)) return;

    const div = document.createElement("div");
    div.className = "item-row";
    div.innerHTML = `
        <select name="items[${itemCount}][descripcion]" required>
            ${renderItemOptions()}
        </select>
        <input type="number" name="items[${itemCount}][cantidad]" placeholder="Cantidad" step="0.01" min="0.01" required>
        <button type="button" onclick="eliminarItem(this)">X</button>
    `;
    container.appendChild(div);
    const select = div.querySelector("select");
    if (select) {
        select.addEventListener("change", () => handleItemSelectChange(select));
    }
    itemCount++;
    syncItemSelectors();
}

document.addEventListener("DOMContentLoaded", () => {
    const selects = document.querySelectorAll("#items-container select[name*='[descripcion]']");
    for (const select of selects) {
        select.addEventListener("change", () => handleItemSelectChange(select));
    }
    syncItemSelectors();
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
                headerTitle.textContent = `Detalle de Requisicion: ${data.folio || "-"}`;
            }
            const items = Array.isArray(data.items) ? data.items : [];
            const showDelivered = items.some((i) => i.cantidad_entregada !== null && i.cantidad_entregada !== undefined);
            const rows = items.map((i) => `
                <tr>
                    <td>${escapeHtml(i.descripcion || "-")}</td>
                    <td class="qty-col qty-solicitada">${fmtQty(i.cantidad)}</td>
                    ${showDelivered ? `<td class="qty-col qty-despachada">${fmtQty(i.cantidad_entregada)}</td>` : ""}
                </tr>
            `).join("");
            const emptyColspan = showDelivered ? 3 : 2;

            content.innerHTML = `
                <section class="detalle-items-section">
                    <h4>Items Solicitados</h4>
                    <div class="detalle-items-wrap">
                        <table class="detalle-items-table">
                            <thead>
                                <tr>
                                    <th>Item / Producto</th>
                                    <th class="qty-col">Cant. Solicitada</th>
                                    ${showDelivered ? '<th class="qty-col">Cant. Despachada</th>' : ""}
                                </tr>
                            </thead>
                            <tbody>
                                ${rows || `<tr><td colspan="${emptyColspan}">Sin items</td></tr>`}
                            </tbody>
                        </table>
                    </div>
                </section>
                <section class="detalle-content-grid">
                    <section class="detalle-block detalle-main">
                        <h4>Informacion General</h4>
                        <div class="detalle-meta-grid">
                            <div class="meta-line"><span>Solicitante</span><strong>${escapeHtml(data.solicitante || "-")}</strong></div>
                            <div class="meta-line"><span>Cod. cliente</span><strong>${escapeHtml(data.cliente_codigo || "-")}</strong></div>
                            <div class="meta-line"><span>Cliente</span><strong>${escapeHtml(data.cliente_nombre || "-")}</strong></div>
                            <div class="meta-line"><span>Ruta principal</span><strong>${escapeHtml(data.cliente_ruta_principal || "-")}</strong></div>
                        </div>
                        <div class="detalle-justificacion">
                            <span>Justificacion</span>
                            <p>${escapeHtml(data.justificacion || "-")}</p>
                        </div>
                    </section>
                    <aside class="detalle-side">
                        <section class="detalle-block">
                            <h4>Estado del Flujo</h4>
                            <dl class="detalle-list">
                                <div><dt>Aprobado por</dt><dd>${escapeHtml(data.approved_by || "-")}</dd></div>
                                <div><dt>Rechazado por</dt><dd>${escapeHtml(data.rejected_by || "-")}</dd></div>
                                <div><dt>Entregado por</dt><dd>${escapeHtml(data.delivered_by || "-")}</dd></div>
                                <div><dt>Recibio</dt><dd>${escapeHtml(data.delivered_to || "-")}</dd></div>
                                <div><dt>Resultado entrega</dt><dd>${escapeHtml(data.delivery_result || "-")}</dd></div>
                            </dl>
                        </section>
                        <section class="detalle-block">
                            <h4>Comentarios</h4>
                            <dl class="detalle-list detalle-list-comments">
                                <div><dt>Aprobacion</dt><dd>${escapeHtml(data.approval_comment || "-")}</dd></div>
                                <div><dt>Razon rechazo</dt><dd>${escapeHtml(data.rejection_reason || "-")}</dd></div>
                                <div><dt>Comentario rechazo</dt><dd>${escapeHtml(data.rejection_comment || "-")}</dd></div>
                                <div><dt>Entrega</dt><dd>${escapeHtml(data.delivery_comment || "-")}</dd></div>
                            </dl>
                        </section>
                    </aside>
                </section>
            `;
            modal.showModal();
        });
}

function cerrarModal() {
    const modal = document.getElementById("modal-detalle");
    if (modal) modal.close();
}
