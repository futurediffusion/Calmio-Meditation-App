import json

logros = [
    {"id": 1, "nombre": "Primera respiración consciente", "tipo": "creativo", "emoji": "🌬️"},
    {"id": 2, "nombre": "Meditaste durante 1 min", "tipo": "tiempo", "emoji": "⏱️"},
    {"id": 3, "nombre": "Meditaste durante 5 min", "tipo": "tiempo", "emoji": "🕔"},
    {"id": 4, "nombre": "Meditaste durante 10 min", "tipo": "tiempo", "emoji": "🔟"},
    {"id": 5, "nombre": "Meditaste durante 15 min", "tipo": "tiempo", "emoji": "🕒"},
    {"id": 6, "nombre": "Meditaste durante 20 min", "tipo": "tiempo", "emoji": "🧘"},
    {"id": 7, "nombre": "Meditaste durante 30 min", "tipo": "tiempo", "emoji": "🌀"},
    {"id": 8, "nombre": "Meditaste durante 45 min", "tipo": "tiempo", "emoji": "🌅"},
    {"id": 9, "nombre": "Meditaste durante 60 min", "tipo": "tiempo", "emoji": "⛰️"},
    {"id": 10, "nombre": "Completaste 1 sesión", "tipo": "sesiones", "emoji": "🎉"},
    {"id": 11, "nombre": "Completaste 3 sesiones", "tipo": "sesiones", "emoji": "🥉"},
    {"id": 12, "nombre": "Completaste 5 sesiones", "tipo": "sesiones", "emoji": "🥈"},
    {"id": 13, "nombre": "Completaste 10 sesiones", "tipo": "sesiones", "emoji": "🥇"},
    {"id": 14, "nombre": "Completaste 20 sesiones", "tipo": "sesiones", "emoji": "🏅"},
    {"id": 15, "nombre": "Completaste 30 sesiones", "tipo": "sesiones", "emoji": "🎖️"},
    {"id": 16, "nombre": "Completaste 50 sesiones", "tipo": "sesiones", "emoji": "🏆"},
    {"id": 17, "nombre": "Completaste 100 sesiones", "tipo": "sesiones", "emoji": "👑"},
    {"id": 18, "nombre": "Sesion terminada a las 11:11", "tipo": "easter egg", "emoji": "⏰"},
    {"id": 19, "nombre": "Sesion terminada a las 22:22", "tipo": "easter egg", "emoji": "⏰"},
    {"id": 20, "nombre": "Sesion terminada a las 12:21", "tipo": "easter egg", "emoji": "⏰"},
    {"id": 21, "nombre": "Meditaste 3 días seguidos", "tipo": "progreso", "emoji": "📅"},
    {"id": 22, "nombre": "Meditaste una semana completa", "tipo": "progreso", "emoji": "🗓️"},
    {"id": 23, "nombre": "Meditaste 30 días seguidos", "tipo": "progreso", "emoji": "📆"},
    {"id": 24, "nombre": "Terminaste una sesión de exactamente 12 minutos", "tipo": "tiempo", "emoji": "🕛"},
    {"id": 25, "nombre": "Terminaste una sesión de exactamente 25 minutos", "tipo": "tiempo", "emoji": "⏲️"},
    {"id": 26, "nombre": "Terminaste una sesión de exactamente 33 minutos", "tipo": "tiempo", "emoji": "⌛"},
    {"id": 27, "nombre": "Completaste 2 sesiones en un mismo día", "tipo": "sesiones", "emoji": "🌓"},
    {"id": 28, "nombre": "Completaste 3 sesiones en un mismo día", "tipo": "sesiones", "emoji": "🌔"},
    {"id": 29, "nombre": "Respiraste profundamente por más de 5 minutos sin interrupción", "tipo": "tiempo", "emoji": "🌬️"},
    {"id": 30, "nombre": "Lograste meditar sin distracciones por 1 hora completa", "tipo": "legendario", "emoji": "🛡️"},
]

# Remove easter egg achievements
logros = [l for l in logros if l['tipo'] != 'easter egg']

while len(logros) < 100:
    idx = len(logros) + 1
    logros.append({
        'id': idx,
        'nombre': f'Logro especial #{idx}',
        'tipo': 'especial',
        'emoji': '✨'
    })

with open('logros_meditacion_100.json', 'w', encoding='utf-8') as f:
    json.dump(logros, f, ensure_ascii=False, indent=2)

print('Archivo generado:', 'logros_meditacion_100.json')
