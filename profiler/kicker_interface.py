from abc import ABC, abstractmethod


class KickerInterface(ABC):
    """
    Interface for kicker implementations that can append content to files
    and clean up modifications.
    """

    @abstractmethod
    def append(self, file):
        """
        Append content to a file.

        Args:
            file: Path to the file to modify
        """
        pass

    @abstractmethod
    def cleanup(self, file):
        """
        Clean up modifications made to a specific file, restoring it to its original state.

        Args:
            file: Path to the file to clean up
        """
        pass

    def cleanup_all(self, files):
        """
        Clean up modifications for all files in the provided iterable.

        Args:
            files: An iterable of file paths to clean up
        """
        for file in files:
            self.cleanup(file)
