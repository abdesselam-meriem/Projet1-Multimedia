from PIL import Image
import numpy as np

# ----------------------------
# RLE compression (générique)
# ----------------------------
def rle_compress_channel(channel_array):
    flat = channel_array.flatten()
    compressed = []
    i = 0
    while i < len(flat):
        run_value = flat[i]
        run_length = 1
        while i + run_length < len(flat) and flat[i + run_length] == run_value:
            run_length += 1

        if run_length >= 3:
            header = (1 << 15) | run_length
            compressed.append((header, run_value))
            i += run_length
        else:
            j = i
            seq = [flat[j]]
            while (j + 1 < len(flat) and 
                   (flat[j+1] != flat[j] or seq.count(flat[j]) < 2)):
                seq.append(flat[j+1])
                j += 1
                if len(seq) > 2 and seq[-1] == seq[-2] == seq[-3]:
                    seq.pop()
                    j -= 1
                    break
            header = (0 << 15) | len(seq)
            compressed.append((header, seq))
            i = j + 1
    return compressed

def save_color_compressed(filename, compressed_R, compressed_G, compressed_B, shape):
    with open(filename, "w") as f:
        f.write(f"{shape[0]} {shape[1]}\n")  # hauteur largeur
        f.write("R\n")
        for header, data in compressed_R:
            f.write(str(header) + " ")
            if isinstance(data, list):
                f.write(" ".join(map(str, data)))
            else:
                f.write(str(data))
            f.write("\n")
        f.write("G\n")
        for header, data in compressed_G:
            f.write(str(header) + " ")
            if isinstance(data, list):
                f.write(" ".join(map(str, data)))
            else:
                f.write(str(data))
            f.write("\n")
        f.write("B\n")
        for header, data in compressed_B:
            f.write(str(header) + " ")
            if isinstance(data, list):
                f.write(" ".join(map(str, data)))
            else:
                f.write(str(data))
            f.write("\n")

# ----------------------------
# RLE decompression (générique)
# ----------------------------
def rle_decompress_channel(lines):
    decompressed = []
    for line in lines:
        parts = list(map(int, line.strip().split()))
        header = parts[0]
        if header >> 15 == 1:
            run_length = header & 0x7FFF
            value = parts[1]
            decompressed.extend([value] * run_length)
        else:
            seq_length = header & 0x7FFF
            seq = parts[1:1+seq_length]
            decompressed.extend(seq)
    return np.array(decompressed, dtype=np.uint8)

def load_color_compressed(filename):
    with open(filename, "r") as f:
        lines = f.readlines()

    # Lire taille
    h, w = map(int, lines[0].strip().split())
    shape = (h, w)

    # Séparer canaux
    R_lines = []
    G_lines = []
    B_lines = []

    section = None
    for line in lines[1:]:
        if line.strip() == "R":
            section = "R"
        elif line.strip() == "G":
            section = "G"
        elif line.strip() == "B":
            section = "B"
        else:
            if section == "R":
                R_lines.append(line)
            elif section == "G":
                G_lines.append(line)
            elif section == "B":
                B_lines.append(line)

    R = rle_decompress_channel(R_lines).reshape(shape)
    G = rle_decompress_channel(G_lines).reshape(shape)
    B = rle_decompress_channel(B_lines).reshape(shape)

    img_array = np.stack([R, G, B], axis=-1)
    return img_array

# ----------------------------
# Main test
# ----------------------------
if __name__ == "__main__":
    # Charger une image couleur
    img = Image.open("image_color.png").convert("RGB")
    arr = np.array(img)

    # Compression par canal
    compressed_R = rle_compress_channel(arr[:,:,0])
    compressed_G = rle_compress_channel(arr[:,:,1])
    compressed_B = rle_compress_channel(arr[:,:,2])

    # Sauvegarde
    save_color_compressed("compressed_color.txt", compressed_R, compressed_G, compressed_B, arr.shape[:2])
    print("Image couleur compressée dans compressed_color.txt")

    # Décompression
    decompressed = load_color_compressed("compressed_color.txt")

    # Sauvegarde et affichage
    img_dec = Image.fromarray(decompressed, mode="RGB")
    img_dec.save("decompressed_color.png")
    img_dec.show()
    print("Image couleur décompressée enregistrée : decompressed_color.png")