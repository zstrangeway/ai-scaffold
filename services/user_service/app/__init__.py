import sys
import os

# Add the API contracts directory to Python path
contracts_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'packages', 'api-contracts', 'generated', 'py')
contracts_path = os.path.abspath(contracts_path)
if contracts_path not in sys.path:
    sys.path.insert(0, contracts_path) 