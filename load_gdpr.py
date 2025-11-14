from dataclasses import dataclass, asdict
from enum import Enum
import re, chromadb, uuid
from copy import deepcopy

@dataclass
class Metadata:
    part: str = "header"
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

def part_switch(line: str, part: str):
    match line:
        case "Whereas:":
            return True, "preamble"
        case "HAVE ADOPTED THIS REGULATION:":
            return True, "body"
        case "J.A. HENNIS-PLASSCHAERT":
            return True, "endnotes"
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
    state = Metadata()
    chunk = Chunk(deepcopy(state))
    for line in f:
        line = line.strip()
        if not line:
            continue
        is_switch, state.part = part_switch(line, state.part)
        
        if is_switch and state.part == "preamble":
            documents.append(chunk)
            chunk = Chunk(deepcopy(state))
            continue
        
        if is_switch and state.part == "endnotes":
            documents.append(chunk)
            state.chapter = 0
            state.chapter_title = "endnotes"
            state.section = 0
            state.section_title = "endnotes"
            state.article = 0
            state.article_title = "endnotes"
            chunk = Chunk(deepcopy(state))

        match state.part:
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

print(f"Number of documents: {len(documents)}")

metadatas = [asdict(document.metadata) for document in documents]
documents = [document.text for document in documents]
ids = [str(uuid.uuid4()) for i in range(len(documents))]

chroma_client = chromadb.HttpClient(host="localhost", port=8000)
# chroma_client.delete_collection(name="my_collection")
collection = chroma_client.get_or_create_collection(name="gdpr")
collection.upsert(
        ids=ids, 
        documents=documents,
        metadatas=metadatas
        )