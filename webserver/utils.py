import os
import re
import pytesseract
import pandas as pd

from .statement.serializers import *
from datetime import datetime
from abc import ABC, abstractmethod
from PIL import Image, ImageFile
from typing import Optional, List, Tuple
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

    @staticmethod
    def largest_smaller(sorted_list: List[int], target: int) -> Optional[int]:
        left, right = 0, len(sorted_list) - 1
        result = None
        
        while left <= right:
            mid = (left + right) // 2
            if sorted_list[mid] < target:
                result = sorted_list[mid]
                left = mid + 1
            else:
                right = mid - 1

        return result


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
    
    def __get_address(self) -> str:
        return self.setting.get_address(self.image)

    def __get_statement_date(self, text: str) -> datetime:
        return self.setting.get_statement_date(text)
    
    def __get_total(self, text: str) -> Tuple[float]:
        return self.setting.get_total(text)
        
    def __set_bank_setting(self) -> None:
        self.setting: BankSetting = {
            "PUBLIC": PublicBankSetting,
            "MAYBANK": MayBankSetting,
        }[self.bank_name]

    def __get_transaction(self, text: str, df: pd.DataFrame, statement_date: datetime):
        return self.setting.get_transaction(text, df, statement_date)

    # this logic currently only works for first page of PBB statement
    def extract(self) -> StatementCreate:
        """
        Alternatively, the total, counts, date etc can be done by cropping and OCR.
        """
        self.preprocess()
        df = pytesseract.image_to_data(self.image, output_type=pytesseract.Output.DATAFRAME)
        text = pytesseract.image_to_string(self.image)
        self.__get_bank(text)
        self.__set_bank_setting()
        address = self.__get_address()
        statement_date = self.__get_statement_date(text)
        total_debit, total_credit, count_debit, count_credit = self.__get_total(text)
        transactions = self.__get_transaction(text, df, statement_date)


        return StatementCreate(
            address=address,
            name=self.bank_name,
            statement_date=statement_date,
            detail={
                "total_debit":total_debit,
                "total_credit":total_credit,
                "no_debit":count_debit,
                "no_credit":count_credit,
            },
            transactions=transactions
        )


class BankSetting(ABC):
    @staticmethod
    @abstractmethod
    def get_address(image: ImageFile) -> str: ...
    
    @staticmethod
    @abstractmethod
    def get_statement_date(text: str) -> datetime: ...

    @staticmethod
    @abstractmethod
    def get_total(text: str) -> Tuple[float]: ...

    @staticmethod
    @abstractmethod
    def get_transaction(text: str, df: pd.DataFrame, statement_date: datetime) -> List[dict]: ...


class PublicBankSetting(BankSetting):
    @staticmethod
    def get_address(image: ImageFile) -> str:
        crop_area = (200, 300, 580, 450)
        cropped_image = image.crop(crop_area)
        return pytesseract.image_to_string(cropped_image)
    
    @staticmethod
    def get_statement_date(text: str) -> datetime: 
        pattern = r'Statement Date\s*(\d{1,2}\s\w{3}\s\d{4})'
        statement_date = re.search(pattern, text)
        if not statement_date:
            raise LookupError("Statement date not found")
        statement_date = datetime.strptime(statement_date.group(1), '%d %b %Y')
        return statement_date
    
    @staticmethod
    def get_total(text: str) -> Tuple[float]:
        def __extract_total(transaction_type: str) -> float:
            pattern = rf'Total\s*' + transaction_type + r'\s*([\d,]+(?:\.\d{2}))'
            total = re.search(pattern, text)
            if not total:
                raise LookupError(f"Total {transaction_type} not found")
            return float(total.group(1).replace(',', ''))
        
        def __extract_count(transaction_type: str) -> int:
            pattern = rf'No\.\s*of\s*' + transaction_type + r'\s*(\d+)'
            count = re.search(pattern, text)
            if not count:
                raise LookupError(f"No. of {transaction_type} not found")
            return int(count.group(1).replace(',', ''))
        
        total_debit = __extract_total("Debits")
        total_credit = __extract_total("Credits")
        count_debit = __extract_count("Debits")
        count_credit = __extract_count("Credits")

        return total_debit, total_credit, count_debit, count_credit
    
    @staticmethod
    def get_transaction(text: str, df: pd.DataFrame, statement_date: datetime) -> List[dict]:
        """
        Hard code to retrieve the debit and credit transactions from the statement due to time constraint.
        
        Better way would be OCR and retrieve the approx x,y of the debit/credits column based on the header, 
        instead of the magic number below.
        """
        debits = df[(df["left"] > 850) & (df["left"] < 1050) & (df["top"] > 950) & (df["top"] < 1200)]
        credits = df[(df["left"] > 1050) & (df["left"] < 1250) & (df["top"] > 950) & (df["top"] < 1400)]

        transaction_date_pattern = r'^\d{2}/\d{2}$'
        date_df = df[df['text'].str.contains(transaction_date_pattern, regex=True, na=False)]
        dates = { row['line_num']: row for _, row in date_df.iterrows() }
        line_nums = sorted(dates)

        def __prepare(tx_df: pd.DataFrame, negative: bool=False) -> None:
            for _, tx in tx_df.iterrows():
                line = tx["line_num"]

                transaction_date = dates.get(line)
                if transaction_date is None:
                    line = Utils.largest_smaller(line_nums, line)
                    if line is None:
                        continue # skip the invalid line

                date = f"{dates.get(line)['text']}/{statement_date.year}"
                date = datetime.strptime(date, "%d/%m/%Y")

                amount = float(tx["text"].replace(',', ''))
                if negative:
                    amount = -amount 

                transactions.append({
                    "transaction_date": date,
                    "amount": amount
                }) 

        transactions = []
        __prepare(debits, negative=True)
        __prepare(credits)
        
        return transactions

class MayBankSetting(BankSetting):
    @staticmethod
    def get_address(image: ImageFile) -> str:
        raise NotImplementedError("Demo class, not implemented yet")

    @staticmethod
    def get_statement_date(text: str) -> datetime:
        raise NotImplementedError("Demo class, not implemented yet")
    
    @staticmethod
    def get_total(text: str) -> Tuple[float]:
        raise NotImplementedError("Demo class, not implemented yet")
    
    @staticmethod
    def get_transaction(text: str, df: pd.DataFrame, statement_date: datetime) -> List[dict]:
        raise NotImplementedError("Demo class, not implemented yet")
    

if __name__ == "__main__":
    # converter = PdfToImageConverter("test_pdf.pdf")
    # converter.convert()

    ocr = StatementExtractor("converted_test_pdf_1.PNG")
    try:
        print(ocr.extract())
    except Exception as e:
        print(f'ERROR: {e}')