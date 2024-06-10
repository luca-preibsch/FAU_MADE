import os
import pytest

import project.data_pipeline as pipeline

expected_db_structure = {
    "emissions": ["geo", "TIME_PERIOD", "OBS_VALUE"],
    "energy_consumption": ['geo', 'TIME_PERIOD', 'OBS_VALUE'],
    "energy_share": ['geo', 'TIME_PERIOD', 'OBS_VALUE']
}


@pytest.fixture
def test_path():
    return "./test-data.sqlite"


# system level pipeline test
def test_pipeline(test_path):
    silent_remove(test_path)
    assert os.path.isfile(test_path) is False  # test requires the database to not exist

    pipeline.main(test_path)

    _test_pipeline_file_exists(test_path)
    _test_pipeline_tables_exist(test_path)


def _test_pipeline_file_exists(file_path):
    assert os.path.isfile(file_path), "The pipeline did not create the database file"


def _test_pipeline_tables_exist(file_path):
    import sqlite3

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


def silent_remove(file_path):
    try:
        os.remove(file_path)
    except OSError:
        pass
