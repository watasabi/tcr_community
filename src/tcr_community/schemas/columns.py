"""Constantes de colunas e tipos do dataset TCR."""

from typing import Final

# Metadados e identificadores
COL_AMOSTRA: Final = "amostra"
COL_ATENDIMENTO: Final = "numero_atendimento"
COL_PACIENTE: Final = "codigo_paciente"

# Demográficas
COL_GENERO: Final = "genero"
COL_FAIXA_ETARIA: Final = "faixa_etaria"
COL_LOCAL_RESIDENCIA: Final = "local_residencia"

# Clínicas
COL_APACHE_II: Final = "escala_apache_ii"
COL_DISPOSITIVO_INVASIVO: Final = "dispositivo_invasivo"
COL_VENTILACAO_MECANICA: Final = "ventilacao_mecanica"
COL_SEDACAO: Final = "sedacao"
COL_DROGAS_VASOATIVAS: Final = "drogas_vasoativas"
COL_TRANSFUSAO: Final = "transfusao_sanguinea"
COL_HEMODIALISE: Final = "hemodialise"
COL_PROCEDIMENTO_CIRURGICO: Final = "procedimento_cirurgico"
COL_PROCEDENCIA: Final = "procedencia"
COL_DIAGNOSTICO: Final = "diagnostico_principal"
COL_COMORBIDADES: Final = "comorbidades"
COL_VICIOS: Final = "vicios"
COL_CUIDADOS_PALIATIVOS: Final = "cuidados_paliativos"
COL_PARADA_CARDIORRESPIRATORIA: Final = "parada_cardiorrespiratoria"
COL_DATA_ADMISSAO: Final = "data_admissao"
COL_DATA_ALTA_OBITO: Final = "data_alta_obito"
COL_CAUSA_OBITO: Final = "causa_obito"
COL_TEMPO_UTI: Final = "tempo_internacao_uti"
COL_DESFECHO: Final = "desfecho_clinico"
COL_DESFECHO_PADRONIZADO: Final = "desfecho_padronizado"
COL_UTI: Final = "uti"
COL_FERIDAS_LPP: Final = "feridas_lpp"

# Labels originais do Excel (linhas) mapeados a colunas normalizadas
EXCEL_ROW_MAP: Final[dict[str, str]] = {
    "Amostra": COL_AMOSTRA,
    "n° do atendimento": COL_ATENDIMENTO,
    "Código do paciente": COL_PACIENTE,
    "Genero": COL_GENERO,
    "Faixa etaria": COL_FAIXA_ETARIA,
    "Local de residencia": COL_LOCAL_RESIDENCIA,
    "Escala de apache II": COL_APACHE_II,
    "Dispositivo invansivo": COL_DISPOSITIVO_INVASIVO,
    "Ventilacao mecanica": COL_VENTILACAO_MECANICA,
    "Sedação": COL_SEDACAO,
    "Drogas Vasoativas": COL_DROGAS_VASOATIVAS,
    "Transfusao sanguinea": COL_TRANSFUSAO,
    "Hemodialise": COL_HEMODIALISE,
    "Procedimento cirurgico": COL_PROCEDIMENTO_CIRURGICO,
    "Procedencia": COL_PROCEDENCIA,
    "Diagnostico principal": COL_DIAGNOSTICO,
    "Comorbidades": COL_COMORBIDADES,
    "Vicios": COL_VICIOS,
    "Cuidados Paliativos": COL_CUIDADOS_PALIATIVOS,
    "Parada cardiorrespiratória": COL_PARADA_CARDIORRESPIRATORIA,
    "Data de Admissão": COL_DATA_ADMISSAO,
    "Data de Alta ou Obito": COL_DATA_ALTA_OBITO,
    "Causa do Obito": COL_CAUSA_OBITO,
    "Tempo de internação na uti": COL_TEMPO_UTI,
    "Desfecho Clinico": COL_DESFECHO,
    "UTI": COL_UTI,
    "Feridas (Lpp)": COL_FERIDAS_LPP,
}

# Linhas de seção no Excel (ignoradas)
SECTION_HEADERS: Final[frozenset[str]] = frozenset(
    {"Variaveis demograficas", "Variaveis Clinicas"}
)

DEMOGRAPHIC_COLS: Final[list[str]] = [
    COL_GENERO,
    COL_FAIXA_ETARIA,
    COL_LOCAL_RESIDENCIA,
]

CLINICAL_CATEGORICAL_COLS: Final[list[str]] = [
    COL_DISPOSITIVO_INVASIVO,
    COL_VENTILACAO_MECANICA,
    COL_SEDACAO,
    COL_DROGAS_VASOATIVAS,
    COL_TRANSFUSAO,
    COL_HEMODIALISE,
    COL_PROCEDIMENTO_CIRURGICO,
    COL_PROCEDENCIA,
    COL_DIAGNOSTICO,
    COL_COMORBIDADES,
    COL_VICIOS,
    COL_CUIDADOS_PALIATIVOS,
    COL_PARADA_CARDIORRESPIRATORIA,
    COL_CAUSA_OBITO,
    COL_DESFECHO,
    COL_DESFECHO_PADRONIZADO,
    COL_FERIDAS_LPP,
]

CLINICAL_NUMERIC_COLS: Final[list[str]] = [
    COL_APACHE_II,
    COL_TEMPO_UTI,
    COL_UTI,
]

ASSOCIATION_PREDICTORS: Final[list[str]] = [
    COL_COMORBIDADES,
    COL_VENTILACAO_MECANICA,
    COL_DROGAS_VASOATIVAS,
    COL_TRANSFUSAO,
    COL_APACHE_II,
    COL_HEMODIALISE,
    COL_PROCEDIMENTO_CIRURGICO,
    COL_CUIDADOS_PALIATIVOS,
]
