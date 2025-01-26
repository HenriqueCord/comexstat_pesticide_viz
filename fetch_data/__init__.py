import requests
import json
import pandas as pd

PRODUCT_IDENTIFIER_COLUMN_NAME = "id_ncm"

POSSIBLE_METRICS = ["FOB", "KG", "Statistic", "Freight", "Insurance", "CIF"]

# NCM stands for "Nomenclatura Comum Mercosul"
# https://portalunico.siscomex.gov.br/classif/#/nesh/consulta?id=114967&dataPesquisa=2025-01-10T19:55:04.000Z&tipoNota=3&tab=11736538995258

NCM_IDS_PREFIX_DICT = {
    'PESTICIDES': '38081',
    'FUNGICIDES': '38082',
    'HERBICIDES': '38083',
    'DESINFETANTES': '38084',
    "UNCLEAR": "38085",  # TODO descobrir oq é o 85
    'OTHERS': '38089',
    "DDT": '29039220',  # NOT A PREFIX ..... but will work 
    "DDT": '29036220',  # NOT A PREFIX .....
}

COLUMN_RENAME_MAP = {
    "coAno": 'ano',
    "coMes": 'mes',
    "noPaispt": "pais",
    "noUf": "estado",
    "noVia": "via_de_transporte",
    "noUrf": "unidade_receita_federal",
    "coNcm": PRODUCT_IDENTIFIER_COLUMN_NAME,
    "noNcmpt": "descritor_ncm",
    "noUnid": "unidade_medida",
    "vlFob": "valor_fob_usd",
    "vlFrete": "valor_frete_usd",
    "vlSeguro": "valor_seguro_usd",
    "vlCif": "valor_cif_usd",
    "kgLiquido": "peso_liq_kg",
    "qtEstat": "qtd_estatistica",
}

BASE_URL = 'https://api-comexstat.mdic.gov.br/general'

HEADERS = {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

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
    "monthDetail": 'true',
    "monthStart": "01",
    "monthEnd": "12",
    "monthStartName": "Janeiro",
    "monthEndName": "Dezembro",
}

def get_comexstat_filter_possible_values(
    filter_name: str,
    base_url = BASE_URL,
) -> list:
  endpoint = "filters"

  url = f'{base_url}/{endpoint}/{filter_name}'
  r = requests.get(url, verify=False) ## DO NOT DO THIS

  return r.json()["data"][0]


def create_id_to_classification_map(response_data: list, prefix_dict: dict = NCM_IDS_PREFIX_DICT):
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
    default_params["filterArray"] = [{"item": ncm_produt_ids, "idInput": "noNcmpt"}]  # do not hardcode  >:(
    default_params["yearStart"] = start_year
    default_params["yearEnd"] = end_year
    for metric in metrics_columns:
        default_params[f'metric{metric}'] = 'true'

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
     assert start_year >= 1997, """Invalid start year. This database starts in 1997"""  # i could check many more things
     
     filter_params = build_query_filter_params(
          ncm_produt_ids=ncm_produt_ids,
          metrics_columns=metrics_columns,
          start_year=start_year,
          end_year=end_year,
          default_params=default_params,
     )

     params = {
           "filter": json.dumps(filter_params)
      }
     try:
      response = requests.get(base_url, headers=headers, params=params, verify=False) ## investigate SSL for this api. No documentation explaining
      response.raise_for_status()  # Raise HTTPError for bad responses
      return response.json()
     
     except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return None
     

def create_denfensivos_agricolas_df() -> pd.DataFrame:
    
    possible_ncm_ids = get_comexstat_filter_possible_values(
        filter_name="ncm"
    )
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

    df_response = pd.DataFrame.from_dict(response['data']['list']).rename(columns=COLUMN_RENAME_MAP)
    df_response.loc[:, "class"] = df_response[PRODUCT_IDENTIFIER_COLUMN_NAME].map(id_to_classification_map)  # THIS IS ENRICHING DATA

    return df_response


# TODO create constant for URL, pass as parameter 
def create_forest_coverage_data_df() -> pd.DataFrame:
    forest_coverage_data_url = "https://dados.florestal.gov.br/pt_BR/api/3/action/datastore_search?resource_id=67d29e7e-0b99-41c5-9586-f0f045bc598c"
    r = requests.get(forest_coverage_data_url)
    return pd.DataFrame(r.json()['result']['records'])