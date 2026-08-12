#!/usr/bin/env python
# -*- coding: utf-8 -*-"
# vim: set expandtab tabstop=4 shiftwidth=4:
"""
This file is part of the XSSer project, https://xsser.03c8.net

Copyright (c) 2010/2026 | psy <epsylon@riseup.net>

xsser is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free
Software Foundation version 3 of the License.

xsser is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
details.

You should have received a copy of the GNU General Public License along
with xsser; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import json, datetime

class json_reporting(object):
    """
    Print results from an attack as a JSON document (for CI / pipelines).
    """
    def __init__(self, xsser):
        self.instance = xsser

    def print_json_results(self, filename):
        inst = self.instance
        found = list(getattr(inst, 'hash_found', []))
        notfound = list(getattr(inst, 'hash_notfound', []))
        total = len(found) + len(notfound)
        try:
            accuracy = round(len(found) * 100.0 / total, 2)
        except ZeroDivisionError:
            accuracy = 0
        opts = inst.options
        report = {
            "tool": "XSSer",
            "version": "1.9",
            "codename": "Bl4ck Swarm!",
            "url": "https://xsser.03c8.net",
            "date": str(datetime.datetime.now()),
            "target": opts.url or opts.target or opts.dork or opts.readfile or "multiple",
            "command": inst.get_command_used() if hasattr(inst, 'get_command_used') else "",
            "techniques": inst.get_techniques_used() if hasattr(inst, 'get_techniques_used') else [],
            "summary": {
                "total_injections": total,
                "successful": len(found),
                "failed": len(notfound),
                "accuracy_percent": accuracy,
            },
            "vulnerabilities": [],
        }
        for line in found:
            if len(line) > 1 and line[1] == "[Heuristic test]":
                report["vulnerabilities"].append({
                    "type": "heuristic",
                    "target": str(line[6]) if len(line) > 6 else "",
                    "vector": str(line[3]) if len(line) > 3 else "",
                    "character": str(line[5]) if len(line) > 5 else "",
                    "status": "NOT FILTERED",
                })
            elif len(line) > 1 and line[1] == "[hashing check]":
                report["vulnerabilities"].append({
                    "type": "hashing check",
                    "target": str(line[6]) if len(line) > 6 else "",
                    "vector": str(line[3]) if len(line) > 3 else "",
                    "status": "HASH FOUND",
                })
            else:
                report["vulnerabilities"].append({
                    "type": "xss",
                    "target": str(line[6]) if len(line) > 6 else "",
                    "method": str(line[2]).upper() if len(line) > 2 else "URL",
                    "parameter": str(line[3]) if len(line) > 3 else "",
                    "context": str(line[1]) if len(line) > 1 else "",
                    "payload": str(line[0]),
                    "confirmed": bool(getattr(opts, 'reversecheck', False)),
                })
        try:
            report["connections"] = {
                "total": inst.success_connection + inst.not_connection + inst.forwarded_connection + inst.other_connection,
                "ok": inst.success_connection,
                "failed": inst.not_connection,
                "forwarded": inst.forwarded_connection,
                "other": inst.other_connection,
            }
        except Exception:
            pass
        if getattr(opts, 'statistics', False):
            try:
                report["duration"] = str(datetime.datetime.now() - inst.time).split('.')[0]
            except Exception:
                pass
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
