import os
import random
import string

from base_kicker import BaseKicker

KICK_MARKER = "_kicked_"
FUNCTION_LENGTH = 100


class FunctionKicker(BaseKicker):
    __function_templates = {
        "py": "def _{marker}_{name}():\n    pass",
        "java": "public static void _{marker}_{name}() {{}}",
        "kt": "fun _{marker}_{name}() {{}}",
    }

    def _validate_file_type(self, file):
        ext = os.path.splitext(file)[1].lstrip(".")
        if not ext:
            raise ValueError("File must have an extension")
        if ext.lower() not in self.__function_templates:
            raise ValueError(f"No function template defined for file extension: {ext}")

    def _generate_content(self, file):
        self._validate_file_type(file)
        ext = os.path.splitext(file)[1].lstrip(".").lower()
        template = self.__function_templates[ext]
        func_name = "".join(random.choices(string.ascii_letters, k=FUNCTION_LENGTH))
        return template.format(marker=KICK_MARKER, name=func_name)
