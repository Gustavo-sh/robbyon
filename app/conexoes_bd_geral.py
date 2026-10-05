import pyodbc
from collections import defaultdict

CONNECTION_STRING = "Driver={SQL Server};Server=primno4;Database=Robbyson;Trusted_Connection=yes;"
UPDATE_SEMANA = """
    UPDATE dbo.RobbyOn SET semana = semana + 1
    WHERE terminado = 0;
    """
INTOS = """
SET NOCOUNT ON

if object_id('tempdb..#base') is not null drop table #base;
if object_id('tempdb..#hominum') is not null drop table #hominum;
if object_id('tempdb..#colaboradores') is not null drop table #colaboradores;
if object_id('tempdb..#agg') is not null drop table #agg;
if object_id('tempdb..#base_resultados') is not null drop table #base_resultados;
if object_id('tempdb..#atingimento') is not null drop table #atingimento;
if object_id('tempdb..#resultados_pivot') is not null drop table #resultados_pivot;
if object_id('tempdb..#tipos_indicadores') is not null drop table #tipos_indicadores;
if object_id('tempdb..#mensagens_alavanca') is not null drop table #mensagens_alavanca;

-- Etapa 1: base
SELECT
    chave_externa as matricula,
    semana,
    indicador
INTO #base
FROM dbo.RobbyOn (NOLOCK)
WHERE terminado = 0;

-- Etapa 2: hominum d-1
SELECT DISTINCT
    matricula,
    produto,
    segmento,
    diretoratendimento,
    CONSULTOR_AUTONOMO as id_ambiente,
    hmn.site
INTO #hominum
FROM rlt.hmn (NOLOCK) hmn
left join dim.atributo b on hmn.atributo = b.atributo
WHERE 
    data = cast(getdate()-1 as date)
    and situacaohominum in ('ativo')
    and tipohierarquia = 'operação'
    and nivelhierarquico = 'operacional'
    and funcaorm not like 'auxiliar%'
    and funcaorm not like 'analista%'
    and validado = 1

-- Etapa 3: colaboradores para pegar nome social
SELECT 
    matricula,
    nome
INTO #colaboradores
FROM dim.colaborador (NOLOCK);

-- Etapa 4: agregação de resultados
SELECT
    data,
    id,
    id_segmento,
    chave_externa,
    formula_resultado,
    formula_meta,
    formula_atingimento,

    SUM(resultado)  AS s_resultado,
    SUM(fator)      AS s_fator,
    SUM(fator_2)    AS s_fator2,
    SUM(fator_3)    AS s_fator3,
    SUM(fator_4)    AS s_fator4,
    SUM(meta)       AS s_meta,
    SUM(hc)         AS s_hc

INTO #agg 
FROM rlt.bussola (NOLOCK) a
inner join #base b on a.chave_externa = b.matricula and a.id = b.indicador
where
    data >= dateadd(day, 1, eomonth(getdate(), -3))
GROUP BY
    data,
    id,
    id_segmento,
    chave_externa,
    formula_resultado,
    formula_meta,
    formula_atingimento

-- Etapa 5: resultado calculado e meta calculada
SELECT
    data,
    id AS id_indicador,
    id_segmento,
    chave_externa,
    formula_atingimento,
    s_hc,

    CASE 
        WHEN formula_resultado = 2 THEN s_resultado
        WHEN formula_resultado = 3 THEN iif(s_fator = 0, 0, s_resultado / s_fator)
        WHEN formula_resultado = 5 THEN (s_resultado / s_fator) - (s_fator2 / s_fator3)
        WHEN formula_resultado = 6 THEN iif(s_fator2 = 0, 0, s_resultado / s_fator2)
        WHEN formula_resultado = 7 THEN IIF(s_fator = 0,0,s_fator / s_resultado)
        WHEN formula_resultado = 8 THEN 1 - (s_resultado / s_fator)
        WHEN formula_resultado = 9 THEN ((s_resultado / s_fator2) - (s_fator2 / s_fator3)) * 100
        WHEN formula_resultado = 10 THEN (s_resultado / s_fator) + (s_fator2 / s_fator3)
        WHEN formula_resultado = 11 THEN IIF((s_fator = 0 OR s_fator4 > s_fator),0,(s_resultado/(s_fator2/s_fator))*(1-(s_fator3/s_fator)))
        WHEN formula_resultado = 12 THEN (s_resultado - s_fator) / s_fator2
        WHEN formula_resultado = 13 THEN (s_resultado / s_fator) - (s_fator2 / s_fator)
    END AS resultado,

    CASE
        WHEN formula_meta = 1  THEN s_meta
        WHEN formula_meta = 2  THEN iif(s_fator2 = 0,0,s_fator / s_fator2)
        WHEN formula_meta = 3  THEN s_fator4
        WHEN formula_meta = 4  THEN IIF(s_fator3 = 0,0,s_fator4 / s_fator3)
        WHEN formula_meta = 5  THEN IIF(s_hc = 0,0,s_meta / s_hc)
        WHEN formula_meta = 6  THEN s_fator2
        WHEN formula_meta = 7  THEN IIF(s_fator = 0,0,s_meta / s_fator)
        WHEN formula_meta = 8  THEN IIF(s_fator2 = 0,0,s_meta / s_fator2)
        WHEN formula_meta = 9  THEN IIF(s_fator4 = 0,0,s_meta / s_fator4)
        WHEN formula_meta = 10 THEN IIF(s_fator = 0,0,s_fator2 / s_fator)
        WHEN formula_meta = 11 THEN IIF(s_fator3 = 0,0,s_fator2 / s_fator3)
    END AS meta
INTO #base_resultados
FROM #agg

-- Etapa 6: calcular atingimento por hc por data
SELECT
    data,
    id_indicador,
    chave_externa,
    resultado,
    meta,
    CASE 
        WHEN formula_atingimento = 2 THEN IIF(resultado = 0, 10, meta/resultado)
        WHEN formula_atingimento = 3 THEN IIF(meta = 0 OR resultado <= 0, 0, resultado/meta)
        WHEN formula_atingimento = 4 THEN IIF(resultado > meta, meta/resultado, resultado/meta)
        WHEN formula_atingimento = 6 THEN IIF(meta = -1, 0, (resultado+1)/(meta+1))
        WHEN formula_atingimento = 7 THEN IIF(meta > 0.00001, resultado/meta,IIF(resultado = 0, 1, resultado/meta))
        WHEN formula_atingimento = 8 THEN IIF(resultado/meta >= 1, 0, resultado/meta)
        WHEN formula_atingimento = 9 THEN IIF(resultado >= 0, 10, meta/resultado)
    END AS atingimento
into #atingimento
FROM #base_resultados

-- Etapa 7: rank para poder pivotear depois
;WITH ranked AS (
    SELECT
        chave_externa,
        data,
        resultado,
        atingimento,
        meta,
        id_indicador,
        -- ANCORAR NO MÊS ATUAL (fim do mês corrente)
        DATEDIFF(MONTH, data, EOMONTH(GETDATE(), 0)) AS diff_mes
    FROM #atingimento
)

-- Etapa 8: pivot de resultado para ter uma linha por colaborador
SELECT
    chave_externa,
    id_indicador,
    CAST(MAX(CASE WHEN diff_mes = 0 THEN resultado END) AS DECIMAL(10,4)) AS Resultado_M0,
    CAST(MAX(CASE WHEN diff_mes = 1 THEN resultado END) AS DECIMAL(10,4)) AS Resultado_M1,
    CAST(MAX(CASE WHEN diff_mes = 2 THEN resultado END) AS DECIMAL(10,4)) AS Resultado_M2,
    CAST(MAX(CASE WHEN diff_mes = 0 THEN meta END) AS DECIMAL(10,4)) AS Meta_M0,
    CAST(MAX(CASE WHEN diff_mes = 0 THEN atingimento END) AS DECIMAL(10,4)) AS Atingimento_M0
INTO #resultados_pivot
FROM ranked
GROUP BY
    chave_externa,
    id_indicador;

-- Etapa 9: tipos de indicadores para saber se é maior ou menor melhor e qual formato
SELECT 
    id_indicador,
    indicador_nome,
    case when formula_perc_atingimento like '%meta/resultado%' then 'Menor Melhor'
    when formula_perc_atingimento like '%resultado/meta%' then 'Maior Melhor'
    when formula_perc_atingimento is null then 'Nenhum'
    else 'Maior Melhor' end as tipo,
    tipo_medida_indicador as formato
INTO #tipos_indicadores
FROM rby.indicador (NOLOCK)
where formula_perc_atingimento is not null

-- Etapa 10: mensagens de alavanca para cada indicador
SELECT
    id_indicador,
    mensagem_alavanca
into #mensagens_alavanca
from dbo.DeParaRobbyOn (nolock)
    """
QUERY_FINAL = """
-- Etapa 11: query final com selects para pegar nome do colaborador e situação no hominum para mandar mensagem personalizada
SELECT distinct
    r.chave_externa,
    r.id_indicador,
    t.indicador_nome,
    t.tipo,
    t.formato,
    r.resultado_m0 as resultado_m0,
    r.resultado_m1 as resultado_m1,
    r.resultado_m2 as resultado_m2,
    r.meta_m0,
    r.atingimento_m0,
    b.semana,
    col.nome,
    m.mensagem_alavanca,
    h.produto,
    h.segmento,
    h.diretoratendimento,
    case when h.id_ambiente = 1 then 'HO' else 'PRESENCIAL' end as id_ambiente,
    h.site
FROM #resultados_pivot r
inner JOIN #hominum h
       ON r.chave_externa = h.matricula
LEFT JOIN #colaboradores col
       ON r.chave_externa = col.matricula
LEFT JOIN #base b
       ON r.chave_externa = b.matricula
left join #tipos_indicadores t
       on r.id_indicador = t.id_indicador
left join #mensagens_alavanca m
       on r.id_indicador = m.id_indicador
--where Resultado_M0 is not null
order by id_indicador
    """

DROPS = """
DROP TABLE #base;
DROP TABLE #hominum;
DROP TABLE #colaboradores;
drop table #agg;
drop table #base_resultados;
drop table #atingimento;
DROP TABLE #resultados_pivot;
DROP TABLE #tipos_indicadores;
DROP TABLE #mensagens_alavanca;
    """
def get_resultados_geral():
    conn = pyodbc.connect(CONNECTION_STRING, timeout=20)
    cur = conn.cursor()
    cur.execute(UPDATE_SEMANA)
    cur.execute(INTOS)
    cur.execute(QUERY_FINAL)
    rows = cur.fetchall()
    cur.execute(DROPS)
    cur.commit()
    resultados = defaultdict(list)
    for i in rows:
        resultados[i[0]].append({
            "id_indicador": i[1],
            "indicador_nome": i[2],
            "tipo": i[3],
            "formato": i[4],
            "resultado_m0": i[5],
            "resultado_m1": i[6],
            "resultado_m2": i[7],
            "meta_m0": i[8],
            "atingimento_m0": i[9],
            "semana": i[10],
            "nome": i[11],
            "mensagem_alavanca": i[12],
            "produto": i[13],
            "segmento": i[14],
            "diretoratendimento": i[15],
            "id_ambiente": i[16],
            "site": i[17]
        })

    cur.close()
    conn.close()
    return resultados

def get_semana_geral():
    conn = pyodbc.connect(CONNECTION_STRING, timeout=20)
    cur = conn.cursor()
    cur.execute("""select distinct semana from dbo.RobbyOn (nolock) where terminado = 0;""")
    rows = cur.fetchone()
    cur.close()
    conn.close()
    return rows

def update_terminado_geral():
    conn = pyodbc.connect(CONNECTION_STRING, timeout=20)
    cur = conn.cursor()
    cur.execute("""update dbo.RobbyOn set terminado = 1 where terminado = 0;""")
    cur.commit()
    cur.close()
    conn.close()