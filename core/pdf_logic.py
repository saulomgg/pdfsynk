from pypdf import PdfReader, PdfWriter
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import io

class PdfProcessor:
    @staticmethod
    def parse_page_selection(page_str, page_count):
        """Converte a string de seleção de páginas em uma lista de índices 0-based."""
        selected_pages = set()
        page_str = page_str.replace(" ", "")
        
        for part in page_str.split(','):
            if '-' in part:
                try:
                    start, end = map(int, part.split('-'))
                    start = max(1, start)
                    end = min(page_count, end)
                    for page_num in range(start, end + 1):
                        selected_pages.add(page_num - 1)
                except ValueError:
                    continue
            elif part:
                try:
                    page_num = int(part)
                    if 1 <= page_num <= page_count:
                        selected_pages.add(page_num - 1)
                except ValueError:
                    continue
                    
        return sorted(list(selected_pages))

    @staticmethod
    def extract_pages(reader, page_indices):
        writer = PdfWriter()
        for index in page_indices:
            writer.add_page(reader.pages[index])
        return writer

    @staticmethod
    def merge_pdfs(file_list):
        writer = PdfWriter()
        for path in file_list:
            reader = PdfReader(path)
            for page in reader.pages:
                writer.add_page(page)
        return writer

    @staticmethod
    def rotate_pages(reader, page_indices, angle):
        writer = PdfWriter()
        page_count = len(reader.pages)
        for i in range(page_count):
            page = reader.pages[i]
            if i in page_indices:
                page.rotate(angle)
            writer.add_page(page)
        return writer

    @staticmethod
    def apply_watermark(reader, watermark_reader, page_indices):
        writer = PdfWriter()
        watermark_page = watermark_reader.pages[0]
        page_count = len(reader.pages)
        for i in range(page_count):
            page = reader.pages[i]
            if i in page_indices:
                page.merge_page(watermark_page)
            writer.add_page(page)
        return writer

    @staticmethod
    def images_to_pdf(image_paths):
        images = []
        for path in image_paths:
            img = Image.open(path).convert('RGB')
            images.append(img)
        
        output = io.BytesIO()
        if images:
            images[0].save(output, "PDF", resolution=100.0, save_all=True, append_images=images[1:])
        return output.getvalue()

    @staticmethod
    def protect_pdf(reader, user_password, owner_password=None):
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        writer.encrypt(user_password, owner_password=owner_password)
        return writer

    @staticmethod
    def update_metadata(reader, metadata_dict):
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        
        formatted_metadata = {}
        for key, value in metadata_dict.items():
            if value:
                formatted_metadata[f'/{key}'] = value
        
        writer.add_metadata(formatted_metadata)
        return writer

    @staticmethod
    def compress_pdf(reader):
        """Compacta o PDF reduzindo a qualidade de imagens e removendo objetos duplicados."""
        writer = PdfWriter()
        for page in reader.pages:
            page.compress_content_streams()  # Comprime fluxos de conteúdo
            writer.add_page(page)
        
        # Reduz o tamanho de imagens (se possível via pypdf)
        for page in writer.pages:
            for img in page.images:
                img.replace(img.image, quality=60)
        
        return writer
