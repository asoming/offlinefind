"""SQLite persistence and query operations. All documents stay on disk."""

import json
import sqlite3
import threading
import time
from pathlib import Path

from .text import grams, match_expression, normalize, query_terms, ranges, snippet

SCHEMA = """
CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS roots(id INTEGER PRIMARY KEY, path TEXT UNIQUE NOT NULL,
    excluded TEXT NOT NULL DEFAULT '[]', available INTEGER NOT NULL DEFAULT 1);
CREATE TABLE IF NOT EXISTS documents(
    id INTEGER PRIMARY KEY, path TEXT UNIQUE NOT NULL, name TEXT NOT NULL,
    type TEXT NOT NULL, size INTEGER NOT NULL, mtime_ns INTEGER NOT NULL,
    fingerprint TEXT NOT NULL, status TEXT NOT NULL, body TEXT NOT NULL,
    blocks TEXT NOT NULL, title_tokens TEXT NOT NULL, body_tokens TEXT NOT NULL,
    saved INTEGER NOT NULL DEFAULT 0, updated REAL NOT NULL);
CREATE VIRTUAL TABLE IF NOT EXISTS search_index USING fts5(
    title_tokens, body_tokens, content='documents', content_rowid='id', detail='none');
CREATE TRIGGER IF NOT EXISTS docs_insert AFTER INSERT ON documents BEGIN
    INSERT INTO search_index(rowid,title_tokens,body_tokens)
    VALUES(new.id,new.title_tokens,new.body_tokens);
END;
CREATE TRIGGER IF NOT EXISTS docs_delete AFTER DELETE ON documents BEGIN
    INSERT INTO search_index(search_index,rowid,title_tokens,body_tokens)
    VALUES('delete',old.id,old.title_tokens,old.body_tokens);
END;
CREATE TRIGGER IF NOT EXISTS docs_update
AFTER UPDATE OF title_tokens,body_tokens ON documents BEGIN
    INSERT INTO search_index(search_index,rowid,title_tokens,body_tokens)
    VALUES('delete',old.id,old.title_tokens,old.body_tokens);
    INSERT INTO search_index(rowid,title_tokens,body_tokens)
    VALUES(new.id,new.title_tokens,new.body_tokens);
END;
"""


class Store:
    def __init__(self, directory: Path):
        directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.directory = directory.resolve()
        self.path = directory / "library.sqlite3"
        self.lock = threading.RLock()
        self.connection = sqlite3.connect(self.path, check_same_thread=False, timeout=10)
        self.connection.row_factory = sqlite3.Row
        self.connection.create_function("normalize_name", 1, normalize, deterministic=True)
        self.connection.execute("PRAGMA journal_mode=WAL")
        self.connection.execute("PRAGMA secure_delete=ON")
        self.connection.execute("PRAGMA cache_size=-8192")
        self.connection.executescript(SCHEMA)
        columns = {row[1] for row in self.connection.execute("PRAGMA table_info(documents)")}
        if "seen_scan" not in columns:
            self.connection.execute(
                "ALTER TABLE documents ADD COLUMN seen_scan TEXT NOT NULL DEFAULT ''"
            )
        self.connection.execute(
            "CREATE INDEX IF NOT EXISTS documents_status ON documents(status,id)"
        )
        self.connection.execute(
            "CREATE INDEX IF NOT EXISTS documents_recent ON documents(mtime_ns DESC,id) "
            "WHERE status != 'unavailable'"
        )
        self.connection.execute("CREATE INDEX IF NOT EXISTS documents_saved ON documents(saved)")
        self.path.chmod(0o600)

    def close(self):
        with self.lock:
            self.connection.close()

    def roots(self) -> list[dict]:
        with self.lock:
            return [
                dict(row, excluded=json.loads(row["excluded"]))
                for row in self.connection.execute("SELECT * FROM roots ORDER BY id")
            ]

    def add_root(self, path: Path) -> int:
        if not path.is_dir():
            raise ValueError("invalid_folder")
        path = path.resolve()
        if (
            path == Path(path.anchor)
            or path == self.directory
            or self.directory.is_relative_to(path)
        ):
            raise ValueError("folder_too_broad")
        with self.lock, self.connection:
            self.connection.execute("INSERT OR IGNORE INTO roots(path) VALUES(?)", (str(path),))
            return self.connection.execute(
                "SELECT id FROM roots WHERE path=?", (str(path),)
            ).fetchone()[0]

    def add_automatic_root(self, path: Path):
        # Only OS discovery calls this; the RPC never accepts arbitrary disk roots.
        with self.lock, self.connection:
            self.connection.execute("INSERT OR IGNORE INTO roots(path) VALUES(?)", (str(path),))

    def discover_batch(self, entries, scan_id):
        values = []
        for path, stat, fingerprint, kind, status in entries:
            values.append(
                (
                    str(path),
                    path.name,
                    kind,
                    stat.st_size,
                    stat.st_mtime_ns,
                    fingerprint,
                    status,
                    grams(path.name),
                    time.time(),
                    scan_id,
                )
            )
        with self.lock, self.connection:
            self.connection.executemany(
                """INSERT INTO documents
                (path,name,type,size,mtime_ns,fingerprint,status,body,blocks,title_tokens,
                 body_tokens,updated,seen_scan) VALUES(?,?,?,?,?,?,?,'','[]',?,'',?,?)
                ON CONFLICT(path) DO UPDATE SET name=excluded.name,type=excluded.type,
                size=excluded.size,mtime_ns=excluded.mtime_ns,fingerprint=excluded.fingerprint,
                status=excluded.status,body='',blocks='[]',title_tokens=excluded.title_tokens,
                body_tokens='',updated=excluded.updated,seen_scan=excluded.seen_scan
                WHERE documents.fingerprint != excluded.fingerprint
                   OR documents.size != excluded.size OR documents.mtime_ns != excluded.mtime_ns
                   OR documents.status='unavailable'""",
                values,
            )
            self.connection.executemany(
                "UPDATE documents SET seen_scan=? WHERE path=?",
                [(scan_id, row[0]) for row in values],
            )

    def finish_discovery(self, scan_id):
        with self.lock, self.connection:
            self.connection.execute(
                """UPDATE documents SET status='unavailable',body='',blocks='[]',body_tokens=''
                   WHERE seen_scan != ? AND status != 'unavailable'""",
                (scan_id,),
            )

    def queue_contents(self):
        with self.lock, self.connection:
            self.connection.execute(
                """UPDATE documents SET status='pending',body='',blocks='[]',body_tokens=''
                   WHERE type IN ('pdf','md','docx') AND status != 'unavailable'"""
            )

    def pending_batch(self, after_id):
        with self.lock:
            return [
                dict(row)
                for row in self.connection.execute(
                    "SELECT id,path FROM documents WHERE status='pending' AND id>? "
                    "ORDER BY id LIMIT 64",
                    (after_id,),
                )
            ]

    def setting(self, key, default=None):
        with self.lock:
            row = self.connection.execute(
                "SELECT value FROM settings WHERE key=?", (key,)
            ).fetchone()
            return json.loads(row[0]) if row else default

    def set_setting(self, key, value):
        with self.lock, self.connection:
            self.connection.execute(
                "INSERT OR REPLACE INTO settings VALUES(?,?)", (key, json.dumps(value))
            )

    def upsert(self, path: Path, stat, fingerprint: str, result: dict):
        body = "\n".join(block["text"] for block in result["blocks"])
        values = (
            str(path),
            path.name,
            path.suffix.lower().lstrip(".").replace("markdown", "md"),
            stat.st_size,
            stat.st_mtime_ns,
            fingerprint,
            result["status"],
            body,
            json.dumps(result["blocks"], ensure_ascii=False),
            grams(path.name),
            grams(body),
            time.time(),
        )
        with self.lock, self.connection:
            self.connection.execute(
                """INSERT INTO documents
                (path,name,type,size,mtime_ns,fingerprint,status,body,blocks,title_tokens,
                 body_tokens,updated) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(path) DO UPDATE SET name=excluded.name,type=excluded.type,
                size=excluded.size,mtime_ns=excluded.mtime_ns,fingerprint=excluded.fingerprint,
                status=excluded.status,body=excluded.body,blocks=excluded.blocks,
                title_tokens=excluded.title_tokens,body_tokens=excluded.body_tokens,
                updated=excluded.updated""",
                values,
            )

    def inventory(self) -> dict:
        with self.lock:
            return {
                row["path"]: dict(row)
                for row in self.connection.execute(
                    "SELECT id,path,size,mtime_ns,fingerprint,status FROM documents"
                )
            }

    def invalidate(self, path: str, status: str = "unavailable"):
        with self.lock, self.connection:
            self.connection.execute(
                """UPDATE documents SET status=?,body='',blocks='[]',
                body_tokens='' WHERE path=?""",
                (status, path),
            )

    def remove_root(self, root_id: int):
        with self.lock, self.connection:
            self.connection.execute("DELETE FROM roots WHERE id=?", (root_id,))

    def exclude(self, root_id: int, relative: str):
        root = next((r for r in self.roots() if r["id"] == root_id), None)
        if root is None:
            raise ValueError("invalid_folder")
        base = Path(root["path"])
        child = (base / relative).resolve()
        if not relative.strip() or child == base or not child.is_relative_to(base):
            raise ValueError("invalid_exclusion")
        excludes = sorted(set(root["excluded"] + [child.relative_to(base).as_posix()]))
        with self.lock, self.connection:
            self.connection.execute(
                "UPDATE roots SET excluded=? WHERE id=?", (json.dumps(excludes), root_id)
            )

    def delete_outside(self, allowed):
        with self.lock, self.connection:
            after_id = 0
            while True:
                rows = self.connection.execute(
                    "SELECT id,path FROM documents WHERE id>? ORDER BY id LIMIT 128", (after_id,)
                ).fetchall()
                if not rows:
                    break
                for row in rows:
                    after_id = row["id"]
                    if not allowed(Path(row["path"])):
                        self.connection.execute("DELETE FROM documents WHERE id=?", (row["id"],))
        self.compact()

    def remove_exclusion(self, root_id: int, relative: str):
        root = next((r for r in self.roots() if r["id"] == root_id), None)
        if root is None:
            raise ValueError("invalid_folder")
        if relative not in root["excluded"]:
            raise ValueError("invalid_exclusion")
        remaining = [rule for rule in root["excluded"] if rule != relative]
        with self.lock, self.connection:
            self.connection.execute(
                "UPDATE roots SET excluded=? WHERE id=?", (json.dumps(remaining), root_id)
            )

    def issues(self, offset: int = 0, allowed=None):
        offset = max(0, min(int(offset), 100000))
        items, skipped = [], 0
        with self.lock:
            rows = self.connection.execute(
                "SELECT id,name,path,type,status FROM documents "
                "WHERE status NOT IN ('ready','metadata') ORDER BY id"
            )
            for row in rows:
                if allowed and not allowed(Path(row["path"])):
                    continue
                if skipped < offset:
                    skipped += 1
                    continue
                if len(items) == 20:
                    return {"items": items, "has_more": True, "offset": offset}
                items.append(dict(row))
        return {"items": items, "has_more": False, "offset": offset}

    def compact(self):
        with self.lock:
            self.connection.execute("PRAGMA wal_checkpoint(TRUNCATE)")
            self.connection.execute("VACUUM")

    def clear(self):
        with self.lock, self.connection:
            self.connection.execute("DELETE FROM documents")
            self.connection.execute("DELETE FROM roots")
            self.connection.execute("DELETE FROM settings")
        self.compact()

    def counts(self) -> dict:
        with self.lock:
            rows = self.connection.execute(
                "SELECT status,count(*) n FROM documents GROUP BY status"
            )
            counts = {row["status"]: row["n"] for row in rows}
            return {
                "total": sum(counts.values()),
                "by_status": counts,
                "saved": self.connection.execute(
                    "SELECT count(*) FROM documents WHERE saved=1"
                ).fetchone()[0],
            }

    def bookmark(self, document_id: int, saved: bool):
        with self.lock, self.connection:
            self.connection.execute(
                "UPDATE documents SET saved=? WHERE id=?", (int(saved), document_id)
            )

    def get(self, document_id: int):
        with self.lock:
            row = self.connection.execute(
                "SELECT * FROM documents WHERE id=?", (document_id,)
            ).fetchone()
            return dict(row) if row else None

    def search(
        self,
        query: str,
        file_type: str = "all",
        root_id: int | None = None,
        saved: bool = False,
        sort: str = "relevance",
        offset: int = 0,
        allowed=None,
        mode: str = "all",
    ) -> dict:
        terms = query_terms(query.strip(), allow_single=mode != "content")
        offset = max(0, min(int(offset), 100000))
        params, conditions = [], ["d.status != 'unavailable'"]
        join = ""
        indexed_terms = [term for term in terms if len(term) >= 2]
        if indexed_terms:
            join = " JOIN search_index ON search_index.rowid=d.id"
            conditions.append("search_index MATCH ?")
            params.append(match_expression(indexed_terms))
        for term in terms:
            if len(term) == 1:
                conditions.append("instr(normalize_name(d.name),?) > 0")
                params.append(term)
        if file_type in {"pdf", "md", "docx", "folder"}:
            conditions.append("d.type=?")
            params.append(file_type)
        if saved:
            conditions.append("d.saved=1")
        root = next((r for r in self.roots() if r["id"] == root_id), None)
        if root_id is not None and root is None:
            return {"items": [], "has_more": False, "terms": terms, "offset": offset}
        order = (
            "d.mtime_ns DESC,d.id"
            if sort == "date" or not indexed_terms
            else ("bm25(search_index,5.0,1.0),d.mtime_ns DESC,d.id")
        )
        # Sort lightweight candidates, then load text only as needed for literal verification.
        sql = (
            f"SELECT d.id,d.path FROM documents d{join} "
            f"WHERE {' AND '.join(conditions)} ORDER BY {order}"
        )
        items, skipped = [], 0
        with self.lock:
            cursor = self.connection.execute(sql, params)
            for candidate in cursor:
                path = Path(candidate["path"])
                if root and not path.is_relative_to(root["path"]):
                    continue
                fields = "name" if mode == "name" else "name,body"
                text = self.connection.execute(
                    f"SELECT {fields} FROM documents WHERE id=?", (candidate["id"],)
                ).fetchone()
                title = "" if mode == "content" else normalize(text["name"])
                body = "" if mode == "name" else normalize(text["body"])
                if not all(term in title or term in body for term in terms):
                    continue
                # Reject gram false positives before expensive filesystem checks.
                # Every returned item still passes the same scope/permission verification.
                if allowed and not allowed(path, check_file=True):
                    continue
                if skipped < offset:
                    skipped += 1
                    continue
                if len(items) == 50:
                    return {"items": items, "has_more": True, "terms": terms, "offset": offset}
                row = self.connection.execute(
                    "SELECT * FROM documents WHERE id=?", (candidate["id"],)
                ).fetchone()
                matches = [
                    b
                    for b in json.loads(row["blocks"])
                    if any(term in normalize(b["text"]) for term in terms)
                ]
                content = matches[0]["text"] if matches else row["body"]
                excerpts = [snippet(b["text"], terms) for b in matches[:2]]
                if not excerpts:
                    excerpts = [snippet(content, terms)]
                items.append(
                    {
                        key: row[key]
                        for key in (
                            "id",
                            "name",
                            "path",
                            "type",
                            "size",
                            "mtime_ns",
                            "saved",
                            "status",
                        )
                    }
                )
                items[-1].update(
                    {
                        "excerpts": excerpts,
                        "title_ranges": ranges(row["name"], terms),
                        "name_only": bool(terms) and not matches,
                    }
                )
        return {"items": items, "has_more": False, "terms": terms, "offset": offset}
