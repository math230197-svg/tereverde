const API_URL = "https://tereverde.onrender.com/api";

// 1. Função das Abas (Mantém o funcionamento das páginas dos parques)
function openTab(evt, tabName) {
    const tabcontent = document.getElementsByClassName("tab-content");
    for (let i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }

    const tablinks = document.getElementsByClassName("tab-link");
    for (let i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }

    const target = document.getElementById(tabName);
    if (target) {
        target.style.display = "block";
    }
    if (evt && evt.currentTarget) {
        evt.currentTarget.className += " active";
    }
}

// 2. Integração com o Back-End (Condições das Trilhas e Eventos/Temporadas)
async function carregarDadosDoBackend() {
    try {
        const resposta = await fetch(`${API_URL}/dados/`);
        if (!resposta.ok) return;
        const dados = await resposta.json();

        // Atualiza a lista <ul class="condicoes"> no parque.html
        const listaCondicoes = document.querySelector("ul.condicoes");
        if (listaCondicoes && dados.condicoes) {
            listaCondicoes.innerHTML = "";
            dados.condicoes.forEach(item => {
                const li = document.createElement("li");
                li.className = item.status; // 'aberto', 'fechado' ou 'atencao'
                li.textContent = `${item.nome}: ${item.descricao}`;
                listaCondicoes.appendChild(li);
            });
        }

        // Insere a seção de Eventos e Temporadas na aba "Info" do parque.html
        const abaInfo = document.getElementById("Info");
        if (abaInfo && dados.eventos) {
            let containerEventos = document.getElementById("eventos-dinamicos");
            if (!containerEventos) {
                containerEventos = document.createElement("div");
                containerEventos.id = "eventos-dinamicos";
                containerEventos.style.marginTop = "20px";
                abaInfo.appendChild(containerEventos);
            }

            let htmlEventos = `<p><strong>Eventos e Temporadas Ativas:</strong></p><ul>`;
            dados.eventos.forEach(ev => {
                htmlEventos += `<li><strong>[${ev.parque}] ${ev.titulo}</strong> — Data: ${ev.data} (${ev.disponibilidade})</li>`;
            });
            htmlEventos += `</ul>`;
            containerEventos.innerHTML = htmlEventos;
        }
    } catch (erro) {
        console.log("Modo estático ativo (Back-end local offline).");
    }
}

document.addEventListener("DOMContentLoaded", carregarDadosDoBackend); 
