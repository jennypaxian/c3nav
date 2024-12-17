async def generate_payload(msg, type, in_seq, out_seq):
    pass

async def hash_payload(key, payload):
    pass

async def generate_key(keysize):
    pass

async def generate_kdf(key,hash):
    pass

async def encrypt_ige(key, iv):
    pass

async def generate_fingerprint(hash_payload):
    pass

async def construct_frame(fingerprint, key, enc_data):
    pass