import argparse
import json
import sys


def iter_json_array(path, encoding, chunk_size=1024 * 1024):
    decoder = json.JSONDecoder()
    with open(path, 'r', encoding=encoding, errors='strict') as f:
        buf = ''
        pos = 0

        def read_more():
            nonlocal buf
            chunk = f.read(chunk_size)
            if not chunk:
                return False
            buf += chunk
            return True

        # Find array start
        while True:
            if pos >= len(buf):
                if not read_more():
                    raise ValueError('Empty file or invalid JSON')
            while pos < len(buf) and buf[pos].isspace():
                pos += 1
            if pos < len(buf):
                if buf[pos] == '[':
                    pos += 1
                    break
                raise ValueError('Top-level JSON is not an array')

        while True:
            # Skip whitespace and commas
            while True:
                if pos >= len(buf):
                    if not read_more():
                        raise ValueError('Unexpected EOF while parsing array')
                if pos < len(buf) and (buf[pos].isspace() or buf[pos] == ','):
                    pos += 1
                    continue
                break

            if pos < len(buf) and buf[pos] == ']':
                return

            while True:
                try:
                    obj, end = decoder.raw_decode(buf, pos)
                    pos = end
                    yield obj
                    if pos > chunk_size:
                        buf = buf[pos:]
                        pos = 0
                    break
                except json.JSONDecodeError:
                    if not read_more():
                        raise


def normalize_translations(translations):
    out = []
    if isinstance(translations, list):
        items = translations
    elif isinstance(translations, dict):
        items = [translations]
    elif isinstance(translations, str):
        items = [{'translation': translations}]
    else:
        items = []

    for item in items:
        if isinstance(item, dict):
            t_type = item.get('type', '') or ''
            t_val = item.get('translation')
            if t_val is None:
                t_val = item.get('trans')
            if t_val is None:
                t_val = item.get('meaning')
            if t_val is None:
                continue
            out.append({'type': str(t_type), 'translation': str(t_val)})
        elif isinstance(item, str):
            out.append({'type': '', 'translation': item})
    return out


def normalize_phrase_translations(phrase_obj):
    collected = []
    for key in ('translations', 'trans', 'meanings'):
        val = phrase_obj.get(key)
        if isinstance(val, list):
            for item in val:
                if isinstance(item, str):
                    collected.append(item)
                elif isinstance(item, dict):
                    item_val = item.get('translation') or item.get('trans') or item.get('meaning')
                    if item_val is not None:
                        collected.append(str(item_val))
        elif isinstance(val, str):
            collected.append(val)

    for key in ('translation', 'trans'):
        val = phrase_obj.get(key)
        if isinstance(val, str):
            collected.append(val)

    seen = set()
    out = []
    for item in collected:
        if item in seen:
            continue
        seen.add(item)
        out.append(item)
    return out


def transform_entry(entry):
    if not isinstance(entry, dict):
        return None
    word = entry.get('word')
    if word is None:
        return None

    out = {'word': str(word)}
    out['translations'] = normalize_translations(entry.get('translations', []))

    phrases_in = entry.get('phrases')
    if isinstance(phrases_in, list):
        phrases_out = []
        for phrase_obj in phrases_in:
            if not isinstance(phrase_obj, dict):
                continue
            phrase_text = phrase_obj.get('phrase')
            if not phrase_text:
                continue
            p_out = {'phrase': str(phrase_text)}
            trans_list = normalize_phrase_translations(phrase_obj)
            if trans_list:
                p_out['translations'] = trans_list
            phrases_out.append(p_out)
        if phrases_out:
            out['phrases'] = phrases_out
    return out


def dump_item(obj, out_f):
    text = json.dumps(obj, ensure_ascii=False, indent=2)
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if i == 0:
            out_f.write('  ' + line)
        else:
            out_f.write('\n  ' + line)


def convert(input_path, output_path, encoding):
    count = 0
    with open(output_path, 'w', encoding='utf-8') as out_f:
        out_f.write('[\n')
        first = True
        for entry in iter_json_array(input_path, encoding=encoding):
            transformed = transform_entry(entry)
            if transformed is None:
                continue
            if not first:
                out_f.write(',\n')
            dump_item(transformed, out_f)
            first = False
            count += 1
        out_f.write('\n]\n')
    return count


def main():
    parser = argparse.ArgumentParser(
        description='Format and convert a large JSON word list without loading it all into memory.'
    )
    parser.add_argument('input', help='Input JSON file (top-level array).')
    parser.add_argument('output', help='Output JSON file (pretty formatted).')
    parser.add_argument('--encoding', default='utf-8', help='Input file encoding (default: utf-8).')
    args = parser.parse_args()

    try:
        count = convert(args.input, args.output, args.encoding)
    except UnicodeDecodeError as exc:
        msg = (
            'Decode error while reading input. Try --encoding gbk (or the correct encoding).\n'
            f'Details: {exc}'
        )
        print(msg, file=sys.stderr)
        return 2
    except Exception as exc:
        print(f'Error: {exc}', file=sys.stderr)
        return 1

    print(f'Converted {count} entries -> {args.output}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
