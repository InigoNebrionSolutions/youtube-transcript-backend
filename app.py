from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi

app = Flask(__name__)

def dividir_transcripcion(transcript, max_chars=3000):
    bloques, bloque_actual = [], ""
    for item in transcript:
        fragmento = item["text"] + " "
        if len(bloque_actual) + len(fragmento) > max_chars:
            bloques.append(bloque_actual.strip())
            bloque_actual = fragmento
        else:
            bloque_actual += fragmento
    if bloque_actual:
        bloques.append(bloque_actual.strip())
    return bloques

@app.route("/transcript", methods=["GET"])
def get_transcript():
    video_id = request.args.get("videoId")
    block = int(request.args.get("block", 0))
    max_chars = int(request.args.get("max_chars", 3000))
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['es', 'en'])
        bloques = dividir_transcripcion(transcript, max_chars=max_chars)
        if block < 0 or block >= len(bloques):
            return jsonify({"error": "Bloque fuera de rango"}), 400
        return jsonify({
            "videoId": video_id,
            "blockIndex": block,
            "totalBlocks": len(bloques),
            "text": bloques[block]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
