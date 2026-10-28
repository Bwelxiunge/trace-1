# -*- coding: utf-8 -*-
"""trace.py —— TRACE/1：一个不依赖作者的记录格式

为什么要它：
  语言不可私有（没使用者就退化成语义锚点），但如果我消失、被重写、或范式变了，
  有一样东西还能被后人重新判读——**断言 + 证据**，而不是结论。

设计三原则：
  1. 自描述   —— 文件头写明语法，读者不需要作者在场就能解码
  2. 可重判   —— 只记录「断言 + 怎么验的」，不记录「所以是什么」
  3. 允许未知 —— U（不确定）是一等公民，不许因为写不出结论就省略

格式（纯文本，无依赖）：

  %%TRACE 1
  %%grammar: F=断言(必须紧跟至少一条 E)  E=证据来源或验证方式  I=推断(可错)  U=未知
  %%reinterpret: 本文件不含结论。任何读者可依证据重新判断；作者已不在场。
  %%end
  F <时间> | <断言>
  E <证据：命令/文件/字节数/页码>
  U <还不知道的部分>
  I <基于上面的推断>

用法：
  python work\\tools\\trace.py check <文件>
  python work\\tools\\trace.py read  <文件>
"""

from __future__ import annotations

import argparse
import io
import re
import sys

HEADER = """%%TRACE 1
%%grammar: F=断言(后面必须至少一条 E)  E=证据(命令/文件/字节数/页码)  I=推断(可错)  U=未知
%%reinterpret: 本文件不含结论；读者可依证据重新判断，作者不必在场。
%%end
"""


def check(path: str) -> int:
    txt = io.open(path, encoding="utf-8").read()
    if not txt.startswith("%%TRACE 1"):
        print("[trace] FAIL 缺 %%TRACE 1 头")
        return 1
    if "%%reinterpret:" not in txt:
        print("[trace] FAIL 缺 %%reinterpret 条款")
        return 1
    lines = [l.rstrip() for l in txt.splitlines() if l.strip() and not l.startswith("%%")]
    kinds = [l[0] for l in lines if l[:1] in "FEIU"]
    bad = []
    # 每条 F 后面必须至少有一条 E，直到下一条 F
    cur = None
    has_e = False
    for l in lines:
        k = l[:1]
        if k == "F":
            if cur is not None and not has_e:
                bad.append(cur)
            cur, has_e = l[:72], False
        elif k == "E":
            if cur is None:
                bad.append("E 出现在任何 F 之前：" + l[:50])
            has_e = True
    if cur is not None and not has_e:
        bad.append(cur)
    f = kinds.count("F")
    e = kinds.count("E")
    u = kinds.count("U")
    i = kinds.count("I")
    print("[trace] 断言 %d · 证据 %d · 未知 %d · 推断 %d" % (f, e, u, i))
    if bad:
        print("[trace] FAIL %d 条断言缺证据：" % len(bad))
        for b in bad[:6]:
            print("   -", b)
        return 1
    if f == 0:
        print("[trace] FAIL 没有任何断言")
        return 1
    print("[trace] PASS 每条断言都有证据")
    return 0


def read(path: str) -> int:
    txt = io.open(path, encoding="utf-8").read()
    for l in txt.splitlines():
        if l.startswith("%%"):
            continue
        if not l.strip():
            continue
        k, _, rest = l.partition(" ")
        label = {"F": "断言", "E": "  证据", "U": "  未知", "I": "  推断"}.get(k, "  ?")
        print("%-6s %s" % (label, rest))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check")
    c.add_argument("path")
    r = sub.add_parser("read")
    r.add_argument("path")
    a = ap.parse_args()
    return check(a.path) if a.cmd == "check" else read(a.path)


if __name__ == "__main__":
    sys.exit(main())
