from flask import Flask, render_template, redirect, request, session
import json
import arquivos

app = Flask(__name__)

app.secret_key = "chave_secreta"

@app.route("/")
def home():
    return render_template ("index.html")

@app.route("/<name>")
def get_page(name):
    if name == "apostila":
        return redirect("/apostila/introducao")
    if name == "quiz":
        return redirect ("quiz/iniciar")
    if name == "ferramentas":
        return redirect("/ferramentas/ferramentas")
    if name == "avaliação":
        return redirect("/avaliacao")
    return render_template(f"{name}.html")

@app.route("/ferramentas/<name>")
def ferramentas(name):
    return render_template(f"/ferramentas/{name}.html")


@app.route("/apostila/<name>")
def find_apostila(name):
    #arquivo json para guardar as páginas e ser usado para a construção do indice
    apostila_paginas = json.load(open("./static/apostila_paginas.json", encoding='utf-8'))
    return render_template(f"{name}.html", paginas = arquivos.apostila_paginas)


#contrução do quiz
#as perguntas são retiradas do arquivo json correspondente a cada capitulo
@app.route("/quiz/<name>")
def quiz_page(name, sem_resposta=False):
    perguntas = arquivos.quiz_perguntas
    questao = ""
    num_quest = 0
    pagina_anterior = "#"
    proxima_pagina = "#"

    if name == "assunto7":
        return redirect("/quiz/resultado")

    if name in perguntas:
        page = "quiz_capitulo"
        questao = perguntas[name]
        verificar = name
        print(questao)
    else: page = name
    
    for i in range(len(perguntas)):
        if name == f"quiz_assunto{i+1}":
            num_quest = i+1
            proxima_pagina = f"assunto{i+2}"
            pagina_anterior = f"assunto{i+1}"
    
    if pagina_anterior in ["quiz_assunto0", "assunto0"]: pagina_anterior = "assunto1"
    if proxima_pagina in ["quiz_assunto7", "assunto7"]: proxima_pagina = "resultado"

    if sem_resposta == True:
        nao_respondido = arquivos.modal_sem_resposta
        return render_template(f"/quiz/{page}.html", questao = questao, num_quest=num_quest, proxima = proxima_pagina, anterior = pagina_anterior, verificar = num_quest, sem_resposta=nao_respondido, paginas=arquivos.apostila_paginas)

    return render_template(f"/quiz/{page}.html", questao = questao, num_quest=num_quest, proxima = proxima_pagina, anterior = pagina_anterior, verificar = num_quest, paginas=arquivos.apostila_paginas)



#rota para salvar as respostas do usuário
@app.route("/salvar_respostas/<verificar>", methods=["POST", "GET"])
def salvar_respostas(verificar):
    try:
        session[f"resposta{verificar}"] = request.form[f"resposta{verificar}"]
    except KeyError:
        return quiz_page(f"quiz_assunto{verificar}", True)
        
    return redirect (f"/quiz/assunto{int(verificar) + 1}")


#rota para verificação dos resultados do quiz e visualização da página de resultados
@app.route("/quiz/resultado")
def resultado():
    perguntas = arquivos.quiz_perguntas
    acertos = 0
    questoes_erradas = {}
    correcao = arquivos.erro_assunto
    resposta1 = session.get("resposta1", "")
    resposta2 = session.get("resposta2", "")
    resposta3 = session.get("resposta3", "")
    resposta4 = session.get("resposta4", "")
    resposta5 = session.get("resposta5", "")
    resposta6 = session.get("resposta6", "")

    respostas = [resposta1, resposta2, resposta3, resposta4, resposta5, resposta6]

    for i in range(1, len(respostas)+1):
        if perguntas[f"quiz_assunto{i}"][5] == session[f"resposta{i}"]:
            acertos += 1
        else: questoes_erradas[i] = correcao[f"erro_assunto{i}"]

    erros = len(perguntas) - acertos
    porcentagem = f"{(acertos/len(perguntas) * 100):.2f}%"

    return render_template("/quiz/resultado.html", acertos = acertos, erros = erros, porcentagem = porcentagem, respostas = respostas, questoes_erradas = questoes_erradas, correcao = correcao)


# rota para avaliação e resultado da avaliação
@app.route("/avaliacao", methods=["POST", "GET"])
def avaliacao():
    apostila_paginas = arquivos.apostila_paginas
    perguntas = arquivos.quiz_perguntas
    correcao = arquivos.erro_assunto
    questoes_erradas = {}

    if request.method == "POST":
        respostas_avaliacao = {}
        acertos = 0

        for i in range(1, len(perguntas)+1):
            respostas_avaliacao[i] = request.form.get(f"respostaquiz_assunto{i}")
        
        for key, value in respostas_avaliacao.items():
            if value == perguntas[f"quiz_assunto{key}"][5]:
                acertos += 1
            else:
                questoes_erradas[key] = correcao[f"erro_assunto{key}"]
        
        erros = len(perguntas) - acertos
        porcentagem = f"{(acertos/len(perguntas) * 100):.2f}%"

        return render_template("/avaliacao/resultado_avaliacao.html", acertos = acertos, erros = erros, porcentagem = porcentagem, respostas = respostas_avaliacao, questoes_erradas = questoes_erradas, correcao = correcao, paginas = apostila_paginas)

    return render_template("/avaliacao/avaliacao.html", perguntas = perguntas, paginas = apostila_paginas)


#rota para o PACER
@app.route("/pacer", methods = ["POST", "GET"])
def pacer_page():
    qtd_funcionarios = 0

    if request.method == "POST":
        qtd_funcionarios = int(request.form.get("qtd_funcionarios"))
        return redirect (f"pacer/{qtd_funcionarios}")

    return render_template("pacer.html", qtd_funcionarios=qtd_funcionarios)


#recarrega a pagina com um questionario para cada membro da equipe
@app.route("/pacer/<name>", methods=["POST", "GET"])
def get_pacer(name):
    return render_template ("pacer.html", qtd_funcionarios = int(name))


#retorno do PACER para o usuário
@app.route("/pacer/ver/<name>", methods=["POST", "GET"])
def pacer_res(name):
    
    pacer_funcionarios = {}

    for i in range(int(name)):
        nome_funcionario = request.form.get(f"nome_funcionario{i}")
        productivity = request.form.get(f"productivity{i}")
        autonomy = request.form.get(f"autonomy{i}")
        collaboration = request.form.get(f"collaboration{i}")
        results = request.form.get(f"results{i}")

        calculo_final = productivity + autonomy + collaboration + results
        pacer_funcionarios[nome_funcionario] = [productivity, autonomy, collaboration, results, calculo_final]
    
    return render_template("pacer_res.html", pacer= pacer_funcionarios)


if __name__ == "__main__":
    app.run(debug=True)