"""Struktur-, PDF- und Reviewprüfung; braucht pdfinfo und pdftotext."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    source = (ROOT / 'blatt01.tex').read_text()
    assert re.findall(r'\\aufgabe\{([^}]+)\}', source) == ['1.1', '1.2', '1.3', '1.4', '1.5']
    assert source.count('\\teil{') == 16
    assert source.count('\\begin{tabularx}') == 2
    assert source.count('\\begin{tikzpicture}') == 1
    assert '% grafik-verlangt' in source
    assert '\\draw[<->] (net.south)--(bank.north);' in source
    assert 'empfängt Daten von den Kommunikationsgeräten und sendet Daten an diese zurück' in source
    review = json.loads((ROOT / 'independent_review.json').read_text())
    assert review['result']['passed'] is True and not review['result']['findings']
    context = json.loads((ROOT / 'context_used.json').read_text())
    assert context['source_hash'] and context['materials']
    assert all(material['course_lv'] == '621.150' for material in context['materials'])
    pdfs = {}
    for filename in ('loesung_blatt01.pdf', 'erklaerung_blatt01.pdf'):
        pdf = ROOT / filename
        info = subprocess.check_output(['pdfinfo', str(pdf)], text=True)
        page_match = re.search(r'^Pages:\s+(\d+)', info, re.M)
        assert page_match is not None, 'pdfinfo liefert keine Seitenzahl'
        pages = int(page_match.group(1))
        assert pages > 0
        text = subprocess.check_output(['pdftotext', '-layout', str(pdf), '-'], text=True)
        for number in ('1.1', '1.2', '1.3', '1.4', '1.5'):
            assert 'Aufgabe ' + number in text
        assert 'eER' in text and 'Authentizität' in text
        if filename.startswith('loesung'):
            assert 'Erklärung' not in text
        else:
            assert text.count('Erklärung') >= 17
        pdfs[filename] = {'pages': pages, 'sha256': sha(pdf), 'text_verified': True}
    assert pdfs['erklaerung_blatt01.pdf']['pages'] >= pdfs['loesung_blatt01.pdf']['pages']
    result = {'passed': True, 'tasks': ['1.1', '1.2', '1.3', '1.4', '1.5'],
              'named_subtasks': 16, 'pdfs': pdfs, 'tex_sha256': sha(ROOT / 'blatt01.tex'),
              'independent_review_passed': True,
              'limits': 'Structural checks do not replace semantic review; typography-only changes after the second review were checked in the main run.'}
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
