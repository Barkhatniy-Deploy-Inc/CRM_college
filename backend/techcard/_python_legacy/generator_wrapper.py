import json
import sys
import os
from database.models_techcard import TechCard, TechCardStage
from utils.docx_generator import generate_techcard_docx

def main():
    try:
        # Читаем JSON из stdin
        input_data = json.load(sys.stdin)
        
        # Эмулируем объекты для оригинальной функции
        class MockObj:
            def __init__(self, **entries):
                self.__dict__.update(entries)
        
        techcard_data = MockObj(**input_data['techcard'])
        techcard_data.stages = [MockObj(**s) for s in input_data['stages']]
        
        # Вызываем оригинальный генератор
        # techcard_data, group_name, lesson_name, teacher_name, lesson_type_name
        file_stream = generate_techcard_docx(
            techcard_data,
            input_data.get('group_name', ''),
            input_data.get('lesson_name', ''),
            input_data.get('teacher_name', ''),
            input_data.get('lesson_type_name', '')
        )
        
        # Сохраняем во временный файл и выводим путь
        output_path = os.path.join('/tmp', f"techcard_{techcard_data.id}.docx")
        with open(output_path, 'wb') as f:
            f.write(file_stream.getbuffer())
            
        print(output_path)
        
    except Exception as e:
        print(f"ERROR: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    # Исправляем PYTHONPATH чтобы видеть utils
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    main()
