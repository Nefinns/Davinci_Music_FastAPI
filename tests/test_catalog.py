from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend'))

from catalog import BY_ID, CATALOG, VIEWS, exercise_code
from seed import DEMO_TAG, demo_collections


def test_eighteen_demo_documents_and_references():
    docs = demo_collections()
    assert len(docs) == 9
    assert sum(map(len, docs.values())) == 18
    assert all(doc['demo_unidad6'] == DEMO_TAG for collection in docs.values() for doc in collection)
    assert len({doc['_id'] for collection in docs.values() for doc in collection}) == 18
    client_ids = {user['cliente']['id_cliente'] for user in docs['usuario'] if 'cliente' in user}
    teacher_ids = {user['maestro']['id_maestro'] for user in docs['usuario'] if 'maestro' in user}
    instrument_ids = {item['id_instrumento'] for item in docs['instrumento']}
    assert all(sale['id_cliente'] in client_ids for sale in docs['venta'])
    assert all(item['id_instrumento'] in instrument_ids for sale in docs['venta'] for item in sale['detalles'])
    assert all(course['id_maestro'] in teacher_ids for course in docs['clase'])
    assert all(enrollment['id_cliente'] in client_ids for enrollment in docs['inscripcion_clase'])


def test_all_queries_are_predefined_and_read_only():
    assert len(CATALOG) == 21
    assert len(BY_ID) == len(CATALOG)
    assert len(VIEWS) == 3
    forbidden = ('$out', '$merge', '$function', '$where', 'deleteMany', 'drop()')
    for exercise in CATALOG:
        code = exercise_code(exercise)
        assert '.forEach(printjson)' in code
        assert not any(needle in code for needle in forbidden)
        assert exercise.collection


def test_sales_total_contains_decimal_arithmetic():
    assert '"$multiply"' in exercise_code(BY_ID['A01'])
    assert '"$lookup"' in exercise_code(BY_ID['J01'])
