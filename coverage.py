import unittest
import os
from mock import patch, MagicMock
from peewee import *

import work_log_db
from work_log_db import Entry

test_db = SqliteDatabase(':memory:')


class WorkLogTest(unittest.TestCase):
    def setUp(self):

        test_db.bind(Entry, bind_refs=False, bind_backrefs=False)
        test_db.connect()
        test_db.create_tables(Entry)

        # self.user_name = 'Ken'
        # self.task_name = 'Homework'
        # self.task_time = 5
        # self.add_notes = 'Naw'
        # work_log_db.Entry.create(
        #     user_name=self.user_name,
        #     task_name=self.task_name,
        #     task_time=self.task_time,
        #     add_notes=self.add_notes
        #     )


    def test_db_init(self):
        work_log_db.initialize()
        self.assertTrue(os.path.isfile('work_log.db'))


    def test_add_entry(self):
        self.assertEqual(Entry.user_name, self.user_name)
        self.assertEqual(Entry.task_name, self.task_name)
        self.assertEqual(Entry.task_time, self.task_time)
        self.assertEqual(Entry.add_notes, self.add_notes)

    def test_name_search(self):
        with patch('builtins.input', return_value='Ken'):
            self.assertFalse(work_log_db.name_search() != None)

    def test_task_search(self):
        with patch('builtins.input', return_value='Homework'):
            self.assertFalse(work_log_db.exact_search() != None)

    def test_note_search(self):
        with patch('builtins.input', return_value='Naw'):
            self.assertFalse(work_log_db.exact_search() != None)

    def time_search(self):
        with patch('builtins.input', return_value=5):
            self.assertFalse(work_log_db.time_search() != None)



if __name__ == '__main__':
    unittest.main()