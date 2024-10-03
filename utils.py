import os
import pytesseract

from PIL import Image, ImageFile
from typing import Optional
from pdf2image import convert_from_path

class Utils:
    @staticmethod
    def file_exists(path: str, raise_exception=False) -> bool:
        exists = os.path.isfile(path)

        if not exists and raise_exception: 
            raise FileExistsError("File specified does not exist")
        
        return exists
    
    @staticmethod
    def open_image(path: str, raise_exception=False) -> Optional[ImageFile.ImageFile]:
        try:
            return Image.open(path)
        except Exception as e:
            if raise_exception:
                raise e


class PdfToImageConverter:
    def __init__(self, path: str, target_type: str="PNG") -> None:
        if not path:
            raise ValueError("Invalid or missing file path")
        
        if target_type not in ["JPG", "PNG"]:
            raise ValueError("Invalid image target type")
        
        Utils.file_exists(self.path, raise_exception=True)
        
        self.path = path
        self.target_type = target_type
        self.converted_path = []
    
    def convert(self):
        images = convert_from_path(self.path)
        filename = self.path.split(".")[0]

        for i, image in enumerate(images):
            image.save(f"converted_{filename}_{i + 1}.{self.target_type}", self.target_type)


class StatementExtractor:
    def __init__(self, path: str) -> None:
        if not path:
            raise ValueError("Invalid or missing file path")
        
        Utils.file_exists(path, raise_exception=True)
        self.image = Utils.open_image(self.path, raise_exception=True)
        
    def preprocess(self) -> None:
        pass

    def ocr(self):
        text = pytesseract.image_to_string(self.image)
        return text



if __name__ == "__main__":
    # converter = PdfToImageConverter("test_pdf.pdf")
    # converter.convert()

    ocr = StatementExtractor("converted_test_pdf_1.PNG")
    ocr.preprocess()
    print(ocr.ocr())