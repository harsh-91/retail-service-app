import os

def generate_markdown_tree(root_path, output_file):
    with open(output_file, "w", encoding="utf-8") as f:
        for dirpath, dirnames, filenames in os.walk(root_path):
            depth = dirpath[len(root_path):].count(os.sep)
            indent = "  " * depth
            f.write(f"{indent}- 📁 {os.path.basename(dirpath) or dirpath}\n")
            for filename in filenames:
                file_indent = "  " * (depth + 1)
                f.write(f"{file_indent}- 📄 {filename}\n")

folder_path = r"C:\retail_management_app"
output_md_file = "folder_structure.md"
generate_markdown_tree(folder_path, output_md_file)
