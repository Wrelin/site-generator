from filework import clean_public_and_copy_static
from utilities import generate_pages_recursive
import os

def main():
    clean_public_and_copy_static()
    generate_pages_recursive("content", "template.html", "public")


if __name__ == "__main__":
    main()