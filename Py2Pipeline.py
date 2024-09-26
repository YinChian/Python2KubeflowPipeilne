import json
import os
from jinja2 import Environment, FileSystemLoader

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

def main():
    try:
        file_path = os.path.join(script_dir, 'pipeline_settings.json')
        with open(file_path, 'r') as f:
            data = json.load(f)
    except FileNotFoundError as e:
        print("Error: File not found!")
    except json.JSONDecodeError as e:
        print(f"Error: Failed to decode JSON. {e}")
    except PermissionError as e:
        print(f"Error: Permission denied when trying to read the file. {e}")
    except IOError as e:
        print(f"Error: An I/O error occurred. {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    fill_evaluation_python_template(data)
    fill_evaluation_dockerfile_template(data)



def fill_evaluation_python_template(values):
    env = Environment(
        loader=FileSystemLoader(os.path.join(script_dir, 'Template'))
    )
    template= env.get_template('CodeTemplate.py.jinja')

    with open('Evaluation.py') as f:
        user_code = f.read()

    code_sections = user_code.split('### USER IMPORT START ###')
    if len(code_sections) == 2:
        user_inputs = code_sections[1].split('### USER CODE START ###')
        if len(user_inputs) == 2:
            ret = template.render(pipeline_settings=values, user_import=user_inputs[0], user_code=user_inputs[1])
        else:
            raise Exception('User code start mark count != 1')
    else:
        raise Exception('User import start mark count != 1')

    with open('./Output/pipeline.py', 'w+') as f:
        f.write(ret)


def fill_evaluation_dockerfile_template(values):
    env = Environment(
        loader=FileSystemLoader(os.path.join(script_dir, 'Template'))
    )
    template= env.get_template('evaluation.jinja')
    with open('./Output/evaluation', 'w+') as f:
        ret = template.render(pipeline_settings=values)
        f.write(ret)


if __name__ == '__main__':
    main()