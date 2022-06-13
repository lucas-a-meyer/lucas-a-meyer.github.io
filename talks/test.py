from pptx import Presentation
import os

for entry in os.scandir():
    print(f"Processing {entry.path}")
    if entry.path.endswith(".pptx"):
        prs = Presentation(entry.path)
        print(prs.core_properties.title)
        print(prs.core_properties.author)
        print(prs.core_properties.modified)

