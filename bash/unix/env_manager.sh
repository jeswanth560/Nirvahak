#!/usr/bin/env bash

# CHANGE THIS if you use zsh or something else
CONFIG_FILE="$HOME/.zshrc"
# For zsh, use:
# CONFIG_FILE="$HOME/.zshrc"

# Make sure the file exists
touch "$CONFIG_FILE"

show_menu() {
  echo "=========================================="
  echo "  Environment Variable Manager (User)"
  echo "  Config file: $CONFIG_FILE"
  echo "=========================================="
  echo "1) Create or update variable"
  echo "2) Delete variable"
  echo "3) Exit"
  echo
}

read_var_name() {
  echo
  read -r -p "Enter environment variable name: " VAR_NAME
  if [ -z "$VAR_NAME" ]; then
    echo "Variable name cannot be empty."
    return 1
  fi
  return 0
}

get_existing_value() {
  # Look for a line like: export VAR_NAME=...
  existing_line=$(grep -E "^export[[:space:]]+$VAR_NAME=" "$CONFIG_FILE" 2>/dev/null || true)

  if [ -n "$existing_line" ]; then
    EXISTING_VALUE=${existing_line#*=}
    # strip surrounding quotes if any
    EXISTING_VALUE=${EXISTING_VALUE#\"}
    EXISTING_VALUE=${EXISTING_VALUE%\"}
  else
    EXISTING_VALUE=""
  fi
}

create_or_update() {
  if ! read_var_name; then
    read -r -p "Press Enter to continue..." _
    return
  fi

  get_existing_value

  if [ -n "$EXISTING_VALUE" ]; then
    echo
    echo "Variable '$VAR_NAME' already exists."
    echo "Current value: $EXISTING_VALUE"
  else
    echo
    echo "Variable '$VAR_NAME' does not exist yet."
  fi

  echo
  read -r -p "Enter new value for $VAR_NAME: " VAR_VALUE
  if [ -z "$VAR_VALUE" ]; then
    echo "Value cannot be empty."
    read -r -p "Press Enter to continue..." _
    return
  fi

  if [ -n "$EXISTING_VALUE" ]; then
    echo
    echo "New value: $VAR_VALUE"
    read -r -p "Override existing value? (y/n): " CHOICE
    case "$CHOICE" in
      y|Y) ;;
      *) echo "No changes made."; read -r -p "Press Enter to continue..." _; return ;;
    esac
  else
    echo
    echo "Variable will be created with value: $VAR_VALUE"
  fi

  # Remove any existing definition
  grep -Ev "^export[[:space:]]+$VAR_NAME=" "$CONFIG_FILE" > "${CONFIG_FILE}.tmp" || true
  mv "${CONFIG_FILE}.tmp" "$CONFIG_FILE"

  # Append new definition
  echo "export $VAR_NAME=\"$VAR_VALUE\"" >> "$CONFIG_FILE"

  echo
  echo "Saved: export $VAR_NAME=\"$VAR_VALUE\""
  echo "In file: $CONFIG_FILE"
  echo
  echo "To apply this in the current shell, run:"
  echo "  source \"$CONFIG_FILE\""
  echo "New terminals will pick it up automatically."
  read -r -p "Press Enter to continue..." _
}

delete_var() {
  if ! read_var_name; then
    read -r -p "Press Enter to continue..." _
    return
  fi

  get_existing_value

  if [ -z "$EXISTING_VALUE" ]; then
    echo
    echo "Variable '$VAR_NAME' does not exist in $CONFIG_FILE."
    read -r -p "Press Enter to continue..." _
    return
  fi

  echo
  echo "Variable '$VAR_NAME' found with value: $EXISTING_VALUE"
  read -r -p "Are you sure you want to DELETE this variable? (y/n): " CHOICE
  case "$CHOICE" in
    y|Y)
      grep -Ev "^export[[:space:]]+$VAR_NAME=" "$CONFIG_FILE" > "${CONFIG_FILE}.tmp" || true
      mv "${CONFIG_FILE}.tmp" "$CONFIG_FILE"
      echo
      echo "Variable '$VAR_NAME' removed from $CONFIG_FILE."
      echo "Open a new terminal or run: source \"$CONFIG_FILE\""
      ;;
    *)
      echo
      echo "Deletion cancelled."
      ;;
  esac
  read -r -p "Press Enter to continue..." _
}

# Main loop
while true; do
  clear
  show_menu
  read -r -p "Choose an option (1-3): " ACTION

  case "$ACTION" in
    1) create_or_update ;;
    2) delete_var ;;
    3) echo "Exiting..."; exit 0 ;;
    *) echo "Invalid choice."; read -r -p "Press Enter to continue..." _ ;;
  esac
done

