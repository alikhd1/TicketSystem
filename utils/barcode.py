import unittest


def generate_checksum(code: str):
    # generate checksum based on EAN13 algorithm
    if len(code) == 12:
        # Get the digits in even positions
        even_digits = [int(code[i]) for i in range(len(code) - 1, -1, -2)]

        # Get the sum of even digits and multiply by 3
        even_sum = sum(even_digits) * 3

        # Get the digits in odd positions (except the last one)
        odd_digits = [int(code[i]) for i in range(len(code) - 2, -1, -2)]

        # Get the sum of odd digits and add to the even sum
        odd_sum = sum(odd_digits) + even_sum

        # Get the remainder after dividing by 10
        remainder = odd_sum % 10

        # If remainder is not zero, subtract from 10 to get the check digit
        check_digit = 10 - remainder if remainder != 0 else 0

        # Add the check digit to the end of the barcode
        code += str(check_digit)
        return code

    if len(code) == 13 and generate_checksum(code[:12]):
        return code
    raise ValueError('invalid number')


class TestBarcodeChecksum(unittest.TestCase):
    def test_barcode_checksum(self):
        self.assertEqual(generate_checksum('107862657008'), '1078626570084')
        self.assertEqual(generate_checksum('223160543118'), '2231605431182')
        self.assertEqual(generate_checksum('871972388488'), '8719723884881')
        self.assertEqual(generate_checksum('4792966392133'), '4792966392133')
        self.assertEqual(generate_checksum('1923734319288'), '1923734319288')
