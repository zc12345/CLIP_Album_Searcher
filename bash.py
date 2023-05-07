import argparse
import matplotlib.pyplot as plt
from PIL import Image
from loguru import logger

from album import Album

if __name__ == "__main__":
    parser =argparse.ArgumentParser()
    parser.add_argument("--root_path", type=str, default="D:\documents\images")
    parser.add_argument("--dump_path", type=str, default="db.pt")
    parser.add_argument("--backup_path", type=str, default="backup")
    parser.add_argument("--query", type=str, default=None)
    parser.add_argument("--image", type=str, default=None)
    parser.add_argument("--k", type=int, default=3)
    parser.add_argument("--threshold", type=float, default=None)
    args = parser.parse_args()
    
    album = Album(args.root_path, args.dump_path, args.backup_path)
    if args.query is not None:
        paths, probs = album.text_search([args.query], args.k, args.threshold)
        for img_path, prob in zip(paths, probs):
            print(img_path, prob)
            img = Image.open(img_path)
            plt.imshow(img)
            plt.show()
    elif args.image is not None:
        try:
            paths, probs = album.image_search(Image.open(args.image), args.k, args.threshold)
            for img_path, prob in zip(paths, probs):
                print(img_path, prob)
                img = Image.open(img_path)
                plt.imshow(img)
                plt.show()
        except Exception as e:
            logger.error(f"Error searching image: {e}, can't open {args.image}")
    else:
        logger.error("Please specify --query or --image")