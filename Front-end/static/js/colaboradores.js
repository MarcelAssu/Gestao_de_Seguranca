document.addEventListener("DOMContentLoaded", () => {

    const modal = document.getElementById("modalOverlay");
    const openModal = document.getElementById("openModal");
    const closeModal = document.getElementById("closeModal");

    openModal.addEventListener("click", () => {
        modal.style.display = "flex";
        console.log("aqui")
    });

    closeModal.addEventListener("click", () => {
        modal.style.display = "none";
    });

    window.addEventListener("click", (e) => {
        if (e.target === modal) {
            modal.style.display = "none";
        }
    });

    const form = document.getElementById("userForm");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const nome = document.getElementById("nome").value;
        const rfid = document.getElementById("rfid").value;
        const cargo = document.getElementById("cargo").value;
        const acesso = document.querySelector('input[name="acesso"]:checked').value;
        const status = document.querySelector('input[name="status"]:checked').value;

        await fetch("/usuarios", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                tag: rfid,
                nome: nome,
                cargo: cargo,
                autorizado: acesso === "Sim"
            })
        });

        form.reset();
        modal.style.display = "none";
        carregarUsuarios();
    });

    carregarUsuarios();

});

async function carregarUsuarios() {
    const resposta = await fetch("/usuarios");
    const usuarios = await resposta.json();
    const tbody = document.querySelector("tbody");
    tbody.innerHTML = "";

    Object.entries(usuarios).forEach(([tag, usuario]) => {
        tbody.innerHTML += `
            <tr>
                <td><input class="checkbox" type="checkbox"></td>
                <td>${usuario.nome}</td>
                <td>${tag}</td>
                <td>${usuario.cargo}</td>
                <td class="${usuario.status === 'ativo' ? 'status-ativo' : 'status-inativo'}">
                    ${usuario.status}
                </td>
                <td>--</td>
            </tr>
        `;
    });
}