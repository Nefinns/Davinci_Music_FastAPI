"""Pruebas sin credenciales ni conexión externa: python -m unittest discover -s tests."""
import unittest
from collections import Counter
from app.catalog import EXERCISES, GROUPS
from app.objects import VIEWS, FUNCTIONS, TRIGGERS, trigger_source
from main import catalog, checked_params, run, RunBody
from fastapi import HTTPException

class CatalogTests(unittest.TestCase):
    def test_exact_65_exercises(self):
        self.assertEqual(len(EXERCISES), 65)
        counts = Counter(ex.group for ex in EXERCISES.values())
        self.assertEqual(dict(counts), {g['id']:g['target'] for g in GROUPS})

    def test_5_views_and_trigger_pairs(self):
        self.assertEqual((len(VIEWS), len(FUNCTIONS), len(TRIGGERS)),(5,5,5))
        for key in FUNCTIONS:
            self.assertIn('CREATE OR REPLACE FUNCTION',trigger_source(key))
            self.assertIn('CREATE TRIGGER',trigger_source(key))

    def test_catalog_api_is_usable_without_database(self):
        result = catalog()
        self.assertEqual(result['total'],65)
        self.assertIn('CREATE TRIGGER', next(x for x in result['exercises'] if x['code']=='T01')['sql'])

    def test_parameters_are_validated(self):
        exercise=EXERCISES['S02']
        self.assertEqual(checked_params(exercise,{'max_stock':'5'}), {'max_stock':5})
        with self.assertRaises(Exception): checked_params(exercise, {'otro':'DROP TABLE usuario'})
        with self.assertRaises(Exception): checked_params(exercise, {'max_stock':'malicioso'})

    def test_unknown_exercise(self):
        with self.assertRaises(HTTPException) as context:
            run('NOEXISTE', RunBody())
        self.assertEqual(context.exception.status_code,404)

if __name__ == '__main__': unittest.main()
