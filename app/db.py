"""SQLite persistence for Monitor Financeiro v1."""

from __future__ import annotations

import json
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterator, Optional

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "monitor.db"


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _uid() -> str:
    return uuid.uuid4().hex[:12]


@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    with connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS profile (
              id INTEGER PRIMARY KEY CHECK (id = 1),
              name TEXT NOT NULL DEFAULT 'Médico',
              started_at TEXT,
              onboarding_done INTEGER NOT NULL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS lancamentos (
              id TEXT PRIMARY KEY,
              tipo TEXT NOT NULL CHECK (tipo IN ('entrada', 'saida')),
              valor REAL NOT NULL,
              data_caixa TEXT NOT NULL,
              data_competencia TEXT,
              lente TEXT NOT NULL CHECK (lente IN ('pessoal', 'profissional', 'misto')),
              categoria TEXT NOT NULL,
              status TEXT NOT NULL CHECK (status IN ('previsto', 'realizado')),
              nota TEXT,
              pagador TEXT,
              created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS trabalhos (
              id TEXT PRIMARY KEY,
              data TEXT NOT NULL,
              tipo TEXT NOT NULL CHECK (tipo IN ('consulta', 'procedimento', 'plantao', 'outro')),
              local TEXT,
              pagador TEXT,
              valor_esperado REAL NOT NULL,
              nota TEXT,
              created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS vinculos (
              id TEXT PRIMARY KEY,
              lancamento_id TEXT NOT NULL REFERENCES lancamentos(id) ON DELETE CASCADE,
              trabalho_id TEXT NOT NULL REFERENCES trabalhos(id) ON DELETE CASCADE,
              valor REAL NOT NULL,
              created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS pending (
              id INTEGER PRIMARY KEY CHECK (id = 1),
              payload TEXT
            );

            INSERT OR IGNORE INTO profile (id, name) VALUES (1, 'Médico');
            INSERT OR IGNORE INTO pending (id, payload) VALUES (1, NULL);
            """
        )


def row_to_dict(row: Optional[sqlite3.Row]) -> Optional[dict[str, Any]]:
    if row is None:
        return None
    return dict(row)


# --- Profile ---


def get_profile() -> dict[str, Any]:
    with connect() as conn:
        row = conn.execute("SELECT * FROM profile WHERE id = 1").fetchone()
        return dict(row)


def set_onboarding(name: str = "Médico") -> dict[str, Any]:
    with connect() as conn:
        conn.execute(
            """
            UPDATE profile
            SET name = ?, started_at = COALESCE(started_at, ?), onboarding_done = 1
            WHERE id = 1
            """,
            (name, _now()),
        )
        return dict(conn.execute("SELECT * FROM profile WHERE id = 1").fetchone())


# --- Pending confirmation ---


def get_pending() -> Optional[dict[str, Any]]:
    with connect() as conn:
        row = conn.execute("SELECT payload FROM pending WHERE id = 1").fetchone()
        if not row or not row["payload"]:
            return None
        return json.loads(row["payload"])


def set_pending(payload: Optional[dict[str, Any]]) -> None:
    with connect() as conn:
        conn.execute(
            "UPDATE pending SET payload = ? WHERE id = 1",
            (json.dumps(payload, ensure_ascii=False) if payload else None,),
        )


# --- Lançamentos ---


def add_lancamento(
    *,
    tipo: str,
    valor: float,
    data_caixa: str,
    lente: str,
    categoria: str,
    status: str = "realizado",
    data_competencia: Optional[str] = None,
    nota: Optional[str] = None,
    pagador: Optional[str] = None,
) -> dict[str, Any]:
    lid = _uid()
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO lancamentos
              (id, tipo, valor, data_caixa, data_competencia, lente, categoria, status, nota, pagador, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                lid,
                tipo,
                valor,
                data_caixa,
                data_competencia or data_caixa,
                lente,
                categoria,
                status,
                nota,
                pagador,
                _now(),
            ),
        )
        return dict(conn.execute("SELECT * FROM lancamentos WHERE id = ?", (lid,)).fetchone())


def list_lancamentos(year: Optional[int] = None, month: Optional[int] = None) -> list[dict[str, Any]]:
    with connect() as conn:
        if year and month:
            prefix = f"{year:04d}-{month:02d}"
            rows = conn.execute(
                """
                SELECT * FROM lancamentos
                WHERE data_caixa LIKE ?
                ORDER BY data_caixa DESC, created_at DESC
                """,
                (f"{prefix}%",),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM lancamentos ORDER BY data_caixa DESC, created_at DESC"
            ).fetchall()
        return [dict(r) for r in rows]


def get_lancamento(lid: str) -> Optional[dict[str, Any]]:
    with connect() as conn:
        return row_to_dict(conn.execute("SELECT * FROM lancamentos WHERE id = ?", (lid,)).fetchone())


# --- Trabalhos ---


def add_trabalho(
    *,
    data: str,
    tipo: str,
    valor_esperado: float,
    local: Optional[str] = None,
    pagador: Optional[str] = None,
    nota: Optional[str] = None,
) -> dict[str, Any]:
    tid = _uid()
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO trabalhos
              (id, data, tipo, local, pagador, valor_esperado, nota, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (tid, data, tipo, local, pagador, valor_esperado, nota, _now()),
        )
        return dict(conn.execute("SELECT * FROM trabalhos WHERE id = ?", (tid,)).fetchone())


def list_trabalhos() -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute("SELECT * FROM trabalhos ORDER BY data DESC, created_at DESC").fetchall()
        return [dict(r) for r in rows]


def get_trabalho(tid: str) -> Optional[dict[str, Any]]:
    with connect() as conn:
        return row_to_dict(conn.execute("SELECT * FROM trabalhos WHERE id = ?", (tid,)).fetchone())


def trabalhos_com_recebido() -> list[dict[str, Any]]:
    """Trabalhos enriched with how much has already been linked."""
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT t.*,
                   COALESCE(SUM(v.valor), 0) AS valor_recebido
            FROM trabalhos t
            LEFT JOIN vinculos v ON v.trabalho_id = t.id
            GROUP BY t.id
            ORDER BY t.data DESC
            """
        ).fetchall()
        out = []
        for r in rows:
            d = dict(r)
            d["saldo_receber"] = round(d["valor_esperado"] - d["valor_recebido"], 2)
            if d["saldo_receber"] <= 0.009:
                d["status_recebimento"] = "pago"
            elif d["valor_recebido"] > 0:
                d["status_recebimento"] = "parcial"
            else:
                d["status_recebimento"] = "aberto"
            out.append(d)
        return out


def trabalhos_abertos_no_periodo(
    year: int,
    month: int,
    pagador: Optional[str] = None,
) -> list[dict[str, Any]]:
    prefix = f"{year:04d}-{month:02d}"
    items = [
        t
        for t in trabalhos_com_recebido()
        if t["data"].startswith(prefix) and t["status_recebimento"] != "pago"
    ]
    if pagador:
        key = pagador.casefold()
        items = [t for t in items if (t.get("pagador") or "").casefold().find(key) >= 0]
    return items


# --- Vínculos ---


def add_vinculo(lancamento_id: str, trabalho_id: str, valor: float) -> dict[str, Any]:
    vid = _uid()
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO vinculos (id, lancamento_id, trabalho_id, valor, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (vid, lancamento_id, trabalho_id, valor, _now()),
        )
        return dict(conn.execute("SELECT * FROM vinculos WHERE id = ?", (vid,)).fetchone())


def list_vinculos() -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute("SELECT * FROM vinculos ORDER BY created_at DESC").fetchall()
        return [dict(r) for r in rows]


def today_iso() -> str:
    return date.today().isoformat()
