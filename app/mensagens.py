from datetime import timedelta

def checar_dados_disponibilidade(db, tipo):
    if tipo == "ho":
        if db["resultado_m0_disponibilidade"] == "Sem dados":
            return {"Matricula": db["matricula"], "tipo": "Sem dados", "semana":db["semana"], "Mensagem": "Sem dados para o indicador no Mês Atual."}
        elif db["resultado_m1_disponibilidade"] == "Sem dados" and db["resultado_m2_disponibilidade"] == "Sem dados":
            return {"Matricula": db["matricula"], "tipo": "Sem dados", "semana":db["semana"], "Mensagem": "Sem dados para o indicador nos últimos períodos."}
    else:
        if db["resultado_m0"] == "Sem dados":
            return {"Matricula": db["matricula"], "tipo": "Sem dados", "semana":db["semana"], "produto": db["produto"], "segmento": db["segmento"], "diretoratendimento": db["diretoratendimento"], "Mensagem": "Sem dados para o indicador no Mês Atual.", "id_indicador": db["id_indicador"]}
        elif db["resultado_m1"] == "Sem dados" and db["resultado_m2"] == "Sem dados":
            return {"Matricula": db["matricula"], "tipo": "Sem dados", "semana":db["semana"], "produto": db["produto"], "segmento": db["segmento"], "diretoratendimento": db["diretoratendimento"], "Mensagem": "Sem dados  para o indicador nos últimos períodos.", "id_indicador": db["id_indicador"]}
    return None

def to_float_percent(valor):
    try:
        return float(str(valor).replace("%", "").strip())
    except (TypeError, ValueError):
        return 0.0
    
def normalize_values(db):
    if db["formato"] == "admin_generic_hour":
        db["resultado_m0"] = str(timedelta(seconds=round(db["resultado_m0"]))) if db["resultado_m0"] != "Sem dados" else db["resultado_m0"]
        db["resultado_m1"] = str(timedelta(seconds=round(db["resultado_m1"]))) if db["resultado_m1"] != "Sem dados" else db["resultado_m1"]
        db["meta_m0"] = str(timedelta(seconds=round(db["meta_m0"])))
    elif db["formato"] == "admin_generic_percentage":
        db["resultado_m0"] = round(to_float_percent(db['resultado_m0'])*100, 2) if db["resultado_m0"] != "Sem dados" else db["resultado_m0"]
        db["resultado_m1"] = round(to_float_percent(db['resultado_m1'])*100, 2) if db["resultado_m1"] != "Sem dados" else db["resultado_m1"]
        db["meta_m0"] = round(to_float_percent(db["meta_m0"])*100, 2) if db["meta_m0"] != "Sem dados" else db["meta_m0"]
    elif db["formato"] == "admin_generic_float":
        db["resultado_m0"] = to_float_percent(db['resultado_m0']) if db["resultado_m0"] != "Sem dados" else db["resultado_m0"]
        db["resultado_m1"] = to_float_percent(db['resultado_m1']) if db["resultado_m1"] != "Sem dados" else db["resultado_m1"]
        db["meta_m0"] = to_float_percent(db["meta_m0"]) if db["meta_m0"] != "Sem dados" else db["meta_m0"]
    else:
        db["resultado_m0"] = round(db["resultado_m0"]) if db["resultado_m0"] != "Sem dados" else db["resultado_m0"]
        db["resultado_m1"] = round(db["resultado_m1"]) if db["resultado_m1"] != "Sem dados" else db["resultado_m1"]
        db["meta_m0"] = round(db["meta_m0"]) if db["meta_m0"] != "Sem dados" else db["meta_m0"]


def mensagem_semana_1_ho(db):
    texto =  f"""
                Olá, {db["nome"].split(" ")[0]}! 😊 Eu sou o Robby e tô passando pra dar uma noticia super legal! Você está participando do Robby ON na Disponibilidade, criado para apoiar sua evolução no indicador de % de Disponibilidade.
                No último mês, seu resultado foi {db["resultado_m1_disponibilidade"]}, e nos últimos períodos ele apareceu entre G3 e G4. A partir de agora, vamos trabalhar juntos para melhorar isso com constância 💪
                Toda semana eu vou te enviar aqui na Robbyson dicas rápidas + um resumo da sua evolução.
                Já confere os pilares da sua disponibilidade:
                Tempo logado — Meta: {db["meta_tempo_logado"]} | Atual: {db["resultado_tempo_logado"]}
                Pausa NR17 — Meta: {db["meta_nr17"]} | Atual: {db["resultado_nr17"]}
                ABS — Meta: {db["meta_abs"]} | Atual: {db["resultado_abs"]}
                E sempre que precisar, chama seu supervisor: ele é seu parceiro nesse processo🤝
                Conta comigo, Robby
            """
    return {"Matricula": db["matricula"], "tipo": "abertura", "semana":db["semana"], "Mensagem": texto}

def mensagem_semanas_2_3_ho(db):
    texto = None
    tipo = None
    evoluiu_porcentagem = None
    checar_dados = checar_dados_disponibilidade(db, "ho")
    if checar_dados is not None:
        return checar_dados
    if db["resultado_m1_disponibilidade"] == "Sem dados":
        evoluiu_porcentagem = to_float_percent(db["resultado_m0_disponibilidade"]) > to_float_percent(db["resultado_m2_disponibilidade"])
    else:
        evoluiu_porcentagem = to_float_percent(db["resultado_m0_disponibilidade"]) > to_float_percent(db["resultado_m1_disponibilidade"])
    if evoluiu_porcentagem:
        texto = f"""
        Fala, {db["nome"].split(" ")[0]}! 🎉
        Boa! Acredita que você evoluiu sua % de Disponibilidade em relação ao resultado anterior? Parabéns pelo seu esforço! 👏
        Mês anterior: {db["resultado_m1_disponibilidade"]}
        Mês atual: {db["resultado_m0_disponibilidade"]}
        Pra manter a subida, confere os pilares da sua disponibilidade:
        Tempo logado — Meta: {db["meta_tempo_logado"]} | Atual: {db["resultado_tempo_logado"]}
        Pausa NR17 — Meta: {db["meta_nr17"]} | Atual: {db["resultado_nr17"]}
        ABS — Meta: {db["meta_abs"]} | Atual: {db["resultado_abs"]}
        Seu próximo nível é repetir o que funcionou e ajustar o que ainda oscila 🔎
        Sigo te acompanhando por aqui 🚀
        Robby
                """
        tipo = "evolucao"
    else:
        texto = f"""
        Olá, {db["nome"].split(" ")[0]}!
        Vi aqui que sua % de Disponibilidade não evoluiu em relação ao resultado anterior. Bora ajustar a rota juntos?
        Mês anterior: {db["resultado_m1_disponibilidade"]}
        Mês atual: {db["resultado_m0_disponibilidade"]}
        Pra encontrar a alavanca mais rápida, confere os componentes:
        Tempo logado — Meta: {db["meta_tempo_logado"]} | Atual: {db["resultado_tempo_logado"]}
        Pausa NR17 — Meta: {db["meta_nr17"]} | Atual: {db["resultado_nr17"]}
        ABS — Meta: {db["meta_abs"]} | Atual: {db["resultado_abs"]}
        Escolhe 1 ponto pra atacar primeiro 🎯 (o que estiver mais distante da meta costuma dar ganho mais rápido). Se quiser, chama seu supervisor pra montar um plano simples de 7 dias 🤝
        Tamo junto,
        Robby
                """
        tipo = "involucao"
    return {"Matricula": db["matricula"], "tipo": tipo, "semana":db["semana"], "Mensagem": texto}

def mensagem_semana_4_ho(db):
    texto = None
    tipo = None
    evoluiu_grupo = True if to_float_percent(db["resultado_m0_disponibilidade"]) >= 94.0 else False # mudar aqui para m0, descomentar o codigo abaixo e mudar as mensagens para ciclo de abril em diante 
    evoluiu_porcentagem = None
    checar_dados = checar_dados_disponibilidade(db, "ho")

    if checar_dados is not None:
        return checar_dados
    if db["resultado_m1_disponibilidade"] == "Sem dados":
        evoluiu_porcentagem = to_float_percent(db["resultado_m0_disponibilidade"]) > to_float_percent(db["resultado_m2_disponibilidade"])
    else:
        evoluiu_porcentagem = to_float_percent(db["resultado_m0_disponibilidade"]) > to_float_percent(db["resultado_m1_disponibilidade"])

    # if db["resultado_m1_disponibilidade"] == "Sem dados" or db["resultado_m2_disponibilidade"] == "Sem dados":
    #     return {"Matricula": db["matricula"], "tipo": "Sem dados", "semana":db["semana"], "Mensagem": "Sem dados disponibilidade Mês Anterior ou Dois Meses Atras."}
    # evoluiu_porcentagem = to_float_percent(db["resultado_m1_disponibilidade"]) > to_float_percent(db["resultado_m2_disponibilidade"])

    if evoluiu_grupo and evoluiu_porcentagem:
        texto = f"""
        Ei, {db["nome"].split(" ")[0]}! 🎉
        Encerramos o ciclo do Robby ON e seu resultado melhorou na % de Disponibilidade, e melhor: você virou de grupo!! 🏆
        M-1: {db["resultado_m1_disponibilidade"]}
        M-0: {db["resultado_m0_disponibilidade"]}
        Isso mostra que seu esforço teve impacto real.
        Neste momento, você não precisa seguir no próximo ciclo de acompanhamento 🙌
        Seu desafio agora é simples: manter o padrão que te trouxe até aqui 💻
        Parabéns!
        Robby
        """
        tipo = r"evolucao % e grupo"
    elif evoluiu_porcentagem:
        texto = f"""
        Fala, {db["nome"].split(" ")[0]}! 🙌
        Fechamos o ciclo do Robby ON e eu vi sua evolução na % de Disponibilidade — parabéns pela dedicação! 👏
        M-1: {db["resultado_m1_disponibilidade"]}
        M-0: {db["resultado_m0_disponibilidade"]}
        Mesmo com a melhora, você ainda aparece em G3/G4 por enquanto. E isso não é rótulo, é só o ponto de partida do próximo ciclo, tá? Vamos seguir juntos até você virar de grupo 💪
        Conta comigo,
        Robby
        """
        tipo = r"evolucao %"
    else:
        texto = f"""
        Olá, {db["nome"].split(" ")[0]}!
        Encerramos o Robby ON e identificamos que, neste ciclo, seu resultado de % de Disponibilidade não evoluiu em relação ao mês anterior.
        Resultado (mês M-1): {db["resultado_m1_disponibilidade"]} Disponibilidade
        Resultado (mês M-0): {db["resultado_m0_disponibilidade"]} Disponibilidade
        Sei que desafios acontecem 💭, mas é importante reforçar que a evolução nesse indicador é essencial para o seu crescimento dentro da operação.
        Por isso, você seguirá com a gente em um novo ciclo de acompanhamento até a sua melhoria.
        Conto com o seu comprometimento para transformar esse resultado 💪. Estamos juntos nesse propósito ✨. Abraços, Robby!
        """
        tipo = "involucao"
    return {"Matricula": db["matricula"], "tipo": tipo, "semana":db["semana"], "Mensagem": texto}


def mensagem_semana_1_geral(db):
    normalize_values(db)
    mensagem_alavanca = db["mensagem_alavanca"].replace("\\n", "\n")
    texto =  f"""
Olá, {db["nome"].split(" ")[0]}! 😊
Você está participando do Robby ON no indicador {db["indicador_nome"]}, um acompanhamento criado para apoiar sua evolução e fortalecer seus resultados 💬
No último mês, seu resultado ficou em {db["resultado_m1"]}, aparecendo entre os grupos foco do indicador.
A partir de agora, vamos acompanhar sua evolução com dicas rápidas, feedbacks e direcionamentos para apoiar sua melhoria 💪
Seu resultado atual: {db["resultado_m0"]} | Meta: {db["meta_m0"]}
Alguns pontos que fazem diferença no {db["indicador_nome"]}: 
{mensagem_alavanca}
E lembre: seu supervisor está junto com você nesse processo 🤝
Conta comigo, Robby
            """
    return {"Matricula": db["matricula"], "tipo": "abertura", "semana":db["semana"], "id_indicador": db["id_indicador"],
            "produto": db["produto"], "segmento": db["segmento"], "diretoratendimento": db["diretoratendimento"],
            "id_ambiente": db["id_ambiente"], "site": db["site"], "Mensagem": texto}

def mensagem_semanas_2_3_geral(db):
    texto = None
    tipo = None
    evoluiu_porcentagem = None
    checar_dados = checar_dados_disponibilidade(db, "geral")
    if checar_dados is not None:
        return checar_dados

    if db["resultado_m1"] == "Sem dados":
        if db["tipo"] == "Maior Melhor":
            evoluiu_porcentagem = to_float_percent(db["resultado_m0"]) > to_float_percent(db["resultado_m2"])
        else:
            evoluiu_porcentagem = to_float_percent(db["resultado_m0"]) < to_float_percent(db["resultado_m2"])
    else:
        if db["tipo"] == "Maior Melhor":
            evoluiu_porcentagem = to_float_percent(db["resultado_m0"]) > to_float_percent(db["resultado_m1"])
        else:
            evoluiu_porcentagem = to_float_percent(db["resultado_m0"]) < to_float_percent(db["resultado_m1"])
    
    normalize_values(db)
    mensagem_alavanca = db["mensagem_alavanca"].replace("\\n", "\n")

    if evoluiu_porcentagem:
        texto = f"""
Fala, {db["nome"].split(" ")[0]}! 🎉
Boa notícia: seu resultado no indicador {db["indicador_nome"]} evoluiu em relação ao último período 👏
Mês anterior: {db["resultado_m1"]} | Mês atual: {db["resultado_m0"]} | Meta: {db["meta_m0"]}
Isso mostra que seus ajustes já estão gerando impacto positivo no resultado 🚀
Continue reforçando:
{mensagem_alavanca}
Cada atendimento faz diferença 🚀
Sigo te acompanhando por aqui, Robby
                """
        tipo = "evolucao"
    else:
        texto = f"""
Olá, {db["nome"].split(" ")[0]}!
Percebi que seu resultado no indicador {db["indicador_nome"]} não evoluiu neste período, mas ainda dá tempo de ajustar a rota 💡
Mês anterior: {db["resultado_m1"]} | Mês atual: {db["resultado_m0"]} | Meta: {db["meta_m0"]}
Vale revisar alguns pontos que costumam impactar diretamente no resultado:
{mensagem_alavanca}
Agora é o momento de identificar os principais pontos de atenção e focar na melhoria 🎯
Se precisar, conte com seu supervisor para construir um plano simples de melhoria 🤝
Tamo junto, Robby
                """
        tipo = "involucao"
    return {"Matricula": db["matricula"], "tipo": tipo, "semana":db["semana"], "id_indicador": db["id_indicador"], 
            "produto": db["produto"], "segmento": db["segmento"], "diretoratendimento": db["diretoratendimento"], 
            "id_ambiente": db["id_ambiente"], "site": db["site"], "Mensagem": texto}

def mensagem_semana_4_geral(db):
    texto = None
    tipo = None
    evoluiu_grupo = True if to_float_percent(db["atingimento_m0"]) >= 1 else False
    evoluiu_porcentagem = None
    checar_dados = checar_dados_disponibilidade(db, "geral")

    if checar_dados is not None:
        return checar_dados
    
    if db["resultado_m1"] == "Sem dados":
        if db["tipo"] == "Maior Melhor":
            evoluiu_porcentagem = to_float_percent(db["resultado_m0"]) > to_float_percent(db["resultado_m2"])
        else:
            evoluiu_porcentagem = to_float_percent(db["resultado_m0"]) < to_float_percent(db["resultado_m2"])
    else:
        if db["tipo"] == "Maior Melhor":
            evoluiu_porcentagem = to_float_percent(db["resultado_m0"]) > to_float_percent(db["resultado_m1"])
        else:
            evoluiu_porcentagem = to_float_percent(db["resultado_m0"]) < to_float_percent(db["resultado_m1"])

    normalize_values(db)

    if evoluiu_grupo and evoluiu_porcentagem:
        texto = f"""
Parabéns, {db["nome"].split(" ")[0]}! 🎉
Encerramos o ciclo do Robby ON no indicador {db["indicador_nome"]} e além da evolução no resultado, você também mudou de grupo 🏆
Mês anterior: {db["resultado_m1"]} |Mês atual: {db["resultado_m0"]} | Meta: {db["meta_m0"]}
Seu desempenho teve impacto positivo e isso merece reconhecimento 👏
Agora o desafio é manter esse padrão de qualidade nos próximos ciclos 💪
Sucesso e parabéns! Robby
        """
        tipo = r"evolucao % e grupo"
    elif evoluiu_porcentagem:
        texto = f"""
Ei, {db["nome"].split(" ")[0]}! 🙌
Fechamos mais um ciclo do Robby ON no indicador {db["indicador_nome"]} e seu resultado apresentou evolução 👏
Mês anterior: {db["resultado_m1"]} |Mês atual: {db["resultado_m0"]} | Meta: {db["meta_m0"]}
Seu esforço trouxe resultado e isso faz toda diferença 🚀
Agora o foco é manter a constância e continuar evoluindo nos atendimentos 🚀
Parabéns pela dedicação!
Robby
        """
        tipo = r"evolucao %"
    else:
        texto = f"""
Olá, {db["nome"].split(" ")[0]}!
Encerramos o ciclo do Robby ON no indicador {db["indicador_nome"]} e identificamos que, neste período, seu resultado ainda não apresentou evolução.
Resultado:
Mês anterior: {db["resultado_m1"]} | Mês atual: {db["resultado_m0"]} | Meta: {db["meta_m0"]}
Sabemos que alguns ciclos são mais desafiadores, mas seguimos juntos no foco da melhoria contínua 💭
Você continuará no acompanhamento para trabalharmos sua evolução no indicador e fortalecer ainda mais seus resultados 🚀
Conto com seu comprometimento nesse processo 💪
Abraços, Robby
        """
        tipo = "involucao"
    return {"Matricula": db["matricula"], "tipo": tipo, "semana":db["semana"], "id_indicador": db["id_indicador"],
            "produto": db["produto"], "segmento": db["segmento"], "diretoratendimento": db["diretoratendimento"],
            "id_ambiente": db["id_ambiente"], "site": db["site"], "Mensagem": texto}