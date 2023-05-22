import os
import time
import markdown

def upgrade_quarto() -> None:
    print("Upgrading Quarto")

    # delete all files in this directory that have the .msi extension
    for fname in os.listdir('.'):
        if fname.endswith('.msi'):
            os.remove(fname)

    # download the latest version of Quarto
    os.system("gh --repo quarto-dev/quarto-cli release download --pattern *.msi")

    time.sleep(1)

    # get the full path of the file that was downloaded
    for fname in os.listdir('.'):
        if fname.endswith('.msi'):
            msi_file = os.path.abspath(fname)

    # install the latest version of Quarto
    os.system(f"msiexec /i {msi_file} /qn")

    # update the PATH, adding c:\Program Files\Quarto\bin if it doesn't already exist
    path = os.environ.get('PATH')
    if 'c:\\Program Files\\Quarto\\bin' not in path:
        os.environ['PATH'] = path + ';c:\\Program Files\\Quarto\\bin'

    # delete the .msi file
    os.remove(msi_file)

    # Show the quarto version
    os.system("quarto --version")

    # Print completion message
    print("Quarto upgrade completed")


def is_valid_markdown(str_post: str) -> bool:
    try:
        markdown.markdown(str_post)
        return True
    except:
        return False

