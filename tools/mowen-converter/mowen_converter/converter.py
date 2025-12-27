import re
import os
import argparse

def process_list_block(list_buffer):
    """
    Process a block of list items.
    list_buffer: list of tuples (line, indent_len, is_ordered, content, marker)
    """
    if not list_buffer:
        return []

    # 1. Determine base indentation (min_indent)
    min_indent = min(item[1] for item in list_buffer)
    
    # 2. Check if it's a nested list (any item has indent > min_indent)
    is_nested = any(item[1] > min_indent for item in list_buffer)
    
    processed_lines = []
    
    for item in list_buffer:
        line, indent_len, is_ordered, content, marker = item
        
        # Calculate relative indent
        relative_indent = indent_len - min_indent
        
        # Determine output marker and indentation
        new_line = ""
        
        if is_ordered:
            # For ordered lists, we generally keep the structure but fix spacing
            # If nested, we apply indentation rules similar to unordered
            # But we keep the number marker.
            # User said: "For ordered lists with nested indentation, follow the same spacing rules as unordered lists"
            # We'll just preserve the marker but normalize indentation.
            
            output_indent = ""
            if relative_indent > 0:
                 # Calculate level based on 2-space or 4-space steps
                 # Let's assume 2 spaces is a step
                 level = relative_indent // 2
                 output_indent = "    " * level
            
            new_line = f"{output_indent}{marker} {content}"
            
        else:
            # Unordered List Logic
            if not is_nested:
                # Flat list: use "• "
                new_line = f"• {content}"
            else:
                # Nested list
                if relative_indent == 0:
                    # Level 1: "● "
                    new_line = f"● {content}"
                else:
                    # Level > 1: "• " with indentation
                    # Calculate level
                    # Level 2 starts at relative_indent > 0.
                    # User: "且没往下一级，要缩进4个空格" -> Level 2 needs 4 spaces.
                    
                    # Assume 2 spaces in source = 1 level deeper
                    # (indent_len - min_indent) >= 2 -> Level 2
                    
                    # We map source indentation to output indentation (multiples of 4 spaces)
                    # To be robust, we can treat any >0 indent as at least Level 2.
                    # If we want to support Level 3, we need to distinguish.
                    
                    # Simple heuristic:
                    # If source indent is small (e.g. 2 or 4), it's Level 2 -> 4 spaces
                    # If source indent is large (e.g. 6 or 8), it's Level 3 -> 8 spaces
                    
                    level_idx = max(1, relative_indent // 2) 
                    output_indent = "    " * level_idx
                    new_line = f"{output_indent}• {content}"
        
        processed_lines.append(new_line)
        processed_lines.append("") # Add blank line after item

    return processed_lines

def convert_to_mowen(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    output = []
    in_code_block = False
    
    # Buffer for list processing
    # Stores tuples: (original_line, indent_len, is_ordered, content, marker)
    list_buffer = [] 
    
    i = 0
    while i < len(lines):
        line = lines[i].rstrip('\n') 
        
        # Code Block Logic
        if line.strip().startswith('```'):
            # If we were in a list, flush it
            if list_buffer:
                output.extend(process_list_block(list_buffer))
                list_buffer = []

            in_code_block = not in_code_block
            output.append(line)
            if not in_code_block:
                # End of code block, treat as block element -> 2 blank lines
                output.append("")
                output.append("")
            i += 1
            continue
            
        if in_code_block:
            output.append(line)
            i += 1
            continue

        # Check for list items
        match_ul = re.match(r'^(\s*)([-*])\s+(.*)', line)
        match_ol = re.match(r'^(\s*)(\d+\.)\s+(.*)', line)
        
        is_list_item = match_ul or match_ol
        
        if is_list_item:
            indent_str = (match_ul or match_ol).group(1)
            indent_len = len(indent_str.replace('\t', '    '))
            content = (match_ul or match_ol).group(3)
            
            if match_ul:
                marker = (match_ul).group(2)
                is_ordered = False
            else:
                marker = (match_ol).group(2)
                is_ordered = True
                
            list_buffer.append((line, indent_len, is_ordered, content, marker))
            i += 1
            continue
            
        # If line is blank, check if we are buffering a list
        if not line.strip():
            # If we are in a list, a blank line *might* be part of the list (loose list), 
            # or it might separate lists.
            # But since we are reformatting completely and adding blank lines anyway,
            # we can just ignore blank lines inside a list buffer?
            # Or we can treat it as a break?
            # Markdown usually treats blank lines as separators unless indented.
            # Let's assume for this format converter, we consume blank lines if we are in a list,
            # but we don't add them to the buffer (because we generate our own spacing).
            # BUT, if we hit a blank line and then a non-list line, the list ends.
            # If we hit a blank line and then a list item, it's the same list.
            
            # So, we just skip blank lines, but we need to know if the *next* non-blank line is a list item.
            # If it is, we continue buffering.
            # If it's not, we flush.
            
            # To simplify: Just skip blank lines here. 
            # The decision to flush happens when we hit a non-list, non-blank line.
            i += 1
            continue
            
        # If we reach here, it's a non-list, non-blank, non-code-block line.
        # Flush list buffer if exists
        if list_buffer:
            output.extend(process_list_block(list_buffer))
            list_buffer = []
            
        # Headings
        match_h = re.match(r'^(#+)\s+(.*)', line)
        if match_h:
            hashes = match_h.group(1)
            text = match_h.group(2)
            level = len(hashes)
            
            # Bold text if not already bold
            if not (text.startswith('**') and text.endswith('**')):
                text = f"**{text}**"
            
            prefix = ""
            if level == 1 or level == 2:
                prefix = "▎ "
            elif level == 3:
                prefix = "▏ "
            else:
                prefix = "" # Remove hash
            
            output.append(f"{prefix}{text}")
            output.append("")
            output.append("")
            i += 1
            continue
            
        # Paragraph / Text
        output.append(line)
        output.append("")
        output.append("")
        i += 1

    # Flush any remaining list buffer at EOF
    if list_buffer:
        output.extend(process_list_block(list_buffer))

    return output

def main():
    parser = argparse.ArgumentParser(description="Convert Markdown to Mo Wen style.")
    parser.add_argument("file_path", help="Path to the input Markdown file")
    args = parser.parse_args()

    file_path = args.file_path

    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        exit(1)

    new_lines = convert_to_mowen(file_path)
    
    # Create new file path
    dir_name = os.path.dirname(file_path)
    base_name = os.path.basename(file_path)
    name_without_ext = os.path.splitext(base_name)[0]
    new_file_path = os.path.join(dir_name, f"{name_without_ext}_mowen.md")
    
    print(f"Converting {file_path} -> {new_file_path}")
    
    # Save to new file
    with open(new_file_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(new_lines))
    
    print("Done.")

if __name__ == "__main__":
    main()
