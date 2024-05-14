import requests
import os
from nltk.tokenize import sent_tokenize
import re

def natural_keys(text):
    '''
    A helper function to generate a list of integer and non-integer parts of a string.
    Useful for 'natural' sorting that considers numerical values.
    '''
    return [int(c) if c.isdigit() else c.lower() for c in re.split('(\d+)', text)]

def GenerateTopic(chunk1, chunk2, url):
    print("Generating topic for the next text chunk...")
    specific_question = (
        "Given the detailed explanation in chunk 1 and any relevant context available in chunk 2, \
        Generate an appropriate and informative topic name for chunk 1? \
        Rules: \
        -> Only generate the title name. \
        -> No Explanation \
        -> No Brackets \
        -> No Quotes \
        -> No Notes \
        -> No ORs \
        Just the title name for chunk 1!"
        "\n\nChunk 1:\n%s\n\nChunk 2:\n%s" % (chunk1, chunk2)
    )

    payload = {
        "model": "mistral:instruct", 
        "prompt": specific_question,
        "stream": False,
    }
    try:
        response = requests.post(url, json=payload, timeout=30)  

        if response.status_code == 200:
            parsed_json = response.json()
            if parsed_json['done']:
                print("Topic generation successful.")
                return parsed_json['response'].strip()
            else:
                print("Response not completed, using default topic name.")
                return "General Topic"
        else:
            print("Failed to get response from Ollama: %s, using default topic name." % response.text)
            return "General Topic"
    except requests.exceptions.RequestException as e:
        print("Request to Ollama API failed: %s" % e)
        return "General Topic"

def ProcessMD(playlist_path, output_file, num_sentences=10, overlap=1):
    print("Processing Markdown files in '%s'..." % playlist_path)
    for root, dirs, _ in os.walk(playlist_path):
        dirs.sort(key=natural_keys)
        for dir_name in dirs:
            compiled_content = ""
            dir_path = os.path.join(root, dir_name)
            files = sorted(os.listdir(dir_path), key=natural_keys)  # Sort files in natural order
            file_count = 0

            for file in files:
                if file.endswith('.md'):
                    compiled_content = ""
                    file_path = os.path.join(dir_path, file)
                    print("Reading file: %s" % file_path)
                    
                    with open(file_path, 'r', encoding='utf-8') as md_file:
                        md_data = md_file.read()
                        sentences = sent_tokenize(md_data)
                        print("File read successfully. Generating topics...")

                        i = 0
                        while i < len(sentences):
                            chunk1 = " ".join(sentences[i:i + num_sentences])
                            chunk2 = " ".join(sentences[i + num_sentences - overlap: i + 2 * num_sentences - overlap])
                            topic_name = GenerateTopic(chunk1, chunk2 if i + num_sentences < len(sentences) else "", "http://10.1.1.28:11434/api/generate")
                            print("## %s\n\n%s\n\n" % (topic_name, chunk1))
                            compiled_content += "## %s\n\n%s\n\n" % (topic_name, chunk1)
                            i += num_sentences - overlap
                 
                    with open(output_file, 'a', encoding='utf-8') as out_file:
                        out_file.write(compiled_content)
                        print("Appended content from '%s' to '%s'." % (file_path, output_file))

if __name__ == "__main__":
    md_files_path = 'output/Pattern Recognition Lecture Winter 2021'
    output_file = 'output/Compiled_Course_Material.md'
    open(output_file, 'w').close()
    ProcessMD(md_files_path, output_file, num_sentences=10, overlap=1)