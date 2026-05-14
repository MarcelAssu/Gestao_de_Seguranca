
Milena Alves (1136912), Nicole Arend (1136202), Marcel Assunção (1136750) e Gabriel Cannini (1135604). 

# SafeEntry RFID - Sistema de Gestão e Controle de Acesso Distribuído

## Descrição do Projeto
O SafeEntry RFID é uma solução robusta e integrada para o monitoramento e controle de acesso físico em ambientes restritos. O sistema utiliza tecnologia de identificação por radiofrequência (RFID) para autenticar usuários, processar permissões em tempo real e gerar registros detalhados de presença e segurança. Através de uma arquitetura distribuída que conecta hardware dedicado, serviços em nuvem e uma interface de gestão centralizada, o projeto oferece total visibilidade operacional e auditoria automatizada.

## Visão Geral
O propósito fundamental do sistema é substituir métodos tradicionais de registro manual por um ecossistema digital inteligente e resiliente. Ele resolve problemas críticos como a entrada de pessoas não autorizadas, a falta de dados sobre o tempo de permanência em salas específicas e a perda de registros durante falhas de conectividade. O sistema é ideal para escritórios, laboratórios de pesquisa ou almoxarifados que exigem um histórico confiável de quem acessou o local, por quanto tempo e em quais horários.

## Funcionalidades
* Autenticação por Tags RFID: Validação instantânea de usuários cadastrados no banco de dados.
* Monitoramento em Tempo Real: Dashboard web que exibe entradas, saídas e tentativas de invasão no exato momento em que ocorrem.
* Gestão de Usuários (CRUD): Interface completa para cadastrar, consultar, editar e excluir colaboradores, incluindo campos específicos para Matrícula e Cargo.
* Resiliência e Modo Offline: Capacidade de operar sem conexão com a internet, utilizando cache local de usuários e armazenamento temporário de eventos para sincronização posterior.
* Feedback Visual e Sonoro: Utilização de componentes de hardware para sinalização de acesso permitido ou negado através de LEDs e Buzzer.
* Análise de Dados Avançada: Módulo dedicado para processamento de logs, permitindo calcular tempos de permanência e identificar padrões de tentativas de acesso indevido.
* Sincronização Remota: Atualização dinâmica da lista de acesso no hardware assim que alterações são feitas na interface administrativa.

## Tecnologias Utilizadas
* Hardware e IoT: Raspberry Pi como unidade de processamento de borda e Leitor RFID RC522 para captura de dados físicos.
* Ambiente de Execução: Python como linguagem central para a lógica de hardware e para o servidor de aplicação.
* Back-end: Microframework Flask para disponibilização de rotas de API e gerenciamento de requisições.
* Banco de Dados: SQLite3 para persistência local de informações cadastrais e registros de log.
* Mensageria e Sincronismo: Serviço PubNub para comunicação em tempo real via arquitetura Publish/Subscribe.
* Front-end: Desenvolvimento estruturado em HTML5, CSS3 e JavaScript (Vanilla) para alta performance e baixa dependência de bibliotecas externas.
* Ciência de Dados: Biblioteca Pandas para a análise estatística dos registros de movimentação.

## Arquitetura do Projeto
O sistema segue uma arquitetura modular dividida em três camadas principais:

1. Camada de Borda (Edge): Composta pela Raspberry Pi, que lida com a interface física de sensores e atuadores. Ela toma decisões rápidas de acesso e mantém a persistência local em caso de instabilidade de rede.
2. Camada de Comunicação: Utiliza o protocolo HTTP para transações pesadas e o serviço PubNub para atualizações leves e instantâneas entre o servidor e o hardware.
3. Camada Central: O servidor Flask gerencia as regras de negócio complexas, o armazenamento centralizado no banco de dados e serve a interface web de administração.

## Estrutura do Projeto
O ecossistema está organizado de forma a separar as responsabilidades técnicas:
* Módulo de Hardware: Contém a lógica de controle de sensores, gerência de feedback eletrônico e sistemas de redundância offline.
* Módulo de Servidor: Concentra as definições das tabelas de banco de dados, rotas de API REST e o motor de renderização da interface web.
* Módulo de Interface: Agrupa os estilos visuais, scripts de interatividade dinâmica e componentes de visualização de dados.
* Módulo Analítico: Composto pelo ambiente de processamento estatístico que transforma logs brutos em informações gerenciais.

## Fluxo de Funcionamento
1. Início: O usuário aproxima a tag RFID do leitor posicionado na entrada.
2. Identificação: O hardware lê o identificador único da tag e verifica na lista de usuários (em memória ou cache local).
3. Validação: O sistema verifica se o usuário possui status Ativo e se está autorizado para aquele ambiente.
4. Feedback Físico: Caso autorizado, o LED verde acende e a trava é liberada. Caso contrário, o LED vermelho pisca e o buzzer emite um alerta sonoro.
5. Registro: O evento é enviado ao servidor central. Se houver falha de rede, o evento é enfileirado localmente.
6. Atualização: O dashboard web recebe o evento via PubNub e atualiza os gráficos e tabelas automaticamente para o administrador.
7. Saída: Ao aproximar a tag novamente para sair, o sistema calcula o intervalo de permanência e finaliza o log da sessão.

## Regras de Negócio
* Autorização Obrigatória: Somente usuários com a flag de autorização definida como verdadeira podem liberar o acesso físico.
* Status do Colaborador: Usuários marcados como Inativos no sistema têm seu acesso bloqueado imediatamente, independente de possuírem uma tag válida.
* Unicidade de Identificação: Cada tag RFID é vinculada exclusivamente a um único registro de usuário e matrícula.
* Lógica de Permanência: O sistema diferencia automaticamente entre entrada e saída baseando-se no estado atual da tag no ambiente.
* Integridade de Registro: Todo evento de invasão (tag desconhecida) é registrado com alta prioridade para análise de segurança.

## Segurança
* Isolamento de Credenciais: As chaves de sincronismo e autenticação são mantidas em variáveis de ambiente ou arquivos de configuração protegidos.
* Proteção contra Invasão: O sistema identifica tentativas repetidas de tags não cadastradas e gera um ranking de insistência para monitoramento preventivo.
* Persistência de Auditoria: Os logs são imutáveis e armazenados com timestamps precisos, garantindo que o histórico não possa ser alterado sem acesso direto ao banco de dados.
* Validação de Dados: Todos os inputs na interface administrativa passam por processos de sanitização para evitar injeções maliciosas.

## Performance e Escalabilidade
* Processamento em Borda: A decisão de abrir a porta ocorre na Raspberry Pi, eliminando a dependência da latência da nuvem para o funcionamento básico.
* Comunicação Assíncrona: O uso de PubNub permite que múltiplos dashboards estejam abertos simultaneamente sem sobrecarregar o servidor Flask.
* Banco de Dados Otimizado: O SQLite3 é utilizado de forma indexada, garantindo consultas rápidas mesmo com milhares de registros de acesso.
* Arquivos CSV Rotativos: Os registros analíticos são salvos de forma incremental, facilitando o backup e a limpeza periódica do sistema.

## Integrações
* PubNub Cloud: Utilizada para a ponte de comunicação bidirecional entre o hardware remoto e a interface web do administrador.
* Hardware SPI: Protocolo de comunicação serial utilizado para a integração direta entre o processador da Raspberry Pi e o módulo leitor de RFID.
* Interface Pandas: Integração do sistema de logs com o motor de análise de dados para geração de relatórios de conformidade.

## Diferenciais do Projeto
* Autonomia Operacional: O sistema não para de funcionar se o servidor cair ou a internet oscilar, graças ao mecanismo de sincronização inteligente.
* Convergência de Dados: Une o controle físico com a análise de dados profissional, permitindo que gestores de RH utilizem os logs para conferência de horas de trabalho.
* Interface Intuitiva: Dashboard limpo focado em métricas operacionais críticas (Entradas, Saídas, Invasões).
* Hardware Customizado: Solução de baixo custo com performance de nível industrial através do uso otimizado de GPIOs.

## Possíveis Melhorias Futuras
* Integração com Biometria: Adição de uma segunda camada de autenticação para ambientes de segurança máxima.
* Interface Mobile: Desenvolvimento de um aplicativo dedicado para notificações de alerta em tempo real.
* Expansão Multi-Sede: Suporte para gerenciar múltiplas salas ou unidades geográficas a partir de um único servidor central.
* Câmera de Monitoramento: Captura automática de fotos em caso de tentativa de invasão ou acesso negado.

## Considerações Finais
O SafeEntry RFID representa uma solução completa e tecnicamente refinada para o controle de ambientes. Através da integração harmoniosa entre hardware e software, o projeto demonstra como tecnologias acessíveis podem ser aplicadas para resolver problemas reais de segurança e gestão. A arquitetura resiliente e as capacidades analíticas tornam este sistema uma ferramenta indispensável para qualquer organização que preze pela integridade de seus espaços físicos e pela precisão de seus dados operacionais.