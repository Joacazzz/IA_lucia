import datetime
import json
import os
import spacy

# Carregar modelo de linguagem
nlp = spacy.load("pt_core_news_sm")

ARQUIVO_PROTOCOLOS = "protocolos.json"
CONTADOR_ARQUIVO = "contador.json"

# -------------------------
# DEPARTAMENTOS
# -------------------------

DEPARTAMENTOS = {
    "suporte": {
        "nome": "Suporte Técnico",
        "icone": "🛠️",
        "ramal": "1001",
        "email": "suporte@empresa.com.br",
        "horario": "Seg–Sex: 08h–18h",
        "descricao": "Problemas técnicos, sistemas, equipamentos e TI.",
        "palavras_chave": ["suporte", "técnico", "sistema", "computador", "internet", "acesso", "senha", "erro", "bug", "ti"]
    },
    "rh": {
        "nome": "Recursos Humanos",
        "icone": "👥",
        "ramal": "1002",
        "email": "rh@empresa.com.br",
        "horario": "Seg–Sex: 08h–17h",
        "descricao": "Admissão, férias, folha de pagamento e benefícios.",
        "palavras_chave": ["rh", "recursos humanos", "férias", "salário", "contrato", "admissão", "demissão", "benefício", "folha", "ponto"]
    },
    "financeiro": {
        "nome": "Financeiro",
        "icone": "💰",
        "ramal": "1003",
        "email": "financeiro@empresa.com.br",
        "horario": "Seg–Sex: 09h–17h",
        "descricao": "Pagamentos, cobranças, notas fiscais e reembolsos.",
        "palavras_chave": ["financeiro", "pagamento", "cobrança", "nota fiscal", "boleto", "reembolso", "fatura", "débito", "crédito", "dívida"]
    },
    "obras": {
        "nome": "Secretaria de Obras",
        "icone": "🏗️",
        "ramal": "1004",
        "email": "obras@empresa.com.br",
        "horario": "Seg–Sex: 07h–16h",
        "descricao": "Licenças, alvarás, reformas e infraestrutura.",
        "palavras_chave": ["obras", "construção", "alvará", "licença", "reforma", "engenharia", "planta", "infraestrutura", "manutenção", "reparo"]
    },
    "juridico": {
        "nome": "Jurídico",
        "icone": "⚖️",
        "ramal": "1005",
        "email": "juridico@empresa.com.br",
        "horario": "Seg–Sex: 09h–18h",
        "descricao": "Contratos, assessoria legal e compliance.",
        "palavras_chave": ["jurídico", "contrato", "lei", "advogado", "processo", "compliance", "legal", "judicial", "ação", "direito"]
    },
    "ouvidoria": {
        "nome": "Ouvidoria",
        "icone": "📢",
        "ramal": "1006",
        "email": "ouvidoria@empresa.com.br",
        "horario": "Seg–Sex: 08h–18h | Sáb: 08h–12h",
        "descricao": "Reclamações, sugestões, elogios e denúncias.",
        "palavras_chave": ["ouvidoria", "reclamação", "sugestão", "elogio", "denúncia", "queixa", "crítica", "feedback", "insatisfação", "problema"]
    },
    "compras": {
        "nome": "Compras e Licitações",
        "icone": "🛒",
        "ramal": "1007",
        "email": "compras@empresa.com.br",
        "horario": "Seg–Sex: 08h–17h",
        "descricao": "Aquisições, licitações, fornecedores e cotações.",
        "palavras_chave": ["compras", "licitação", "fornecedor", "cotação", "aquisição", "pedido", "estoque", "produto", "orçamento", "pregão"]
    },
    "ti": {
        "nome": "Tecnologia da Informação",
        "icone": "💻",
        "ramal": "1008",
        "email": "ti@empresa.com.br",
        "horario": "Seg–Sex: 08h–18h",
        "descricao": "Infraestrutura digital, servidores e segurança da informação.",
        "palavras_chave": ["ti", "tecnologia", "servidor", "rede", "firewall", "segurança", "dados", "backup", "software", "hardware"]
    }
}

# -------------------------
# UTILIDADES
# -------------------------

def saudacao():
    hora = datetime.datetime.now().hour
    if 5 <= hora < 12:
        return "Bom dia"
    elif 12 <= hora < 18:
        return "Boa tarde"
    else:
        return "Boa noite"


def gerar_protocolo():
    agora = datetime.datetime.now()

    if os.path.exists(CONTADOR_ARQUIVO):
        with open(CONTADOR_ARQUIVO, "r") as f:
            dados = json.load(f)
        contador = dados.get("contador", 0) + 1
    else:
        contador = 1

    with open(CONTADOR_ARQUIVO, "w") as f:
        json.dump({"contador": contador}, f)

    return f"{agora.strftime('%Y%m%d')}-{str(contador).zfill(4)}"


def painel():
    agora = datetime.datetime.now()
    print("\n" + "=" * 52)
    print("        CENTRAL DE ATENDIMENTO AO CIDADÃO")
    print("                  Sistema LUCÍA")
    print(f"  {saudacao()}! | {agora.strftime('%d/%m/%Y')} | {agora.strftime('%H:%M')}")
    print("=" * 52)
    print("  Digite o nome do departamento ou descreva")
    print("  sua solicitação para ser direcionado(a).")
    print("=" * 52)


# -------------------------
# NLP — IDENTIFICAR DEPARTAMENTO
# -------------------------

def identificar_departamento(frase):
    frase_lower = frase.lower()

    # Verificar palavras-chave de cada departamento
    pontuacao = {}
    for chave, depto in DEPARTAMENTOS.items():
        pontos = sum(1 for palavra in depto["palavras_chave"] if palavra in frase_lower)
        if pontos > 0:
            pontuacao[chave] = pontos

    if pontuacao:
        return max(pontuacao, key=pontuacao.get)

    return None


def interpretar_navegacao(frase):
    frase_lower = frase.lower()

    if any(p in frase_lower for p in ["sair", "encerrar", "tchau", "fechar", "fim"]):
        return "sair"

    if any(p in frase_lower for p in ["menu", "início", "voltar", "departamentos", "opções"]):
        return "menu"

    if any(p in frase_lower for p in ["protocolo", "meu protocolo", "meus protocolos", "histórico"]):
        return "protocolos"

    depto = identificar_departamento(frase)
    if depto:
        return depto

    return "desconhecido"


# -------------------------
# ARMAZENAMENTO DE PROTOCOLOS
# -------------------------

def carregar_protocolos():
    if not os.path.exists(ARQUIVO_PROTOCOLOS):
        return []
    with open(ARQUIVO_PROTOCOLOS, "r", encoding="utf-8") as f:
        return json.load(f)


def salvar_protocolo(protocolo):
    registros = carregar_protocolos()
    registros.append(protocolo)
    with open(ARQUIVO_PROTOCOLOS, "w", encoding="utf-8") as f:
        json.dump(registros, f, indent=4, ensure_ascii=False)


# -------------------------
# EXIBIÇÃO
# -------------------------

def exibir_menu_departamentos():
    print("\n┌─────────────────────────────────────────────┐")
    print("│           DEPARTAMENTOS DISPONÍVEIS          │")
    print("├─────────────────────────────────────────────┤")

    for i, (chave, depto) in enumerate(DEPARTAMENTOS.items(), 1):
        linha = f"│  {i}. {depto['icone']} {depto['nome']:<35}│"
        print(linha)

    print("├─────────────────────────────────────────────┤")
    print("│  📋 'protocolos' — Ver meus atendimentos      │")
    print("│  🚪 'sair'       — Encerrar atendimento       │")
    print("└─────────────────────────────────────────────┘")


def exibir_departamento(chave):
    depto = DEPARTAMENTOS[chave]

    print(f"\n{'=' * 50}")
    print(f"  {depto['icone']}  {depto['nome'].upper()}")
    print(f"{'=' * 50}")
    print(f"  📋 {depto['descricao']}")
    print(f"  📞 Ramal   : {depto['ramal']}")
    print(f"  📧 E-mail  : {depto['email']}")
    print(f"  🕐 Horário : {depto['horario']}")
    print(f"{'=' * 50}")

    print("\n  O que você precisa?")
    print("  1. 📝 Abrir novo protocolo de atendimento")
    print("  2. 📞 Apenas consultar contato")
    print("  3. 🔙 Voltar ao menu principal")

    while True:
        opcao = input("\n  [Opção]: ").strip()

        if opcao == "1":
            abrir_protocolo(chave)
            break
        elif opcao == "2":
            print(f"\n  [Lucía] Contato do {depto['nome']} anotado!")
            print(f"          Ramal {depto['ramal']} | {depto['email']}")
            break
        elif opcao == "3" or opcao.lower() in ["voltar", "menu"]:
            break
        else:
            print("  [Lucía] Opção inválida. Digite 1, 2 ou 3.")


def abrir_protocolo(chave_depto):
    depto = DEPARTAMENTOS[chave_depto]

    print(f"\n  📝 ABERTURA DE PROTOCOLO — {depto['nome'].upper()}")
    print("  " + "-" * 45)

    nome = input("  Seu nome completo : ").strip()
    if not nome:
        nome = "Não informado"

    contato = input("  Telefone ou e-mail: ").strip()
    if not contato:
        contato = "Não informado"

    print("  Descreva sua solicitação (pressione Enter duas vezes para finalizar):")
    linhas = []
    while True:
        linha = input("  > ")
        if linha == "" and linhas and linhas[-1] == "":
            break
        linhas.append(linha)
    descricao = "\n".join(linhas).strip() or "Não informado"

    protocolo_id = gerar_protocolo()
    agora = datetime.datetime.now()

    registro = {
        "protocolo": protocolo_id,
        "departamento": depto["nome"],
        "nome": nome,
        "contato": contato,
        "descricao": descricao,
        "status": "Aberto",
        "data": agora.strftime("%d/%m/%Y"),
        "hora": agora.strftime("%H:%M")
    }

    salvar_protocolo(registro)

    print(f"\n  ✅ PROTOCOLO REGISTRADO COM SUCESSO!")
    print(f"  ┌───────────────────────────────────────┐")
    print(f"  │  Número do protocolo : {protocolo_id:<16}│")
    print(f"  │  Departamento        : {depto['nome']:<16}│")
    print(f"  │  Data/Hora           : {agora.strftime('%d/%m/%Y %H:%M'):<16}│")
    print(f"  │  Status              : Aberto          │")
    print(f"  └───────────────────────────────────────┘")
    print(f"  [Lucía] Guarde o número do seu protocolo.")
    print(f"          Responderemos via {depto['email']}")


def exibir_protocolos():
    registros = carregar_protocolos()

    print("\n  📋 HISTÓRICO DE PROTOCOLOS")
    print("  " + "=" * 48)

    if not registros:
        print("  Nenhum protocolo registrado ainda.")
        return

    for reg in reversed(registros[-10:]):  # Últimos 10
        status_icon = "✅" if reg["status"] == "Resolvido" else "🔄"
        print(f"\n  {status_icon} Protocolo : {reg['protocolo']}")
        print(f"     Depto    : {reg['departamento']}")
        print(f"     Nome     : {reg['nome']}")
        print(f"     Data     : {reg['data']} às {reg['hora']}")
        print(f"     Status   : {reg['status']}")
        print("  " + "-" * 48)


# -------------------------
# INTERFACE PRINCIPAL
# -------------------------

def menu():
    exibir_menu_departamentos()

    while True:
        entrada = input("\n[Você]: ").strip()

        if not entrada:
            continue

        acao = interpretar_navegacao(entrada)

        if acao == "sair":
            print("\n[Lucía] Obrigado pelo contato. Tenha um ótimo dia! 👋\n")
            break

        elif acao == "menu":
            exibir_menu_departamentos()

        elif acao == "protocolos":
            exibir_protocolos()

        elif acao in DEPARTAMENTOS:
            exibir_departamento(acao)
            exibir_menu_departamentos()

        elif entrada.isdigit():
            chaves = list(DEPARTAMENTOS.keys())
            idx = int(entrada) - 1
            if 0 <= idx < len(chaves):
                exibir_departamento(chaves[idx])
                exibir_menu_departamentos()
            else:
                print("[Lucía] Número fora do intervalo. Tente novamente.")

        else:
            print("[Lucía] Não consegui identificar o departamento.")
            print("        Tente digitar o nome (ex: 'financeiro', 'rh') ou o número da opção.")


# -------------------------
# EXECUÇÃO
# -------------------------

if __name__ == "__main__":
    painel()
    menu()
