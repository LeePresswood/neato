import sys
import importlib
import os

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <run_name>")
        print("Available runs:")
        # List available runs dynamically
        runs_dir = os.path.join(os.path.dirname(__file__), 'runs')
        if os.path.exists(runs_dir):
            for f in os.listdir(runs_dir):
                if f.startswith('run') and f.endswith('.py'):
                    print(f"  - {f[:-3]}")
        return

    run_name = sys.argv[1]
    
    # Add current directory to path so imports work
    sys.path.append(os.path.dirname(__file__))
    
    try:
        # Import the requested run module
        module_name = f"runs.{run_name}"
        run_module = importlib.import_module(module_name)
        
        # Execute the run function
        if hasattr(run_module, 'run'):
            # Pass the config path relative to the run script
            config_path = os.path.join('runs', 'configs', f"config-{run_name.split('_')[0]}")
            print(f"Starting {run_name} with config {config_path}...")
            run_module.run(config_path)
        else:
            print(f"Error: Module {module_name} does not have a 'run' function.")
            
    except ImportError as e:
        print(f"Error: Could not import run '{run_name}'. Make sure 'runs/{run_name}.py' exists.")
        print(e)
    except Exception as e:
        print(f"An error occurred while executing {run_name}:")
        print(e)

if __name__ == "__main__":
    main()
