import subprocess
import os
import click
import sys
sys.path.append('..')
from episode_parser import extract_meta_data


@click.command()
@click.option('--template_path', prompt='Path to the After Effects project')
@click.option('--episode', prompt='Episode number')
def run_after_effects_script(template_path, episode):
    name, occupation, company, subtitle = extract_meta_data(episode)
    dir_path = os.path.dirname(os.path.realpath(__file__))
    script_name = "automate.jsx"
    script_path = os.path.join(dir_path, script_name)
    assets_path = os.path.join(dir_path, "assets")
    function_call="render('{}', '{}', '{}', '{}', '{}', '{}')".format(name, company, occupation, episode,assets_path + "/", template_path + "/")
    cmd = 'arch -x86_64 osascript ASfile.scpt "{}" "{}"'.format(script_path, function_call)
    print(cmd)
    ae = subprocess.call(cmd,shell=True)


if __name__ == '__main__':
    run_after_effects_script()
