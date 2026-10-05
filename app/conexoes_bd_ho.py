import pyodbc
CONNECTION_STRING = "Driver={SQL Server};Server=primno4;Database=Robbyson;Trusted_Connection=yes;"
UPDATE_SEMANA = """
    UPDATE rlt.HomeFlowDispPublico SET semana = semana + 1
    WHERE terminado = 0;
    """
INTOS = """
        SET NOCOUNT ON;

        SELECT
            matricula,
            semana
        INTO #base
        FROM rlt.HomeFlowDispPublico (NOLOCK)
        WHERE terminado = 0;


        SELECT DISTINCT
            matricula,
            situacaohominum,
            DIRETORATENDIMENTO
        INTO #hmn
        FROM rlt.hmn (NOLOCK)
        WHERE data = CONVERT(DATE, GETDATE() - 1)
        AND tipohierarquia = 'operação'
        AND nivelhierarquico = 'operacional'
        AND funcaorm NOT LIKE '%analista%';


        SELECT 
            matricula,
            nome
        INTO #colaboradores
        FROM dim.colaborador (NOLOCK);


        ;WITH base_disp AS (
            SELECT
                chave_externa,
                data,
                1.0 - SUM(resultado) / NULLIF(SUM(fator), 0) AS Resultado_Disp,
                SUM(meta) / SUM(hc) AS Meta_Disp
            FROM rlt.bussola WITH (NOLOCK)
            WHERE data >= DATEADD(DAY, 1, EOMONTH(GETDATE(), -4))
            AND id = 901
            AND chave_externa IN (SELECT matricula FROM #base)
            GROUP BY
                data,
                chave_externa
        ),
        ranked AS (
            SELECT
                chave_externa,
                data,
                Resultado_Disp,
                Meta_Disp,
                -- ANCORAR NO MÊS ATUAL (fim do mês corrente)
                DATEDIFF(MONTH, data, EOMONTH(GETDATE(), 0)) AS diff_mes
            FROM base_disp
        )
        SELECT
            chave_externa,
            CAST(MAX(CASE WHEN diff_mes = 0 THEN Resultado_Disp END) AS DECIMAL(10,4)) AS Resultado_M0_Disp,
            CAST(MAX(CASE WHEN diff_mes = 1 THEN Resultado_Disp END) AS DECIMAL(10,4)) AS Resultado_M1_Disp,
            CAST(MAX(CASE WHEN diff_mes = 2 THEN Resultado_Disp END) AS DECIMAL(10,4)) AS Resultado_M2_Disp,
            CAST(MAX(Meta_Disp) AS DECIMAL(10,4)) AS Meta_Disp
        INTO #disp
        FROM ranked
        GROUP BY
            chave_externa;


        SELECT
            data,
            chave_externa,
            CAST(SUM(resultado) / SUM(fator_2) AS DECIMAL(10,4)) AS Resultado_Tempo_Logado,
            CAST(SUM(meta) / SUM(hc) AS DECIMAL(10,4)) AS Meta_Tempo_Logado
        INTO #tl
        FROM rlt.bussola (NOLOCK)
        WHERE data >= DATEADD(DAY, 1, EOMONTH(GETDATE(), -1))
        AND id = 15
        AND chave_externa IN (SELECT matricula FROM #base)
        GROUP BY
            data,
            chave_externa;


        SELECT
            data,
            chave_externa,
            CAST(SUM(resultado) / SUM(fator_2) AS DECIMAL(10,4)) AS Resultado_NR17,
            CAST(SUM(meta) / SUM(hc) AS DECIMAL(10,4)) AS Meta_NR17
        INTO #nr
        FROM rlt.bussola (NOLOCK)
        WHERE data >= DATEADD(DAY, 1, EOMONTH(GETDATE(), -1))
        AND id = 25
        AND chave_externa IN (SELECT matricula FROM #base)
        GROUP BY
            data,
            chave_externa;


        SELECT
            data,
            chave_externa,
            CAST(SUM(resultado) / SUM(fator) AS DECIMAL(10,4)) AS Resultado_ABS,
            CAST(SUM(meta) / SUM(hc) AS DECIMAL(10,4)) AS Meta_ABS
        INTO #abs
        FROM rlt.bussola (NOLOCK)
        WHERE data >= DATEADD(DAY, 1, EOMONTH(GETDATE(), -1))
        AND id = 6
        AND chave_externa IN (SELECT matricula FROM #base)
        GROUP BY
            data,
            chave_externa;
    """
QUERY_FINAL = """
        SELECT
            d.chave_externa,
            FORMAT(d.resultado_m0_disp, 'P') as Resultado_M0_Disponibilidade, 
            FORMAT(d.resultado_m1_disp, 'P') as Resultado_M1_Disponibilidade, 
            FORMAT(d.resultado_m2_disp, 'P') as Resultado_M2_Disponibilidade,
            FORMAT(d.meta_disp, 'P') as Meta_Disponibilidade,
            FORMAT(DATEADD(second, t.resultado_tempo_logado, '00:00:00'), 'HH:mm:ss') as Resultado_Tempo_Logado, 
            FORMAT(DATEADD(second, t.meta_tempo_logado, '00:00:00'), 'HH:mm:ss') as Meta_Tempo_Logado,
            FORMAT(DATEADD(second, n.resultado_nr17, '00:00:00'), 'HH:mm:ss') as resultado_nr17, 
            FORMAT(DATEADD(second, n.meta_nr17, '00:00:00'), 'HH:mm:ss') as meta_nr17, 
            FORMAT(resultado_abs, 'P') as Resultado_ABS, 
            FORMAT(meta_abs, 'P') as Meta_ABS,
            b.semana,
            col.nome
            --,h.situacaohominum
            --,DIRETORATENDIMENTO
        FROM #disp d
        LEFT JOIN #tl t
            ON t.chave_externa = d.chave_externa
        LEFT JOIN #nr n
            ON n.chave_externa = d.chave_externa
        LEFT JOIN #abs a
            ON a.chave_externa = d.chave_externa
        LEFT JOIN #colaboradores col
            ON d.chave_externa = col.matricula
        LEFT JOIN #hmn h
            ON d.chave_externa = h.matricula
        LEFT JOIN #base b
            ON d.chave_externa = b.matricula
        WHERE h.situacaohominum = 'ativo'
    """

DROPS = """
        DROP TABLE #disp;
        DROP TABLE #tl;
        DROP TABLE #nr;
        DROP TABLE #abs;
        DROP TABLE #base;
        DROP TABLE #hmn;
        DROP TABLE #colaboradores;
    """
def get_resultados_ho():
    conn = pyodbc.connect(CONNECTION_STRING, timeout=20)
    cur = conn.cursor()
    cur.execute(UPDATE_SEMANA)
    cur.execute(INTOS)
    cur.execute(QUERY_FINAL)
    rows = cur.fetchall()
    cur.execute(DROPS)
    cur.commit()
    resultados = {
        i[0]: {
            "Resultado_M0_Disp": i[1],
            "Resultado_M1_Disp": i[2],
            "Resultado_M2_Disp": i[3],
            "Meta_Disp": i[4],
            "Resultado_Tempo_Logado": i[5],
            "Meta_Tempo_Logado": i[6],
            "Resultado_NR17": i[7],
            "Meta_NR17": i[8],
            "Resultado_ABS": i[9],
            "Meta_ABS": i[10],
            "Semana": i[11],
            "Nome": i[12]
        }
    for i in rows} 

    cur.close()
    conn.close()
    return resultados

def get_semana_ho():
    conn = pyodbc.connect(CONNECTION_STRING, timeout=20)
    cur = conn.cursor()
    cur.execute("""select distinct semana from rlt.HomeFlowDispPublico (nolock) where terminado = 0;""")
    rows = cur.fetchone()
    cur.close()
    conn.close()
    return rows

def update_terminado_ho():
    conn = pyodbc.connect(CONNECTION_STRING, timeout=20)
    cur = conn.cursor()
    cur.execute("""update rlt.HomeFlowDispPublico set terminado = 1 where terminado = 0;""")
    cur.commit()
    cur.close()
    conn.close()