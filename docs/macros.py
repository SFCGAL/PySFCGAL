
def define_env(env):
    """Define variables, macros, and filters.

    Args:
        env: The environment object used for defining macros and variables.

    Returns:
        None
    """
    @env.macro
    def include_python_file(filename: str) -> str:
        """Include and display the contents of a Python file.

        Args:
            filename (str): The path to the Python file to include.

        Returns:
            str: The content of the file formatted as a code block,
                 or an error message if the file is not found.

        Raises:
            FileNotFoundError: If the specified file cannot be found.
        """
        try:
            with open(filename, "r", encoding="utf-8") as file:
                content = file.read()
                formatted_content = f"```python\n{content}\n```"
                return formatted_content
        except FileNotFoundError:
            return f"File not found: {filename}"
