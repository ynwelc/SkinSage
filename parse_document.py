import re
import json
import os
from typing import List, Dict, Any

# 尝试导入依赖库，如果失败则标记为None
try:
    from pypdf import PdfReader
    pypdf_available = True
except ImportError:
    PdfReader = None
    pypdf_available = False

try:
    from docx import Document as DocxDocument
    python_docx_available = True
except ImportError:
    DocxDocument = None
    python_docx_available = False

class DocumentParser:
    def __init__(self):
        # 重新设计正则表达式，准确匹配文档格式
        self.title_pattern = re.compile(r'^#\s*\*+\s*([^\*]+?)\s*\*+$')
        self.category_pattern = re.compile(r'^##\s*\*+\s*(\d+、([^\*]+?))\s*\*+$')
        self.question_pattern = re.compile(r'^(\d+)\.问：(.+?)$')
        self.answer_pattern = re.compile(r'^答：(.+?)$')
    
    def parse_pdf(self, file_path: str) -> Dict[str, Any]:
        """解析PDF格式的文档"""
        if not pypdf_available:
            raise ImportError("pypdf库未安装，无法解析PDF文件")
        
        reader = PdfReader(file_path)
        text = ""
        
        # 提取所有页面的文本
        for page in reader.pages:
            extracted_text = page.extract_text()
            if extracted_text:
                text += extracted_text + "\n"
        
        return self._parse_generic_text(text, file_path)
    
    def parse_word(self, file_path: str) -> Dict[str, Any]:
        """解析Word格式的文档"""
        if not python_docx_available:
            raise ImportError("python-docx库未安装，无法解析Word文件")
        
        doc = DocxDocument(file_path)
        text = ""
        
        # 提取所有段落的文本
        for para in doc.paragraphs:
            if para.text.strip():
                text += para.text + "\n"
        
        return self._parse_generic_text(text, file_path)
    
    def parse_markdown(self, file_path: str) -> Dict[str, Any]:
        """解析Markdown格式的文档"""
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        return self._parse_generic_text(text, file_path)
    
    def _parse_generic_text(self, text: str, file_path: str) -> Dict[str, Any]:
        """通用文本解析方法"""
        result = {
            "title": os.path.basename(file_path),
            "categories": [{"name": "默认分类", "questions": []}]
        }
        
        # 简单的文本分块，将连续文本按段落分割
        paragraphs = text.split('\n\n')
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        # 将每个段落作为一个问题-回答对
        for i, para in enumerate(paragraphs):
            result["categories"][0]["questions"].append({
                "question": f"文档内容{i+1}",
                "answer": para
            })
        
        return result
    
    def chunk_document(self, parsed_doc: Dict[str, Any], chunk_size: int = 500, overlap: int = 50) -> List[Dict[str, Any]]:
        """将文档分块，支持语义分块（重叠50字，最大500字）"""
        chunks = []
        
        for category in parsed_doc["categories"]:
            category_name = category["name"]
            
            for qna in category["questions"]:
                question = qna["question"]
                answer = qna["answer"]
                
                # 组合问题和回答为一个文本块
                text = f"问题：{question}\n回答：{answer}"
                
                # 按字符数分块，重叠50字，最大500字
                start = 0
                while start < len(text):
                    end = min(start + chunk_size, len(text))
                    chunk = text[start:end]
                    
                    chunks.append({
                        "category": category_name,
                        "question": question,
                        "chunk_content": chunk,
                        "start_index": start,
                        "end_index": end
                    })
                    
                    # 如果不是最后一块，添加重叠
                    if end < len(text):
                        start = end - overlap
                    else:
                        break
        
        return chunks
    
    def save_chunks(self, chunks: List[Dict[str, Any]], output_path: str):
        """保存分块结果到JSON文件"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, ensure_ascii=False, indent=2)
    
    def run(self, input_file: str, output_file: str):
        """执行完整的解析和分块流程，自动识别文件类型"""
        print(f"开始解析文档：{input_file}")
        
        # 根据文件扩展名选择解析方法
        file_ext = os.path.splitext(input_file)[1].lower()
        
        if file_ext == '.pdf':
            parsed_doc = self.parse_pdf(input_file)
        elif file_ext in ['.docx', '.doc']:
            parsed_doc = self.parse_word(input_file)
        elif file_ext == '.md':
            parsed_doc = self.parse_markdown(input_file)
        else:
            raise ValueError(f"不支持的文件类型：{file_ext}")
        
        print(f"解析完成，标题：{parsed_doc['title']}")
        print(f"共包含 {len(parsed_doc['categories'])} 个分类")
        
        total_questions = sum(len(cat['questions']) for cat in parsed_doc['categories'])
        print(f"共包含 {total_questions} 个问题")
        
        print("开始分块...")
        chunks = self.chunk_document(parsed_doc)
        print(f"分块完成，共生成 {len(chunks)} 个块")
        
        self.save_chunks(chunks, output_file)
        print(f"分块结果已保存到：{output_file}")

if __name__ == "__main__":
    parser = DocumentParser()
    parser.run(
        input_file="d:/code/beauty-system/售后百问百答.md",
        output_file="d:/code/beauty-system/document_chunks.json"
    )
