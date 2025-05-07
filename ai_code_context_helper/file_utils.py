from pathlib import Path
from charset_normalizer import from_path, is_binary

def normalize_path(path):
    """将路径中的正斜杠转换为反斜杠，统一使用Windows风格路径"""
    if path:
        return path.replace("/", "\\")
    return path

def is_text_file(file_path):
    """检测文件是否为文本文件，使用charset-normalizer判断"""
    path = Path(file_path)
    
    # 检查文件大小
    try:
        file_size = path.stat().st_size
        if file_size > 10 * 1024 * 1024:  # 超过10MB就不处理
            return False
        if file_size == 0:  # 空文件视为文本文件
            return True
    except Exception:
        return False
    
    try:
        with open(str(path), "rb") as f:
            content = f.read()
            # 如果是二进制文件，返回False
            if is_binary(content):
                return False
            # 使用from_path尝试检测编码，如果有结果则是文本文件
            matches = from_path(str(path))
            return len(matches) > 0
    except Exception:
        return False
    
    # 默认返回False
    return False

def read_file_content(path_obj):
    """智能读取文件内容，使用多种方法尝试检测正确的编码"""
    try:
        # 如果文件不存在或大小为0，返回空字符串
        if not path_obj.exists() or path_obj.stat().st_size == 0:
            return ""
        
        # 先检查是否为文本文件
        if not is_text_file(path_obj):
            raise Exception("文件不是文本文件")
        
        # 使用charset_normalizer检测可能的编码并遍历所有匹配项
        matches = from_path(str(path_obj))
        
        # 尝试所有中文常见编码（如果检测到中文）
        best_match = matches.best()
        if best_match and best_match.language == "Chinese":
            chinese_encodings = ['utf-8', 'gb18030', 'gbk', 'gb2312', 'big5']
            for encoding in chinese_encodings:
                try:
                    with open(str(path_obj), 'r', encoding=encoding) as f:
                        content = f.read()
                        # 检查是否有乱码特征
                        if not '\ufffd' in content[:1000]:  # 检查前1000个字符中是否有替换字符
                            return content
                except UnicodeDecodeError:
                    continue
        
        # 返回最可能匹配的结果
        if len(matches) > 0:
            return str(matches.best())
        
        return open(str(path_obj), 'r', encoding='utf-8', errors='replace').read()
            
    except Exception as e:
        raise Exception(f"无法读取文件: {str(e)}")