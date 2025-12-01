'''
Celine Ma & Mariyam Member
INFR-4900U: Blockchain Final Project 
Blockchain use-case: Blockchain-Based Gym Membership Verification
Backend code
'''

# Libraries
import hashlib
import json
from datetime import datetime, date

class Block:
    def __init__(self, index, timestamp, data, prev_hash, signature):
        self.index = index
        self.timestamp = timestamp
        self.data = data # e.g. {"member_id": "1234", "status": "active", "expiry": "2025-12-31"}
        self.prev_hash = prev_hash
        self.signature = signature # Simulated digital signature for this block - signed by gym (using private key)  
        self.hash = self.calculate_hash()

    def calculate_hash(self): # Calculate SHA-256 hash of the block content
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "prev_hash": self.prev_hash,
            "signature": self.signature
        }, sort_keys=True).encode()

        return hashlib.sha256(block_string).hexdigest() 

class Blockchain:
    def __init__(self, gym_private_key: str):
        self.chain = [] # List of all blocks in the chain
        self.gym_private_key = gym_private_key
        self.create_genesis_block()

    def create_genesis_block(self):
        # First block in the chain. Hard-coded data - immutable
        genesis_data = {"info": "Genesis block - Gym Membership Chain"}
        signature = self.sign_data(genesis_data)
        genesis_block = Block(
            index=0,
            timestamp=str(datetime.utcnow()),
            data=genesis_data,
            prev_hash="0",
            signature=signature
        )
        self.chain.append(genesis_block)

    def get_latest_block(self):
        # Return the most recent block in the chain
        return self.chain[-1] 

    def sign_data(self, data_dict):
        # We used simulated digital signature -> SHA-256( serialized data + gym_private_key )
        # In real life, we would use proper public/private key crypto. 

        message = json.dumps(data_dict, sort_keys=True) + self.gym_private_key
        return hashlib.sha256(message.encode()).hexdigest()

    def add_membership_block(self, member_id, status, expiry_date): 
        # Add or update a member record on the blockchain.
        data = {
            "member_id": member_id,
            "status": status, # "active" / "expired" / "invalid"
            "expiry": expiry_date
        }
        signature = self.sign_data(data) # Creates a pseudo-signature for this membership record

        new_block = Block(
            index=len(self.chain),
            timestamp=str(datetime.utcnow()),
            data=data,
            prev_hash=self.get_latest_block().hash,
            signature=signature
        )
        self.chain.append(new_block)
        return new_block

    def is_chain_valid(self):
        # Validate whole chain: hashes and links
        for i in range(1, len(self.chain)):
            cur = self.chain[i]
            prev = self.chain[i - 1]

            # Check if the stored hash still matches the recalculated hash
            if cur.hash != cur.calculate_hash():
                return False

            # Check if the previous hash link is valid
            if cur.prev_hash != prev.hash:
                return False

        return True

    def verify_membership(self, member_id):
        # Verify a member by checking the most recent block with their member_id 
        # Returns True/False with message
        for block in reversed(self.chain): # Search from the end of the chain for the latest record of this member
            data = block.data
            if data.get("member_id") == member_id:
                # verify signature
                expected_sig = self.sign_data(data) # expected signature
                if expected_sig != block.signature:
                    return False, "Signature invalid (possible tampering)."

                status = data.get("status")
                expiry = data.get("expiry")

                # Below is our auto-expiry logic
                # If today's date is after the expiry date, override status to "expired".
                try:
                    expiry_date = datetime.strptime(expiry, "%Y-%m-%d").date()
                    today = date.today()

                    if today > expiry_date:
                        status = "expired"
                except Exception:
                    # If expiry is missing or in the wrong format, just skip this check
                    pass

                return True, f"Member {member_id} is {status}, expiry: {expiry}"

        return False, "Member cannot be found on chain."
