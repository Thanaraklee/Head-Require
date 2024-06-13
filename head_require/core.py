import os
import subprocess
import re
import glob
import argparse
from typing import List, Dict, Any


VERSION = '2.0.3'
os.environ['LC_ALL'] = 'en_US.utf8'

class HeadRequire:
    def __init__(self, directory_env: str, directory_project: str = '.') -> None:
        """
        Initialize the HeadRequire object.

        This class helps in identifying and listing all the imported packages 
        in a given directory and generating a requirements.txt file with the 
        corresponding package versions installed in the current environment.

        Parameters
        ----------
        directory_env : str
            The path to the directory environment containing the 'Lib/' directory, 
            such as '.venv/' or '.env/'.
        directory_project : str, optional
            The path to the directory of your project or the root path of the project. Default is '.' (current directory)
        
        Examples
        --------
        >> source .venv/Scripts/activate
        >> head-require

        Returns
        -------
        Automated create requirements.txt file in the current directory.
        """

        self.directory_env = directory_env
        self.directory_project = directory_project

    def list_files(self, directory_project: str) -> List[str]:
        """
        List all Python and Jupyter notebook files in the given project directory.

        Parameters
        ----------
        directory_project : str
            The path to the directory of your project.

        Returns
        -------
        List[str]
            A list of file paths to Python and Jupyter notebook files in the project.
        """
        try:
            file_list = []
            for root, dirs, files in os.walk(directory_project):
                dirs[:] = [d for d in dirs if not d.startswith('.') and not d.startswith('_') and d not in self.directory_env and d not in ['env', 'venv']]
                files[:] = [f for f in files if not f.startswith('.') and not f.startswith('_') and (f.endswith('.py') or f.endswith('.ipynb'))]
                for file in files:
                    file_list.append(os.path.join(root, file))
            print(f"    - Number of files found: {len(file_list)} 🕵️")
            return file_list
        except Exception as e:
            print(f"    An error occurred in listing files: {e} ⚠️")

    def extract_imports(self, directory_path: str) -> List[List[str]]:
        """
        Extract all import statements from Python and Jupyter notebook files in the given directory.

        Parameters
        ----------
        directory_path : str
            The path to the directory to search for import statements.

        Returns
        -------
        List[List[str]]
            A list of lists where each sublist contains the components of an import statement.
        """
        try:
            files = self.list_files(directory_path)
            list_module = []
            for file in files:
                try:
                    result = subprocess.check_output(['grep', '-Po', r'(^(?! *#)\s*("(from .+ import .+)"|("import .+")))|(^import .+|^from .*import .*)', file]).decode()
                    list_module.append(result)
                except subprocess.CalledProcessError:
                    pass
            formatted_data = []
            for string in list_module:
                imports_lines = string.replace('"', '').strip().split('\n')
                imports = [line.split() for line in imports_lines]
                imports = [[word.replace('\\n', '') for word in imp] for imp in imports]
                for imp in imports:
                    formatted_data.append(imp)
            return formatted_data
        except Exception as e:
            print(f"    An error occurred in extracting imports: {e} ⚠️")

    def get_installed_packages(self) -> Dict[str, str]:
        """
        Get a list of installed packages in the current Python environment.

        Returns
        -------
        Dict[str, str]
            A dictionary of installed packages and their versions.
        """
        try:
            pip_list_output = subprocess.run(["pip", "list"], capture_output=True, text=True).stdout
            installed_packages = {}
            for line in pip_list_output.split('\n')[2:]:
                if line.strip():
                    package, version = re.match(r'^(\S+)\s+(\S+)', line).groups()
                    installed_packages[package] = version
            return installed_packages
        except Exception as e:
            print(f"    An error occurred in getting installed packages: {e} ⚠️")

    def write_requirements_txt(self, matched_packages: Dict[str, str]) -> None:
        """
        Write matched packages to a requirements.txt file.

        Parameters
        ----------
        matched_packages : Dict[str, str]
            A dictionary of matched packages and their versions.
        """
        try:
            with open(f'{self.directory_project}/requirements.txt', 'w') as file:
                sorted_packages = sorted(matched_packages.items(), key=lambda x: x[0])
                for package, version in sorted_packages:
                    file.write(f"{package}=={version}\n")
            print(f'    - Creating requirements.txt... ✍️')
        except Exception as e:
            print(f"    An error occurred in writing requirements.txt: {e} ⚠️")

    def find_top_level_text(self, directory_env: str) -> Dict[str, List[str]]:
        """
        Find top-level module names from top_level.txt files in the environment.

        Parameters
        ----------
        directory_env : str
            The path to the directory environment containing the 'Lib/' directory.

        Returns
        -------
        Dict[str, List[str]]
            A dictionary of package names and their top-level module names.
        """
        try:
            # template for lib don't have top_level.txt file
            template = {
                'scikit-learn':['sklearn'],
            }

            top_level_text = {}
            site_packages_dir = os.path.join(directory_env, 'Lib', 'site-packages')
            dist_info_dirs = glob.glob(os.path.join(site_packages_dir, '*.dist-info'))
            for dist_info_dir in dist_info_dirs:
                top_level_txt_path = os.path.join(dist_info_dir, 'top_level.txt')
                if os.path.exists(top_level_txt_path):
                    with open(top_level_txt_path, 'r') as file:
                        top_level_text[os.path.basename(dist_info_dir).split('-')[0].replace('_', '-')] = file.read().splitlines()
            return {**template,**top_level_text}
        except Exception as e:
            print(f"    An error occurred in finding top level text: {e} ⚠️")

    def check_matching_packages(self, directory_env: str, import_statements: List[str]) -> List[str]:
        """
        Check which packages match the import statements.

        Parameters
        ----------
        directory_env : str
            The path to the directory environment containing the 'Lib/' directory.
        import_statements : List[str]
            A list of import statements.

        Returns
        -------
        List[str]
            A list of matching package names.
        """
        try:
            top_level_text_dict = self.find_top_level_text(directory_env)
            matching_packages = []
            for directory_name, top_level_text in top_level_text_dict.items():
                for import_statement in import_statements:
                    if import_statement == top_level_text[0]:
                        matching_packages.append(directory_name)
                        break
            return matching_packages
        except Exception as e:
            print(f"    An error occurred in checking matching packages: {e} ⚠️")

    def matching_packages_with_versions(self, directory_env: str, directory_project: str) -> Dict[str, str]:
        """
        Match packages with their versions based on the import statements and environment.

        Parameters
        ----------
        directory_env : str
            The path to the directory environment containing the 'Lib/' directory.
        directory_project : str
            The path to the directory of your project.

        Returns
        -------
        Dict[str, str]
            A dictionary of matched packages and their versions.
        """
        try:
            import_statements = self.extract_imports(directory_project)
            import_statements = [sublist[1].split('.')[0].replace('_', '-') for sublist in import_statements]
            matching_packages = self.check_matching_packages(directory_env, import_statements)
            installed_packages = self.get_installed_packages()
            matched_packages_file = {}
            all_packages = list(set(matching_packages+import_statements))
            for module in all_packages:
                if module in installed_packages:
                    matched_packages_file[module] = installed_packages[module]
            return matched_packages_file
        except Exception as e:
            print(f"    An error occurred in matching packages with versions: {e} ⚠️")

    def head_require_function(self) -> None:
        """
        Main function to manage the requirement checking and writing process.
        """
        try:
            print(' Processing... 🎈')
            matched_packages = self.matching_packages_with_versions(self.directory_env, self.directory_project)
            self.write_requirements_txt(matched_packages)
        except Exception as e:
            print(f"    An error occurred in head_require_function: {e} ⚠️")
        else:
            print(' Successfully 🎉')


def get_default_directory_env() -> str:
    """
    Get the default directory environment for the Python interpreter.

    Returns
    -------
    str
        The path to the default directory environment.
    """
    try:
        pip_path = subprocess.check_output(['which', 'pip']).decode().strip()
        env_dir = os.path.dirname(os.path.dirname(pip_path))
        env = os.path.basename(env_dir)
        return env
    except Exception as e:
        print(f"    An error occurred in getting default directory environment: {e} ⚠️")

def main() -> None:
    """
    Main function to parse arguments and generate requirements.txt.
    """
    parser = argparse.ArgumentParser(description='Generate requirements.txt based on imported packages in Python files.')
    parser.add_argument('--version', action='store_true', help='Show the version of the head-require tool.')
    parser.add_argument('--directory_project', '-dp',metavar='', type=str, default='.', help='Path to the directory of your project or the root path of the project. Default is the current directory. For example, C:\\Users\\username\\path_to_project.')
    args = parser.parse_args()

    if args.version:
        print(f"{VERSION}")
        return
    
    directory_env = get_default_directory_env()
    directory_project = rf'{args.directory_project}'
    pkg_manager = HeadRequire(directory_env, directory_project)
    pkg_manager.head_require_function()

if __name__ == "__main__":
    main()
