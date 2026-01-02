---
tags:
  - map/project
  - p/image-workflow
  - type/pipeline
  - domain/image-processing
  - status/active
  - tech/python
  - high-volume
  - mission-critical
created: 2025-12-31
---

# image-workflow

High-volume image processing pipeline that handles 10,000+ images per day through multiple quality control passes. This production system processes 5,000-7,000 real people images plus 4,500 AI-generated images daily, with comprehensive safety systems and disaster recovery built from 2.5+ months of battle-testing. The workflow includes face grouping, version selection, character sorting, pair comparison, and automated cropping with a web dashboard for activity tracking.

## Key Components

### Main Scripts
- `scripts/` - Core processing scripts (237 Python files)
  - Image quality filtering
  - Face grouping algorithms
  - Version selection tools
  - Character sorter
  - Pair comparison engine
  - Crop automation

### Documentation
- `Documents/` - Comprehensive documentation (178 MD files)
  - Architecture guides
  - Safety systems
  - Disaster recovery procedures
  - Session archives

### Tools
- Web dashboard for progress tracking
- Activity timer integration
- Companion file system (PNG+YAML pairs)
- Safety monitoring and alerts

### Data Management
- YAML configuration system
- Session snapshots
- Backup systems
- Archive management

## Status

**Tags:** #map/project #p/image-workflow  
**Status:** #status/active #status/production  
**Last Major Update:** December 2025 (actively maintained)  
**Priority:** #mission-critical #high-volume



## Recent Activity

- **2026-01-01 22:36**: analyze_backups.py: .

- **2026-01-01 22:36**: incremental_backup.py: .

- **2026-01-01 22:37**: incremental_backup.py: .

- **2026-01-01 22:37**: analyze_backups.py: .

- **2026-01-01 22:37**: analyze_backups.py: .

- **2026-01-01 22:38**: incremental_backup.py: .

- **2026-01-01 22:38**: incremental_backup.py: .

- **2026-01-01 22:38**: incremental_backup.py: .

- **2026-01-01 22:38**: analyze_backups.py: .

- **2026-01-01 22:38**: analyze_backups.py: .

- **2026-01-01 22:38**: analyze_backups.py: .

- **2026-01-01 22:39**: analyze_backups.py: .

- **2026-01-01 22:39**: analyze_backups.py: .

