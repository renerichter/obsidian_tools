import argparse
import os
import re
import shutil


def sanitize_section_name(section_name):
    # Convert to lowercase
    if "case" in section_name: 
        pass
    section_name = section_name.lower()
    # Replace spaces and slashes with hyphens
    section_name = section_name.replace(' ', '-').replace('/', '-')
    # Remove any remaining non-alphanumeric characters except hyphens
    section_name = re.sub(r'[^\w\-]', '', section_name)
    # Replace multiple consecutive hyphens with a single hyphen
    #section_name = re.sub(r'-+', '-', section_name)
    return section_name

def replace_links(content):
    # Replace Obsidian-style links to sections
    section_link_pattern = re.compile(r'\[\[([^\[\]#]+)#([^\[\]]+)\]\]')
    content = section_link_pattern.sub(lambda m: f"[{sanitize_section_name(m.group(2))}]({sanitize_filename(m.group(1))}.md#{sanitize_section_name(m.group(2))})", content)
    
    # Replace Obsidian-style links to files
    file_link_pattern = re.compile(r'\[\[([^\[\]]+)\]\]')
    content = file_link_pattern.sub(lambda m: f"[{m.group(1)}]({sanitize_filename(m.group(1))}.md)", content)
    
    return content

def sanitize_filename(filename):
    # Remove non-ASCII characters
    filename = filename.encode('ascii', 'ignore').decode('ascii')
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    # Remove any remaining non-alphanumeric characters except underscores and periods
    filename = re.sub(r'[^\w\.-]', '', filename)
    return filename

def replace_media_links(content, steps_to_root, src_media_dir, goal_media_dir):
    def media_replacement(match):
        media_file = match.group(1)
        sanitized_media_file = sanitize_filename(media_file)
        src_media_path = os.path.join(src_media_dir, media_file)
        goal_media_path = os.path.join(goal_media_dir, sanitized_media_file)
        
        if not os.path.exists(goal_media_dir):
            os.makedirs(goal_media_dir)
        
        if os.path.exists(src_media_path):
            shutil.copy2(src_media_path, goal_media_path)
        
        return f'![{sanitized_media_file}]({steps_to_root}media/{sanitized_media_file})'
    
    media_link_pattern = re.compile(r'!\[\[([^\[\]]+)\]\]')
    content = media_link_pattern.sub(media_replacement, content)
    
    return content

def process_files(src_dir, src_media_dir, goal_dir):
    goal_media_dir = os.path.join(goal_dir,'media')
    for root, _, files in os.walk(src_dir):
        if ['media','interna'] in root:
            continue
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                steps_to_root = os.path.relpath(src_dir,file_path)[:-2]
                content = replace_media_links(content, steps_to_root,src_media_dir, goal_media_dir)
                content = replace_links(content)
                
                goal_path = os.path.join(goal_dir, os.path.relpath(file_path, src_dir))
                goal_folder = os.path.dirname(goal_path)
                if not os.path.exists(goal_folder):
                    os.makedirs(goal_folder)
                
                with open(goal_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"---> Processed {file_path} -> {goal_path}")

def main():
    parser = argparse.ArgumentParser(description='Process Obsidian markdown files and media.')
    parser.add_argument('-s', '--src', required=True, help='Source directory containing markdown files.')
    parser.add_argument('-sm', '--src_media', required=True, help='Source directory containing media files.')
    parser.add_argument('-g', '--goal', required=True, help='Goal directory to save processed files.')

    args = parser.parse_args()

    process_files(args.src, args.src_media, args.goal)

    """eg call: 
    python extract_local.py -s "/Users/tanoshimi/Library/CloudStorage/GoogleDrive-dr.rene.lachmann@gmail.com/My Drive/MyCloud/Notes/Inside_Tanoshimi_Vault/Inside Tanoshimi/Notes/Projects/openUC2" -sm "/Users/tanoshimi/Library/CloudStorage/GoogleDrive-dr.rene.lachmann@gmail.com/My Drive/MyCloud/Notes/Inside_Tanoshimi_Vault/Inside Tanoshimi/Media" -g "/Users/tanoshimi/Downloads/clickup_backup/test" """

if __name__ == '__main__':
    main()
