from web3 import Web3

# Connect to Infura
infura_url = 'https://sepolia.infura.io/v3/b65b518166e243a4b3979ca95d549d51'
web3 = Web3(Web3.HTTPProvider(infura_url))

# Check if connected
if not web3.is_connected():
    print("Failed to connect to Infura")
    exit()

# Contract details
private_key = '0x9f3cb367028eb5eb3c86f5419205eb9c0a82233e8236ad30db6218dedcb978b9'
contract_address = '0x2bE451ed60658fe78Ea129c1ee5156419a296895'
contract_abi = [
    # Replace this with the actual ABI of your smart contract
    {
        "inputs": [
            {"internalType": "string", "name": "examId", "type": "string"},
            {"internalType": "uint256", "name": "releaseDate", "type": "uint256"},
            {"internalType": "string", "name": "hashcode", "type": "string"},
            {"internalType": "string", "name": "teacherId", "type": "string"}
        ],
        "name": "storeHash",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "string", "name": "examId", "type": "string"},
            {"internalType": "string", "name": "teacherId", "type": "string"}
        ],
        "name": "retrieveHash",
        "outputs": [{"internalType": "string", "name": "", "type": "string"}],
        "stateMutability": "view",
        "type": "function"
    }
]

# Create contract instance
contract = web3.eth.contract(address=contract_address, abi=contract_abi)

# Function to store hash
def store_hash(exam_id, release_date, hashcode, teacher_id):
    account = web3.eth.account.from_key(private_key)
    nonce = web3.eth.get_transaction_count(account.address)

    # Build transaction
    tx = contract.functions.storeHash(exam_id, release_date, hashcode, teacher_id).build_transaction({
        'chainId': 11155111,  # Sepolia chain ID
        'gas': 3000000,
        'gasPrice': web3.to_wei('10', 'gwei'),
        'nonce': nonce,
    })

    # Sign transaction
    signed_tx = web3.eth.account.sign_transaction(tx, private_key)
    
    # Send transaction
    tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
    
    print(f'Transaction sent with hash: {web3.to_hex(tx_hash)}')

# Function to retrieve hash
def retrieve_hash(exam_id, teacher_id):
    result = contract.functions.retrieveHash(exam_id, teacher_id).call()
    return result

# # Example usage
# if __name__ == "__main__":
#     # Replace these values with actual data
#     private_key = '0x9f3cb367028eb5eb3c86f5419205eb9c0a82233e8236ad30db6218dedcb978b9'  # Make sure to keep this safe!
    
#     # Store a hash
#     # store_hash("exam1", 1733560800, "success", "tec1", private_key)
    
#     # Retrieve a hash
#     retrieve_hash("exam1", "tec1")