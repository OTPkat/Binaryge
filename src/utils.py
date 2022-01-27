
class BinaryUtils(object):

    @staticmethod
    def is_positive_binary_string(s: str):
        return all(x in '01' for x in s) and any(x == '1' for x in s)

    @classmethod
    def count_ones_from_binary_string(cls, s: str):
        return sum(x == '1' for x in s)

    @classmethod
    def count_zeros_from_binary_string(cls, s: str):
        return sum(x == '0' for x in s)

    @classmethod
    def count_zeros_in_binary_from_int(cls, n: int):
        return cls.count_ones_from_binary_string(cls.int_to_binary_string(n))

    @classmethod
    def count_ones_in_binary_from_int(cls, n: int):
        return cls.count_zeros_from_binary_string(cls.int_to_binary_string(n))

    @classmethod
    def int_to_binary_string(cls, n: int) -> str:
        return '{0:b}'.format(n)

    @classmethod
    def binary_string_to_int(cls, s: str) -> int:
        return int(s, 2)


if __name__ == '__main__':
    print(BinaryUtils.is_positive_binary_string("111"))