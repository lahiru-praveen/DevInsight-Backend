import ast
import jsbeautifier
import javalang

class CodeLanguageDetector:
    @staticmethod
    def __is_python_code(code):
        try:
            # Attempt to parse the code snippet as Python code
            ast.parse(code)
            # If parsing is successful, it's likely Python code
            return True
        except SyntaxError:
            # If parsing fails, it's not Python code
            return False

    @staticmethod
    def __is_javascript_code(code):
        try:
            # Attempt to beautify the JavaScript code
            jsbeautified_code = jsbeautifier.beautify(code)
            # If the code can be beautified, it's likely JavaScript code
            return True
        except:
            # If beautification fails, it's not JavaScript code
            return False

    @staticmethod
    def __is_java_code(code):
        try:
            # Attempt to parse the code snippet as Java code
            javalang.parse.parse(code)
            # If parsing is successful, it's likely Java code
            return True
        except javalang.parser.JavaSyntaxError:
            # If parsing fails, it's not Java code
            return False

    @staticmethod
    def __is_csharp_code(code):
        # Check for common C# keywords
        csharp_keywords = ["namespace", "class", "struct", "enum", "interface", "using", "public", "private",
                           "protected", "static", "void", "int", "double", "string", "new", "return", "if", "else",
                           "for", "while", "foreach"]
        # Count the number of C# keywords in the code snippet
        keyword_count = sum(1 for keyword in csharp_keywords if keyword in code)
        # If a sufficient number of keywords are found, it's likely C# code
        return keyword_count > 5

    @staticmethod
    def __is_cpp_code(code):
        # Check for common C++ keywords
        cpp_keywords = ["int", "double", "float", "char", "string", "void", "namespace", "class", "struct", "enum",
                        "public", "private", "protected", "static", "return", "if", "else", "for", "while", "do",
                        "switch", "case", "break", "continue"]
        # Count the number of C++ keywords in the code snippet
        keyword_count = sum(1 for keyword in cpp_keywords if keyword in code)
        # If a sufficient number of keywords are found, it's likely C++ code
        return keyword_count > 5

    @staticmethod
    def __is_php_code(code):
        php_keywords = ["<?php", "<?", "echo", "if", "else", "elseif", "while", "for", "foreach", "function", "class",
                        "require", "include", "$", "->", "::"]
        # Check for the presence of common PHP keywords
        keyword_count = sum(1 for keyword in php_keywords if keyword in code)
        # If a sufficient number of keywords are found, it's likely PHP code
        return keyword_count > 3

    @staticmethod
    def __is_ruby_code(code):
        # Check for common Ruby keywords
        ruby_keywords = ["def", "end", "class", "module", "require", "if", "else", "elsif", "unless", "case", "when",
                         "while", "until", "for", "do", "yield", "return"]
        # Count the number of Ruby keywords in the code snippet
        keyword_count = sum(1 for keyword in ruby_keywords if keyword in code)
        # If a sufficient number of keywords are found, it's likely Ruby code
        return keyword_count > 5

    @staticmethod
    def __is_swift_code(code):
        # Check for common Swift keywords
        swift_keywords = ["import", "func", "class", "struct", "enum", "extension", "var", "let", "if", "else",
                          "switch", "case", "for", "while", "return"]
        # Count the number of Swift keywords in the code snippet
        keyword_count = sum(1 for keyword in swift_keywords if keyword in code)
        # If a sufficient number of keywords are found, it's likely Swift code
        return keyword_count > 5

    @staticmethod
    def __is_go_code(code):
        # Check for common Go keywords
        go_keywords = ["package", "import", "func", "struct", "interface", "var", "const", "if", "else", "switch",
                       "case", "for", "range", "return"]
        # Count the number of Go keywords in the code snippet
        keyword_count = sum(1 for keyword in go_keywords if keyword in code)
        # If a sufficient number of keywords are found, it's likely Go code
        return keyword_count > 5

    @staticmethod
    def __is_typescript_code(code):
        # Check for common TypeScript keywords
        typescript_keywords = ["interface", "class", "enum", "function", "const", "let", "var", "import", "export",
                               "if", "else", "switch", "case", "for", "while", "return"]
        # Count the number of TypeScript keywords in the code snippet
        keyword_count = sum(1 for keyword in typescript_keywords if keyword in code)
        # If a sufficient number of keywords are found, it's likely TypeScript code
        return keyword_count > 5

    @staticmethod
    def __is_html_code(code):
        # Check for common HTML tags
        html_tags = ["<!DOCTYPE", "<html", "<head", "<title", "<body", "<div", "<p", "<a", "<img", "<ul", "<ol", "<li",
                     "<table", "<tr", "<td", "<form", "<input", "<button"]
        # Count the number of HTML tags in the code snippet
        tag_count = sum(1 for tag in html_tags if tag in code)
        # If a sufficient number of tags are found, it's likely HTML code
        return tag_count > 2

    @staticmethod
    def __is_c_code(code):
        # Check for common C keywords
        c_keywords = ["int", "double", "float", "char", "void", "struct", "enum", "typedef", "sizeof", "if", "else",
                      "switch", "case", "for", "while", "do", "break", "continue", "return"]
        # Count the number of C keywords in the code snippet
        keyword_count = sum(1 for keyword in c_keywords if keyword in code)
        # If a sufficient number of keywords are found, it's likely C code
        return keyword_count > 5

    @staticmethod
    def detect_language(code: str, language: str):
        match language:
            case "python":
                result = CodeLanguageDetector.__is_python_code(code)
                return result
            case "javascript":
                result = CodeLanguageDetector.__is_javascript_code(code)
                return result
            case "java":
                result = CodeLanguageDetector.__is_java_code(code)
                return result
            case "html":
                result = CodeLanguageDetector.__is_html_code(code)
                return result
            case "c":
                result = CodeLanguageDetector.__is_c_code(code)
                return result
            case "csharp":
                result = CodeLanguageDetector.__is_csharp_code(code)
                return result
            case "cpp":
                result = CodeLanguageDetector.__is_cpp_code(code)
                return result
            case "php":
                result = CodeLanguageDetector.__is_php_code(code)
                return result
            case "ruby":
                result = CodeLanguageDetector.__is_ruby_code(code)
                return result
            case "swift":
                result = CodeLanguageDetector.__is_swift_code(code)
                return result
            case "go":
                result = CodeLanguageDetector.__is_go_code(code)
                return result
            case "typescript":
                result = CodeLanguageDetector.__is_typescript_code(code)
                return result

