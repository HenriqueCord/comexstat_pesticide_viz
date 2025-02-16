import requests
import json
import pandas as pd
import warnings

from datetime import datetime
from statsmodels.tsa.seasonal import seasonal_decompose

DATA_QUALITY_CHECK_CONSEQUENCE = "warning"

PRODUCT_IDENTIFIER_COLUMN_NAME = "id_ncm"

# POSSIBLE_METRICS = ["FOB", "KG", "Statistic", "Freight", "Insurance", "CIF"]
POSSIBLE_METRICS = ["KG"]  # TODO allow every metric

ANALYSIS_VALUE_KEYS = ["net_weight_kg"]
ANALYSIS_DT_KEY = "dt"

# NCM stands for "Nomenclatura Comum Mercosul"
# https://portalunico.siscomex.gov.br/classif/#/nesh/consulta?id=114967&dataPesquisa=2025-01-10T19:55:04.000Z&tipoNota=3&tab=11736538995258

NCM_IDS_PREFIX_DICT = {
    "PESTICIDES": "38081",
    "FUNGICIDES": "38082",
    "HERBICIDES": "38083",
    "DESINFETANTES": "38084",
    "UNCLEAR": "38085",  # TODO descobrir oq é o 85
    "OTHERS": "38089",
    "DDT": "29039220",  # NOT A PREFIX ..... but will work
    "DDT": "29036220",  # NOT A PREFIX .....
}

COLUMN_RENAME_MAP = {
    "coAno": "year",
    "coMes": "month",
    "noPaispt": "export_country",
    "noUf": "import_brazillian_state",
    "noVia": "transport_method",
    "noUrf": "federal_agency",
    "coNcm": PRODUCT_IDENTIFIER_COLUMN_NAME,
    "noNcmpt": "description_ncm",
    "noUnid": "unit",
    "vlFob": "value_fob_usd",
    "vlFrete": "value_frete_usd",
    "vlSeguro": "value_insurance_usd",
    "vlCif": "value_cif_usd",
    "kgLiquido": "net_weight_kg",
    "qtEstat": "statistical_quantity",
}

BASE_URL = "https://api-comexstat.mdic.gov.br/general"

HEADERS = {"Accept": "application/json", "Content-Type": "application/json"}

DEFAULT_FILTER_PARAMS = {
    "typeForm": 2,
    "typeOrder": 1,
    "filterList": [
        {
            "id": "noNcmpt",
            "text": "NCM - Nomenclatura Comum do Mercosul",
            "route": "/pt/product/ncm",
            "type": "2",
            "group": "sh",
            "groupText": "Sistema Harmonizado (SH)",
            "hint": "fieldsForm.general.noNcm.description",
            "placeholder": "NCM",
        }
    ],
    "detailDatabase": [
        {
            "id": "noPaispt",
            "text": "País",
            "group": "gerais",
            "groupText": "Gerais",
        },
        {
            "id": "noUf",
            "text": "UF do Produto",
            "group": "gerais",
            "groupText": "Gerais",
        },
        {
            "id": "noVia",
            "text": "Via",
            "group": "gerais",
            "groupText": "Gerais",
        },
        {
            "id": "noUrf",
            "text": "URF",
            "group": "gerais",
            "groupText": "Gerais",
        },
        {
            "id": "noNcmpt",
            "text": "NCM - Nomenclatura Comum do Mercosul",
            "parentId": "coNcm",
            "parent": "Código NCM",
            "group": "sh",
            "groupText": "Sistema Harmonizado (SH)",
        },
    ],
    "formQueue": "general",
    "langDefault": "pt",
    "monthDetail": "true",
    "monthStart": "01",
    "monthEnd": "12",
    "monthStartName": "Janeiro",
    "monthEndName": "Dezembro",
}

COUNTRY_PT_TO_ISO3_CODE_MAP = {  # TODO dimensions file with this kind of mapping
    "Alemanha": "DEU",  # Germany
    "Antilhas Holandesas": "ANT",  # Netherlands Antilles (Note: This entity no longer exists as a country)
    "Argentina": "ARG",
    "Austrália": "AUS",  # Australia
    "Belarus": "BLR",
    "Brasil": "BRA",  # Brazil
    "Bulgária": "BGR",  # Bulgaria
    "Bélgica": "BEL",  # Belgium
    "Canadá": "CAN",  # Canada
    "Cayman, Ilhas": "CYM",  # Cayman Islands
    "Chile": "CHL",
    "China": "CHN",
    "Cocos (Keeling), Ilhas": "CCK",  # Cocos (Keeling) Islands
    "Colômbia": "COL",  # Colombia
    "Coreia do Norte": "PRK",  # North Korea
    "Coreia do Sul": "KOR",  # South Korea
    "Costa Rica": "CRI",
    "Cuba": "CUB",
    "Dinamarca": "DNK",  # Denmark
    "Emirados Árabes Unidos": "ARE",  # United Arab Emirates
    "Equador": "ECU",  # Ecuador
    "Eslovênia": "SVN",  # Slovenia
    "Espanha": "ESP",  # Spain
    "Estados Unidos": "USA",  # United States
    "Filipinas": "PHL",  # Philippines
    "Finlândia": "FIN",  # Finland
    "França": "FRA",  # France
    "Grécia": "GRC",  # Greece
    "Guatemala": "GTM",
    "Hong Kong": "HKG",  # Hong Kong (Special Administrative Region of China)
    "Hungria": "HUN",  # Hungary
    "Indonésia": "IDN",  # Indonesia
    "Inglaterra": "GBR",  # England (part of the United Kingdom)
    "Irlanda": "IRL",  # Ireland
    "Israel": "ISR",
    "Itália": "ITA",  # Italy
    "Iugoslávia": "YUG",  # Yugoslavia (Note: This entity no longer exists as a country)
    "Japão": "JPN",  # Japan
    "Jordânia": "JOR",  # Jordan
    "Lituânia": "LTU",  # Lithuania
    "Macau": "MAC",  # Macau (Special Administrative Region of China)
    "Malta": "MLT",
    "Malásia": "MYS",  # Malaysia
    "México": "MEX",  # Mexico
    "Nigéria": "NGA",  # Nigeria
    "Noruega": "NOR",  # Norway
    "Nova Zelândia": "NZL",  # New Zealand
    "Panamá": "PAN",  # Panama
    "Paquistão": "PAK",  # Pakistan
    "Paraguai": "PRY",  # Paraguay
    "Países Baixos (Holanda)": "NLD",  # Netherlands
    "Peru": "PER",
    "Polônia": "POL",  # Poland
    "Porto Rico": "PRI",  # Puerto Rico (Territory of the United States)
    "Portugal": "PRT",
    "Reino Unido": "GBR",  # United Kingdom
    "República Dominicana": "DOM",  # Dominican Republic
    "Rússia": "RUS",  # Russia
    "Singapura": "SGP",  # Singapore
    "Sudão": "SDN",  # Sudan
    "Suécia": "SWE",  # Sweden
    "Suíça": "CHE",  # Switzerland
    "Tailândia": "THA",  # Thailand
    "Taiwan (Formosa)": "TWN",  # Taiwan (Province of China)
    "Tcheca, República": "CZE",  # Czech Republic
    "Turquia": "TUR",  # Turkey
    "Uruguai": "URY",  # Uruguay
    "Venezuela": "VEN",
    "Vietnã": "VNM",  # Vietnam
    "África do Sul": "ZAF",  # South Africa
    "Áustria": "AUT",  # Austria
    "Índia": "IND",  # India
}


def get_comexstat_filter_possible_values(
    filter_name: str,
    base_url=BASE_URL,
) -> list:
    endpoint = "filters"

    url = f"{base_url}/{endpoint}/{filter_name}"
    r = requests.get(url, verify=False)  ## DO NOT DO THIS

    return r.json()["data"][0]


def create_id_to_classification_map(
    response_data: list, prefix_dict: dict = NCM_IDS_PREFIX_DICT
):
    """
    Create a mapping dictionary from ID to classification.

    Args:
        response_data (list): List of dictionaries containing 'id'.
        prefix_dict (dict): Dictionary of prefixes to match.

    Returns:
        dict: A dictionary mapping IDs to their classification.
    """
    id_to_classification = {}

    for item in response_data:
        item_id = item["id"]  # ID is a string

        for classification, prefix in prefix_dict.items():
            if item_id.startswith(prefix):
                id_to_classification[item["id"]] = classification
                break

    return id_to_classification


def build_query_filter_params(
    ncm_produt_ids: list,
    metrics_columns: list,
    start_year: int,
    end_year: int,
    default_params: dict,
):
    default_params["filterArray"] = [
        {"item": ncm_produt_ids, "idInput": "noNcmpt"}
    ]  # do not hardcode  >:(
    default_params["yearStart"] = start_year
    default_params["yearEnd"] = end_year
    for metric in metrics_columns:
        default_params[f"metric{metric}"] = "true"

    return default_params


def query_defensivos_agricolas_from_comexstat(
    ncm_produt_ids: list,
    metrics_columns: list,
    start_year: int,
    end_year: int,
    base_url=BASE_URL,
    headers=HEADERS,
    default_params=DEFAULT_FILTER_PARAMS,
):
    assert (
        start_year >= 1997
    ), """Invalid start year. This database starts in 1997"""  # i could check many more things

    filter_params = build_query_filter_params(
        ncm_produt_ids=ncm_produt_ids,
        metrics_columns=metrics_columns,
        start_year=start_year,
        end_year=end_year,
        default_params=default_params,
    )

    params = {"filter": json.dumps(filter_params)}
    try:
        response = requests.get(
            base_url, headers=headers, params=params, verify=False
        )  ## investigate SSL for this api. No documentation explaining
        response.raise_for_status()  # Raise HTTPError for bad responses
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


def check_data_quality(df, consequence_level="warning"):
    """
    Check for NaN values and duplicates in a DataFrame.
    """
    valid_levels = {"warning", "error"}
    if consequence_level not in valid_levels:
        raise ValueError(
            f"Invalid consequence_level: '{consequence_level}'. "
            f"Must be one of {valid_levels}"
        )

    issues = []

    if df.isna().any().any():
        issues.append("NaN values detected in the DataFrame.")

    if df.duplicated().any():
        issues.append("Duplicate rows detected in the DataFrame.")

    if issues:
        full_message = " ".join(issues)

        if consequence_level == "error":
            raise ValueError(f"Data Quality Issues: {full_message}")

        warnings.warn(f"Data Quality Issues: {full_message}")

    else:
        print("Data quality check passed - no NaNs or duplicates found.")


def map_column_to_iso3_country_code(column: pd.Series):
    return column.map(COUNTRY_PT_TO_ISO3_CODE_MAP)


def process_defensivos_agricolas_df(df: pd.DataFrame):
    """
    Lower description strings, Enforce dtype and add Date columns
    """
    _df = df.copy()
    # is this bad hardcoding?
    _df["description_ncm"] = _df["description_ncm"].str.lower()
    _df["net_weight_kg"] = _df["net_weight_kg"].astype(float)
    _df["dt"] = pd.to_datetime(_df["year"] + "-" + _df["month"] + "-01")
    _df["extracted_at"] = datetime.today()
    _df["export_country_code"] = map_column_to_iso3_country_code(_df["export_country"])

    return _df


def create_one_hot_classification(df: pd.DataFrame):
    _df = df.copy()

    # one hot categories
    _df["is_domissanitario"] = False
    _df["is_herbicide"] = False
    _df["is_inseticide"] = False
    _df["is_fungicide"] = False
    _df["is_ddt"] = False  # unused. values were too low in exploratory analysis

    domissanit_cond = _df["description_ncm"].str.contains("domissanit")
    _df.loc[domissanit_cond, "is_domissanitario"] = True

    herbicide_cond = _df["description_ncm"].str.contains("herbicida|germina")
    _df.loc[herbicide_cond, "is_herbicide"] = True

    inseticide_cond = _df["description_ncm"].str.contains("inseticid")
    _df.loc[inseticide_cond, "is_inseticide"] = True

    fungicide_cond = _df["description_ncm"].str.contains("fungicid")
    _df.loc[fungicide_cond, "is_fungicide"] = True

    ddt_cond = _df["description_ncm"].str.contains("ddt")
    _df.loc[ddt_cond, "is_ddt"] = True

    # multiple categories
    _df["is_multiple_categories"] = False
    pesticide_classes_cols = ["is_herbicide", "is_inseticide", "is_fungicide"]
    multiple_cond = _df[pesticide_classes_cols].sum(axis=1) > 1
    _df.loc[multiple_cond, "is_multiple_categories"] = True

    return _df


def create_denfensivos_agricolas_df(consequence_level: str = DATA_QUALITY_CHECK_CONSEQUENCE) -> pd.DataFrame:
    possible_ncm_ids = get_comexstat_filter_possible_values(filter_name="ncm")
    id_to_classification_map = create_id_to_classification_map(
        response_data=possible_ncm_ids
    )
    interest_ncm_ids_list = list(id_to_classification_map.keys())

    response = query_defensivos_agricolas_from_comexstat(
        ncm_produt_ids=interest_ncm_ids_list,
        metrics_columns=POSSIBLE_METRICS,
        start_year=1997,
        end_year=2024,
    )

    df_response = pd.DataFrame.from_dict(response["data"]["list"]).rename(
        columns=COLUMN_RENAME_MAP
    )

    check_data_quality(df_response, consequence_level=consequence_level)

    df_processed = process_defensivos_agricolas_df(df_response)  # process
    df_classified = create_one_hot_classification(df_processed)  # enriches

    return df_classified


def melt_and_group_by_classes_and_dt(
    df: pd.DataFrame,
    value_keys: list = ANALYSIS_VALUE_KEYS,
    dt_key: str = ANALYSIS_DT_KEY,
):
    _df = df.copy()

    dt_keys = [dt_key]
    one_hot_keys = [
        "is_domissanitario",
        "is_herbicide",
        "is_inseticide",
        "is_fungicide",
    ]
    _df_keys = value_keys + dt_keys + one_hot_keys

    # group
    class_sums_df = _df[_df_keys].groupby(dt_keys + one_hot_keys).sum().reset_index()
    # melt
    melted_agg_df = class_sums_df.melt(
        id_vars=dt_keys + value_keys,
        value_vars=one_hot_keys,
        var_name="class",
        value_name="is_present",
    )

    melted_agg_df = melted_agg_df[
        melted_agg_df["is_present"] == 1
    ]  # keep only values of classes that existed
    # in the original data.
    melted_agg_df = melted_agg_df.drop(columns=["is_present"])

    return melted_agg_df


def seasonal_decompose_pesticide_import_data(
    df: pd.DataFrame,
    value_keys: list = ANALYSIS_VALUE_KEYS,
    dt_key: str = ANALYSIS_DT_KEY,
):
    _df = df.copy()
    monthly_ts_df = (
        _df[[dt_key] + value_keys].resample("ME", on=dt_key).sum()
    )  # ts = timeseries
    return seasonal_decompose(monthly_ts_df)


# # TODO create constant for URL, pass as parameter
# def create_forest_coverage_data_df() -> pd.DataFrame:
#     forest_coverage_data_url = "https://dados.florestal.gov.br/pt_BR/api/3/action/datastore_search?resource_id=67d29e7e-0b99-41c5-9586-f0f045bc598c"
#     r = requests.get(forest_coverage_data_url)
#     return pd.DataFrame(r.json()['result']['records'])
