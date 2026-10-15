"""Pure tree identity helpers only; IPC geometry is pending candidate."""
def nodes(node):
    yield node
    for child in node.get('nodes', []) + node.get('floating_nodes', []):
        yield from nodes(child)


def workspace(tree, name):
    rows = [n for n in nodes(tree) if n.get('type') == 'workspace' and n.get('name') == name]
    assert len(rows) == 1, 'workspace identity'
    return rows[0]


def ancestry(tree, con_id, path=()):
    if tree.get('id') == con_id:
        return path + (tree,)
    for child in tree.get('nodes', []) + tree.get('floating_nodes', []):
        found = ancestry(child, con_id, path + (tree,))
        if found:
            return found
    return ()
