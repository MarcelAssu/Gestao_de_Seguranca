const btnLogin = document.getElementById("btnLogin");
btnLogin.addEventListener("click", async () => {
    const usuario = document.getElementById("usuario").value;
    const senha = document.getElementById("senha").value;
    const erro = document.getElementById("erro-login");
    try {

        const resposta = await fetch("/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                usuario: usuario,
                senha: senha
            })
        });

        const dados = await resposta.json();
        if (dados.autenticado) {
            window.location.href = "/gerencia-users";

        } else {
            erro.innerText = "Usuário ou senha inválidos";
            erro.style.color = "red";

        }

    } catch (e) {
        erro.innerText = "Erro ao conectar com o servidor";
        erro.style.color = "red";

    }

});