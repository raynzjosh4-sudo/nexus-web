import os
import sys

print('==================================================')
print('====================================================')
print('testing')

def run_test():
    test = sys.argv[0]
    print('testing:', test)
    run = f'{test}python run -d windows'
    sys.exit(run)

run_test()