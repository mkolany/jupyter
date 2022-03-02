_all = ['Handler', 'FileHandler','DataHandler', 'Pipeline', 'DataModel']

import pathlib
from IPython.display import display
from abc import ABC, abstractmethod
from typing import Callable, Optional, List
import pandas as pd
import numpy as np
import itertools

class Handler(ABC):
    @abstractmethod
    def handle(self, *args, **kwargs):
        raise NotImplementedError("You should implement this!")
        
    def update_handler(self, new_handler: Callable) -> None:
        self.handle = new_handler
        
class FileHandler(Handler):
    def handle(self, path: pathlib.Path) -> pd.DataFrame:
        with open(path) as f:
            for i, row in enumerate(f):
                for delimiter, decimal in (itertools.product([';',',','\t'], ['.',','])):
                    try:
                        return pd.read_csv(
                            path,
                            delimiter=delimiter,
                            decimal=decimal,
                            index_col=0,
                            skiprows=i,
                            header=None,
                            on_bad_lines='skip',
                            dtype=np.float64,
                        )

                                        # return df[df.columns[-1]]

                    except Exception:
                        pass
    
class DataHandler(Handler):
    def __init__(self, name:Optional[str]='handler', handler: Optional[Callable]=None):
        self.name=name

        super().__init__()
        
        if handler is not None:
            self.update_handler(handler)
        
    def handle(self,  data: pd.DataFrame) -> pd.DataFrame:
        return data

class Pipeline(DataHandler):
    def __init__(self) -> None:
        self.operations: List[DataHandler] = []
        
    def handle(self,  df: pd.DataFrame) -> pd.DataFrame:
        for o in self.operations:
            data = df[df.columns[-1]]
            df[o.name]= o.handle( data )
        return df

    def add(self, *operations: DataHandler) -> None:
        for o in operations:
            self.operations.append(o)

    def remove(self,*operations: DataHandler) -> None:
        for o in operations:
            self.operations.remove(o)
            
class DataModel(ABC):
    def __init__(self, path: pathlib.Path, reader: Optional[FileHandler]=FileHandler(), pipeline: Optional[Pipeline]=None ) -> None:
        self._path=path
        self._reader=reader

        self._pipeline=pipeline if pipeline is not None else Pipeline()

        self.update()

    def update(self):
        self.raw_data = self._reader.handle(self.path)
        self.all_data = self._pipeline.handle(self.raw_data)
        self.data = self.all_data[self.all_data.columns[-1]]

    def add_to_pipeline(self, *operations: DataHandler):
        self._pipeline.add(*operations)
        self.update()
    @property
    def path(self):
        return self._path
    
    @path.setter
    def path(self, path: pathlib.Path):
        self._path = path
        self.update()