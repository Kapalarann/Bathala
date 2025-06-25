# utils/inventory.py

from utils.items import normalize_item_name, ABSTRACT_RESOURCES

def transfer_item(characters, source_id, target_id, item, amount=1, base=None):
    """
    Transfer items between characters and/or base inventory.

    Returns:
        (success: bool, transferred_count: int, item_name: str)
    """
    print(f"🔁 Transferring {item} x{amount} from {source_id} to {target_id}")

    item = normalize_item_name(item)

    def get_inventory(entity_id):
        if entity_id == "base":
            if base is None:
                raise ValueError("Base object must be provided when using 'base' as an ID.")
            return base["inventory"]
        if entity_id not in characters:
            raise ValueError(f"Character '{entity_id}' not found.")
        return characters[entity_id]["inventory"]

    try:
        source_inv = get_inventory(source_id)
        target_inv = get_inventory(target_id)
    except ValueError as e:
        print(f"❌ {e}")
        return False, 0, item

    # --- Handle stackable resources ---
    if item in ABSTRACT_RESOURCES:
        matches = [i for i in source_inv if normalize_item_name(i) == item]
        if len(matches) < amount:
            print(f"❌ Not enough '{item}'. Needed {amount}, found {len(matches)}")
            return False, len(matches), item

        for i in matches[:amount]:
            source_inv.remove(i)
            target_inv.append(i)
        return True, amount, item

    # --- Handle single items (non-stackable) ---
    # Prioritize non-equipped versions (do not start with "E:")
    non_equipped_matches = [i for i in source_inv if normalize_item_name(i) == item and not i.startswith("E:")]
    equipped_matches = [i for i in source_inv if normalize_item_name(i) == item and i.startswith("E:")]

    all_matches = non_equipped_matches + equipped_matches

    if len(all_matches) < amount:
        print(f"❌ Not enough '{item}' to transfer. Needed {amount}, found {len(all_matches)}")
        return False, len(all_matches), item

    for i in all_matches[:amount]:
        source_inv.remove(i)
        target_inv.append(i)

    return True, amount, item

def remove_item(entity, item, amount=1):
    """
    Removes a specific number of items from an inventory.

    Args:
        entity: dict containing an 'inventory' list (character or base)
        item: name of item to remove (case-insensitive, normalized)
        amount: number of items to remove

    Returns:
        (success: bool, removed_count: int, item_name: str)
    """
    item = normalize_item_name(item)
    inventory = entity.get("inventory", [])

    print(f"🗑️ Removing {amount}x '{item}' from inventory.")

    if item in ABSTRACT_RESOURCES:
        matches = [i for i in inventory if normalize_item_name(i) == item]
        if len(matches) < amount:
            print(f"❌ Not enough '{item}' to remove. Needed {amount}, found {len(matches)}")
            return False, len(matches), item

        for i in matches[:amount]:
            inventory.remove(i)
        return True, amount, item

    # Handle non-stackable items
    non_equipped = [i for i in inventory if normalize_item_name(i) == item and not i.startswith("E:")]
    equipped = [i for i in inventory if normalize_item_name(i) == item and i.startswith("E:")]

    all_matches = non_equipped + equipped

    if len(all_matches) < amount:
        print(f"❌ Not enough '{item}' to remove. Needed {amount}, found {len(all_matches)}")
        return False, len(all_matches), item

    for i in all_matches[:amount]:
        inventory.remove(i)

    return True, amount, item
