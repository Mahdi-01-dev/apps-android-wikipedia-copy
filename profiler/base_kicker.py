import os
from abc import abstractmethod

from kicker_interface import KickerInterface


class BaseKicker(KickerInterface):
    """
    Abstract base class for kicker implementations that append content to files.

    This class provides common functionality for file handling, dirty file tracking,
    and error handling.
    """

    def __init__(self):
        self.dirty_files = set()

    @abstractmethod
    def _generate_content(self, file):
        pass

    @abstractmethod
    def _validate_file_type(self, file):
        pass

    def _append_content(self, file, content):
        if file in self.dirty_files:
            self._remove_appended_content(file)
        try:
            if not os.path.exists(file):
                raise FileNotFoundError
            with open(file, "a") as f:
                f.write(f"\n{content}\n")
            self.dirty_files.add(file)
        except FileNotFoundError:
            print(f"Error: The file '{file}' does not exist.")
            raise
        except IOError as e:
            print(f"Error: An I/O error occurred while writing to '{file}': {e}")
            raise
        except Exception as e:
            print(f"Error: An unexpected error occurred: {e}")
            raise

    def _remove_appended_content(self, file):
        try:
            # Calculate the actual byte length based on the generated content
            sample_content = self._generate_content(file)
            content_bytes_len = len(
                "\n".encode("utf-8")
            ) * 2 + len(  # for the two newlines, before and after
                sample_content.encode("utf-8")
            )
            with open(file, "rb+") as f:
                f.seek(0, os.SEEK_END)
                file_size = f.tell()
                if file_size < content_bytes_len:
                    print(
                        f"Warning: File '{file}' is smaller than expected content length."
                    )
                    return
                f.truncate(file_size - content_bytes_len)
        except FileNotFoundError:
            print(f"Error: The file '{file}' does not exist.")
        except IOError as e:
            print(f"Error: An I/O error occurred while reverting '{file}': {e}")
        except Exception as e:
            print(f"Error: An unexpected error occurred: {e}")

    def append(self, file):
        self._validate_file_type(file)
        content = self._generate_content(file)
        self._append_content(file, content)

    def cleanup(self, file):
        self._remove_appended_content(file)

    def cleanup_all_dirty(self):
        super().cleanup_all(self.dirty_files)
        self.dirty_files.clear()
