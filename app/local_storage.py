import os
import streamlit as st
import streamlit.components.v1 as components

# Get the path to the component's index.html
parent_dir = os.path.dirname(os.path.abspath(__file__))
component_dir = os.path.join(parent_dir, "components", "local_storage")

# Declare the component
_local_storage_component = components.declare_component(
    "local_storage",
    path=component_dir
)

def local_storage(action: str, key: str = "", value: str = None, operations: list = None, element_key: str = None):
    """
    Interacts with the browser's localStorage using a custom component.
    
    actions:
      - 'get': gets a value by key
      - 'set': sets a value by key
      - 'clear': deletes a value by key
      - 'get_all': retrieves all key-value pairs where key starts with 'session_'
      - 'batch': executes a list of set/clear operations
    """
    return _local_storage_component(
        action=action,
        storage_key=key,
        value=value,
        operations=operations,
        default=None,
        key=element_key
    )
