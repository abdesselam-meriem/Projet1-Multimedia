from PIL import Image
import numpy as np

def rle_compress(image_array):
    """Compresse une image binaire (0 et 255) en utilisant RLE"""
    flat = image_array.flatten()
    compressed = []
    i = 0
    while i < len(flat):
        run_value = flat[i]
        run_length = 1
        # Compter les répétitions
        while i + run_length < len(flat) and flat[i + run_length] == run_value:
            run_length += 1

        if run_length >= 3:
            # Mot de deux octets avec bit fort = 1
            header = (1 << 15) | run_length
            compressed.append((header, run_value))
            i += run_length
        else:
            # Suite de pixels non répétitifs
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

def save_compressed(filename, compressed):
    """Sauvegarde dans un fichier texte binaire simple"""
    with open(filename, "w") as f:
        for header, data in compressed:
            f.write(str(header) + " ")
            if isinstance(data, list):
                f.write(" ".join(map(str, data)))
            else:
                f.write(str(data))
            f.write("\n")

def calculate_compression_ratio(original, compressed_file):
    original_size = original.size  # nombre de pixels
    compressed_size = sum(len(line.split()) for line in open(compressed_file))
    return original_size / compressed_size

if __name__ == "__main__":
    # Charger une image noir/blanc (format PNG recommandé)
    img = Image.open("image_bw.png").convert("L")  # "L" = niveaux de gris
    arr = np.array(img)

    compressed = rle_compress(arr)
    save_compressed("compressed_rle.txt", compressed)

    ratio = calculate_compression_ratio(arr, "compressed_rle.txt")
    print(f"Taux de compression : {ratio:.2f}")