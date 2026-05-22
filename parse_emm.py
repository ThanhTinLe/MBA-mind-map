import xml.etree.ElementTree as ET
import json
import re
import os

def clean_tag(tag):
    if '}' in tag:
        return tag.split('}', 1)[1]
    return tag

def get_text_from_textbox(textbox_elem):
    # Find all paragraph (p) tags and concatenate their chars
    text_pieces = []
    # Find all 'p' elements inside textbox_elem
    for p in textbox_elem.iter():
        if clean_tag(p.tag) == 'p':
            p_text = ""
            for char_elem in p.iter():
                if clean_tag(char_elem.tag) == 'char' and char_elem.text:
                    p_text += char_elem.text
            if p_text:
                text_pieces.append(p_text)
    return " ".join(text_pieces).strip()

def get_link_from_topic(topic_elem):
    # Search for field elements and check m:command or command attributes
    for sub in topic_elem.iter():
        if clean_tag(sub.tag) == 'field':
            for attr_name, attr_val in sub.attrib.items():
                if attr_name.endswith('command') and attr_val:
                    # Search for <link>...</link> inside command
                    match = re.search(r'<link>(.*?)</link>', attr_val)
                    if match:
                        return match.group(1).strip()
    return None

def build_tree(topic_elem):
    # 1. Get name
    name = ""
    # Find textBox inside mainElement of this topic
    for child in topic_elem:
        if clean_tag(child.tag) == 'mainElement':
            for tb in child:
                if clean_tag(tb.tag) == 'textBox':
                    name = get_text_from_textbox(tb)
                    break
            break
            
    if not name:
        name = "Untitled Topic"
        
    # 2. Get link
    link = get_link_from_topic(topic_elem)
    
    # 3. Get children
    children = []
    # Find topicBranch child of this topic
    for child in topic_elem:
        if clean_tag(child.tag) == 'topicBranch':
            # Iterate through children topics
            for sub_topic in child:
                if clean_tag(sub_topic.tag) == 'topic':
                    children.append(build_tree(sub_topic))
            break
            
    # Build node dict
    node = {"name": name}
    if link:
        node["link"] = link
    if children:
        node["children"] = children
        
    return node

def parse_emm_file(xml_path):
    print(f"Parsing XML file: {xml_path}")
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    # Find the top-level topic (Central Topic)
    # The root tag is Map. It has a topicBranch which contains the central topic.
    central_topic_elem = None
    for child in root:
        if clean_tag(child.tag) == 'topicBranch':
            for sub in child:
                if clean_tag(sub.tag) == 'topic':
                    central_topic_elem = sub
                    break
            break
            
    if central_topic_elem is None:
        raise ValueError("Could not find the central topic in XML structure.")
        
    central_topic = build_tree(central_topic_elem)
    
    result = {
        "file": "SEMBAKhung_MBA_22_1",
        "centralTopic": [central_topic]
    }
    
    return result

def main():
    xml_path = "map1.xml"
    if not os.path.exists(xml_path):
        print(f"Error: {xml_path} does not exist. Please extract it first.")
        return
        
    try:
        new_data = parse_emm_file(xml_path)
        
        # Save parsed data to semba_mba_khung.json
        output_path = "semba_mba_khung.json"
        print(f"Saving parsed data to {output_path}...")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(new_data, f, ensure_ascii=False, indent=2)
            
        print("Success! JSON file updated with parsed EMM data.")
        
        # Compare with previous if exists (but here we just overwrite to ensure 100% completeness)
        # Let's count nodes
        def count_nodes(node):
            count = 1
            for child in node.get("children", []):
                count += count_nodes(child)
            return count
            
        total_nodes = count_nodes(new_data["centralTopic"][0])
        print(f"Total nodes parsed: {total_nodes}")
        
    except Exception as e:
        print(f"Error occurred during parsing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
