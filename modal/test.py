import modal
from pathlib import Path
import os

cls = modal.Cls.lookup("nougat-app", "Model")
model = cls()

input_image_path = "./data/test.png"

input_image_path = Path(os.path.abspath(input_image_path))
with open(input_image_path, "rb") as f:
    image = f.read()

res = model.generate.remote(image, max_new_tokens=1000)
with open("./data/test.mmd", "w") as f:
    f.write(res)
