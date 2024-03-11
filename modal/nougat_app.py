import os
from pathlib import Path
from modal import Image, Stub, method, Secret

MODEL_DIR = "/model"
BASE_MODEL = "facebook/nougat-base"


def download_model_to_folder():
    from huggingface_hub import snapshot_download
    from transformers.utils import move_cache

    os.makedirs(MODEL_DIR, exist_ok=True)

    snapshot_download(
        BASE_MODEL,
        local_dir=MODEL_DIR,
        token=os.environ["HF_TOKEN"],
    )
    move_cache()


image = (
    Image.from_registry(
        "nvidia/cuda:12.1.0-base-ubuntu22.04", add_python="3.10"
    )
    .pip_install(
        "huggingface_hub",
        "hf-transfer",
        "torch",
        "transformers",
        "pillow",
        "python-Levenshtein",
        "nltk",
        "timm==0.5.4",
        "orjson",
        "opencv-python-headless",
        "datasets[vision]",
        "lightning>=2.0.0,<2022",
        "sentencepiece",
        "sconf>=0.2.3",
        "albumentations>=1.0.0",
        "pypdf>=3.1.0",
        "pypdfium2",
    )
    # Use the barebones hf-transfer package for maximum download speeds. No progress bar, but expect 700MB/s.
    .env({"HF_HUB_ENABLE_HF_TRANSFER": "1"})
    .run_function(
        download_model_to_folder,
        secrets=[Secret.from_name("huggingface-secret")],
        timeout=60 * 20,
    )
)

stub = Stub("nougat", image=image)

@stub.cls(gpu="T4", secrets=[Secret.from_name("huggingface-secret")])
class Model:
    def __enter__(self):
        from transformers import NougatProcessor, VisionEncoderDecoderModel

        self.processor = NougatProcessor.from_pretrained(BASE_MODEL)
        self.model = VisionEncoderDecoderModel.from_pretrained(BASE_MODEL).to("cuda")


    @method()
    def generate(self, image: bytes, max_new_tokens: int):
        import io
        from PIL import Image
        
        # prepare PDF image for the model
        image = Image.open(io.BytesIO(image)).convert("RGB")
        pixel_values = self.processor(image, return_tensors="pt").pixel_values

        outputs = self.model.generate(
            pixel_values.to("cuda"),
            min_length=1,
            max_new_tokens=max_new_tokens,
            bad_words_ids=[[self.processor.tokenizer.unk_token_id]],
        )

        sequence = self.processor.batch_decode(outputs, skip_special_tokens=True)[0]
        sequence = self.processor.post_process_generation(sequence, fix_markdown=False)

        return sequence


@stub.local_entrypoint()
def main(input_image_path: str, max_new_tokens: int=1000):
    input_image_path = Path(os.path.abspath(input_image_path))

    if input_image_path.exists():
        with open(input_image_path, "rb") as f:
            image = f.read()
    else:
        raise FileNotFoundError(f"File {input_image_path} does not exist")

    model = Model()
    model.generate.remote(image, max_new_tokens)
