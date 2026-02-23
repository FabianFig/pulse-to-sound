# pulse-to-sound

Transforms Strava activity data into generative ambient sound and live replay visualisations. Each activity becomes something you can listen to or watch back.

## What it will do

**Activity as Sound** - heart rate, cadence, power, and elevation mapped to slowly evolving drones and textures. Inspired by Masakatsu Takagi's Marginalia series, Kali Malone, Yara Asmar.

**Race Replay** - stream any past activity back to the browser second by second via WebSockets. Head-to-head mode to race two efforts against each other.

## Planned stack

- Python, FastAPI, PostgreSQL
- Tone.js / SuperCollider
- D3.js, vanilla JS

## Roadmap

- [ ] Strava API ingestion
- [ ] PostgreSQL schema + loader
- [ ] FastAPI basic endpoints
- [ ] Basic frontend
- [ ] WebSocket replay engine
- [ ] Tone.js audio mapping
- [ ] SuperCollider rendering
- [ ] Deployment
