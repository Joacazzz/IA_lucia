import datetime
import json
import os
import spacy
import spacy

nlp = spacy.load("pt_core_news_sm")

doc = nlp("Estudar programação amanhã")

for token in doc:
    print(token.text, token.pos_)

# carregar modelo de linguagem
nlp = spacy.load("pt_core_news_sm")

ARQUIVO_TAREFAS = "tarefas.json"


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


def painel():
    agora = datetime.datetime.now()

    print("\n" + "=" * 45)
    print("SISTEMA LUCÍA")
    print(f"{saudacao()} | {agora.strftime('%d/%m/%Y')} | {agora.strftime('%H:%M')}")
    print("=" * 45)


# -------------------------
# NLP (spaCy)
# -------------------------

def interpretar_comando(frase):

    frase = frase.lower()
    doc = nlp(frase)

    if "adicionar" in frase or "criar" in frase:
        return "add"

    if "ver" in frase or "listar" in frase:
        return "listar"

    if "remover" in frase or "apagar" in frase:
        return "remover"

    if "concluir" in frase or "finalizar" in frase:
        return "concluir"

    if "sair" in frase or "encerrar" in frase:
        return "sair"

    return "desconhecido"


# -------------------------
# ARMAZENAMENTO
# -------------------------

def carregar_tarefas():

    if not os.path.exists(ARQUIVO_TAREFAS):
        return []

    with open(ARQUIVO_TAREFAS, "r", encoding="utf-8") as f:
        return json.load(f)


def salvar_tarefas(tarefas):

    with open(ARQUIVO_TAREFAS, "w", encoding="utf-8") as f:
        json.dump(tarefas, f, indent=4, ensure_ascii=False)


# -------------------------
# FUNÇÕES DE TAREFA
# -------------------------

def listar_tarefas():

    tarefas = carregar_tarefas()

    print("\n--- SUAS TAREFAS ---")

    if not tarefas:
        print("Nenhuma tarefa registrada.")
        return

    for i, tarefa in enumerate(tarefas, 1):

        status = "✔" if tarefa["concluida"] else " "

        print(f"{i}. [{status}] {tarefa['descricao']}")

    print("--------------------")


def adicionar_tarefa():

    descricao = input("\nDigite a tarefa: ")

    tarefas = carregar_tarefas()

    tarefas.append({
        "descricao": descricao,
        "concluida": False,
        "data": datetime.datetime.now().strftime("%d/%m/%Y")
    })

    salvar_tarefas(tarefas)

    print(f"\n[Lucía] Tarefa adicionada: {descricao}")


def concluir_tarefa():

    tarefas = carregar_tarefas()

    listar_tarefas()

    try:
        numero = int(input("\nNúmero da tarefa para concluir: ")) - 1

        tarefas[numero]["concluida"] = True

        salvar_tarefas(tarefas)

        print("[Lucía] Tarefa concluída.")

    except:
        print("[Lucía] Número inválido.")


def remover_tarefa():

    tarefas = carregar_tarefas()

    listar_tarefas()

    try:
        numero = int(input("\nNúmero da tarefa para remover: ")) - 1

        removida = tarefas.pop(numero)

        salvar_tarefas(tarefas)

        print(f"[Lucía] Tarefa removida: {removida['descricao']}")

    except:
        print("[Lucía] Número inválido.")


# -------------------------
# INTERFACE PRINCIPAL
# -------------------------

def menu():

    while True:

        comando = input("\n[Você]: ")

        acao = interpretar_comando(comando)

        if acao == "add":
            adicionar_tarefa()

        elif acao == "listar":
            listar_tarefas()

        elif acao == "remover":
            remover_tarefa()

        elif acao == "concluir":
            concluir_tarefa()

        elif acao == "sair":
            print("\n[Lucía] Encerrando sistema.")
            break

        else:
            print("[Lucía] Não entendi o comando.")


# -------------------------
# EXECUÇÃO
# -------------------------

if __name__ == "__main__":
    painel()
    menu()