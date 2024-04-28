import difflib
import filecmp
import os
import tempfile
import unittest
from main import main

TEST_DIR = os.path.join(os.path.dirname(__file__), 'test_data')
INPUT_DIR = os.path.join(TEST_DIR, 'input')
EXPECTED_OUTPUT_DIR = os.path.join(TEST_DIR, 'expected_output')

TMP_OUTPUT_DIR = tempfile.TemporaryDirectory()


class Test(unittest.TestCase):
    def test_main(self):
        output_xml = os.path.join(TMP_OUTPUT_DIR.name, 'wordpress_export.xml')
        main(INPUT_DIR, TMP_OUTPUT_DIR.name)
        self.compare_and_assert(output_xml, os.path.join(EXPECTED_OUTPUT_DIR, 'wordpress_export.xml'))

    def compare_and_assert(self, file1, file2):
        result = filecmp.cmp(file1, file2, shallow=False)

        if not result:
            file1_lines = open(file1, 'r').readlines()
            file2_lines = open(file2, 'r').readlines()

            diff = difflib.unified_diff(file1_lines, file2_lines, fromfile=file1, tofile=file2)

            print(f"Diff between {file1} and {file2}")
            for line in diff:
                print(line, end='')

        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()
