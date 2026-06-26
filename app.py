from flask import Flask, render_template, request
from RAG import chunk_text, score_chunks
from groq import Groq
from dotenv import load_dotenv
import os

app = Flask(__name__)
load_dotenv()
client = Groq(
    api_key= os.environ.get("GROQ_API_KEY")
) 

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == "POST":

        punctuation = ".,?!;:'\"-"
        stopwords = ["what", "is", "the", "of", "how", "a", "an", 
                        "does", "are", "in", "to", "for", "do", "i", "me"]
        keywords = []

        file = request.files["file"]
        text = file.read()
        cleaned_text = text.decode("utf-8")
        question = request.form["question"]

        chunks = chunk_text(cleaned_text)

        question_formatted = question.split()

        for word in question_formatted:
            word_lower = word.lower()
            word_stripped = word_lower.strip(punctuation)

            if word_stripped not in stopwords:
                keywords.append(word_stripped)
        
        best_chunk = score_chunks(chunks, keywords)

        if best_chunk == None:
            return render_template("index.html", content= "No relevant information found.")

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"You are a helpful assitant using ONLY the provided information (Do not state according to the provided information just give the answer), answer the users question: {question} Text: {best_chunk}. ",
                }
            ],
            model=("llama-3.3-70b-versatile")
        )
        
        AI_content = chat_completion.choices[0].message.content
                
        return render_template("index.html", content = AI_content)
    
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug = True)