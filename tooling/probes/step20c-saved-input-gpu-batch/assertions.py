"""EXPERIMENTAL predicate inventory; classification is not execution coverage."""
import ast
from plans import HERE
from saved_assertions import inventory

CONTRACTS = {
    'input.py': ('event delivery and standard return', 'IPC/wire/native PI/full RGB',
                 'test_input.InputTests.test_real_mutation',
                 'test_input.InputTests.test_negative_owner_output_serial_recipient_local_pending_destroyed_clip'),
    'input_validators.py': ('applied input state', 'timestamped PI + actual Wayland buttons',
                            'test_input.InputTests.test_real_mutation',
                            'test_input.InputTests.test_status_pass_empty'),
    'native_replay.py': ('native output pairing', '(output, commit_seq) raw records',
                         'test_native.NativeTests.test_real_all_821',
                         'test_native.NativeTests.test_wrong_output_fake_present'),
    'gpu_replay.py': ('whole RGB and source identity', 'entire retained PNGs and SHM dumps',
                      'test_gpu_replay.GPUReplayTests.test_real_whole_differences',
                      'test_gpu_replay.GPUReplayTests.test_masked_whole_and_source_buffer_output_falseproof'),
}

def all_assertions():
    # WHY: omissions must be visible before one-shot runtime reservations.
    # CONTRACT: list executable checks with their evidence and regression family.
    # INVARIANT: test-family classification never claims every source site ran.
    rows = inventory()
    for filename, (step, evidence, positive, negative) in CONTRACTS.items():
        path = HERE / filename
        source = path.read_text()
        for n in ast.walk(ast.parse(source)):
            name = n.func.id if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) else ''
            if name in ('require', 'need', 'correlate', 'standard_return', 'wire_delivery', 'exact', 'validate_claims', 'diff'):
                rows.append(dict(file=str(path), line=n.lineno, step=step,
                    predicate=ast.get_source_segment(source, n), evidence=evidence,
                    positive=positive, negative=negative,
                    coverage='regression family; individual runtime-site execution NOT CLAIMED',
                    runtime_dependency='exact A/G runtime where applicable; atomic/GPU generation NOT PROVEN'))
    return sorted(rows, key=lambda r: (r['file'], r['line']))

if __name__ == '__main__':
    import json
    print(json.dumps(all_assertions(), indent=2))
