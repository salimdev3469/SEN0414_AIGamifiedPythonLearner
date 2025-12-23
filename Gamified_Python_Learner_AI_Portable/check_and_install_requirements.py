"""
Check and install only missing packages from requirements.txt
"""
import subprocess
import sys

# Try to use importlib.metadata (Python 3.8+), fallback to pkg_resources
try:
    from importlib.metadata import distributions
    USE_IMPORTLIB = True
except ImportError:
    try:
        import pkg_resources
        USE_IMPORTLIB = False
    except ImportError:
        # If neither works, install setuptools first
        print("Installing setuptools...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'setuptools'])
        import pkg_resources
        USE_IMPORTLIB = False

def get_installed_packages():
    """Get list of installed package names (lowercase)"""
    if USE_IMPORTLIB:
        # Python 3.8+ standard library approach
        try:
            # Try using name property (Python 3.10+)
            return {dist.name.lower(): dist for dist in distributions()}
        except AttributeError:
            # Fallback to metadata dict (Python 3.8-3.9)
            return {dist.metadata.get('Name', dist.metadata.get('name', '')).lower(): dist 
                   for dist in distributions() if dist.metadata.get('Name') or dist.metadata.get('name')}
    else:
        # Fallback to pkg_resources
        return {pkg.key.lower(): pkg for pkg in pkg_resources.working_set}

def parse_requirement(requirement_line):
    """Parse requirement line and return package name"""
    requirement_line = requirement_line.strip()
    if not requirement_line or requirement_line.startswith('#'):
        return None
    
    # Remove version specifiers
    for separator in ['==', '>=', '<=', '>', '<', '~=', '!=']:
        if separator in requirement_line:
            requirement_line = requirement_line.split(separator)[0]
    
    return requirement_line.strip().lower()

def check_and_install_missing():
    """Check requirements.txt and install only missing packages"""
    try:
        with open('requirements.txt', 'r', encoding='utf-8') as f:
            requirements = f.readlines()
    except FileNotFoundError:
        print("requirements.txt not found")
        return False
    
    try:
        installed_packages = get_installed_packages()
    except Exception as e:
        print(f"Warning: Could not get installed packages list: {e}")
        print("Installing setuptools and retrying...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'setuptools'], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            # Retry getting installed packages
            global USE_IMPORTLIB
            try:
                from importlib.metadata import distributions
                USE_IMPORTLIB = True
                installed_packages = {dist.name.lower(): dist for dist in distributions()}
            except (ImportError, AttributeError):
                import pkg_resources
                USE_IMPORTLIB = False
                installed_packages = {pkg.key.lower(): pkg for pkg in pkg_resources.working_set}
        except Exception as e2:
            print(f"Error: Could not get package list. Installing all requirements...")
            # Fallback: install all requirements
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
                return True
            except subprocess.CalledProcessError:
                return False
    
    missing_packages = []
    
    for req_line in requirements:
        pkg_name = parse_requirement(req_line)
        if pkg_name and pkg_name not in installed_packages:
            # Get original requirement line for installation
            original_req = req_line.strip()
            if not original_req.startswith('#'):
                missing_packages.append(original_req)
    
    if missing_packages:
        print(f"Found {len(missing_packages)} missing package(s):")
        for pkg in missing_packages:
            print(f"  - {pkg}")
        
        print("\nInstalling missing packages...")
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install'
            ] + missing_packages)
            print("All missing packages installed successfully.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error installing packages: {e}")
            return False
    else:
        print("All required packages are already installed.")
        return True

if __name__ == '__main__':
    success = check_and_install_missing()
    sys.exit(0 if success else 1)

