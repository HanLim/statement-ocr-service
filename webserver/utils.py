import os
import re
import pytesseract

from PIL import Image, ImageFile
from typing import Optional, List
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
        
        Utils.file_exists(path, raise_exception=True)
        
        self.path = path
        self.target_type = target_type
        self.converted_path = []
    
    def convert(self) -> List[str]:
        images = convert_from_path(self.path)
        filename = self.path.split(".")[0]

        names = []
        for i, image in enumerate(images):
            image_name = f"converted_{filename}_{i + 1}.{self.target_type}"
            image.save(image_name, self.target_type)
            names.append(image_name)

        return names


class StatementExtractor:
    def __init__(self, path: str) -> None:
        if not path:
            raise ValueError("Invalid or missing file path")
        
        Utils.file_exists(path, raise_exception=True)
        self.image = Utils.open_image(path, raise_exception=True)
        self.SUPPORTED_BANK = ['PUBLIC']
        
    def preprocess(self) -> None:
        self.__image_preprocess()

    def __image_preprocess(self) -> None:
        # increase sharpess etc
        pass

    def __get_bank(self, statement_content: str) -> None:
        pattern = r'(?i)(\b\w+\b)\s+BANK'
        matches = re.findall(pattern, statement_content)

        if not matches:
            raise ValueError("Unable to detect the bank name from the statement")
        
        self.bank_name = matches[0]

        if self.bank_name.upper() not in self.SUPPORTED_BANK:
            raise ValueError(f"Statement of the bank not supported. Currently supports only {self.SUPPORTED_BANK}")

    def ocr(self):
        self.preprocess()
        text = pytesseract.image_to_string(self.image)
        self.__get_bank(text)

        return ""



if __name__ == "__main__":
    # converter = PdfToImageConverter("test_pdf.pdf")
    # converter.convert()

    ocr = StatementExtractor("converted_test_pdf_1.PNG")
    try:
        print(ocr.ocr())
    except Exception as e:
        print(f'ERROR: {e}')