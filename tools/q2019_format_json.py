#!/usr/bin/env python3
import argparse
import json
import re


PARENS_RE = re.compile(r"（[^）]*）|\([^)]*\)")
BRACKETS_RE = re.compile(r"\[[^\]]*\]")

POS_RE = re.compile(
    r"^\s*(?:n|v|adj|adv|vt|vi|prep|conj|pron|interj|abbr|aux|num|art|det|modal)\.\s*",
    re.IGNORECASE,
)

SEP_RE = re.compile(r"[;；]+")


def clean_text(s: str) -> str:
    s = PARENS_RE.sub("", s)       # 删（...）/(...)
    s = BRACKETS_RE.sub("", s)     # 删[...]
    s = POS_RE.sub("", s)          # 删开头 v. / n. / adj. ...
    s = re.sub(r"\s+", " ", s)     # 压缩多余空白
    return s.strip(" \t\r\n;；，,")  # 顺便去掉边缘符号


def split_senses(s: str) -> list[str]:
    parts = [p.strip() for p in SEP_RE.split(s)]
    return [p for p in parts if p]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("infile", help="输入 JSON 文件路径")
    ap.add_argument("-o", "--out", required=True, help="输出 JSON 文件路径")
    ap.add_argument(
        "--split-phrases",
        action="store_true",
        help="把 phrases[*].translation 按 ;/； 拆成 phrases[*].translations 数组",
    )
    args = ap.parse_args()

    with open(args.infile, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise SystemExit("你的 JSON 顶层看起来应是数组（list）。")

    for entry in data:
        # 清洗单词 translations（通常是 [{translation,type}, ...]）
        word_trans = entry.get("translations")
        if isinstance(word_trans, list):
            for t in word_trans:
                if isinstance(t, dict) and isinstance(t.get("translation"), str):
                    t["translation"] = clean_text(t["translation"])

        # 清洗/拆分 phrases
        phrases = entry.get("phrases")
        if isinstance(phrases, list):
            for ph in phrases:
                if not isinstance(ph, dict):
                    continue

                if isinstance(ph.get("translation"), str):
                    cleaned = clean_text(ph["translation"])
                    if args.split_phrases:
                        ph["translations"] = split_senses(cleaned)
                        del ph["translation"]
                    else:
                        ph["translation"] = cleaned

                # 如果有 phrases[*].translations (list[str])，也顺便清洗
                if isinstance(ph.get("translations"), list):
                    ph["translations"] = [
                        clean_text(x) for x in ph["translations"] if isinstance(x, str)
                    ]

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


if __name__ == "__main__":
    main()
