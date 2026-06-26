import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(
    api_key = os.environ.get("GROQ_API_KEY")
)

file_name = input("Enter a file name to load (without .txt)".lower())


def load_file (file_name):
    while True:
        try:
            with open(f"{file_name}.txt", "r")as file:
                text = file.read()
                
                return text
            
        except FileNotFoundError:
            print ("File not found Try again.")


def chunk_text(text):

    chunks = []

    for chunk in range(0, len(text), 100):
        chunks.append(text[chunk: chunk + 100])

    return chunks

def get_question():

    keywords = []
    clean_format = []
    punctuation = ".,?!;:'\"-"
    stopwords = ["what", "is", "the", "of", "how", "a", "an", 
                "does", "are", "in", "to", "for", "do", "i", "me"]

    question = input("Ask a question about the Porsche 911 GT2 RS ").lower()
    question_words = question.split()

    for word in question_words:
        clean_word = word.strip(punctuation)
        clean_format.append(clean_word)

    for word in clean_format:
        if word not in stopwords:
            keywords.append(word)
    
    return (question, keywords)

def score_chunks(chunks, keywords):

    punctuation = ".,?!;:'\"-()"
    result = {}

    for index, chunk in enumerate(chunks):

        cleaned_chunks = []
    
        chunk_lower = chunk.lower()
        chunk_words = chunk_lower.split()
        score = 0

        for word in chunk_words:
            cleaned_chunk_word = word.strip(punctuation)
            cleaned_chunks.append(cleaned_chunk_word)

        for word in cleaned_chunks:
            if word in keywords:
                score += 1

        result[index] = score


    result_value = max(result.values())

    if result_value == 0:
        return None

    #Sorts result values, make it a list, sort the items, by key x[1] ([1] is value [0] is key) reverse the values only wanting the highest
    sorted_results = (list(sorted(result.items(), key=lambda x: x[1], reverse=True)))
    #take the highest 3 results 0:3 (0 is default so :3 works) since it was already reverse the highest are the first 3
    best_indexs = (sorted_results[:3])
    #List to append each index in because best_indexs are in a tuple (0, 3) 
    best_index = []
    #For every tuple append the tuple's first value (index)
    for indexs in best_indexs:
        best_index.append(indexs[0])

    best_chunks = []
    for index in best_index:
        best_chunks.append(chunks[index])
    
    joined = " ".join(best_chunks)

    return joined
        
def main(): 
    
    text = load_file(file_name)

    while True:
    
        chunks = chunk_text(text)
        question, keywords = get_question()
        best_chunk = score_chunks(chunks, keywords)

        if best_chunk == None:
            print ("No relevent information found, Please try again.")
            continue

        chat_completion = client.chat.completions.create(
            messages = [
                {
                    "role": "user",
                    "content": f"You are a helpful assitant using ONLY the provided information (Do not state according to the provided information just give the answer), answer the users question: {question} Text: {best_chunk}. ",
                }
            ], 
            model = "llama-3.3-70b-versatile",
        )

        print('-'*45)
        print ("AI overview:".center(45))
        print("\n")
        print(chat_completion.choices[0].message.content.center(45))
        print ("-"*45)
        print ("Provided by Groq")
        print("\n")

        output = input("Would you like to ask another question? (y/n)").lower()

        if output == "n":
            print ("Goodbye.")
            break

        elif output == "y": 
            pass

        else:
            print ("Invalid input please input (y/n)")
 
if __name__ == "__main__":
    main()
