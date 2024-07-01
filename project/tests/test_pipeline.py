import os
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal
import sqlite3

import project.data_pipeline as pipeline

expected_db_structure = {
    "emissions": ["geo", "TIME_PERIOD", "OBS_VALUE"],
    "energy_consumption": ['geo', 'TIME_PERIOD', 'OBS_VALUE'],
    "energy_share": ['geo', 'TIME_PERIOD', 'OBS_VALUE']
}
tests_dir = "./project/tests"


@pytest.fixture
def test_db_path():
    return f"{tests_dir}/test-data.sqlite"


@pytest.fixture
def test_csv_path():
    return f"{tests_dir}/test_csv.csv"


@pytest.fixture
def test_df(test_csv_path):
    return pd.read_csv(test_csv_path, sep=",")


# system level pipeline test
def test_pipeline(test_db_path):
    silent_remove(test_db_path)
    assert os.path.isfile(test_db_path) is False  # test requires the database to not exist

    pipeline.main(test_db_path)

    _test_pipeline_file_exists(test_db_path)
    _test_pipeline_tables_exist(test_db_path)
    _test_pipeline_all_eu_countries(test_db_path)


def _test_pipeline_file_exists(file_path):
    assert os.path.isfile(file_path), "The pipeline did not create the database file"


def _test_pipeline_tables_exist(file_path):
    conn = sqlite3.connect(file_path)
    cursor = conn.cursor()

    for expected_table, expected_columns in expected_db_structure.items():
        # check the tables exist
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{expected_table}';")
        assert cursor.fetchone() is not None, f"Table {expected_table} does not exist."

        cursor.execute(f"PRAGMA table_info({expected_table});")
        columns = [info[1] for info in cursor.fetchall()]
        for expected_column in expected_columns:
            assert expected_column in columns, f"Column {expected_column} does not exist in table {expected_table}."

    conn.close()


def _test_pipeline_all_eu_countries(file_path):
    conn = sqlite3.connect(file_path)
    cursor = conn.cursor()

    def get_country_codes_from_db(table_name):
        cursor.execute(f"SELECT DISTINCT geo FROM {table_name}")
        rows = cursor.fetchall()

        country_codes = {row[0] for row in rows}
        return country_codes

    for table in expected_db_structure.keys():
        db_country_codes = get_country_codes_from_db(table)
        assert db_country_codes == set(pipeline.country_codes.keys()), \
            f"Expected: {set(pipeline.country_codes.keys())}, but got: {db_country_codes}"

    conn.close()


def test_to_csv(test_csv_path, test_df):
    data = pipeline.to_csv(test_csv_path)
    assert_frame_equal(data, test_df)


def test_load(tmp_path, test_df):
    db_name = 'test_db'
    sql_engine = f'sqlite:///{tmp_path}/test.sqlite'
    pipeline.load(test_df, db_name, sql_engine)

    loaded_data = pd.read_sql_table(db_name, sql_engine)
    assert_frame_equal(loaded_data, test_df)


def silent_remove(file_path):
    try:
        os.remove(file_path)
    except OSError:
        pass
