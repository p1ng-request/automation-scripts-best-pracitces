import os
import re
import nltk
import textstat
from typing import List, Tuple
from pathlib import Path
import markdown
from nltk.sentiment import SentimentIntensityAnalyzer
from language_tool_python import LanguageTool
import textblob as tb

nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')

def clean_html(documentation: str) -> str:
    """Removes any HTML tags from the documentation
    :param documentation: str
    :return: str
    """
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', documentation)
    return cleantext

def parse_markdown(documentation: str) -> str:
    """Convert markdown to html
    :param documentation: str
    :return: str
    """
    return markdown.markdown(documentation)

def remove_header(documentation: str) -> str:
    """Remove YAML front matter
    :param documentation: str
    :return: str
    """
    lines = documentation.split("\n")
    for i, line in enumerate(lines):
        if line.strip() == "---":
            start = i
            break
    for i, line in enumerate(lines[start+1:]):
        if line.strip() == "---":
            end = i + start + 1
            break
    return "\n".join(lines[end+1:])

def check_tone(documentation: str) -> str:
    """Check for Tone in the text
    :param documentation: str
    :return: str
    """
    # Create an instance of the sentiment intensity analyzer
    sentiment_analyzer = SentimentIntensityAnalyzer()
    # Get the sentiment score of the documentation
    sentiment_score = sentiment_analyzer.polarity_scores(documentation)
    if sentiment_score['compound'] < -0.5:
        return "The documentation is written in a very negative tone."
    elif sentiment_score['compound'] < 0:
        return "The documentation is written in a negative tone."
    elif sentiment_score['compound'] == 0:
        return "The documentation is written in a neutral tone."
    elif sentiment_score['compound'] > 0:
        return "The documentation is written in a positive tone."
    elif sentiment_score['compound'] > 0.5:
        return "The documentation is written in a very positive tone."

def score_documentation(documentation: str) -> float:
    """
    Compute the Flesch-Kincaid readability test
    """
    fk_score = textstat.flesch_kincaid_grade(documentation)
    return fk_score


def suggest_improvements(documentation: str) -> List[Tuple[str, str]]:
    suggestions = []
    # create an instance of the LanguageTool class
    tool = LanguageTool('en-US')
    # Cehck with Grammarly
    # grammarly.Client.check(documentation)
    # Compute the Flesch-Kincaid readability test
    fk_score = score_documentation(documentation)
    coleman_score = textstat.coleman_liau_index(documentation)
    # Check if the documentation has an objective tone
    objective_score = textstat.automated_readability_index(documentation)
    clear_score = textstat.flesch_reading_ease(documentation)
    if fk_score > 18:
        suggestions.append(("The document appears to be written at a higher reading level than the target audience. Consider simplifying the language.", "Readability"))
    elif fk_score < 10:
        suggestions.append(("The document appears to be written at a lower reading level than the target audience. Consider using more complex vocabulary.", "Readability"))
    if coleman_score > 18:
        suggestions.append(("The document appears to be written at a higher reading level than the target audience. Consider simplifying the language.", "Readability"))
    elif coleman_score < 10:
        suggestions.append(("The document appears to be written at a lower reading level than the target audience. Consider using more complex vocabulary.", "Readability"))
    if objective_score > 18:
        suggestions.append(("The document appears to be written in an objective tone.", "Objectivity"))
    elif objective_score < 10:
        suggestions.append(("The document appears to be written in a subjective tone.", "Objectivity"))
    if clear_score < 30:
        suggestions.append(("The document appears to be difficult to read. Consider simplifying the language.", "Readability"))
    return suggestions

def scan_documentation(file: str) -> float:
    # read the documentation file
    with open(file, 'r') as f:
        documentation = f.read()

    # remove the header
    documentation = remove_header(documentation)
    
    # parse the markdown and get the plain text
    documentation = parse_markdown(documentation)
    
    # remove any HTML tags from the documentation
    documentation = clean_html(documentation)

    # remove any invalid characters from the documentation string
    documentation = re.sub(r'[^\x00-\x7F]+', '', documentation)

    # check the tone of the documentation
    check_tone(documentation)
   
    # score the documentation
    score = score_documentation(documentation)
    
    # get suggestions for improvement
    suggestions = suggest_improvements(documentation)
    
    # print the score and suggestions
    print("Score:",score)
    for suggestion in suggestions:
        print(suggestion)
    return score




def scan_all_documentations(root_dir: str):
    scores = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                score = scan_documentation(file_path)
                scores.append(score)
                print('File:', file)
        for subdir in dirs:
            subdir_path = os.path.join(root, subdir)
            scores.extend(scan_all_documentations(subdir_path))
    return scores


def main():
    root_dir = '/path'
    scores = scan_all_documentations(root_dir)
    # print(scores)

if __name__ == '__main__':
    main()
