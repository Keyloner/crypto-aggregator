import os
import pandas as pd
from typing import List
from app.schemas.market_data import CryptoPrice

class CsvStorage:
    FILENAME = "history.csv"
    def save(self,prices:List[CryptoPrice]):
        data=[price.model_dump() for price in prices]
        df=pd.DataFrame(data)
#Проверка существует ли файл
        file_exists = os.path.isfile(self.FILENAME)

        df.to_csv(
            self.FILENAME,
            mode="a",
            header=not file_exists,
            index=False
        )
        print(f"Saved {len(prices)} records to {self.FILENAME}")