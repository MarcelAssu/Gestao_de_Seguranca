let usuariosCadastrados = {};

document.addEventListener("DOMContentLoaded", () => {
    const modal = document.getElementById("modalOverlay");
    const openModal = document.getElementById("openModal");
    const closeModal = document.getElementById("closeModal");
    const form = document.getElementById("userForm");

    // Seleção robusta dos botões baseada no texto interno
    let btnEditar, btnExcluir;
    document.querySelectorAll(".button-secondary").forEach(btn => {
        if (btn.innerText.includes("Editar")) btnEditar = btn;
        if (btn.innerText.includes("Excluir")) btnExcluir = btn;
    });

    // --- ABRIR MODAL (CADASTRO) ---
    if (openModal) {
        openModal.addEventListener("click", () => {
            form.reset();
            document.getElementById("rfid").readOnly = false;
            document.querySelector(".modal-title-container h2").innerText = "Cadastrar Usuário";
            modal.style.display = "flex";
        });
    }

    // --- FUNÇÃO EDITAR ---
    if (btnEditar) {
        btnEditar.addEventListener("click", () => {
            const selecionado = document.querySelector("tbody input.checkbox:checked");
           
            if (!selecionado) {
                alert("Selecione um usuário para editar.");
                return;
            }

            const linha = selecionado.closest("tr");
            // Puxa o RFID direto do atributo 'data-tag' que salvamos na linha
            const tag = linha.getAttribute("data-tag");

            console.log("Editando TAG:", tag);

            const usuario = usuariosCadastrados[tag];

            if (usuario) {
                document.getElementById("nome").value = usuario.nome || "";
                document.getElementById("matricula").value = usuario.matricula || "";
                document.getElementById("rfid").value = tag;
                document.getElementById("rfid").readOnly = true;
                document.getElementById("cargo").value = usuario.cargo || "";

                // Ajusta os botões de rádio (Sim/Não)
                const radioAcesso = document.querySelector(`input[name="acesso"][value="${usuario.autorizado ? 'Sim' : 'Não'}"]`);
                if (radioAcesso) radioAcesso.checked = true;

                // Ajusta os botões de status (Ativo/Inativo)
                const statusTexto = usuario.status === 'ativo' ? 'Ativo' : 'Inativo';
                const radioStatus = document.querySelector(`input[name="status"][value="${statusTexto}"]`);
                if (radioStatus) radioStatus.checked = true;

                document.querySelector(".modal-title-container h2").innerText = "Editar Usuário";
                modal.style.display = "flex";
            } else {
                alert("Erro: não foi possível encontrar os dados deste usuário na memória.");
            }
        });
    }

    // --- FUNÇÃO EXCLUIR ---
    if (btnExcluir) {
        btnExcluir.addEventListener("click", async () => {
            const selecionados = document.querySelectorAll("tbody input.checkbox:checked");
            if (selecionados.length === 0) return alert("Selecione ao menos um usuário.");

            if (confirm(`Excluir ${selecionados.length} usuário(s)?`)) {
                for (let cb of selecionados) {
                    const tagParaDeletar = cb.closest("tr").getAttribute("data-tag");
                    if (tagParaDeletar) {
                        await fetch(`/usuarios/${tagParaDeletar}`, { method: "DELETE" });
                    }
                }
                carregarUsuarios();
            }
        });
    }

    // --- SALVAR (POST) ---
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const payload = {
            tag: document.getElementById("rfid").value,
            nome: document.getElementById("nome").value,
            matricula: document.getElementById("matricula").value,
            cargo: document.getElementById("cargo").value,
            autorizado: document.querySelector('input[name="acesso"]:checked').value === "Sim",
            status: document.querySelector('input[name="status"]:checked').value.toLowerCase()
        };

        const response = await fetch("/usuarios", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            modal.style.display = "none";
            // Força a atualização da memória e da tela
            await carregarUsuarios();
        }
    });

    if (closeModal) {
        closeModal.addEventListener("click", () => modal.style.display = "none");
    }

    carregarUsuarios();
});

// --- RENDERIZAR TABELA ---
async function carregarUsuarios() {
    const resposta = await fetch("/usuarios");
    usuariosCadastrados = await resposta.json();
   
    const tbody = document.querySelector("tbody");
    if (!tbody) return;
   
    tbody.innerHTML = "";
    Object.entries(usuariosCadastrados).forEach(([tag, usuario]) => {
        // A MÁGICA: Guardamos a tag no atributo 'data-tag' da linha <tr>
        const tr = document.createElement("tr");
        tr.setAttribute("data-tag", tag);
       
        tr.innerHTML = `
            <td><input class="checkbox" type="checkbox"></td>
            <td>${usuario.nome}</td>
            <td>${tag}</td>
            <td>${usuario.matricula || '--'}</td>
            <td>${usuario.cargo}</td>
            <td class="${usuario.status === 'ativo' ? 'status-ativo' : 'status-inativo'}">
                ${usuario.status}
            </td>
            <td>--</td>
        `;
        tbody.appendChild(tr);
    });
}