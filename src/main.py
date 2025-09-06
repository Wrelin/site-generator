from filework import clean_public_and_copy_static
from utilities import generate_pages_recursive
import sys


def main():
    basepath = sys.argv[1] if len(sys.argv) > 1 else '/'

    clean_public_and_copy_static()
    generate_pages_recursive("content", "template.html", "docs", basepath)


if __name__ == "__main__":
    main()
