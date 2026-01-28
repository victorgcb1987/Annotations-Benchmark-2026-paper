import yaml
from sys import argv


def main():
    metada = yaml.load(argv[1])
    print(metada)


if __name__ == "__main__":
    main()