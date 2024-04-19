import sys




def translate(source, target):
    with open(source, "r", encoding="utf-8") as f:
        source = f.read()
    
    

if __name__ == "__main__":
    assert len(sys.argv) == 3, "Invalid usage: python3 translator.py <source> <target>"
    translate(sys.argv[0], sys.argv[1])