# steganography/utils.py

def modify_lsb(cover_data, payload_data, num_lsbs):
    # Assuming cover_data and payload_data are in bytes
    cover_bits = bytearray(cover_data)
    payload_bits = bytearray(payload_data)
    
    # Convert payload length to bits
    payload_index = 0
    payload_length = len(payload_bits) * 8
    for i in range(len(cover_bits)):
        if payload_index < payload_length:
            cover_byte = cover_bits[i]
            for j in range(num_lsbs):
                if payload_index < payload_length:
                    payload_bit = (payload_bits[payload_index // 8] >> (7 - (payload_index % 8))) & 1
                    cover_byte = (cover_byte & ~(1 << j)) | (payload_bit << j)
                    payload_index += 1
            cover_bits[i] = cover_byte

    return bytes(cover_bits)

