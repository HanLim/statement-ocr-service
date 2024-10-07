import os
import re
import pytesseract

from datetime import datetime
from abc import ABC, abstractmethod
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
        # increase sharpness, remove noise etc
        pass

    def __get_bank(self, statement_content: str) -> None:
        pattern = r'(?i)(\b\w+\b)\s+BANK'
        matches = re.findall(pattern, statement_content)

        if not matches:
            raise ValueError("Unable to detect the bank name from the statement")
        
        # getting the first as logically, the the first X bank will be the statement's bank name
        self.bank_name = matches[0]

        if self.bank_name.upper() not in self.SUPPORTED_BANK:
            raise ValueError(f"Statement of the bank not supported. Currently supports only {self.SUPPORTED_BANK}")
    
    def __get_address(self):
        return self.setting.get_address(self.image)

    def __get_statement_date(self, text: str):
        return self.setting.get_statement_date(text)
        
    def __set_bank_setting(self) -> None:
        self.setting: BankSetting = {
            "PUBLIC": PublicBankSetting,
            "MAYBANK": MayBankSetting,
        }[self.bank_name]

    # this logic currently only works for first page of PBB statement
    def extract(self) -> None:
        self.preprocess()
        text = pytesseract.image_to_string(self.image)
        self.__get_bank(text)
        self.__set_bank_setting()
        address = self.__get_address()
        date = self.__get_statement_date(text)

        # print(text)
        

        return ""
    

class BankSetting(ABC):
    @staticmethod
    @abstractmethod
    def get_address(image: ImageFile): pass
    
    @staticmethod
    @abstractmethod
    def get_statement_date(text: str): pass


class PublicBankSetting(BankSetting):
    @staticmethod
    def get_address(image: ImageFile):
        crop_area = (200, 300, 580, 450)
        cropped_image = image.crop(crop_area)
        return pytesseract.image_to_string(cropped_image)
    
    @staticmethod
    def get_statement_date(text: str): 
        pattern = r'Tarikh Penyata / Statement Date (\d{1,2} \w{3} \d{4})'
        statement_date = re.search(pattern, text)
        if not statement_date:
            raise LookupError("Statement date not found")
        statement_date = datetime.strptime(statement_date.group(1), '%d %b %Y')
        return statement_date


class MayBankSetting(BankSetting):
    @staticmethod
    def get_address(image: ImageFile):
        raise NotImplementedError("Demo class, not implemented yet")

    @staticmethod
    def get_statement_date(text: str):
        raise NotImplementedError("Demo class, not implemented yet")

if __name__ == "__main__":
    # converter = PdfToImageConverter("test_pdf.pdf")
    # converter.convert()

    ocr = StatementExtractor("converted_test_pdf_1.PNG")
    try:
        print(ocr.extract())
    except Exception as e:
        print(f'ERROR: {e}')