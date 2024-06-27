import ast
import jsbeautifier
import javalang

class CodeLanguageDetector:
    @staticmethod
    def __is_python_code(code):
        try:
            ast.parse(code)
            return True
        except SyntaxError:
            return False

    @staticmethod
    def __is_javascript_code(code):
        try:
            jsbeautifier.beautify(code)
            return True
        except:
            return False

    @staticmethod
    def __is_java_code(code):
        try:
            javalang.parse.parse(code)
            return True
        except javalang.parser.JavaSyntaxError:
            return False
        except javalang.tokenizer.LexerError:
            return False
        except Exception as e:
            # Log the unexpected error
            print(f"Unexpected error in Java code detection: {e}")
            return False

    @staticmethod
    def __is_csharp_code(code):
        csharp_keywords = ["namespace", "class", "struct", "enum", "interface", "using", "public", "private",
                           "protected", "static", "void", "int", "double", "string", "new", "return", "if", "else",
                           "for", "while", "foreach"]
        keyword_count = sum(1 for keyword in csharp_keywords if keyword in code)
        return keyword_count > 5

    @staticmethod
    def __is_cpp_code(code):
        cpp_keywords = ["int", "double", "float", "char", "string", "void", "namespace", "class", "struct", "enum",
                        "public", "private", "protected", "static", "return", "if", "else", "for", "while", "do",
                        "switch", "case", "break", "continue"]
        keyword_count = sum(1 for keyword in cpp_keywords if keyword in code)
        return keyword_count > 5

    @staticmethod
    def __is_php_code(code):
        php_keywords = ["<?php", "<?", "echo", "if", "else", "elseif", "while", "for", "foreach", "function", "class",
                        "require", "include", "$", "->", "::"]
        keyword_count = sum(1 for keyword in php_keywords if keyword in code)
        return keyword_count > 3

    @staticmethod
    def __is_ruby_code(code):
        ruby_keywords = ["def", "end", "class", "module", "require", "if", "else", "elsif", "unless", "case", "when",
                         "while", "until", "for", "do", "yield", "return"]
        keyword_count = sum(1 for keyword in ruby_keywords if keyword in code)
        return keyword_count > 5

    @staticmethod
    def __is_swift_code(code):
        swift_keywords = ["import", "func", "class", "struct", "enum", "extension", "var", "let", "if", "else",
                          "switch", "case", "for", "while", "return"]
        keyword_count = sum(1 for keyword in swift_keywords if keyword in code)
        return keyword_count > 5

    @staticmethod
    def __is_go_code(code):
        go_keywords = ["package", "import", "func", "struct", "interface", "var", "const", "if", "else", "switch",
                       "case", "for", "range", "return"]
        keyword_count = sum(1 for keyword in go_keywords if keyword in code)
        return keyword_count > 5

    @staticmethod
    def __is_typescript_code(code):
        typescript_keywords = ["interface", "class", "enum", "function", "const", "let", "var", "import", "export",
                               "if", "else", "switch", "case", "for", "while", "return"]
        keyword_count = sum(1 for keyword in typescript_keywords if keyword in code)
        return keyword_count > 5

    @staticmethod
    def __is_html_code(code):
        html_tags = ["<!DOCTYPE", "<html", "<head", "<title", "<body", "<div", "<p", "<a", "<img", "<ul", "<ol", "<li",
                     "<table", "<tr", "<td", "<form", "<input", "<button"]
        tag_count = sum(1 for tag in html_tags if tag in code)
        return tag_count > 2

    @staticmethod
    def __is_c_code(code):
        c_keywords = ["int", "double", "float", "char", "void", "struct", "enum", "typedef", "sizeof", "if", "else",
                      "switch", "case", "for", "while", "do", "break", "continue", "return"]
        keyword_count = sum(1 for keyword in c_keywords if keyword in code)
        return keyword_count > 5

    @staticmethod
    def detect_language(code: str, language: str):
        try:
            match language.lower():
                case "python":
                    return CodeLanguageDetector.__is_python_code(code)
                case "javascript":
                    return CodeLanguageDetector.__is_javascript_code(code)
                case "java":
                    return CodeLanguageDetector.__is_java_code(code)
                case "html":
                    return CodeLanguageDetector.__is_html_code(code)
                case "c":
                    return CodeLanguageDetector.__is_c_code(code)
                case "csharp":
                    return CodeLanguageDetector.__is_csharp_code(code)
                case "cpp":
                    return CodeLanguageDetector.__is_cpp_code(code)
                case "php":
                    return CodeLanguageDetector.__is_php_code(code)
                case "ruby":
                    return CodeLanguageDetector.__is_ruby_code(code)
                case "swift":
                    return CodeLanguageDetector.__is_swift_code(code)
                case "go":
                    return CodeLanguageDetector.__is_go_code(code)
                case "typescript":
                    return CodeLanguageDetector.__is_typescript_code(code)
        except Exception as e:
            print(f"Unexpected error in language detection: {e}")
            return False
