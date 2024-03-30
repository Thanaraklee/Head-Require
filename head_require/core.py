import os
import subprocess
import re
import glob
import argparse

class head_require:
    def __init__(self, directory, directory_project='.'):
        '''
        directory_env: The path to the directory environment containing the 'Lib/' directory, such as '.venv/' or '.env/'.
        directory_project: The path to the directory of your project or the root path of the project. Default is '.' (current directory)
        '''
        self.directory = directory
        self.directory_project = directory_project

    def list_files(self, directory_project):
        try:
            file_list = []
            for root, dirs, files in os.walk(directory_project):
                # Exclude directories starting with '.' or '_'
                dirs[:] = [d for d in dirs if not d.startswith('.') and not d.startswith('_') and d not in self.directory and d not in ['env','venv']]
                for file in files:
                    # Check if the file ends with '.ipynb' or '.py'
                    if (file.endswith('.ipynb') or file.endswith('.py')) and not file.startswith('_'):
                        file_list.append(os.path.join(root, file))
            return file_list
        except Exception as e:
            print(f"An error occurred in listing files: {e}")
            return []

    def extract_imports(self, directory_path):
        try:
            files = self.list_files(directory_path)

            list_module = []
            for file in files:
                try:
                    result = subprocess.check_output(['grep', '-Po', '(^(?! *#)\s*("(from .+ import .+)"|("import .+")))|(^import .+|^from .*import .*)', file]).decode()
                    list_module.append(result)
                except subprocess.CalledProcessError:
                    pass 

            formatted_data = []
            for string in list_module:
                imports_lines = string.replace('"','').strip().split('\n')
                imports = [line.split() for line in imports_lines]
                imports = [[word.replace('\\n', '') for word in imp] for imp in imports]
                for imp in imports:
                    formatted_data.append(imp)
            
            return formatted_data
        except Exception as e:
            print(f"An error occurred in extracting imports: {e}")
            return []

    def get_installed_packages(self):
        try:
            pip_list_output = subprocess.run(["pip", "list"], capture_output=True, text=True).stdout
            installed_packages = {}
            for line in pip_list_output.split('\n')[2:]:
                if line.strip():
                    package, version = re.match(r'^(\S+)\s+(\S+)', line).groups()
                    installed_packages[package] = version
            return installed_packages
        except Exception as e:
            print(f"An error occurred in getting installed packages: {e}")
            return {}

    def get_matched_packages(self, directory_path):
        try:
            import_statements = self.extract_imports(directory_path)
            module_list = [item[1].split('.')[0].replace('_', '-') for item in import_statements]
            installed_packages = self.get_installed_packages()
            matched_packages = {}
            for module in module_list:
                if module in installed_packages:
                    matched_packages[module] = installed_packages[module]

            return matched_packages
        except Exception as e:
            print(f"An error occurred in getting matched packages: {e}")
            return {}

    def write_requirements_txt(self, matched_packages):
        try:
            with open(f'{self.directory_project}/requirements.txt', 'w') as file:
                sorted_packages = sorted(matched_packages.items(), key=lambda x: x[0])
                for package, version in sorted_packages:
                    file.write(f"{package}=={version}\n")
        except Exception as e:
            print(f"An error occurred in writing requirements.txt: {e}")

    def deep_requir_check_pip(self, directory_path):
        try:
            # import_statements = self.extract_imports(directory_path)
            matched_packages = self.get_matched_packages(directory_path)
            return matched_packages
        except Exception as e:
            print(f"An error occurred in deep_requir_check_pip: {e}")
            return {}

    def find_top_level_text(self, directory_env):
        try:
            top_level_text = {}
            site_packages_dir = os.path.join(directory_env, 'Lib', 'site-packages')
            dist_info_dirs = glob.glob(os.path.join(site_packages_dir, '*.dist-info'))
            for dist_info_dir in dist_info_dirs:
                top_level_txt_path = os.path.join(dist_info_dir, 'top_level.txt')
                if os.path.exists(top_level_txt_path):
                    with open(top_level_txt_path, 'r') as file:
                        top_level_text[os.path.basename(dist_info_dir).split('-')[0].replace('_','-')] = file.read().splitlines()
            return top_level_text
        except Exception as e:
            print(f"An error occurred in finding top level text: {e}")
            return {}

    def check_matching_packages(self, directory_env, import_statements):
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
            print(f"An error occurred in checking matching packages: {e}")
            return []

    def matching_packages_with_versions(self, directory_env, directory_project):
        try:
            import_statements = self.extract_imports(directory_project)
            import_statements = [sublist[1].split('.')[0].replace('_','-') for sublist in import_statements]
            matching_packages = self.check_matching_packages(directory_env, import_statements)

            installed_packages = self.get_installed_packages()
            matched_packages_file = {}
            for module in matching_packages:
                if module in installed_packages:
                    matched_packages_file[module] = installed_packages[module]
            return matched_packages_file
        except Exception as e:
            print(f"An error occurred in matching packages with versions: {e}")
            return {}

    def head_require_function(self):
        try:
            matched_packages = self.matching_packages_with_versions(self.directory, self.directory_project)
            result = self.deep_requir_check_pip(self.directory_project)
            combined_packages = {**matched_packages, **result}
            self.write_requirements_txt(combined_packages)
        except Exception as e:
            print(f"An error occurred in head_require_function: {e}")

def get_default_directory_env():
    try:
        # Run 'which pip' command to get the path of the currently active Python environment
        pip_path = subprocess.check_output(['which', 'pip']).decode().strip()
        env_dir = os.path.dirname(os.path.dirname(pip_path))  
        env = os.path.basename(env_dir)
        return env  
    except Exception as e:
        print(f"An error occurred in getting default directory environment: {e}")
        return '.venv/'  # Default value if pip path cannot be determined
    
def main():
    parser = argparse.ArgumentParser(description='Generate requirements.txt based on imported packages in Python files.')
    # parser.add_argument('--directory_env', '-de', type=str, default=get_default_directory_env(), help='Important: If you have multiple environments in the current project, specify the directory for the desired environment. Possible environment names include: env, venv, ... (add more if necessary)')
    parser.add_argument('--directory_project', '-dp', type=str, default='.', help='Path to the directory of your project or the root path of the project. Default is the current directory. For example, C:\\Users\\username\\path_to_project.')
    args = parser.parse_args()
    directory = get_default_directory_env()
    directory_project = rf'{args.directory_project}'

    pkg_manager = head_require(directory, directory_project)
    pkg_manager.head_require_function()

if __name__ == "__main__":
    main()