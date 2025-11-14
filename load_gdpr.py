from dataclasses import dataclass
from enum import Enum
import re
from copy import deepcopy

class Part(Enum):
    HEADER = "header"
    PREAMBLE = "preamble"
    BODY = "body"
    ENDNOTES = "endnotes"

@dataclass
class Metadata:
    part: Part
    chapter: int = 0
    chapter_title: str = ""
    section: int = 0
    section_title: str = ""
    article: int = 0
    article_title: str = ""

@dataclass
class Chunk:
    metadata: Metadata
    text: str = ""

def part_switch(line: str, part: Part):
    match line:
        case "Whereas:":
            return True, Part.PREAMBLE
        case "HAVE ADOPTED THIS REGULATION:":
            return True, Part.BODY
        case "J.A. HENNIS-PLASSCHAERT":
            return True, Part.ENDNOTES
        case _:
            return False, part
        
def make_chunk(line: str, chunk: Chunk):
    chunk.text = chunk.text + " " + line
    return chunk 

roman_numerals = {
    'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9, 'X': 10, 'XI': 11
}

## removes the empty lines from the file:
# open("./notes/gdpr_clean.txt", "w").writelines(
#     line for line in open("./notes/gdpr.txt") if line.strip()
# )

with open("./notes/gdpr_clean.txt", "r", encoding="utf-8") as f:
    documents = []
    state = Metadata(part=Part.HEADER)
    chunk = Chunk(deepcopy(state))
    for line in f:
        line = line.strip()
        if not line:
            continue
        is_switch, state.part = part_switch(line, state.part)
        
        if is_switch and state.part.value == "preamble":
            documents.append(chunk)
            chunk = Chunk(deepcopy(state))
            continue
        
        if is_switch and state.part.value == "endnotes":
            documents.append(chunk)
            state.chapter = 0
            state.chapter_title = "endnotes"
            state.section = 0
            state.section_title = "endnotes"
            state.article = 0
            state.article_title = "endnotes"
            chunk = Chunk(deepcopy(state))

        match state.part.value:
            case "header":
                make_chunk(line, chunk)
            case "preamble":
                preamble_pattern = re.compile(r'^\(\d+\)$')
                if preamble_pattern.match(line):
                    chunk.text = chunk.text + " " + line
                    continue
                else:
                    chunk.text = chunk.text + " " + line
                    documents.append(chunk)
                    chunk = Chunk(deepcopy(state))
            case "body":
                chapter_pattern = re.compile(r"^CHAPTER (?:I|II|III|IV|V|VI|VII|VIII|IX|X|XI)$")
                section_pattern = re.compile(r"^Section \d+$")
                article_pattern = re.compile(r"^Article \d+$")
                
                match line:
                    case _ if (m := chapter_pattern.match(line)):
                        ch = line.split(" ")
                        state.chapter = roman_numerals[ch[1]]
                        state.chapter_title = next(f).strip()
                    case _ if (m := section_pattern.match(line)):
                        sec = line.split(" ")
                        state.section = int(line.split()[1])
                        state.section_title = next(f).strip()
                    case _ if (m := article_pattern.match(line)):
                        documents.append(chunk)
                        chunk = Chunk(deepcopy(state))
                        ar = line.split(" ")
                        state.article = int(line.split()[1])
                        state.article_title = next(f).strip()
                    case _:
                        chunk.text = chunk.text + " " + line
            case "endnotes":
                make_chunk(line, chunk)

documents.append(chunk)

for document in documents:
    print(document.metadata)
    print(document.text)
    print("\n")

print(f"Number of documents: {len(documents)}")