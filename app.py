from flask import Flask, request, jsonify
from flask_cors import CORS
from blockchain_backend import Blockchain  # Celine's classes

app = Flask(__name__)
CORS(app)  # lets HTML + JS call this from the browser

# Create one global blockchain for the gym
gym_chain = Blockchain(gym_private_key="super_secret_gym_key")

def block_to_dict(block):
    return {
        "index": block.index,
        "timestamp": block.timestamp,
        "data": block.data,
        "prev_hash": block.prev_hash,
        "hash": block.hash,
        "signature": block.signature,
    }

@app.route("/add_membership", methods=["POST"])
def add_membership():
    body = request.get_json()
    member_id = body.get("member_id")
    status = body.get("status")
    expiry = body.get("expiry")

    if not member_id or not status:
        return jsonify({"error": "member_id and status are required"}), 400

    block = gym_chain.add_membership_block(member_id, status, expiry)
    return jsonify({
        "message": f"Block created for member {member_id}",
        "block": block_to_dict(block)
    })

@app.route("/verify_membership", methods=["GET"])
def verify_membership():
    member_id = request.args.get("member_id")
    if not member_id:
        return jsonify({"error": "member_id is required"}), 400

    ok, msg = gym_chain.verify_membership(member_id)
    return jsonify({
        "ok": ok,
        "message": msg
    })

@app.route("/chain_valid", methods=["GET"])
def chain_valid():
    valid = gym_chain.is_chain_valid()
    return jsonify({
        "valid": valid,
        "length": len(gym_chain.chain)
    })

@app.route("/blocks", methods=["GET"])
def blocks():
    # Return last 5 blocks (or all if less than 5)
    last_n = int(request.args.get("last", 5))
    subset = gym_chain.chain[-last_n:]
    # reverse so newest first
    subset = list(reversed(subset))
    return jsonify([block_to_dict(b) for b in subset])

if __name__ == "__main__":
    app.run(debug=True)
