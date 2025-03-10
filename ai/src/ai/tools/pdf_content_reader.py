from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import fitz
from typing import Optional

class PDFContentReaderInput(BaseModel):
    """Input schema for PDFContentReader."""
    file_path: str = Field(..., description="Path to the PDF file.")

class PDFContentReader(BaseTool):
    name: str = "PDF Content Reader"
    description: str = (
        "A tool that reads and extracts text from a given PDF file."
    )
    args_schema: Type[BaseModel] = PDFContentReaderInput
    file_path: Optional[str] = None
    
    def __init__(self, file_path: Optional[str] = None, **kwargs):
        """Initializes the PDFContentReader tool.
        
        Args:
            file_path (Optional[str]): Path to the PDF file to read.
            **kwargs: Additional keyword arguments passed to BaseTool.
        """
        if file_path is not None:
            kwargs["description"] = (
                f"A tool that reads and extracts text from a given PDF file. "
                f"The default file path is {file_path}, but you can provide a different 'file_path' parameter to read another file."
            )
        
        super().__init__(**kwargs)
        self.file_path = file_path

    def _run(self, **kwargs) -> str:
        """Reads and extracts text from a given PDF file.
        
        Args:
            **kwargs: Additional keyword arguments.
        
        Returns:
            str: Extracted text from the PDF file.
        """
        file_path = kwargs.get("file_path", self.file_path)
        if file_path is None:
            return "Error: No file path provided. Please provide a file path either in the constructor or as an argument."
        
        text = ""
        with fitz.open(file_path) as pdf_file:
            for page in pdf_file:
                text += page.get_text()
        
        return text
    
if __name__ == "__main__":
    # Example usage
    file_path = "./knowledge/CV_YuvalMehta.pdf"
    pdf_reader = PDFContentReader()
    print(pdf_reader.run(file_path=file_path))