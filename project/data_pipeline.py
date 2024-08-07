import urllib.request

import pandas as pd
import sqlalchemy as sql

destination_dir = 'data'
country_codes = {
    'AT': 'Austria',
    'BE': 'Belgium',
    'BG': 'Bulgaria',
    'HR': 'Croatia',
    'CY': 'Cyprus',
    'CZ': 'Czechia',
    'DK': 'Denmark',
    'EE': 'Estonia',
    'FI': 'Finland',
    'FR': 'France',
    'DE': 'Germany',
    'EL': 'Greece',  # (Eurostat: EL)
    'HU': 'Hungary',
    'IE': 'Ireland',
    'IT': 'Italy',
    'LV': 'Latvia',
    'LT': 'Lithuania',
    'LU': 'Luxembourg',
    'MT': 'Malta',
    'NL': 'Netherlands',
    'PL': 'Poland',
    'PT': 'Portugal',
    'RO': 'Romania',
    'SK': 'Slovakia',
    'SI': 'Slovenia',
    'ES': 'Spain',
    'SE': 'Sweden',
}


def drop_rows(df, mask):
    df.drop(df[mask].index, axis=0, inplace=True)


def extract(url):
    return urllib.request.urlopen(url)


def to_csv(data):
    return pd.read_csv(data, sep=',')


def load(data, db_name, sql_engine):
    data.to_sql(db_name, sql_engine, if_exists='replace', index=False)


def drop_non_eu_countries(df):
    eu_mask = ~df['geo'].isin(country_codes.keys())
    drop_rows(df, eu_mask)


def rename_headers(df):
    return df.rename(columns={'TIME_PERIOD': 'year', 'OBS_VALUE': 'value'}, inplace=True)


def load_emissions_data(name, url, sql_engine):
    print('downloading emissions data')
    data = extract(url)
    emissions_sheet = to_csv(data)

    print('processing emissions data')

    # filter rows
    # 1. Source sectors for greenhouse gas emissions:
    #    TOTXMEMONIA - Total (excluding memo items, including international aviation)
    src_crf_mask = emissions_sheet['src_crf'] != 'TOTXMEMONIA'
    drop_rows(emissions_sheet, src_crf_mask)

    # 2. Unit of measure
    #    T_HAB - Tonnes per capita
    unit_mask = emissions_sheet['unit'] != 'T_HAB'
    drop_rows(emissions_sheet, unit_mask)

    # filter columns
    emissions_sheet.drop(labels=['DATAFLOW', 'LAST UPDATE', 'freq', 'airpol', 'src_crf', 'unit', 'OBS_FLAG'], axis=1,
                         inplace=True)

    drop_non_eu_countries(emissions_sheet)

    rename_headers(emissions_sheet)

    print('writing emissions data')
    load(emissions_sheet, name, sql_engine)


def load_energy_consumption_data(name, url, sql_engine):
    print('downloading energy consumption data')
    data = extract(url)
    energy_consumption_sheet = to_csv(data)

    print('processing energy consumption data')

    # filter rows
    # 1. Unit of measure
    #    TOE_HAB - Tonnes of oil equivalent (TOE) per capita
    unit_mask = energy_consumption_sheet['unit'] != 'TOE_HAB'
    drop_rows(energy_consumption_sheet, unit_mask)

    # filter columns
    energy_consumption_sheet.drop(labels=['DATAFLOW', 'LAST UPDATE', 'freq', 'unit', 'OBS_FLAG'], axis=1, inplace=True)

    drop_non_eu_countries(energy_consumption_sheet)

    rename_headers(energy_consumption_sheet)

    print('writing energy consumption data')
    load(energy_consumption_sheet, name, sql_engine)


def load_energy_share_data(name, url, sql_engine):
    print('downloading energy share data')
    data = extract(url)
    energy_share_sheet = to_csv(data)

    print('processing energy share data')

    # filter rows
    # 1. Energy balance
    #    REN - Renewable energy sources
    nrg_bal_mask = energy_share_sheet['nrg_bal'] != 'REN'
    drop_rows(energy_share_sheet, nrg_bal_mask)

    # filter columns
    energy_share_sheet.drop(labels=['DATAFLOW', 'LAST UPDATE', 'freq', 'nrg_bal', 'unit', 'OBS_FLAG'], axis=1,
                            inplace=True)

    drop_non_eu_countries(energy_share_sheet)

    rename_headers(energy_share_sheet)

    print('writing energy share data')
    load(energy_share_sheet, name, sql_engine)


def main(destination_path=f'{destination_dir}/data.sqlite'):
    sql_engine = sql.create_engine(f'sqlite:///{destination_path}')

    print('running: data pipeline')

    # Datasource1: Net greenhouse gas emissions
    emissions_url = 'https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/sdg_13_10/?format=SDMX-CSV&i'
    load_emissions_data('emissions', emissions_url, sql_engine)

    # Datasource2: Primary energy consumption
    energy_consumption_url = 'https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/sdg_07_10/?format=SDMX-CSV&i'
    load_energy_consumption_data('energy_consumption', energy_consumption_url, sql_engine)

    # Datasource3: Share of energy from renewable sources
    energy_share_url = 'https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_ind_ren/?format=SDMX-CSV&i'
    load_energy_share_data('energy_share', energy_share_url, sql_engine)

    print('success: data pipeline')


if __name__ == '__main__':
    main()
