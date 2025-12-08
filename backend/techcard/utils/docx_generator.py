from docxtpl import DocxTemplate
from io import BytesIO
import os


def generate_techcard_docx(techcard_data, group_name, lesson_name, teacher_name, lesson_type_name):
    """
    Генерирует DOCX из шаблона, заполняя его данными из БД.
    """
    # Путь к шаблону
    template_path = os.path.join('templates', 'Tekhnologicheskaia-karta-zaniatiia.docx')

    # Загружаем шаблон
    doc = DocxTemplate(template_path)

    # Подготавливаем данные для подстановки
    context = {
        'lesson_name': lesson_name or '',
        'tema': techcard_data.tema or '',
        'group_name': group_name or '',
        'teacher_name': teacher_name or '',
        'lesson_type_name': lesson_type_name or '',
        'nomer_zanyatiya': techcard_data.nomer_zanyatiya or '',
        'ped_tech': techcard_data.ped_tech or '',
        'cel_zanyatiya': techcard_data.cel_zanyatiya or '',
        'zadachi_obuch': techcard_data.zadachi_obuch or '',
        'zadachi_razv': techcard_data.zadachi_razv or '',
        'zadachi_vosp': techcard_data.zadachi_vosp or '',
        'prognoz_result': techcard_data.prognoz_result or '',
        'oborudovanie': techcard_data.oborudovanie or '',
        'istochniki': techcard_data.istochniki or '',
        'stages': [
            {
                'nomer_etapa': stage.nomer_etapa,
                'nazvanie_etapa': stage.nazvanie_etapa or '',
                'cel_etapa': stage.cel_etapa or '',
                'dlitelnost': stage.dlitelnost or '',
                'deyatelnost_prepod': stage.deyatelnost_prepod or '',
                'deyatelnost_obuch': stage.deyatelnost_obuch or '',
                'formiruemye_kompetencii': stage.formiruemye_kompetencii or ''
            }
            for stage in techcard_data.stages
        ]
    }

    # Заполняем шаблон данными
    doc.render(context)

    # Сохраняем в BytesIO
    file_stream = BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)

    return file_stream
