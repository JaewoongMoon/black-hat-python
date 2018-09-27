import sys

def main():
   # inwas = []
   # for line in sys.stdin:
   #     inwas.append(line)
   # print "%d lines" % len(inwas),
   # print "initials:", ''.join(x[0] for x in inwas)
    buffer = sys.stdin.read()
    
    print(buffer)
    
    
    
if __name__ == '__main__':
    main()