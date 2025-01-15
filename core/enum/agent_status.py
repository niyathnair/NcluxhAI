 # Enum for agent subscription and execution statuses
from enum import Enum

class AgentStatus(Enum):
    # General States
    IDLE = "idle"               # Agent is inactive but ready to be activated.
    ACTIVE = "active"           # Agent is actively performing its tasks.
    INACTIVE = "inactive"       # Agent is temporarily disabled or paused.
    INITIALIZING = "initializing"  # Agent is starting up or being initialized.
    TERMINATED = "terminated"   # Agent has been shut down or unsubscribed.

    # Subscription States
    SUBSCRIBED = "subscribed"   # Agent is subscribed and available for use.
    UNSUBSCRIBED = "unsubscribed"  # Agent is not currently subscribed.

    # Task Execution States
    PROCESSING = "processing"   # Agent is currently executing a task.
    WAITING_FOR_INPUT = "waiting_for_input"  # Agent is awaiting input from another agent or user.
    COMPLETED = "completed"     # Agent has successfully completed its task.
    FAILED = "failed"           # Agent encountered an error during execution.

    # Communication States
    SENDING_DATA = "sending_data"   # Agent is transmitting data to another agent.
    RECEIVING_DATA = "receiving_data"  # Agent is receiving data from another agent.

    # Self-Correction and Simulation States
    SIMULATING = "simulating"   # Agent is running a scenario simulation.
    OPTIMIZING = "optimizing"   # Agent is performing self-correction or optimization.
    ADJUSTING = "adjusting"     # Agent is dynamically modifying its strategy or behavior.

    # Error and Recovery States
    ERROR = "error"             # Agent is in an error state and requires intervention.
    RECOVERING = "recovering"   # Agent is attempting to recover from an error.
    DEPRECATED = "deprecated"   # Agent is outdated or replaced and should not be used.

    # Maintenance and Configuration States
    MAINTENANCE = "maintenance" # Agent is undergoing maintenance or updates.
    CONFIGURING = "configuring" # Agent is being configured or customized.

    # Reserved States for Future Expansion
    RESERVED = "reserved"       # Placeholder for future agent-specific statuses.
