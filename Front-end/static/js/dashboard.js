async function carregarHistoricoInicial() {
    try {
        const res = await fetch('/dashboard/dados');
        const d = await res.json();

        atualizarCards(d.entradas_count, d.entradas_ultima, d.saidas_count, d.saidas_ultima, d.negadas, d.invasoes);
        preencherTabela('tbody-sala', d.na_sala);
        preencherTabela('tbody-entradas', d.ultimas_entradas);
        preencherTabela('tbody-saidas', d.ultimas_saidas);
        preencherTabelaInvasao('tbody-invasoes', d.lista_invasoes);
    } catch (error) {
        console.error("Erro ao buscar dados do servidor:", error);
    }
}

function atualizarCards(ent, entUltima, sai, saiUltima, neg, inv) {
    document.getElementById('entradas-count').innerText = ent;
    document.getElementById('entradas-ultima').innerText = 'Última: ' + entUltima;
    document.getElementById('saidas-count').innerText = sai;
    document.getElementById('saidas-ultima').innerText = 'Última: ' + saiUltima;
    document.getElementById('negadas-count').innerText = neg;
    document.getElementById('invasoes-count').innerText = inv;
}

function preencherTabela(id, lista) {
    const tbody = document.getElementById(id);
    tbody.innerHTML = '';
    lista.forEach(item => {
        tbody.innerHTML += `<tr><td>${item.nome}</td><td>${item.horario}</td><td>${item.tag}</td></tr>`;
    });
}

function preencherTabelaInvasao(id, lista) {
    const tbody = document.getElementById(id);
    tbody.innerHTML = '';
    lista.forEach(item => {
        tbody.innerHTML += `<tr><td>RFID desconhecido</td><td>${item.horario}</td><td>${item.tag}</td></tr>`;
    });
}

// 2. Configura o PubNub para atualizações instantâneas via nuvem
const pubnub = new PubNub({
    publishKey: 'pub-c-321e2501-878f-49c7-ac68-046cd8820f0b',
    subscribeKey: 'sub-c-41217ff2-2c55-4aa7-a562-e0ac1a0624c5',
    userId: "cliente_dashboard"
});

pubnub.addListener({
    message: function(evento) {
        console.log("Chegou evento do PubNub em tempo real!", evento.message);
        // Toda vez que alguém passa a tag e o PubNub avisa, recarregamos as tabelas na hora
        carregarHistoricoInicial();
    }
});

pubnub.subscribe({ channels: ["seguranca_sala"] });

// Roda a primeira vez ao abrir a página
carregarHistoricoInicial();