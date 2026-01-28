import yaml
from sys import argv


def main():
    metada = yaml.load(open(argv[1]), "r")
    print(metada)


if __name__ == "__main__":
    main()