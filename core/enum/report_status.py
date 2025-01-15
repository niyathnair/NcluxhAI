# Enum for report statuses (e.g., SUCCESS, FAILED)
from enum import Enum

class ReportStatus(Enum):
    # Creation and Generation States
    PENDING = "pending"           # Report is queued for generation but has not started.
    GENERATING = "generating"     # Report is actively being generated.
    GENERATED = "generated"       # Report has been successfully generated.
    FAILED = "failed"             # Report generation failed due to an error.

    # Review and Approval States
    UNDER_REVIEW = "under_review" # Report is being reviewed by stakeholders or system.
    APPROVED = "approved"         # Report has been reviewed and approved.
    REJECTED = "rejected"         # Report has been reviewed and rejected, requiring changes.

    # Distribution States
    DISTRIBUTING = "distributing" # Report is in the process of being shared with relevant parties.
    DISTRIBUTED = "distributed"   # Report has been successfully shared.

    # Archival States
    ARCHIVED = "archived"         # Report has been archived and is no longer active.
    DELETED = "deleted"           # Report has been permanently deleted.

    # Reserved for Future States
    RESERVED = "reserved"         # Placeholder for future report states.
