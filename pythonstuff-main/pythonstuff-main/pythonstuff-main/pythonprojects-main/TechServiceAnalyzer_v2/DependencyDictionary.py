services = {
    "Customer Portal": {
        "depends_on": ["Authentication API", "Claims API"],
        "incidents": [30, 45]
    },
    "Authentication API": {
        "depends_on": ["User Database"],
        "incidents": [20]
    },
    "Claims API": {
        "depends_on": ["Claims Database", "Document Service"],
        "incidents": [60, 90, 30]
    },
    "User Database": {
        "depends_on": [],
        "incidents": [15, 25]
    },
    "Claims Database": {
        "depends_on": ["Storage Service"],
        "incidents": [40]
    },
    "Document Service": {
        "depends_on": ["Storage Service"],
        "incidents": []
    },
    "Storage Service": {
        "depends_on": [],
        "incidents": [50, 70]
    },
    "Unused Reporting Tool": {
        "depends_on": [],
        "incidents": [120]
    }
}