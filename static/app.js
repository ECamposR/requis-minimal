let itemCount = 1;

function renderItemOptions() {
    const catalogo = window.CATALOGO_ITEMS || [];
    const options = ['<option value="">Seleccionar item...</option>'];
    for (const item of catalogo) {
        options.push(`<option value="${item}">${item}</option>`);
    }
    return options.join("");
}

function agregarItem() {
    const container = document.getElementById("items-container");
    if (!container) return;

    const div = document.createElement("div");
    div.className = "item-row";
    div.innerHTML = `
        <select name="items[${itemCount}][descripcion]" required>
            ${renderItemOptions()}
        </select>
        <input type="number" name="items[${itemCount}][cantidad]" placeholder="Cantidad" step="0.01" min="0.01" required>
        <button type="button" onclick="this.parentElement.remove()">X</button>
    `;
    container.appendChild(div);
    itemCount++;
}

function verDetalle(id) {
    fetch(`/api/requisiciones/${id}`)
        .then((r) => r.json())
        .then((data) => {
            const content = document.getElementById("modal-content");
            const modal = document.getElementById("modal-detalle");
            if (!content || !modal) return;

            content.innerHTML = `
                <p><strong>Folio:</strong> ${data.folio}</p>
                <p><strong>Solicitante:</strong> ${data.solicitante || "-"}</p>
                <p><strong>Justificacion:</strong> ${data.justificacion}</p>
                <p><strong>Aprobado por:</strong> ${data.approved_by || "-"}</p>
                <p><strong>Comentario aprobacion:</strong> ${data.approval_comment || "-"}</p>
                <p><strong>Rechazado por:</strong> ${data.rejected_by || "-"}</p>
                <p><strong>Razon rechazo:</strong> ${data.rejection_reason || "-"}</p>
                <p><strong>Comentario rechazo:</strong> ${data.rejection_comment || "-"}</p>
                <p><strong>Entregado por:</strong> ${data.delivered_by || "-"}</p>
                <p><strong>Resultado entrega:</strong> ${data.delivery_result || "-"}</p>
                <p><strong>Recibio:</strong> ${data.delivered_to || "-"}</p>
                <p><strong>Comentario entrega:</strong> ${data.delivery_comment || "-"}</p>
                <ul>${(data.items || []).map((i) => `<li>${i.descripcion}: solicitado ${i.cantidad} / entregado ${i.cantidad_entregada ?? "-"}</li>`).join("")}</ul>
            `;
            modal.showModal();
        });
}

function cerrarModal() {
    const modal = document.getElementById("modal-detalle");
    if (modal) modal.close();
}
