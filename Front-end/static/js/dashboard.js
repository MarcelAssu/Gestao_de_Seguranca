async function carregarDashboard() {
    const res = await fetch('/dashboard/dados');
    const d = await res.json();

    // Cards
    document.getElementById('entradas-count').innerText = d.entradas_count;
    document.getElementById('entradas-ultima').innerText = 'Última: ' + d.entradas_ultima;
    document.getElementById('saidas-count').innerText = d.saidas_count;
    document.getElementById('saidas-ultima').innerText = 'Última: ' + d.saidas_ultima;
    document.getElementById('negadas-count').innerText = d.negadas;
    document.getElementById('invasoes-count').innerText = d.invasoes;

    // Tabelas
    preencherTabela('tbody-sala', d.na_sala);
    preencherTabela('tbody-entradas', d.ultimas_entradas);
    preencherTabela('tbody-saidas', d.ultimas_saidas);
    preencherTabelaInvasao('tbody-invasoes', d.lista_invasoes);
}

function preencherTabela(id, lista) {
    const tbody = document.getElementById(id);
    tbody.innerHTML = '';
    lista.forEach(item => {
        tbody.innerHTML += `
            <tr>
                <td>${item.nome}</td>
                <td>${item.horario}</td>
                <td>${item.tag}</td>
            </tr>`;
    });
}

function preencherTabelaInvasao(id, lista) {
    const tbody = document.getElementById(id);
    tbody.innerHTML = '';
    lista.forEach(item => {
        tbody.innerHTML += `
            <tr>
                <td>RFID desconhecido</td>
                <td>${item.horario}</td>
                <td>${item.tag}</td>
            </tr>`;
    });
}

// Atualiza a cada 5 segundos (tempo real)
carregarDashboard();
setInterval(carregarDashboard, 5000);