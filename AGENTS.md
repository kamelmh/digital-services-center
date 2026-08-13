# AGENTS.md — Digital Services Center

## Cross-Project Protocol

### Before Starting Work
1. Read this project's `UPDATES.md` for recent changes
2. Check sibling projects' `UPDATES.md` for changes that might affect this project:
   - `../kdp-publishing-copilot/UPDATES.md` — if working on PDF export
   - `../mahi-spiritual/UPDATES.md` — if working on astrology features
   - `../lifeworkspace-teaching-platform/pilot/UPDATES.md` — if working on education features
   - `../../academix-dss/UPDATES.md` — if working on DSS features

### After Finishing Work
1. Append an entry to this project's `UPDATES.md`
2. Include: date, what changed, files affected, breaking changes, alerts for other projects

### Alert System
If your work produces something other projects should know about:
- **Font/encoding changes** → Alert any project generating PDFs
- **API changes** → Alert any project calling this project's code
- **Data format changes** → Alert any project consuming this project's output
- **Breaking changes** → Alert all projects that reference this project

## Project Context
- **Purpose:** Feasibility generator for Algerian businesses (Decree 26-154)
- **Key file:** `feasibility_generator.py`
- **Tech:** Python, Arabic PDF generation (Tahoma font), Streamlit
