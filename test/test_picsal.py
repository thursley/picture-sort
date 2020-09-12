import unittest
import picsal
import datetime as dt
import os

dir_path = os.path.dirname(os.path.realpath(__file__))

class TestPicsal(unittest.TestCase):

    def test_get_filename(self):
        config_time_only = {'prepend_timestamp': 'true'}
        config_time_only2 = {'prepend_timestamp': 'true', 'keep_filename': 'false'}

        config_name_only = {'keep_filename': 'true'}
        config_name_only2 = {'keep_filename': 'true', 'prepend_time': 'false'}
        
        config_name_time = {'prepend_timestamp': 'true', 'keep_filename': 'true'}

        config_none = {}
        time = dt.datetime(2020, 9, 1, 21, 42, 3)
        filename = 'my-file.jpg'
        string_time = picsal.create_filename(filename, time, config_time_only)
        string_time2 = picsal.create_filename(filename, time, config_time_only2)
        string_name = picsal.create_filename(filename, time, config_name_only)
        string_name2 = picsal.create_filename(filename, time, config_name_only2)
        string_time_name = picsal.create_filename(filename, time, config_name_time)
        
        self.assertEqual(string_time, '2020-09-01_21-42-03.jpg')
        self.assertEqual(string_time2, '2020-09-01_21-42-03.jpg')
        self.assertEqual(string_name, 'my-file.jpg')
        self.assertEqual(string_name2, 'my-file.jpg')
        self.assertEqual(string_time_name, '2020-09-01_21-42-03_my-file.jpg')
        self.assertRaises(Exception, picsal.create_filename, filename, time, config_none)

    def test_get_files(self):
        config_a = {'extensions': ['.a']}
        config_ab = {'extensions': ['.a', '.b']}
        config_c = {'extensions': ['.c']}
        config_none = {}

        self.assertEqual(
            picsal.get_files(f'{dir_path}/testdir', config_a),
            ['a.a', 'b.a', 'c.a'])

        self.assertEqual(
            picsal.get_files(f'{dir_path}/testdir', config_ab),
            ['a.a', 'b.a', 'b.b', 'c.a', 'c.b'])

        self.assertEqual(
            picsal.get_files(f'{dir_path}/testdir', config_c),
            [])

        self.assertRaises(Exception, picsal.get_files, 'directory', config_a)
        self.assertRaises(Exception, picsal.get_files, '', config_a)
        self.assertRaises(Exception, picsal.get_files, f'{dir_path}/testdir', config_none)

class TestFile(unittest.TestCase):

    def test_get_full_path(self):
        name = 'a.a'
        path = '/c/path'
        path_empty = ''
        date = dt.datetime.today()

        f = picsal.File(path, name, date)
        self.assertEqual(f.get_full_path(), '/c/path/a.a')
        self.assertEqual(picsal.File(path_empty, name, date).get_full_path(), '/a.a')

    def test_get_date(self):
        name = 'a.a'
        path = '/c/path'
        date = dt.datetime.today()

        f = picsal.File(path, name, date)
        self.assertEqual(f.get_date(), dt.datetime.today())

class TestTimeRange(unittest.TestCase):

    def test_contains(self):
        start = dt.datetime(2020, 9, 3, 12, 34, 56)
        end = dt.datetime(2020, 12, 24, 23, 56, 12)
        rng = picsal.TimeRange(start, end)

        self.assertFalse(start - dt.timedelta(seconds=1) in rng)
        self.assertTrue(start - dt.timedelta(seconds=0) in rng)
        self.assertTrue(end + dt.timedelta(seconds=0) in rng)
        self.assertFalse(end + dt.timedelta(seconds=1) in rng)

    def test_overlaps(self):
        self.assertFalse(True9)