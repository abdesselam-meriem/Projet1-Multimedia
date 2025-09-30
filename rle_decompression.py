from PIL import Image
import numpy as np

def rle_decompress(filename, image_shape):
    """Lit un fichier compressé et reconstruit l'image originale"""
    decompressed = []

    with open(filename, "r") as f:
        for line in f:
            parts = list(map(int, line.strip().split()))
            header = parts[0]
            if header >> 15 == 1:  # cas répétition
                run_length = header & 0x7FFF  # 15 bits
                value = parts[1]
                decompressed.extend([value] * run_length)
            else:  # cas suite brute
                seq_length = header & 0x7FFF
                seq = parts[1:1+seq_length]
                decompressed.extend(seq)

    arr = np.array(decompressed, dtype=np.uint8).reshape(image_shape)
    return arr

if __name__ == "__main__":
    
    shape = (225, 225)  

    img_array = rle_decompress("compressed_rle.txt", shape)

    # Sauvegarde et affichage
    img = Image.fromarray(img_array, mode="L")
    img.save("decompressed.png")
    img.show()
    print("Image décompressée enregistrée : decompressed.png")