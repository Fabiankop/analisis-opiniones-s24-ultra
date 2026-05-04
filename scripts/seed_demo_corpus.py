"""Seed de un corpus demostrativo de comentarios sobre el Samsung Galaxy
S24 Ultra.

Este script existe para que el pipeline (sentimiento + frecuencia) sea
ejecutable cuando NO se dispone de un Bearer Token de la API de X.
Genera la base SQLite ``data/s24_comments.db`` con la misma estructura
que produciría ``contextualization extraction``.

Los textos son una muestra curada — redactados en estilo de publicación
real de X/Reddit/foros — que cubre los principales aspectos del producto
(cámara, batería, rendimiento, diseño, precio, software, S Pen, IA) en
las tres polaridades (positiva, neutral, negativa).

Cuando se obtenga el token de la API, basta con borrar la base y correr
``contextualization extraction`` para reemplazar el corpus por datos
reales sin tocar el resto del pipeline.
"""

from __future__ import annotations

import hashlib
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "data" / "s24_comments.db"

COMMENTS: list[str] = [
    # ===== Cámara — positivos =====
    "El zoom 100x del S24 Ultra es absurdo, le tomé fotos a la luna y se ven brutales",
    "La cámara nocturna del Galaxy S24 Ultra le da vueltas al iPhone 15 Pro Max, sin discusión",
    "Probé la cámara del S24 Ultra en un concierto y los detalles del escenario quedaron impecables",
    "Las fotos del S24 Ultra con galaxy AI quedan súper nítidas, el procesamiento es muy bueno",
    "El S Pen y la cámara del S24 Ultra son una combinación demasiado pro para crear contenido",

    # ===== Cámara — mixtos / negativos =====
    "La cámara del S24 Ultra está bien pero a veces sobreprocesa los colores, queda muy artificial",
    "El zoom del S24 Ultra es bueno hasta 30x, después ya pierde demasiado detalle",
    "Esperaba más de la cámara del Galaxy S24 Ultra al precio que tiene, es buena pero no excepcional",

    # ===== Batería — mixtos =====
    "La batería del S24 Ultra me dura todo el día con uso normal, muy contento",
    "Con uso intensivo de cámara y juegos la batería del S24 Ultra apenas llega al final del día",
    "La duración de la batería del S24 Ultra es buena pero la carga rápida sigue limitada a 45W",
    "Mi S24 Ultra dura un día y medio si solo uso redes y mensajería, súper",
    "La bateria del S24 Ultra se descarga rápido cuando uso galaxy AI mucho rato",
    "Nada del otro mundo la batería del S24 Ultra, esperaba más por el precio que pagué",

    # ===== Rendimiento =====
    "El Snapdragon 8 Gen 3 del S24 Ultra vuela, no he visto un solo lag en 3 meses",
    "Juego Genshin Impact en ultra y el S24 Ultra ni se inmuta, rendimiento brutal",
    "El S24 Ultra se calienta bastante con juegos pesados, no es el mejor para gaming intensivo",
    "Mi S24 Ultra se calienta cuando uso la cámara mucho rato, no me esperaba eso",
    "Cero lag, fluidez total, el rendimiento del S24 Ultra es de otro nivel",

    # ===== Diseño =====
    "El diseño en titanio del S24 Ultra se siente muy premium en la mano",
    "Me encanta lo cuadrado del S24 Ultra, le da un look muy serio y profesional",
    "El S24 Ultra es enorme y pesado, no es cómodo para usar con una sola mano",
    "El tamaño del S24 Ultra no me convence, es demasiado grande para el bolsillo",
    "El acabado del titanio del Galaxy S24 Ultra se ve hermoso pero atrae demasiadas huellas",
    "El diseño del S24 Ultra es elegante pero ya está cansado, llevan años con la misma idea",

    # ===== Precio / valor =====
    "El precio del Galaxy S24 Ultra es ridículo, vale más que mi laptop",
    "Por ese precio del S24 Ultra prefiero un iPhone, no le veo la diferencia que justifique",
    "El S24 Ultra está caro pero se siente que estás pagando por calidad de verdad",
    "Esperar a que el precio del S24 Ultra baje fue la mejor decisión, ahora vale la pena",
    "El precio del S24 Ultra está totalmente sobreestimado, la diferencia con el S24+ no la justifica",
    "Pagué más de 6 millones por el S24 Ultra y la verdad no siento que valga tanto",

    # ===== Software / Galaxy AI =====
    "Galaxy AI del S24 Ultra cambió mi forma de usar el celular, las traducciones en vivo son magia",
    "Circle to Search de Galaxy AI es la mejor función que han metido en años",
    "One UI 6 en el S24 Ultra está muy fluida, me gusta el rediseño",
    "El bloatware preinstalado en el S24 Ultra es molesto, viene con muchas apps que no se pueden quitar",
    "Las funciones de IA del S24 Ultra son útiles pero algunas estarán pagas después de 2025, eso no me gusta",
    "Samsung promete 7 años de actualizaciones para el S24 Ultra, eso sí es un golazo",
    "La transcripción de notas de voz del S24 Ultra con galaxy AI funciona increíble en español",

    # ===== S Pen =====
    "El S Pen del S24 Ultra sigue siendo único en el mercado, no hay nada igual para tomar notas",
    "Casi no uso el S Pen del S24 Ultra, la verdad es un agregado que pagué pero no aprovecho",
    "El S Pen del S24 Ultra es perfecto para firmar documentos y editar fotos al detalle",
    "Si no usas el lápiz del S24 Ultra estás desperdiciando la mitad del celular",

    # ===== Pantalla =====
    "La pantalla AMOLED del S24 Ultra es la mejor del mercado, brillo brutal a pleno sol",
    "El brillo de la pantalla del S24 Ultra es absurdo, se ve perfecto en exteriores",
    "Los reflejos de la nueva pantalla del S24 Ultra mejoraron mucho, ya no es tan molesto el sol",

    # ===== Comentarios mixtos / generales =====
    "Llevo dos meses con el Galaxy S24 Ultra y sigo descubriendo cosas, vale la pena el cambio",
    "Cambié de iPhone al S24 Ultra y no me arrepiento, Android maduró un montón",
    "El S24 Ultra tiene buen hardware pero el software a veces se siente pesado",
    "Vendí mi S24 Ultra a los 2 meses, no le encontré el valor que prometían las reviews",
    "Mi S24 Ultra se ha portado de maravilla, sin un solo bug en 4 meses de uso",
    "El Galaxy S24 Ultra es excelente pero no es para todos por su tamaño y precio",
    "Compré el S24 Ultra y lo recomiendo si vienes de un Android viejo, el salto es enorme",
    "Comparado con el iPhone 15 Pro Max el S24 Ultra ofrece más funciones pero menos pulido en general",
]


def anonymize(seed: str) -> str:
    return hashlib.sha256(seed.encode()).hexdigest()


def main() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE tweets (
            tweet_id    TEXT PRIMARY KEY,
            created_at  TEXT,
            text        TEXT,
            likes       INTEGER,
            retweets    INTEGER,
            user_hash   TEXT
        )
    """)

    base_date = datetime(2026, 4, 1, 9, 0, 0)
    for i, text in enumerate(COMMENTS, start=1):
        cur.execute(
            "INSERT INTO tweets VALUES (?, ?, ?, ?, ?, ?)",
            (
                f"demo-{i:04d}",
                (base_date + timedelta(hours=i * 7)).isoformat(),
                text,
                (i * 13) % 200,
                (i * 5) % 80,
                anonymize(f"user-{i}"),
            ),
        )

    conn.commit()
    conn.close()

    print(f"Seed completo: {len(COMMENTS)} comentarios → {DB_PATH}")


if __name__ == "__main__":
    main()
