from app.conexoes_bd_ho import get_resultados_ho
from app.conexoes_bd_geral import get_resultados_geral
from app.utils import checar_semana, gerar_mensagens, gerar_exel

def main(resultados=None, tipo=None):

    if resultados is None:
        resultados = get_resultados_ho()
    if tipo is None:
        tipo = "ho"

    if len(resultados) == 0:
        print(f"⚠️ Nenhum resultado obtido — verifique {tipo}.")
        return None

    num_semana = checar_semana(tipo)
    if num_semana is None:
        return
    
    mensagens = gerar_mensagens(resultados, tipo)
    if not mensagens:
        print(f"⚠️ Nenhuma mensagem gerada para {tipo} — verifique os dados.")
        return
    
    gerar_exel(mensagens, num_semana, tipo)


def orchestrate():
    main()

    resultados = get_resultados_geral()
    main(resultados, "geral")


if __name__ == "__main__":
    orchestrate()