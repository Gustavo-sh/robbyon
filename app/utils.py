from app.mensagens import mensagem_semana_1_ho, mensagem_semanas_2_3_ho, mensagem_semana_4_ho, mensagem_semana_1_geral, mensagem_semanas_2_3_geral, mensagem_semana_4_geral
from app.conexoes_bd_ho import get_semana_ho, update_terminado_ho
from app.conexoes_bd_geral import get_semana_geral, update_terminado_geral
from datetime import datetime
from pathlib import Path
import pandas as pd
    
def checar_semana(tipo):
    try:
        if tipo == "ho":
            semana = get_semana_ho()
        else:
            semana = get_semana_geral()

        print(f"Semana capturada para {tipo}:", semana)
        num_semana = int(semana[0])

    except Exception as e:
        print(f"Erro ao obter semana em {tipo}: {e}")
        return None

    if num_semana == 4:
        if tipo == "ho":
            update_terminado_ho()
        else:
            update_terminado_geral()

    return num_semana

def gerar_mensagens(resultados, tipo):
    
    mensagens = []
    for matricula, dados in resultados.items():
        
        
        if tipo == "ho":
            db = {"matricula": matricula, "resultado_m0_disponibilidade": dados["Resultado_M0_Disp"], "resultado_m1_disponibilidade": dados["Resultado_M1_Disp"], 
                "resultado_m2_disponibilidade": dados["Resultado_M2_Disp"],
                "resultado_tempo_logado": dados["Resultado_Tempo_Logado"], "meta_tempo_logado": dados["Meta_Tempo_Logado"], "resultado_nr17": dados["Resultado_NR17"], "meta_nr17": dados["Meta_NR17"], 
                "resultado_abs": dados["Resultado_ABS"], "meta_abs": dados["Meta_ABS"], "semana": dados["Semana"], "nome": dados["Nome"]}
            
            for chave, valor in db.items():
                if valor == None:
                    db[chave] = "Sem dados"

            if db["semana"] == 1:
                mensagens.append(mensagem_semana_1_ho(db))
            elif db["semana"] == 2 or db["semana"] == 3:
                mensagens.append(mensagem_semanas_2_3_ho(db))
            elif db["semana"] == 4:
                mensagens.append(mensagem_semana_4_ho(db))
        else:
            for i in range(len(dados)):
                db = dados[i]
                db["matricula"] = matricula
                
                for chave, valor in db.items():
                    if valor == None:
                        db[chave] = "Sem dados"

                if db["semana"] == 1:
                    mensagens.append(mensagem_semana_1_geral(db))
                elif db["semana"] == 2 or db["semana"] == 3:
                    mensagens.append(mensagem_semanas_2_3_geral(db))
                elif db["semana"] == 4:
                    mensagens.append(mensagem_semana_4_geral(db))

    return mensagens

def gerar_exel(mensagens, num_semana, tipo):
    df_mensagens = pd.DataFrame(mensagens)
    caminho_arquivo = Path.cwd() / f"mensagens_robbyon_{tipo}_semana{num_semana}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    df_mensagens.to_excel(caminho_arquivo, index=False)
    print(f"✅ {len(mensagens)} mensagens geradas para {tipo}.")
    print(f"📄 Arquivo salvo em: {caminho_arquivo}")