import pandas as pd
import pyodbc
import time

CONNECTION_STRING = "Driver={SQL Server};Server=primno4;Database=Robbyson;Trusted_Connection=yes;"

def mount_query(id_indicador, string_extra):
    string_extra += "\n"
    QUERY_PART_1 = f"""
set nocount on;
declare
    @DataInicio date = dateadd(d,1,eomonth(getdate(),-13)),
    @DataMax date = EOMONTH(GETDATE(), -1),
    @ID smallint = {id_indicador};

if object_id('tempdb..#hominum') is not null drop table #hominum;
if object_id('tempdb..#matriculas') is not null drop table #matriculas;
if object_id('tempdb..#dados') is not null drop table #dados;
if object_id('tempdb..#ordenado') is not null drop table #ordenado;
if object_id('tempdb..#reincidentes') is not null drop table #reincidentes;
if object_id('tempdb..#base') is not null drop table #base;

-- delete from dbo.RobbyOn

------ Etapa 1: hominum d-1 com todos os filtros necessarios
select distinct
    a.matricula,
    situacaohominum,
    a.site,
    produto,
    segmento,
    case when a.nomeexibicao is not null then a.nomeexibicao else nome end as nome,
    cast(consultor_autonomo as tinyint) id_ambiente
into #hominum
from rlt.hmn A (nolock)
    inner join dim_atributo B on A.atributo = B.atributo
where 
    a.data = cast(getdate()-1 as date)
    and situacaohominum in ('ativo')
    and tipohierarquia = 'operação'
    and nivelhierarquico = 'operacional'
    and funcaorm not like 'auxiliar%'
    and funcaorm not like 'analista%'
    and validado = 1
    """

    QUERY_PART_2 = """
------ etapa 2: definir publico de consulta
select distinct 
    matricula
into #matriculas 
from bas.relatorio3 (nolock) 
where 
    indicador = @ID 
    and faixa in (3, 4) 
    and mes = @datamax

------ etapa 3: criar #dados
select
    mes as data,
    a.matricula,
    case when faixa in (3, 4) then 1 else 0 end as CheckGrupo
into #dados
from bas.relatorio3 a (nolock)
    inner join #matriculas b on a.matricula = b.matricula
where
    indicador = @ID
    and mes between @DataInicio and @DataMax

-- select * from #dados
-- where matricula = 287801
-- order by data desc

------ etapa 4: criar #ordenado com row_number
select
    data,
    matricula,
    CheckGrupo,
    row_number() over (partition by matricula order by data desc) as rn
into #ordenado
from #dados;
create clustered index ix_ord on #ordenado (matricula, rn);

-- select * from #ordenado
-- where matricula = 287801
-- order by data desc

-------- etapa 5: recursão
;with recursivo as (
    -- base: mês atual
    select
        data,
        matricula,
        CheckGrupo,
        rn,
        case when CheckGrupo = 1 then 1 else 0 end as reincidente
    from #ordenado
    where 
        rn = 1
    union all
    ------ recursão: meses anteriores
    select
        o.data,
        o.matricula,
        o.CheckGrupo,
        o.rn,
        case 
            when o.CheckGrupo = 1 and r.reincidente = 1 then 1
            else 0
        end as reincidente
    from #ordenado o
        inner join recursivo r on o.matricula = r.matricula and o.rn = r.rn + 1
)

-- select * from recursivo
-- where matricula = 287801
-- order by data desc

-------- etapa 6: reincidentes
select
    Data,
    Matricula,
    Reincidente,
    row_number() over (partition by matricula order by data desc) as rn
into #reincidentes
from recursivo
where 
    reincidente = 1

-- select * from #reincidentes
-- where matricula = 287801
-- order by data desc

-------- etapa 7: base final
select
    a.matricula as chave_externa,    
    max(a.rn) as 'meses_reincidente'
    into #base
from #reincidentes a
where
    rn > 2
group by
    a.matricula

-------- etapa 8: query final com inserts
insert into dbo.RobbyOn
select distinct
    cast(getdate() as date) as 'data', 
    a.chave_externa, 
    a.meses_reincidente, 
    0 as 'terminado', 
    0 as 'semana',
    @ID as 'indicador',
    b.id_ambiente,
    b.site,
    b.produto,
    b.segmento
from #base a
inner join #hominum b on a.chave_externa = b.matricula

drop table #hominum;
drop table #matriculas;
drop table #dados;
drop table #ordenado;
drop table #reincidentes;
drop table #base;
    """

    return QUERY_PART_1 + string_extra + QUERY_PART_2

def normalize_values(column, values):
    valor = values.strip()
    if valor and valor.lower() != "nan":
        valores_formatados = ",".join(
            f"'{v.strip()}'"
            for v in valor.split(",")
        )
        return f" and {column} in ({valores_formatados})"
    
def insert_db(query, conn):
    with conn.cursor() as cursor:
        cursor.execute(query)
        conn.commit()

def main():
    df = pd.read_excel("insert_robby_on.xlsx", 
    dtype={
        "ambientes": str,
        "sites": str,
        "produtos": str,
        "segmentos": str
    })
    
    conn = pyodbc.connect(CONNECTION_STRING)

    try:
        for _, row in df.iterrows():
            string_extra = ""
            if not pd.isna(row["ambientes"]):
                string_extra += f"and consultor_autonomo in ({row["ambientes"]})"
            if not pd.isna(row["sites"]):
                string_extra += normalize_values("a.site", row["sites"])
            if not pd.isna(row["produtos"]):
                string_extra += normalize_values("produto", row["produtos"])
            if not pd.isna(row["segmentos"]):
                string_extra += normalize_values("segmento", row["segmentos"])

            query_final = mount_query(row["indicador"], string_extra)
            insert_db(query_final, conn)
            print(f"Inserted for indicador {row['indicador']}\nValues: {string_extra}")
            time.sleep(2)
    finally:
        conn.close()

main()