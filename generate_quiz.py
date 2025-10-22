#!/usr/bin/env python3
"""
Quiz HTML Generator
Generates index.html from Quiz.csv using Quiz.html as template
Only replaces the lessonsData section with data from CSV
"""

import pandas as pd
import re

def read_quiz_data(csv_file='Quiz.csv'):
    """Read quiz data from CSV file and organize by lesson"""
    # Read CSV file - row 0 has headers
    df = pd.read_csv(csv_file, encoding='utf-8')
    
    # The first row should already be the header, so just rename if needed
    # Check if columns are already named properly
    if df.columns[0] != 'Lesson':
        df.columns = ['Lesson', 'Name', 'Question Number', 'Questions', 
                      'Option 1', 'Option 2', 'Option 3', 'Option 4', 
                      'Answer', 'Explanation']
    
    # Organize questions by lesson
    lessons_data = {}
    
    for _, row in df.iterrows():
        lesson_key = row['Lesson']
        lesson_name = row['Name']
        
        # Skip header rows and invalid data
        if pd.notna(lesson_key) and pd.notna(lesson_name) and lesson_key != 'Lesson':
            # Extract lesson number from lesson_key (e.g., "Lesson 01" -> 1)
            try:
                lesson_num = int(lesson_key.split()[-1])
            except (ValueError, IndexError):
                continue
            
            if lesson_num not in lessons_data:
                lessons_data[lesson_num] = {
                    'title': lesson_key,
                    'name': lesson_name,
                    'questions': []
                }
            
            # Find correct answer index (0-based)
            answer_text = str(row['Answer']).strip()
            correct_index = 0
            if 'Option 2' in answer_text or '2' in answer_text:
                correct_index = 1
            elif 'Option 3' in answer_text or '3' in answer_text:
                correct_index = 2
            elif 'Option 4' in answer_text or '4' in answer_text:
                correct_index = 3
            
            # Add question to lesson
            question_data = {
                'question': str(row['Questions']),
                'options': [
                    str(row['Option 1']),
                    str(row['Option 2']),
                    str(row['Option 3']),
                    str(row['Option 4'])
                ],
                'correct': correct_index,
                'explanation': str(row['Explanation']) if pd.notna(row['Explanation']) else ''
            }
            
            lessons_data[lesson_num]['questions'].append(question_data)
    
    return lessons_data

def generate_lessons_data_js(lessons_data):
    """Generate JavaScript code for lessonsData"""
    js_code = "        const lessonsData = {\n"
    
    for lesson_num, lesson_info in sorted(lessons_data.items()):
        js_code += f"            {lesson_num}: {{\n"
        js_code += f"                title: \"{lesson_info['title']}\",\n"
        js_code += f"                name: \"{lesson_info['name']}\",\n"
        js_code += f"                questions: [\n"
        
        for q in lesson_info['questions']:
            js_code += "                    {\n"
            # Escape quotes in question text
            question_text = q['question'].replace('"', '\\"').replace('\n', ' ')
            js_code += f"                        question: \"{question_text}\",\n"
            js_code += f"                        options: [\n"
            for opt in q['options']:
                opt_text = opt.replace('"', '\\"').replace('\n', ' ')
                js_code += f"                            \"{opt_text}\",\n"
            js_code += f"                        ],\n"
            js_code += f"                        correct: {q['correct']},\n"
            explanation_text = q['explanation'].replace('"', '\\"').replace('\n', ' ')
            js_code += f"                        explanation: \"{explanation_text}\"\n"
            js_code += "                    },\n"
        
        js_code += "                ]\n"
        js_code += "            },\n"
    
    js_code += "        };"
    
    return js_code

def generate_html_from_template(lessons_data, template_file='Quiz.html', output_file='index.html'):
    """Generate HTML by replacing lessonsData section in template"""
    
    # Read the template file
    with open(template_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Generate the new lessonsData JavaScript code
    new_lessons_data_js = generate_lessons_data_js(lessons_data)
    
    # Find and replace the lessonsData section
    # Pattern: from "const lessonsData = {" to the closing "};"
    pattern = r'(        const lessonsData = \{.*?        \};)'
    
    # Use re.DOTALL to match across multiple lines
    html_content_new = re.sub(
        pattern,
        new_lessons_data_js,
        html_content,
        flags=re.DOTALL
    )
    
    # Write the new HTML file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content_new)
    
    print(f"Successfully generated {output_file}")
    print(f"Total lessons: {len(lessons_data)}")
    for lesson_num, lesson_info in sorted(lessons_data.items()):
        print(f"  {lesson_info['title']}: {len(lesson_info['questions'])} questions")

if __name__ == '__main__':
    print("Reading quiz data from Quiz.csv...")
    lessons_data = read_quiz_data()
    
    print("Generating HTML file from Quiz.html template...")
    generate_html_from_template(lessons_data)
    
    print("\nDone!")
