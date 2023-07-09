import os
import openai
import pdfplumber
from time import time, sleep
import textwrap
import re
import glob

def open_file(filepath):
    with open(filepath, 'r', encoding="UTF-8") as infile:
        return infile.read()

def save_file(filepath, content):
    with open(filepath, 'w', encoding='UTF8') as outfile:
        outfile.write(content)

def convert_pdf2txt(src_dir, dest_dir):
    files = os.listdir(src_dir)
    files = [i for i in files if '.pdf' in i]
    for file in files:
        try:
            with pdfplumber.open(src_dir+file) as pdf:
                output = ""
                for page in pdf.pages:
                    text = page.extract_text()
                    # Remove dots from the text
                    text = text.replace(".", "")
                    output += text
                    output += '\n\nNEW PAGE\n\n'  # change this for your page demarcation
                save_file(dest_dir+file.replace('.pdf', '.txt'), output.strip())
        except Exception as oops:
            print(oops, file)


openai.api_key = open_file('openaiapikey.txt')

# THIS FUNC USES CURIE-001 TO SUMMARIZE (CHEAPER)
def gpt_3_curie(prompt):
    response = openai.Completion.create(
        model="text-curie-001",
        prompt=prompt,
        temperature=0.1,
        max_tokens=700,
        top_p=0.1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    text = response['choices'][0]['text'].strip()
    return text

# THIS FUNC USES gpt-3.5-turbo
def gpt_3_turbo(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    text = response['choices'][0]['message']['content'].strip()
    return text

# THIS FUNC USES DAVINCI-003
def gpt_3_davinci(prompt):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.1,
        max_tokens=700,
        top_p=0.1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    text = response['choices'][0]['text'].strip()
    return text

if __name__ == '__main__':
    # Call PDF Converter Function
    convert_pdf2txt('PDFs/', 'textPDF/')

    # Your Pathfolder
    pathfolder = 'C:/Users/X/Desktop/polifinitizer/textPDF'

    # get a list of all text files in the specified folder
    files = glob.glob(f'{pathfolder}/*.txt')

    # initialize an empty string to store the contents of all the text files
    alltext = ""

    # iterate over the list of files
    for file in files:
        with open(file, "r", encoding="utf-8") as infile:  # open the file
            alltext += infile.read()  # read the contents of the file and append it to the alltext string
    chunks = textwrap.wrap(alltext, 4000)
    result = list()
    count = 0

    # Save the chunks in a single text file with numbers
    formatted_chunks = [f"Chunk {i+1}:\n{chunk}" for i, chunk in enumerate(chunks)]
    save_file("pdfchunks.txt", '\n\n'.join(formatted_chunks))

    # write a summary
    for chunk in chunks:
        count = count + 1
        prompt = open_file('prompt.txt').replace('<<SUMMARY>>', chunk)
        prompt = prompt.encode(encoding="ASCII", errors="ignore").decode()
        summary = gpt_3_davinci(prompt)
        print('\n\n\n', count, 'out of', len(chunks), "Compressions", ' : ', summary)
        result.append(summary)
        save_file("res1.txt", '\n\n'.join(result))

    # SUMMARY OF NOTES
    resprompt1 = open_file("res1.txt")


    # WRITE A STEP BY STEP GUIDE FROM NOTES
    keytw = open_file("prompt2.txt").replace("<<NOTES>>", resprompt1)
    keytw2 = gpt_3_davinci(keytw)
    print(keytw2)
    save_file("res2.txt", keytw2)


    # 2_METRIC_PROMPT
    resprompt2 = open_file("res2.txt")

    # WRITE A STEP BY STEP GUIDE FROM NOTES
    keytw = open_file("prompt3.txt").replace("<<NOTES>>", resprompt2)
    keytw2 = gpt_3_davinci(keytw)
    print(keytw2)
    save_file("res3.txt", keytw2)

    # 3_METRIC_PROMPT
    resprompt3 = open_file("res3.txt")

    # WRITE A STEP BY STEP GUIDE FROM NOTES
    keytw = open_file("prompt4.txt").replace("<<NOTES>>", resprompt3)
    keytw2 = gpt_3_davinci(keytw)
    print(keytw2)
    save_file("res4.txt", keytw2)


