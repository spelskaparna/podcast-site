import os
def fix_file(name):
    link_found = False
    with open(name) as f:
        new_file = ""
        for line in f:
            line = line.replace('\n','')
            
            if link_found:
                if len(line) > 0 and line[0] != "*" and line[0] != "#":
                    line = "* [{}] ()".format(line)
            result = line.replace(" ","").find("#Länkar")
            if result > -1:
                link_found = True
            new_file += line + '\n'

    with open(name, 'w') as f:
        f.write(new_file)


def fix_files():
    dir_path = os.path.join('content', 'episode')

    for file in os.listdir(dir_path):
        filename = os.fsdecode(file)
        if filename.endswith(".md"):
            path = os.path.join(dir_path, filename)
            fix_file(path)

fix_files()
