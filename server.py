from flask import Flask, request, jsonify
import hashlib
import json
import os

app = Flask(__name__)

KEYS_FILE = "server_keys.json"


def carregar_keys():
    if not os.path.exists(KEYS_FILE):
        return {}

    try:
        with open(KEYS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def guardar_keys(keys):
    with open(KEYS_FILE, "w", encoding="utf-8") as f:
        json.dump(keys, f, indent=4)


def criar_id_pc(pc_info):
    texto = str(pc_info).strip()
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


@app.route("/ativar", methods=["POST"])
def ativar():
    dados = request.get_json(silent=True)

    if not dados:
        return jsonify({
            "ok": False,
            "mensagem": "Pedido invalido."
        }), 400

    key = str(dados.get("key", "")).strip()
    pc_info = str(dados.get("pc_id", "")).strip()

    if not key or not pc_info:
        return jsonify({
            "ok": False,
            "mensagem": "KEY ou PC invalido."
        }), 400

    keys = carregar_keys()

    if key not in keys:
        return jsonify({
            "ok": False,
            "mensagem": "KEY invalida."
        }), 403

    dados_key = keys[key]

    validade = str(dados_key.get("validade", "")).upper()

    if validade != "LIFETIME":
        return jsonify({
            "ok": False,
            "mensagem": "KEY expirada ou invalida."
        }), 403

    pc_hash = criar_id_pc(pc_info)

    if not dados_key.get("pc_id"):
        dados_key["pc_id"] = pc_hash
        guardar_keys(keys)

        return jsonify({
            "ok": True,
            "mensagem": "KEY ativada neste PC.",
            "validade": "LIFETIME"
        })

    if dados_key["pc_id"] != pc_hash:
        return jsonify({
            "ok": False,
            "mensagem": "Esta KEY ja esta vinculada a outro PC."
        }), 403

    return jsonify({
        "ok": True,
        "mensagem": "KEY valida.",
        "validade": "LIFETIME"
    })


@app.route("/")
def inicio():
    return "Zyz Key Server ativo."


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))

    print(f"Zyz server a iniciar na porta {port}")

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
